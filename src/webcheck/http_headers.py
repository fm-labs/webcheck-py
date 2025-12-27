import requests
from typing import Dict

from webcheck.util.content_helper import get_url_content


def http_headers_handler(url: str) -> Dict[str, str]:
    full_url = url if url.startswith('http') else f'https://{url}'

    try:
        #response = requests.get(url)
        #response.raise_for_status()
        #return dict(response.headers)
        status_code, headers, _ = get_url_content(full_url)
        return headers
    except requests.RequestException as error:
        raise Exception(str(error))

handler = http_headers_handler