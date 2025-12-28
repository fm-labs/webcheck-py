import urllib.parse
import urllib.request
import ssl
import re

from webcheck.util.content_helper import get_url_content

SECURITY_TXT_PATHS = [
    '/security.txt',
    '/.well-known/security.txt',
]

def parse_result(result):
    output = {}
    counts = {}
    lines = result.split('\n')
    regex = re.compile(r'^([^:]+):\s*(.+)$')
    
    for line in lines:
        if not line.startswith("#") and not line.startswith("-----") and line.strip() != '':
            match = regex.match(line)
            if match and len(match.groups()) > 1:
                key = match.group(1).strip()
                value = match.group(2).strip()
                if key in output:
                    counts[key] = counts.get(key, 0) + 1
                    key += str(counts[key])
                output[key] = value
    
    return output

def is_pgp_signed(result):
    if '-----BEGIN PGP SIGNED MESSAGE-----' in result:
        return True
    return False

def security_txt_handler(url):
    try:
        if '://' in url:
            parsed_url = urllib.parse.urlparse(url)
        else:
            parsed_url = urllib.parse.urlparse('https://' + url)
        
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    except Exception:
        raise ValueError('Invalid URL format')
    
    for path in SECURITY_TXT_PATHS:
        try:
            #result = fetch_security_txt(base_url, path)
            status_code, headers, content = get_url_content(f"{base_url}{path}")
            if not headers.get('content-type', '').lower().startswith('text/plain'):
                return {'isPresent': False}
            if content and ('<html' in content or '<body' in content or '<meta' in content):
                return {'isPresent': False}
            if content:
                return {
                    'isPresent': True,
                    'foundIn': path,
                    'content': content,
                    'isPgpSigned': is_pgp_signed(content),
                    'fields': parse_result(content),
                }
        except Exception as error:
            raise Exception(str(error))
    
    return {'isPresent': False}

def fetch_security_txt(base_url, path):
    try:
        url = urllib.parse.urljoin(base_url, path)
        
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (compatible; SecurityTxtChecker/1.0)')
        
        with urllib.request.urlopen(req, context=context, timeout=10) as response:
            if response.status == 200:
                return response.read().decode('utf-8', errors='ignore')
            else:
                return None
    except Exception:
        return None


handler = security_txt_handler