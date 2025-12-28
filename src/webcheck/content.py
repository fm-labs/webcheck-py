from pathlib import Path
from urllib.parse import urlparse

from webcheck.conf import WEBCHECK_DATA_DIR
from webcheck.util.content_helper import get_url_content


def webcontent_handler(url):
    try:
        status_code, headers, content = get_url_content(url)
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname

        filename = f"{WEBCHECK_DATA_DIR}/webcheck/{hostname}/content.txt"
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

        status_code, headers, content = get_url_content(url)
        return {
            'url': url,
            'status_code': status_code,
            'headers': headers,
            'content_length': len(content),
            'file': filename,
        }
    except Exception as e:
        raise Exception(f"Error fetching URL content: {str(e)}")
