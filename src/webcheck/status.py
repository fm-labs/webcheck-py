import time
import urllib.request
import urllib.error
import requests
from webcheck.conf import WEBCHECK_USER_AGENT


async def status_handler(url):
    if not url:
        raise ValueError('You must provide a URL query parameter!')

    return await request_status(url, insecure=True)

async def request_status(url, insecure=True):
    
    dns_lookup_time = None
    response_code = None
    start_time = None

    status = {
        'url': url,
        'isUp': False,
        #'dnsLookupTime': None,
        #'responseSize': 0,
        #'responseTime': None,
        #'responseCode': None
    }
    try:
        start_time = time.time()
        
        # request = urllib.request.Request(url, method='GET', headers={'User-Agent': WEBCHECK_USER_AGENT})
        # data = None
        # with urllib.request.urlopen(request, timeout=10) as response:
        #     response_code = response.getcode()
        #     response_headers = response.getheaders()
        #     data = response.read().decode('utf-8')
        
        #if response_code < 200 or response_code >= 400:
        #    raise Exception(f'Received non-success response code: {response_code}')

        # Using requests library for better handling
        headers = {'User-Agent': WEBCHECK_USER_AGENT}
        response = requests.get(url, headers=headers, timeout=10, verify=not insecure)
        response_code = response.status_code
        response_headers = response.headers
        data = response.text
        
        response_time = (time.time() - start_time) * 1000
        #dns_lookup_time = 0
        
        status.update({
            'isUp': True,
            #'dnsLookupTime': dns_lookup_time,
            'responseHeaders': dict(response_headers),
            'responseSize': len(data.encode('utf-8')),
            'responseTime': response_time,
            'responseCode': response_code
        })
    except requests.exceptions.RequestException as e:
        print("Request Header:", e.request.headers.items())
        print("RequestException:", e)
        if "SSLCertVerificationError" in str(e):
            status.update({
                "isUp": False,
                "error": "SSL Certificate Verification Error",
            })
            return status

        status.update({
            "isUp": False,
            "responseHeaders": dict(e.response.headers.items()),
            "responseCode": str(e.response.status_code),
            "error": str(e),
        })
        #raise e
    except Exception as error:
        print("General Exception:", error)
        status.update({
            "isUp": False,
            "error": "Connection error",
        })
        #raise error
    print(status)
    return status


handler = status_handler