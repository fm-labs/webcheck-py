import requests

def redirects_handler(url):
    url = url if url.startswith('http') else f'https://{url}'
    redirects = [url]
    try:
        session = requests.Session()
        session.max_redirects = 12
        
        response = session.get(url, allow_redirects=False, timeout=5.0)
        
        while response.is_redirect and len(redirects) <= 12:
            location = response.headers.get('location')
            if location:
                redirects.append(location)
                response = session.get(location, allow_redirects=False)
            else:
                break
        
        return {
            "redirects": redirects
        }
    except Exception as error:
        raise Exception(f"Error: {str(error)}")

handler = redirects_handler