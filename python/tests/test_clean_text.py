import pytest

from open_discourse.helper.clean_text import (
    clean,
    remove_newlines_in_brackets,
)


def test_clean_replaces_misrecognized_characters():
    input_text = "  — – •"
    expected_output = "- - - - "
    assert clean(input_text, remove_pdf_header=False) == expected_output


def test_clean_removes_pdf_header():
    input_text = "Deutscher Bundestag - 19. Wahlperiode - 123. Sitzung, Berlin, den 12. März 2020\nSome text"
    expected_output = "\n\nSome text"
    assert clean(input_text, remove_pdf_header=True) == expected_output

    input_test = """Das steht auch im Einklang mit den Beschlüssen, die in dieser Organisation mehrfach ge-
Deutscher Bundestag — 6. Wahlperiode — 21. Sitzung. Bonn, Freitag, den 12. Dezember 1969	753
faßt worden sind."""
    expected_output = """Das steht auch im Einklang mit den Beschlüssen, die in dieser Organisation mehrfach gefaßt worden sind."""
    assert clean(input_test, remove_pdf_header=True) == expected_output


def test_clean_removes_delimiter():
    input_text = "This is a test-\ntext"
    expected_output = "This is a testtext"
    assert clean(input_text, remove_pdf_header=False) == expected_output


def test_clean_deletes_newlines_in_brackets():
    input_text = "This is a (test\ntext) with (multiple\nlines)"
    expected_output = "This is a (test text) with (multiple lines)"
    assert clean(input_text, remove_pdf_header=False) == expected_output


def test_clean_combined():
    input_text = "  — – •\nDeutscher Bundestag - 19. Wahlperiode - 123. Sitzung, Berlin, den 12. März 2020\nThis is a test-\ntext with (multiple\nlines)"
    expected_output = "- - - - \n\n\nThis is a testtext with (multiple lines)"
    assert clean(input_text, remove_pdf_header=True) == expected_output


@pytest.mark.parametrize(
    "input_text, expected_output",
    [
        ("This is a (test\ntext)", "This is a (test text)"),
        (
            "This is a (test\ntext) with (multiple\nlines)",
            "This is a (test text) with (multiple lines)",
        ),
        (
            "This is a (test (nested\ntext) example)",
            "This is a (test (nested text) example)",
        ),
        (
            "This is a (complex (nested\ntext) example\nwith multiple\nlines)",
            "This is a (complex (nested text) example with multiple lines)",
        ),
        (
            """(Abg. Wehner: „Nicht einmal" ist gut! —
Weitere Zurufe)""",
            """(Abg. Wehner: „Nicht einmal" ist gut! — Weitere Zurufe)""",
        ),
        (
            """(Abg. Dr. Mommer: Wirtschaftspolitik,
Außenhandelsfragen, Verkehr, Sozialpolitik und innere Verwaltung! — Abg.
Schoettle: Wozu denn? — Abg. Albers:
Das ist doch ein bißchen viel; die Hälfte
genügte hier auch!)""",
            """(Abg. Dr. Mommer: Wirtschaftspolitik, Außenhandelsfragen, Verkehr, Sozialpolitik und innere Verwaltung! — Abg. Schoettle: Wozu denn? — Abg. Albers: Das ist doch ein bißchen viel; die Hälfte genügte hier auch!)""",
        ),
        (
            """(Abg. Müller-
Dash should remain)""",
            """(Abg. Müller- Dash should remain)""",
        ),
        (
            """(This is a test-
text with some lines)""",
            "(This is a testtext with some lines)",
        ),
    ],
)
def test_remove_newlines_in_brackets(input_text, expected_output):
    assert remove_newlines_in_brackets(input_text) == expected_output
