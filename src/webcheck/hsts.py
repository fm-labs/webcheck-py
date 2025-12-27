import urllib.request
import urllib.error
import json
import re

from webcheck.util.content_helper import get_url_content


def hsts_handler(url):
    def error_response(message, status_code=500):
        return {
            "statusCode": status_code,
            "body": json.dumps({"error": message}),
        }
    
    def hsts_incompatible(message, compatible=False, hsts_header=None):
        return {"message": message, "compatible": compatible, "hstsHeader": hsts_header}
    
    try:
        url = url if url.startswith('http') else f'https://{url}'
        #req = urllib.request.Request(url)
        #with urllib.request.urlopen(req) as response:
            #headers = response.headers
        status_code, headers, content = get_url_content(url)
        #print(headers)
        hsts_header = headers.get('strict-transport-security')

        if not hsts_header:
            return hsts_incompatible("Site does not serve any HSTS headers.")
        else:
            max_age_match = re.search(r'max-age=(\d+)', hsts_header)
            includes_sub_domains = 'includeSubDomains' in hsts_header
            preload = 'preload' in hsts_header

            if not max_age_match or int(max_age_match.group(1)) < 10886400:
                return hsts_incompatible("HSTS max-age is less than 10886400.", False, hsts_header)
            elif not includes_sub_domains:
                return hsts_incompatible("HSTS header does not include all subdomains.", False, hsts_header)
            elif not preload:
                return hsts_incompatible("HSTS header does not contain the preload directive.", False, hsts_header)
            else:
                return hsts_incompatible("Site is compatible with the HSTS preload list!", True, hsts_header)
                    
    except urllib.error.URLError as error:
        return error_response(f"Error making request: {str(error)}")
    except Exception as error:
        return error_response(f"Error making request: {str(error)}")

handler = hsts_handler