import os
from dotenv import load_dotenv

load_dotenv()

MODE = os.getenv("MODE", "thesis")  # thesis or public
ENV = os.getenv("ENV", "dev")  # dev or prod

if MODE == "thesis":
    CORPUS_PATH = "data/static_corpus"
    ENABLE_TRANSFORMERS = True
else:
    CORPUS_PATH = "data/uploads"
    ENABLE_TRANSFORMERS = False

if ENV == "dev":
    GEOIP_COUNTRY_DB = "./GeoLite2-Country.mmdb"
    GEOIP_CITY_DB = "./GeoLite2-City.mmdb"
elif ENV == "prod":
    GEOIP_COUNTRY_DB = "/opt/GeoLite2-Country.mmdb"
    GEOIP_CITY_DB = "/opt/GeoLite2-City.mmdb"
else:
    raise RuntimeError("ENV variable must be set to 'prod' or 'dev' to locate GeoIP databases")