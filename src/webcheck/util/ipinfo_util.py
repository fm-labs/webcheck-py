import socket
import requests


def get_ip_for_domain(domain):
    try:
        ip_address = socket.gethostbyname(domain)
        return ip_address
    except socket.gaierror:
        return None


def ipinfo_handler(domain):
    ip_address = get_ip_for_domain(domain)
    url = "https://ipinfo.io/" + ip_address

    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f"Failed to fetch data from ipinfo.io, status code: {response.status_code}"}
    except Exception as error:
        return {'error': f"Error fetching data from ipinfo.io: {str(error)}"}