from collections import namedtuple
from xml.etree.ElementTree import ParseError

import pytest
import regex

import open_discourse.definitions.path as path
from open_discourse.steps.preprocessing.split_xml import (
    define_single_session_regex_pattern,
    split_single_session_xml_data,
)

# Definition Named Tuple for test cases, don't name it Testcase!!!
CaseDataforTest = namedtuple("CaseDataforTest", ["input", "expected", "exception"])

RAW_XML = path.RAW_XML
RAW_TXT = path.RAW_TXT


# ========================================
# test cases for test_pp_split_xml_data (list of namedtuple)
# ========================================
test_cases = []

test_cases.append(
    CaseDataforTest(
        ("Testdummy1.xml", "<root><invalid></root>"),
        expected=None,
        exception=ParseError,
    )
)
test_cases.append(
    CaseDataforTest(("Testdummy2.xml", "<root>"), expected=None, exception=ParseError)
)
test_cases.append(
    CaseDataforTest(
        ("Testdummy3.xml", "invalid content"), expected=None, exception=ParseError
    )
)
test_cases.append(
    CaseDataforTest(
        ("Testdummy3.doc", "invalid content"),
        expected=None,
        exception=FileNotFoundError,
    )
)

# ----------
# Tests with same metadate
expected_metadata = {
    "term": "3",
    "document_type": "PLENARPROTOKOLL",
    "document_number": "03/4",
    "date": "05.11.1957",
}

xml = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE DOKUMENT SYSTEM "BUNDESTAGSDOKUMENTE.dtd">
<DOKUMENT>
  <WAHLPERIODE>3</WAHLPERIODE>
  <DOKUMENTART>PLENARPROTOKOLL</DOKUMENTART>
  <NR>03/4</NR>
  <DATUM>05.11.1957</DATUM>
  <TITEL>Plenarprotokoll vom 05.11.1957</TITEL>
  <TEXT>Deutscher Bundestag — 3. Wahlperiode — 4. Sitzung. Bonn, Dienstag,
den 5. November 1957
4. Sitzung
Bonn, den 5. November 1957
Inhalt:
Die Sitzung ist geschlossen.
(Schluß: 17.53 Uhr.)
Fürst von Bismarck	20. 12.
Kühlthau	25. 11.
Scheel	15. 12.</TEXT>
</DOKUMENT>
"""
text = """Deutscher Bundestag — 3. Wahlperiode — 4. Sitzung. Bonn, Dienstag,
den 5. November 1957
4. Sitzung
Bonn, den 5. November 1957
Inhalt:
Die Sitzung ist geschlossen.
(Schluß: 17.53 Uhr.)
Fürst von Bismarck	20. 12.
Kühlthau	25. 11.
Scheel	15. 12."""
test_cases.append(CaseDataforTest(("03004.xml", xml), (expected_metadata, text), None))
test_cases.append(CaseDataforTest(("03005.xml", xml), (expected_metadata, text), None))
# Filename inconsistent to tag NR

xml = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE DOKUMENT SYSTEM "BUNDESTAGSDOKUMENTE.dtd">
<DOKUMENT>
  <WAHLPERIODE>3</WAHLPERIODE>
  <DOKUMENTART>PLENARPROTOKOLL</DOKUMENTART>
    <DATUM>05.11.1957</DATUM>
  <TITEL>Plenarprotokoll vom 05.11.1957</TITEL>
  <TEXT>Deutscher Bundestag — 3. Wahlperiode — 4. Sitzung. Bonn, Dienstag,
  den 5. November 1957
4. Sitzung
Bonn, den 5. November 1957
Inhalt:
Die Sitzung ist geschlossen.
(Schluß: 17.53 Uhr.)
Fürst von Bismarck	20. 12.
Kühlthau	25. 11.
Scheel	15. 12.</TEXT>
</DOKUMENT>
"""
test_cases.append(
    CaseDataforTest(("03004.xml", xml), (expected_metadata, text), AttributeError)
)  # Tag <NR> fehlt

xml = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE DOKUMENT SYSTEM "BUNDESTAGSDOKUMENTE.dtd">
<DOKUMENT>
  <WAHLPERIODE>3</WAHLPERIODE>
  <DOKUMENTART>PLENARPROTOKOLL</DOKUMENTART>
  <NR>03/4</NR>
  <DATUM>05.11.1957</DATUM>
  <TITEL>Plenarprotokoll vom 05.11.1957</TITEL>
  TEXT>Deutscher Bundestag — 3. Wahlperiode — 4. Sitzung. Bonn, Dienstag,
  den 5. November 1957
4. Sitzung
Bonn, den 5. November 1957
Inhalt:
Die Sitzung ist geschlossen.
(Schluß: 17.53 Uhr.)
Fürst von Bismarck	20. 12.
Kühlthau	25. 11.
Scheel	15. 12.</TEXT>
</DOKUMENT>
"""
test_cases.append(
    CaseDataforTest(("03004.xml", xml), (expected_metadata, text), ParseError)
)  # Fehlerhafter Tag TEXT
# ----------

# TC4
expected_metadata = {
    "term": "4",
    "document_type": "PLENARPROTOKOLL",
    "document_number": "04/19",
    "date": "14.03.1962",
}
xml = """<DOKUMENT>
    <WAHLPERIODE>4</WAHLPERIODE>
    <DOKUMENTART>PLENARPROTOKOLL</DOKUMENTART>
    <NR>04/19</NR>
    <DATUM>14.03.1962</DATUM>
    <TITEL>Plenarprotokoll vom 14.03.1962</TITEL>
    <TEXT>Deutscher Bundestag
    </TEXT>
    </DOKUMENT>"""
test_cases.append(
    CaseDataforTest(
        ("04019.xml", xml),
        expected=(expected_metadata, "Deutscher Bundestag\n    "),
        exception=None,
    )
)


@pytest.mark.parametrize("case", test_cases)
def test_pp_split_xml_data(tmp_path, case: namedtuple):
    # create temp_files for test
    temp_file_1 = tmp_path / case.input[0]
    temp_file_1.write_text(case.input[1], encoding="utf-8")

    if case.exception:
        with pytest.raises(case.exception):
            split_single_session_xml_data(temp_file_1)
    else:
        result = split_single_session_xml_data(temp_file_1)
        assert result[0] == case.expected[0]
        assert result[1] == case.expected[1]


# ========================================
# test cases for define_single_session_regex_pattern (list of namedtuple)
# ========================================
test_cases = []

meta_data = {"document_number": "04/019"}
begin_pattern_default = regex.compile(
    r"Beginn?:?\s?(\d){1,2}(\s?[.,]\s?(\d){1,2})?\s?Uhr"
)
appendix_pattern_default = regex.compile(
    r"\(Schlu(ß|ss)\s?:?(.*?)\d{1,2}\D+(\d{1,2})?(.*?)\)?|\(Ende der Sitzung: \d{"
    r"1,2}\D+(\d{1,2}) Uhr\.?\)"
)
test_cases.append(
    CaseDataforTest(
        meta_data,
        expected=(begin_pattern_default, appendix_pattern_default),
        exception=None,
    )
)

meta_data = {"document_number": "17/250"}
begin_pattern = regex.compile(r"Beginn: 9.02 Uhr(?=\nPräsident)")
appendix_pattern = regex.compile(r"\(Schluss: 0.52 Uhr\)\n\nIch")
test_cases.append(
    CaseDataforTest(
        meta_data,
        expected=(begin_pattern, appendix_pattern),
        exception=None,
    )
)


@pytest.mark.parametrize("case", test_cases)
def test_pp_define_regex_pattern(case: namedtuple):
    if case.exception:
        with pytest.raises(case.exception):
            define_single_session_regex_pattern(case.input)
    else:
        result = define_single_session_regex_pattern(case.input)
        assert result == case.expected
