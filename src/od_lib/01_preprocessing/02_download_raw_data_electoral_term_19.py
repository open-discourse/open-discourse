from bs4 import BeautifulSoup
import od_lib.definitions.path_definitions as path_definitions
import requests
import os
import regex

# output directory
ELECTORAL_TERM_19_OUTPUT = path_definitions.ELECTORAL_TERM_19_STAGE_01

if not os.path.exists(ELECTORAL_TERM_19_OUTPUT):
    os.makedirs(ELECTORAL_TERM_19_OUTPUT)

ROOT_URL = "https://www.bundestag.de/ajax/filterlist/de/services/opendata/543410-543410?offset="

reached_end = False
offset = 0

while not reached_end:
    URL = ROOT_URL + str(offset)
    page = requests.get(URL)

    soup = BeautifulSoup(page.text, "html.parser")
    reached_end = True

    # scrape for links
    for link in soup.find_all("a", attrs={"href": regex.compile("xml$")}):
        reached_end = False
        url = "https://www.bundestag.de" + link.get("href")
        page = requests.get(url)
        session = regex.search(r"\d{5}(?=-data\.xml)", url).group(0)

        print(session)
        with open(
            os.path.join(ELECTORAL_TERM_19_OUTPUT, session + ".xml"), "wb"
        ) as file:
            file.write(page.content)
    offset += 10
