import subprocess
import json

from webcheck.conf import WAPPALYZER_CLI_PATH


def run_wappalyzer(url):

    try:
        result = subprocess.run(
            [WAPPALYZER_CLI_PATH, url, '--quiet', '--json'],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        return {
            "message": "Wappalyzer scan completed!",
            "url": url,
            "technologies": data,
        }
    except subprocess.CalledProcessError as e:
        raise Exception(f"Wappalyzer error: {e.stderr.strip()}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse Wappalyzer output")


def wappalyzer_handler(url):
    if not url:
        raise ValueError("URL is missing from queryStringParameters")

    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'https://' + url

    return run_wappalyzer(url)
