import numpy as np
import regex


def clean(filetext: str, remove_pdf_header: bool = True) -> str:
    # Replaces all the misrecognized characters
    filetext = filetext.replace(r"", "-")
    filetext = filetext.replace(r"", "-")
    filetext = filetext.replace("—", "-")
    filetext = filetext.replace("–", "-")
    filetext = filetext.replace("•", "")
    filetext = regex.sub(r"\t+", " ", filetext)
    filetext = regex.sub(r"  +", " ", filetext)

    # Remove pdf artifact
    if remove_pdf_header:
        filetext = regex.sub(
            r"(?:Deutscher\s?Bundestag\s?-(?:\s?\d{1,2}\s?[,.]\s?Wahlperiode\s?-)?)?\s?\d{1,3}\s?[,.]\s?Sitzung\s?[,.]\s?(?:(?:Bonn|Berlin)[,.])?\s?[^,.]+,\s?den\s?\d{1,2}\s?[,.]\s?[^\d]+\d{4}.*",
            r"\n",
            filetext,
        )
        filetext = regex.sub(r"\s*(\(A\)|\(B\)|\(C\)|\(D\))", "", filetext)

    # Remove delimeter
    filetext = regex.sub(r"-\n+(?![^(]*\))", "", filetext)

    # Deletes all the newlines in brackets
    filetext = remove_newlines_in_brackets(filetext)

    return filetext


def remove_newlines_in_brackets(filetext: str) -> str:
    # Finds all text within parentheses, including nested parentheses
    bracket_text = regex.finditer(r"\(([^(\)]*(\(([^(\)]*)\))*[^(\)]*)\)", filetext)

    for bracket in bracket_text:
        bracket_text = bracket.group()

        # Remove hyphen followed by newline if not preceded by "Abg." or if it is part of a text within square brackets
        bracket_text = regex.sub(
            r"(^((?<!Abg\.).)+|^.*\[.+)(-\n+)",
            r"\1",
            bracket_text,
            flags=regex.MULTILINE,
        )
        # Replace newline with spaces
        bracket_text = regex.sub(r"\n+", " ", bracket_text)
        # Replace the original text with the cleaned text
        filetext = filetext.replace(bracket.group(), bracket_text)

    return filetext


def clean_name_headers(
    filetext: str, names: list[str], contributions_extended_filter: bool = False
):
    """Cleans lines a given text which remained from the pdf header.
    Usually something like: "Präsident Dr. Lammert"
    Keep in mind this also deletes lines from voting lists.
    """
    if contributions_extended_filter:
        table = {ord(c): "" for c in "()[]{}"}
        names = np.unique([name.translate(table) for name in names])

    table = {ord("+"): "\\+", ord("*"): "\\*", ord("?"): "\\?"}
    names_to_clean = ("(" + "|".join(names) + ")").translate(table)
    pattern = (
        r"\n((?:Parl\s?\.\s)?Staatssekretär(?:in)?|Bundeskanzler(?:in)?|Bundesminister(?:in)?|Staatsminister(:?in)?)?\s?"
        + names_to_clean
        + r" *\n"
    )
    filetext = regex.sub(pattern, "\n", filetext)

    pattern = r"\n\d+ *\n"

    filetext = regex.sub(pattern, "\n", filetext)

    return filetext
