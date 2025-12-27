import os

DEFAULT_WEBCHECK_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
WEBCHECK_DATA_DIR = os.getenv("WEBCHECK_DATA_DIR", DEFAULT_WEBCHECK_DATA_DIR)

DEFAULT_WEBCHECK_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:146.0) Gecko/20100101 Firefox/146.0"
WEBCHECK_USER_AGENT = os.getenv("WEBCHECK_USER_AGENT", DEFAULT_WEBCHECK_USER_AGENT)

DEFAULT_WEBCHECK_UI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ui', 'dist')
WEBCHECK_UI_DIR = os.getenv("WEBCHECK_UI_DIR", DEFAULT_WEBCHECK_UI_DIR)

WAPPALYZER_CLI_PATH = os.getenv("WAPPALYZER_CLI_PATH", "bin/wappalyzer")

WEBCHECK_CACHE_ENGINE = "local"
WEBCHECK_CACHE_TTL_SEC = 60 * 60 * 24 * 7  # 7 days

WEBCHECK_QUEUE_ENGINE = os.getenv("WEBCHECK_QUEUE_ENGINE", "mongodb")  # options: "mongodb", "local"

USE_MONGODB = os.getenv("USE_MONGODB", "false").lower() == "true"
MONGODB_URI = os.getenv("MONGODB_URI", None) # "mongodb://mongodb:27017"
MONGODB_DB_NAME = os.getenv("MONGODB_DATABASE", "webcheck")
MONGODB_CACHE_COLLECTION = os.getenv("MONGODB_QUEUE_COLLECTION", "cache")
MONGODB_QUEUE_COLLECTION = os.getenv("MONGODB_QUEUE_COLLECTION", "queue")
MONGODB_DOMAINS_COLLECTION = os.getenv("MONGODB_QUEUE_COLLECTION", "domains")

DNS_PROVIDERS = {
    "google": {
        "nameservers": ["8.8.8.8", "8.8.4.4"],
        "supports_doh": True,
        "allows_dnsbl": False,
    },
    "cloudflare": {
        "nameservers": ["1.1.1.1", "1.0.0.1"],
        "supports_doh": True,
        "allows_dnsbl": False,
    },
    "quad9": {
        "nameservers": ["9.9.9.9", "149.112.112.112"],
        "supports_doh": True,
        "allows_dnsbl": False,  # often partial, treat as False to be safe
    },
    "dns_sb": {
        "nameservers": ["185.222.222.222", "45.11.45.11"],
        "supports_doh": True,
        "allows_dnsbl": True,
    },
    "uncensoreddns": {
        "nameservers": ["91.239.100.100", "89.233.43.71"],
        "supports_doh": True,
        "allows_dnsbl": True,
    },
    "mullvad": {
        "nameservers": ["194.242.2.2"],
        "supports_doh": True,
        "allows_dnsbl": True,
    },
}