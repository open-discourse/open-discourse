from bs4 import BeautifulSoup
import od_lib.definitions.path_definitions as path_definitions
from od_lib.helper_functions.progressbar import progressbar
import requests
import regex
from urllib.parse import urljoin

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
    {
        "election_period": 21,
        "url": "https://www.bundestag.de/ajax/filterlist/de/services/opendata/1058442-1058442?offset={}",  # noqa
    },
]



for election_period in election_periods:
    print(
        f"Scraping links for term {election_period['election_period']}...",
        end="",
        flush=True,
    )
    OUTPUT_PATH = ELECTORAL_TERM_19_20_OUTPUT / "electoral_term_{}".format(
        election_period["election_period"]
    )
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    offset = 0
    xml_links = []
    while True:
        URL = election_period["url"].format(str(offset))
        page = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(page.text, "html.parser")
        # scrape for links
        current_links = list(soup.find_all("a", attrs={"href": regex.compile("xml$")}))
        # doc-offset calculated from link-count (dedup desktop+mobile version!)
        seen_hrefs = {}
        for link in current_links:
            seen_hrefs.setdefault(link.get("href"), link)
        current_links = list(seen_hrefs.values())
        if len(current_links) != 0:
            xml_links += current_links
            offset += len(current_links)
        else:
            break
    print("Done.")

    for link in progressbar(
        xml_links,
        f"Download XML-files for term {election_period['election_period']}...",
    ):
        url = urljoin("https://www.bundestag.de", link.get("href"))
        session = regex.search(r"\d{5}(?=\.xml)", url).group(0)
        target_path = OUTPUT_PATH / (session + ".xml")

        if target_path.exists():
            continue

        page = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        with open(target_path, "w") as file:
            file.write(
                regex.sub(
                    "</sub>",
                    "",
                    regex.sub("<sub>", "", page.content.decode("utf-8")),
                )
            )
