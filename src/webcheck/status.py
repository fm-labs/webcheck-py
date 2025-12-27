import time
import urllib.request
import urllib.error
from urllib.parse import urlparse

async def status_handler(url):
    if not url:
        raise ValueError('You must provide a URL query parameter!')
    
    dns_lookup_time = None
    response_code = None
    start_time = None
    
    try:
        start_time = time.time()
        
        request = urllib.request.Request(url)
        
        with urllib.request.urlopen(request, timeout=5) as response:
            response_code = response.getcode()
            data = response.read().decode('utf-8')
        
        if response_code < 200 or response_code >= 400:
            raise Exception(f'Received non-success response code: {response_code}')
        
        response_time = (time.time() - start_time) * 1000
        #dns_lookup_time = 0
        
        return {
            'url': url,
            'isUp': True,
            #'dnsLookupTime': dns_lookup_time,
            'responseSize': len(data.encode('utf-8')),
            'responseTime': response_time,
            'responseCode': response_code
        }
    
    except Exception as error:
        raise error


handler = status_handler