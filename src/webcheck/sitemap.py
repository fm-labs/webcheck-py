import requests
import xml.etree.ElementTree as ET
import json
from urllib.parse import urljoin


def sitemap_handler(url):
    url = 'https://' + url if '://' not in url else url
    sitemap_url = f"{url}/sitemap.xml"
    hard_timeout = 5.0
    
    try:
        sitemap_res = None
        try:
            sitemap_res = requests.get(sitemap_url, timeout=hard_timeout)
            sitemap_res.raise_for_status()
        except requests.exceptions.HTTPError as error:
            if error.response.status_code == 404:
                robots_res = requests.get(f"{url}/robots.txt", timeout=hard_timeout)
                robots_res.raise_for_status()
                robots_txt = robots_res.text.split('\n')
                
                sitemap_url = None
                for line in robots_txt:
                    if line.lower().startswith('sitemap:'):
                        sitemap_url = line.split(' ')[1].strip()
                        break
                
                if not sitemap_url:
                    return {"skipped": "No sitemap found"}
                
                sitemap_res = requests.get(sitemap_url, timeout=hard_timeout)
                sitemap_res.raise_for_status()
            else:
                raise error
        
        root = ET.fromstring(sitemap_res.text)
        
        def xml_to_dict(element):
            result = {}
            
            if element.text and element.text.strip():
                if len(element) == 0:
                    return element.text.strip()
            
            for child in element:
                child_data = xml_to_dict(child)
                
                tag = child.tag
                if '}' in tag:
                    tag = tag.split('}')[1]
                
                if tag in result:
                    if not isinstance(result[tag], list):
                        result[tag] = [result[tag]]
                    result[tag].append(child_data)
                else:
                    result[tag] = child_data
            
            return result
        
        sitemap = xml_to_dict(root)
        return sitemap
        
    except requests.exceptions.Timeout:
        return {"error": f"Request timed-out after {int(hard_timeout * 1000)}ms"}
    except Exception as error:
        return {"error": str(error)}

handler = sitemap_handler