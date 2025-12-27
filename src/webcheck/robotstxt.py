import requests
import re
from urllib.parse import urlparse
import json

def parse_robots_txt(content):
    lines = content.split('\n')
    rules = []
    sitemaps = []
    
    for line in lines:
        line = line.strip()
        
        match = re.match(r'^(Allow|Disallow):\s*(\S*)$', line, re.IGNORECASE)
        if match:
            rule = {
                'lbl': match.group(1),
                'val': match.group(2)
            }
            rules.append(rule)
        else:
            match = re.match(r'^(User-agent):\s*(\S*)$', line, re.IGNORECASE)
            if match:
                rule = {
                    'lbl': match.group(1),
                    'val': match.group(2)
                }
                rules.append(rule)
            else:
                match = re.match(r'^(Sitemap):\s*(\S*)$', line, re.IGNORECASE)
                if match:
                    sitemap = {
                        'lbl': match.group(1),
                        'val': match.group(2)
                    }
                    sitemaps.append(sitemap)
    
    return {'rules': rules, 'sitemaps': sitemaps}

def robots_handler(url):
    try:
        url = 'https://' + url if '://' not in url else url
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid URL")
    except Exception as error:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid url query parameter'})
        }
    
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    
    try:
        response = requests.get(robots_url, timeout=10)
        
        if response.status_code == 200:
            parsed_data = parse_robots_txt(response.text)
            return {
                'isPresent': True,
                'statusCode': response.status_code,
                'body': str(response.text),
                'rules': parsed_data['rules'],
                'sitemaps': parsed_data['sitemaps']
            }
        else:
            return {
                'isPresent': False,
                'statusCode': response.status_code,
                'body': json.dumps({'error': 'Failed to fetch robots.txt', 'statusCode': response.status_code})
            }
    except Exception as error:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Error fetching robots.txt: {str(error)}'})
        }

handler = robots_handler