import regex

FACTIONS = {
    "Bündnis 90/Die Grünen": regex.compile(
        r"(?:BÜNDNIS\s*(?:90)?/?(?:\s*D[1I]E)?|Bündnis\s*90/(?:\s*D[1I]E)?)?\s*[GC]R[UÜ].?\s*[ÑN]EN?(?:/Bündnis 90)?"
    ),
    # TODO Will be used later, til thennwe use the version which reproduces the errors
    # "Bündnis 90/Die Grünen": regex.compile(
    #     r"(?:BÜNDNIS\s*(?:90)?/?(?:\s*D[1I]E)?|Bündnis\s*90/(?:\s*D[1I]E)?)?\s*[GC]R[UÜ].?\s*[ÑN]EN?(?:/Bündnis 90)?|Bündnis 90/Die Grünen"
    # ),
    "CDU/CSU": regex.compile(
        r"(?:Gast|-)?(?:\s*C\s*[DSMU]\s*S?[DU]\s*(?:\s*[/,':!.-]?)*\s*(?:\s*C+\s*[DSs]?\s*[UÙ]?\s*)?)(?:-?Hosp\.|-Gast|1)?"
    ),
    "BP": regex.compile(r"^BP"),
    "DA": regex.compile(r"^DA"),
    "DP": regex.compile(r"^DP"),
    "DIE LINKE.": regex.compile("DIE LINKE"),
    "DPB": regex.compile(r"(?:^DPB)"),
    "DRP": regex.compile(r"DRP(\-Hosp\.)?|SRP"),
    "FDP": regex.compile(r"\s*F\.?\s*[PDO][.']?[DP]\.?"),
    "Fraktionslos": regex.compile(r"(?:fraktionslos|Parteilos|parteilos)"),
    "FU": regex.compile(r"^FU"),
    "FVP": regex.compile(r"^FVP"),
    "Gast": regex.compile(r"Gast"),
    "GB/BHE": regex.compile(r"(?:GB[/-]\s*)?BHE(?:-DG)?"),
    "KPD": regex.compile(r"^KPD"),
    "PDS": regex.compile(r"(?:Gruppe\s*der\s*)?PDS(?:/(?:LL|Linke Liste))?"),
    "SPD": regex.compile(r"\s*'?S(?:PD|DP)(?:\.|-Gast)?"),
    "SSW": regex.compile(r"^SSW"),
    "SRP": regex.compile(r"^SRP"),
    "WAV": regex.compile(r"^WAV"),
    "Z": regex.compile(r"^Z$"),
    "AfD": regex.compile(r"^AfD$"),
    "DBP": regex.compile(r"^DBP$"),
    "NR": regex.compile(r"^NR$"),
}
