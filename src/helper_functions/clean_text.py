import numpy as np
import regex
import regex


def clean(filetext, remove_pdf_header=True):
    # Replaces all the misplaced hyphens
    filetext = filetext.replace(r"", "-")  # What is replaced here?
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

    # Remove delimeter (maybe delete the first one?)
    filetext = regex.sub(r"-\n+(?![^(]*\))", "", filetext)

    # Delete all the newlines in speaker names:
    # speaker_newlines = regex.findall(r"(?<=\n).*(?:\n.*){1,3}:", filetext)

    # for newline in speaker_newlines:
    #     filetext = filetext.replace(str(newline), regex.sub(r"[-]?\n+", ' ', str(newline)))

    # Deletes all the newlines in brackets
    bracket_text = regex.finditer(r"\(([^(\)]*(\(([^(\)]*)\))*[^(\)]*)\)", filetext)

    for bracket in bracket_text:
        filetext = filetext.replace(
            str(bracket.group()),
            regex.sub(
                r"\n+",
                " ",
                regex.sub(
                    r"(^((?<!Abg\.).)+|^.*\[.+)(-\n+)",
                    r"\1",
                    str(bracket.group()),
                    flags=regex.MULTILINE,
                ),
            ),
        )
    return filetext


def clean_name_headers(filetext, names, contributions_filter=False):
    """ Cleans in a given text lines which remained from the header.
        Usually something like: "Präsident Dr. Lammert"
        Keep in mind this also deletes lines from voting lists.
    """
    names = np.unique(names)
    if contributions_filter:
        for counter, name in enumerate(names):
            names[counter] = regex.sub(r"[()\[\]\{\}]", "", name)

    names_to_clean = "(" + "|".join(np.unique(names)) + ")"
    names_to_clean = regex.sub(r"\+", "\\+", names_to_clean)
    names_to_clean = regex.sub(r"\*", "\\*", names_to_clean)
    names_to_clean = regex.sub(r"\?", "\\?", names_to_clean)
    pattern = (
        r"\n((?:Parl\s?\.\s)?Staatssekretär(?:in)?|Bundeskanzler(?:in)?|Bundesminister(?:in)?|Staatsminister(:?in)?)?\s?"
        + names_to_clean
        + " *\n"
    )
    filetext = regex.sub(pattern, "\n", filetext)

    pattern = "\n\d+ *\n"

    filetext = regex.sub(pattern, "\n", filetext)

    return filetext
