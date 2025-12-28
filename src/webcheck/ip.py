import socket


def get_ip_address(domain):
    try:
        ip_address = socket.gethostbyname(domain)
        return ip_address
    except socket.gaierror:
        return None


def hostip_handler(url):
    domain = url.split("//")[-1].split("/")[0]
    ip_address = get_ip_address(domain)
    if not ip_address:
        raise Exception(f"Unable to resolve domain: {domain}")
    return {
        'domain': domain,
        'ip_address': ip_address
    }
