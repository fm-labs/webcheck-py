import socket
import re
import requests
from urllib.parse import urlparse

def parse_domain(url):
    if '://' not in url:
        url = 'http://' + url
    
    parsed = urlparse(url)
    hostname = parsed.hostname
    
    if hostname:
        parts = hostname.split('.')
        if len(parts) >= 2:
            return '.'.join(parts[-2:])
    
    return hostname

def get_base_domain(url):
    protocol = ''
    if url.startswith('http://'):
        protocol = 'http://'
    elif url.startswith('https://'):
        protocol = 'https://'
    
    no_protocol_url = url.replace(protocol, '')
    domain = parse_domain(no_protocol_url)
    return protocol + domain if domain else url

def parse_whois_data(data):
    if 'No match for' in data:
        return {'error': 'No matches found for domain in internic database'}
    
    lines = data.split('\r\n')
    parsed_data = {}
    last_key = ''
    
    for line in lines:
        index = line.find(':')
        if index == -1:
            if last_key != '':
                parsed_data[last_key] += ' ' + line.strip()
            continue
        
        key = line[:index].strip()
        value = line[index + 1:].strip()
        if len(value) == 0:
            continue
        
        key = re.sub(r'\W+', '_', key)
        last_key = key
        parsed_data[key] = value
    
    return parsed_data

def fetch_from_internic(hostname):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(30)
        client.connect(('whois.internic.net', 43))
        client.send((hostname + '\r\n').encode())
        
        data = ''
        while True:
            chunk = client.recv(4096).decode()
            if not chunk:
                break
            data += chunk
        
        client.close()
        return parse_whois_data(data)
    except Exception as error:
        return {'error': str(error)}

def fetch_from_my_api(hostname):
    try:
        response = requests.post('https://whois-api-zeta.vercel.app/', json={
            'domain': hostname
        })
        return response.json()
    except Exception as error:
        print(f'Error fetching data from your API: {error}')
        return None

def whois_handler(url):
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url
    
    try:
        parsed_url = urlparse(url)
        hostname = get_base_domain(parsed_url.hostname)
    except Exception as error:
        raise Exception(f'Unable to parse URL: {error}')
    
    internic_data = fetch_from_internic(hostname)
    #whois_data = fetch_from_my_api(hostname)
    #print(internic_data)
    
    return {
        'internicData': internic_data,
        #'whoisData': whois_data
    }

handler = whois_handler