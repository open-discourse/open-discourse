from bs4 import BeautifulSoup
import od_lib.definitions.path_definitions as path_definitions
import pandas as pd
import regex
import requests
import os


# Output directory _____________________________________________________________
POLITICIANS_STAGE_01 = path_definitions.POLITICIANS_STAGE_01
save_path = os.path.join(POLITICIANS_STAGE_01 + "/government_members.pkl")

if not os.path.exists(POLITICIANS_STAGE_01):
    os.makedirs(POLITICIANS_STAGE_01)

URL = "https://de.wikipedia.org/wiki/Liste_der_deutschen_Regierungsmitglieder_seit_1949"

page = requests.get(URL)
soup = BeautifulSoup(page.text, "html.parser")
main_section = soup.find("div", {"id": "mw-content-text"})

government_members = {
    "ui": [],
    "last_name": [],
    "first_name": [],
    "position": [],
    "position_from": [],
    "position_until": [],
    "birth_year": [],
    "death_year": [],
    "party": [],
    "additional_party": [],
}

ui = 0

for div in main_section.find_all("div", recursive=False):
    for ul in div.find_all("ul", recursive=False):
        for li in ul.find_all("li", recursive=False):
            find_all_a = li.find_all("a", recursive=False)
            name = find_all_a[0].text

            if "Liste" in name or "Kabinett" in name:
                break

            # This lines exclude Kristine Schröder because of her name change
            # due to marriage she has another structure in here HTML part, and
            # CDU is matched as name.
            # ToDo: Add second name as a entry at the end, not that important
            # as she is member of StammdatenXML
            if "CDU" in name:
                continue
                # government_members["first_name"].append("Kristina")
                # government_members["last_name"].append("Schröder")
                # party = "CDU"
                # government_members["party"][-1] = party

            name = name.split(" ")
            first_name = name[:-1]
            last_name = name[-1]

            if len(find_all_a) > 2:
                party = find_all_a[1].text
                additional_party = find_all_a[2].text
            elif len(find_all_a) == 2:
                party = find_all_a[1].text
                additional_party = ""
            else:
                party = "parteilos"
                additional_party = ""

            birth_death = li.a.next_sibling.strip()

            match_years = regex.findall(r"(\d{4})", birth_death)
            if len(match_years) == 1:
                birth_year = int(match_years[0])
                death_year = -1
            elif len(match_years) == 2:
                birth_year = int(match_years[0])
                death_year = int(match_years[1])
            else:
                raise ValueError("Something is wrong heregex.")

            # Iterate over government position of the current politician.
            for pos in li.find_all("li"):
                pos = pos.text
                match_years = regex.findall(r"(\d{4})", pos)
                if len(match_years) == 2:
                    # Example: "1974–1980 Verkehr und Post- und Fernmeldewesen"
                    position_from = int(match_years[0])
                    position_until = int(match_years[1])
                    position_full = pos.split(" ", 1)
                    if len(position_full) == 2:
                        position = position_full[1]
                    else:
                        print(name)
                        raise ValueError("What is the position?")

                elif len(match_years) == 1:
                    if "seit" in pos:
                        # Example: "seit 2018 Arbeit und Soziales"
                        position_from = int(match_years[0])
                        position_until = -1
                        pos = pos.split(" ", 1)[1]
                        pos = pos.split(" ", 1)
                        position = pos[1]
                    else:
                        # Example: "1969 Justiz"
                        pos = pos.split(" ", 1)
                        position = pos[1]
                        position_from = position_until = 2018

                elif len(match_years) == 4:
                    # Example: "1969–1982, 1982–1983 Keks Beauftragter"
                    position = pos.split(" ", 1)[1]
                    position = position.split(" ", 1)[1]
                    position_from = int(match_years[0])
                    position_until = int(match_years[1])

                    # Position will be appended twice. Here and below after
                    # the if statement.
                    government_members["ui"].append("gov_" + str(ui))
                    government_members["first_name"].append(first_name)
                    government_members["last_name"].append(last_name)
                    government_members["position"].append(position)
                    government_members["position_from"].append(position_from)
                    government_members["position_until"].append(position_until)
                    government_members["birth_year"].append(birth_year)
                    government_members["death_year"].append(death_year)
                    government_members["party"].append(party)
                    government_members["additional_party"].append(additional_party)

                    position_from = int(match_years[2])
                    position_until = int(match_years[3])

                else:
                    raise ValueError("Still something wrong")

                government_members["ui"].append("gov_" + str(ui))
                government_members["first_name"].append(first_name)
                government_members["last_name"].append(last_name)
                government_members["position"].append(position)
                government_members["position_from"].append(position_from)
                government_members["position_until"].append(position_until)
                government_members["birth_year"].append(birth_year)
                government_members["death_year"].append(death_year)
                government_members["party"].append(party)
                government_members["additional_party"].append(additional_party)

            ui += 1

government_members = pd.DataFrame(government_members)
government_members.to_pickle(save_path)
