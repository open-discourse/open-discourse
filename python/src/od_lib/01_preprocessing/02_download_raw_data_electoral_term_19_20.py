from bs4 import BeautifulSoup
import od_lib.definitions.path_definitions as path_definitions
from od_lib.helper_functions.progressbar import progressbar
import requests
import regex
import time

# output directory
ELECTORAL_TERM_19_20_OUTPUT = path_definitions.ELECTORAL_TERM_19_20_STAGE_01
ELECTORAL_TERM_19_20_OUTPUT.mkdir(parents=True, exist_ok=True)

election_periods = [
    {
        "election_period": 19,
        "url": "https://www.bundestag.de/ajax/filterlist/de/services/opendata/543410-543410?offset={}",  # noqa
    },
    {
        "election_period": 20,
        "url": "https://www.bundestag.de/ajax/filterlist/de/services/opendata/866354-866354?offset={}",  # noqa
    },
]

xml_links = []

for election_period in election_periods:
    print(
        f"Scraping links for election period {election_period['election_period']}...",
        end="",
        flush=True,
    )
    OUTPUT_PATH = ELECTORAL_TERM_19_20_OUTPUT / "electoral_term_{}".format(
        election_period["election_period"]
    )
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    offset = 0

    while True:
        URL = election_period["url"].format(str(offset))
        page = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(page.text, "html.parser")
        # scrape for links
        current_links = list(soup.find_all("a", attrs={"href": regex.compile("xml$")}))
        if len(current_links) != 0:
            reached_end = False
            xml_links += current_links
            offset += len(current_links)
        else:
            break
    print("Done.")

for link in progressbar(xml_links, "Downloading XML-files..."):
    url = "https://www.bundestag.de" + link.get("href")
    page = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    session = regex.search(r"\d{5}(?=\.xml)", url).group(0)

    with open(OUTPUT_PATH / (session + ".xml"), "w") as file:
        file.write(
            regex.sub(
                "</sub>",
                "",
                regex.sub("<sub>", "", page.content.decode("utf-8")),
            )
        )
