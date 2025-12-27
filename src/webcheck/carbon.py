import urllib.request
import json

from webcheck.util.content_helper import get_url_content


async def carbon_handler(url):
    def get_html_size(url):
        try:
            # with urllib.request.urlopen(url) as response:
            #     data = response.read()
            #     size_in_bytes = len(data)
            #     return size_in_bytes
            status_code, headers, content = get_url_content(url)
            size_in_bytes = len(content.encode('utf-8'))
            return size_in_bytes
        except Exception as e:
            raise e

    try:
        size_in_bytes = get_html_size(url)
        api_url = f"https://api.websitecarbon.com/data?bytes={size_in_bytes}&green=0"

        with urllib.request.urlopen(api_url) as response:
            data = response.read()
            carbon_data = json.loads(data.decode('utf-8'))

        if not carbon_data.get('statistics') or (carbon_data['statistics'].get('adjustedBytes', 0) == 0 and carbon_data['statistics'].get('energy', 0) == 0):
            return {
                'statusCode': 200,
                'body': json.dumps({'skipped': 'Not enough info to get carbon data'}),
            }

        carbon_data['scanUrl'] = url
        return carbon_data
    except Exception as error:
        raise Exception(f"Error: {str(error)}")


handler = carbon_handler