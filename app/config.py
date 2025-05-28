import os
from dotenv import load_dotenv

load_dotenv()

MODE = os.getenv("MODE")  # thesis or public
if MODE not in ["thesis", "public"]:
    raise RuntimeError("MODE variable must be set to 'thesis' or 'public'")
ENV = os.getenv("ENV")  # dev or prod
if ENV not in ["dev", "prod"]:
    raise RuntimeError("ENV variable must be set to 'dev' or 'prod'")

print(f"Running in {MODE} mode, {ENV} environment")

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