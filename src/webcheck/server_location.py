from webcheck.util.ipinfo_util import ipinfo_handler


def server_location_handler(domain: str):

    # ipinfo_data = {"ip": "151.101.131.5", "city": "San Francisco", "region": "California", "country": "US",
    #                "loc": "37.7621,-122.3971", "org": "AS54113 Fastly, Inc.", "postal": "94107",
    #                "timezone": "America/Los_Angeles", "readme": "https://ipinfo.io/missingauth", "anycast": True}

    ipinfo_data = ipinfo_handler(domain)
    ipinfo_cords = ipinfo_data.get("loc", "0,0").split(",")
    data = {
        "city": ipinfo_data.get("city", ""),
        "region": ipinfo_data.get("region", ""),
        "country": ipinfo_data.get("country", ""),
        "postCode": ipinfo_data.get("postal", ""),
        "countryCode": ipinfo_data.get("country", ""),
        "coords": {
            "latitude": float(ipinfo_cords[0]) if len(ipinfo_cords) > 0 else 0.0,
            "longitude": float(ipinfo_cords[1]) if len(ipinfo_cords) > 1 else 0.0,
        },
        "isp": "Unknown ISP",
        "timezone": ipinfo_data.get("timezone", ""),
        "languages": "",
        "currency": "",
        "currencyCode": "",
    }
    return data
