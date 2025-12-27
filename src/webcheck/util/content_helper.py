import requests

from webcheck.conf import WEBCHECK_USER_AGENT


def fetch_url_content(url):
    res = requests.get(url, timeout=5.0, headers={"User-Agent": WEBCHECK_USER_AGENT})
    headers = {k.lower(): v for k, v in res.headers.items()}
    content = res.text
    status_code = res.status_code
    return status_code, headers, content


def reverse_domain_path(domain, join_char="/"):
    """
    Reverse the parts of a domain for cache key generation.

    :param domain:
    :return:
    """
    parts = domain.split(".")
    parts.reverse()
    return join_char.join(parts)


def build_host_url_cache_key(url):
    """
    Build a cache key for the given URL.
    The key is structured to create a directory-like hierarchy
    based on the first few characters of the domain and the path.

    :param url:
    :return:
    """
    schema, rest = url.split("://", 1)
    domain, path = rest.split("/", 1) if "/" in rest else (rest, "")
    path, querystring = path.split("?", 1) if "?" in path else (path, "")
    head = domain[:3] if len(domain) > 3 else domain
    key = ""
    for c in head:
        key += f"{c}/"
    key += domain + "/"
    key += path
    return key


# def read_cached_file(cache_key):
#     try:
#         with open(f"{WEBCHECK_DATA_DIR}/cache/{cache_key}", "r", encoding="utf-8") as f:
#             return f.read()
#     except FileNotFoundError:
#         return None
#
# def write_cached_file(cache_key, content):
#     with open(f"{WEBCHECK_DATA_DIR}/cache/{cache_key}", "w", encoding="utf-8") as f:
#         f.write(content)

# def get_url_content_cached(url):
#     cache_key = build_url_cache_key(url)
#     try:
#         with open(f"{WEBCHECK_DATA_DIR}/cache/{cache_key}", "r", encoding="utf-8") as f:
#             return f.read()
#     except FileNotFoundError:
#         pass
#
#     headers, content = fetch_url_content(url)
#     with open(f"{WEBCHECK_DATA_DIR}/cache/{cache_key}", "w", encoding="utf-8") as f:
#         f.write(content)
#     print(f"[+] Fetched and cached content for {url}")
#     return result

cache = {}
def get_url_content(url):
    global cache
    cache_key = f"{url.replace('://', '_')}"
    if cache_key in cache:
        print(f"[+] Using cached content for {url}")
        return cache[cache_key]

    result = fetch_url_content(url)
    cache[cache_key] = result
    print(f"[+] Fetched and cached content for {url}")
    return result


def remove_url_from_cache(url):
    global cache
    cache_key = f"{url.replace('://', '_')}"
    if cache_key in cache:
        del cache[cache_key]
        print(f"[+] Removed {url} from cache")


def clear_url_cache():
    global cache
    cache = {}
    print(f"[+] Cleared URL cache")