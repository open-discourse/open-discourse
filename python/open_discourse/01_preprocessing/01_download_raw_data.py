import io
import zipfile

import regex
import requests

import open_discourse.definitions.path_definitions as path_definitions

# output directory
RAW_XML = path_definitions.RAW_XML

zip_links = [
    "https://www.bundestag.de/resource/blob/490392/90738376bb195628b95d117ab5392cfe/pp18-data.zip",
    "https://www.bundestag.de/resource/blob/490378/033276846771aac12dd7109724a1134b/pp17-data.zip",
    "https://www.bundestag.de/resource/blob/490386/80886372e6bbe903dd4d7eb03fe424b3/pp16-data.zip",
    "https://www.bundestag.de/resource/blob/490394/08411d0257e9e07daef24001a958db53/pp15-data.zip",
    "https://www.bundestag.de/resource/blob/490380/c4ca5488b447668f802039f1f769b278/pp14-data.zip",
    "https://www.bundestag.de/resource/blob/490388/84914a1feff6f2f4988ce352a5500845/pp13-data.zip",
    "https://www.bundestag.de/resource/blob/490376/8775517464dccd8660eb96446d18dd26/pp12-data.zip",
    "https://www.bundestag.de/resource/blob/490384/ad57841a599aba6faa794174e53a8797/pp11-data.zip",
    "https://www.bundestag.de/resource/blob/490374/07ce06f666b624d37b47d2fe6e205ab4/pp10-data.zip",
    "https://www.bundestag.de/resource/blob/490382/effcc03f3b3e157f9d8050b4a9d9d089/pp09-data.zip",
    "https://www.bundestag.de/resource/blob/490390/dfcac024ce8e548774e16f03c36293e2/pp08-data.zip",
    "https://www.bundestag.de/resource/blob/488222/b10bae395e887aac9ac08afbd1da62fc/pp07-data.zip",
    "https://www.bundestag.de/resource/blob/488220/b2b4d0d49600ef852d15e4052fabce1e/pp06-data.zip",
    "https://www.bundestag.de/resource/blob/488218/bfba1a02d1090efc873f9a60f318a162/pp05-data.zip",
    "https://www.bundestag.de/resource/blob/488216/3b20f8dd5efad2cafa3fb0b6df24cbb9/pp04-data.zip",
    "https://www.bundestag.de/resource/blob/487970/1c737594587745b399e84bc30f049d69/pp03-data.zip",
    "https://www.bundestag.de/resource/blob/487968/5792895a5cf4ab51ed94c77157297031/pp02-data.zip",
    "https://www.bundestag.de/resource/blob/487966/4078f01fb3198dc3cee8945d6db3b231/pp01-data.zip",
]


for link in zip_links:
    # Extract election period from URL
    electoral_term_str = "electoral_term_" + regex.search(
        r"(?<=pp)\d+(?=-data\.zip)", link
    ).group(0)

    print(f"Download & unzip '{electoral_term_str}'...", end="", flush=True)

    r = requests.get(link)

    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        save_path = RAW_XML / electoral_term_str
        save_path.mkdir(parents=True, exist_ok=True)
        z.extractall(save_path)

    print("Done.")


# Download MDB Stammdaten.
mp_base_data_link = "https://www.bundestag.de/resource/blob/472878/7d4d417dbb7f7bd44508b3dc5de08ae2/MdB-Stammdaten-data.zip"

print("Download & unzip 'MP_BASE_DATA'...", end="", flush=True)

r = requests.get(mp_base_data_link)

with zipfile.ZipFile(io.BytesIO(r.content)) as z:
    mp_base_data_path = path_definitions.DATA_RAW / "MP_BASE_DATA"
    mp_base_data_path.mkdir(parents=True, exist_ok=True)

    z.extractall(mp_base_data_path)

print("Done.")
