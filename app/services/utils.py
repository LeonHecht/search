import geoip2.database

# point to where you placed the DB file
_reader_country = geoip2.database.Reader("/opt/GeoLite2-Country.mmdb")
_reader_city = geoip2.database.Reader("/opt/GeoLite2-City.mmdb")

def country_from_ip(ip: str) -> str | None:
    try:
        resp = _reader_country.country(ip)
        return resp.country.iso_code  # e.g. "US", "PY"
    except geoip2.errors.AddressNotFoundError:
        return None

def city_from_ip(ip: str) -> str | None:
    try:
        resp = _reader_city.city(ip)
        return resp.city.name  # e.g. "Asuncion"
    except geoip2.errors.AddressNotFoundError:
        return None
    except geoip2.errors.GeoIP2Error as e:
        print(f"GeoIP error for {ip}: {e}")
        return None