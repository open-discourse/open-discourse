import pytest

from open_discourse.helper.parser import get_session_content


@pytest.mark.parametrize(
    "text_corpus, expected",
    [
        (
            """2. Sitzung.
Bonn, Montag, den 12. September 1949.
Eidesleistung des Bundespräsidenten . . . 9A
Ansprache des Bundespräsidenten Dr. Heuss 9C
Schlußworte des Präsidenten Dr. Köhler . 11D
Die Sitzung wird um 19 Uhr 18 Minuten durch den Präsidenten Dr. Köhler eröffnet.
Wir werden nunmehr den Herrn Bundespräsidenten hinausgeleiten.
Ich schließe die Sitzung.
(Schluß der Sitzung: 19 Uhr 43 Minuten.)""",
            """.\nWir werden nunmehr den Herrn Bundespräsidenten hinausgeleiten.
Ich schließe die Sitzung.\n""",
        ),
        pytest.param(
            """Die Sitzung wird um 16 Uhr 16 Minuten durch
den Präsidenten Dr. Köhler eröffnet.
Ich breche die Sitzung ab und vertage auf morgen vormittag 11 Uhr.
Die Sitzung ist geschlossen.
(Schluß der Sitzung: 19 Uhr 44 Minuten.)""",
            """.\nIch breche die Sitzung ab und vertage auf morgen vormittag 11 Uhr.
Die Sitzung ist geschlossen.\n""",
            marks=pytest.mark.xfail(
                reason="This test is expected to fail due to known issue with handling line breaks in the regex"
            ),
        ),
        (
            """Die Sitzung wird um 9 Uhr 2 Minuten durch den Vizepräsidenten Dr. Schmid eröffnet.
Test
(Schluß der Sitzung: 20 Uhr 51 Minuten.)""",
            """.\nTest\n""",
        ),
    ],
)
def test_get_session_content(text_corpus, expected):
    assert get_session_content(text_corpus) == expected
