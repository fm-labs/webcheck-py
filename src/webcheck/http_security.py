import json

from webcheck.util.content_helper import get_url_content


def http_security_handler(url):
    full_url = url if url.startswith('http') else f'https://{url}'
    
    try:
        print("[+] Checking HTTP security headers for", full_url)
        #response = requests.get(full_url)
        #headers = response.headers
        status_code, headers, content = get_url_content(full_url)
        return {
            'strictTransportPolicy': bool(headers.get('strict-transport-security')),
            'xFrameOptions': bool(headers.get('x-frame-options')),
            'xContentTypeOptions': bool(headers.get('x-content-type-options')),
            'xXSSProtection': bool(headers.get('x-xss-protection')),
            'contentSecurityPolicy': bool(headers.get('content-security-policy')),
        }
    except Exception as error:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(error)}),
        }

handler = http_security_handler