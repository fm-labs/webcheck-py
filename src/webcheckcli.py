import argparse
import asyncio
import inspect
import json
import socket
import time
from pathlib import Path
from urllib.parse import urlparse

from webcheck.util.cache_helper import cache_read, cache_write
from webcheck.carbon import carbon_handler
from webcheck.conf import WEBCHECK_DATA_DIR, WEBCHECK_CACHE_TTL_SEC
from webcheck.util.content_helper import clear_url_cache
from webcheck.util.content_helper import get_url_content
from webcheck.dns import dns_handler
from webcheck.firewall import firewall_handler
from webcheck.hsts import hsts_handler
from webcheck.http_headers import http_headers_handler
from webcheck.http_security import http_security_handler
from webcheck.mail_config import mail_config_handler
from webcheck.page import page_handler
from webcheck.ping import ping_handler
from webcheck.redirects import redirects_handler
from webcheck.robotstxt import robots_handler
from webcheck.screenshot import screenshot_handler
from webcheck.securitytxt import security_txt_handler
from webcheck.server_location import server_location_handler
from webcheck.sitemap import sitemap_handler
from webcheck.social_tags import social_tags_handler
from webcheck.ssl import ssl_handler
from webcheck.status import status_handler
from webcheck.rank import rank_handler
from webcheck.wappalyzer import wappalyzer_handler
from webcheck.whois import whois_handler
from scanhistory import add_scanhistory


def get_ip_address(domain):
    try:
        ip_address = socket.gethostbyname(domain)
        return ip_address
    except socket.gaierror:
        return None


def webcontent_handler(url):
    try:
        status_code, headers, content = get_url_content(url)
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname

        filename = f"{WEBCHECK_DATA_DIR}/webcheck/{hostname}/content.txt"
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

        status_code, headers, content = get_url_content(url)
        return {
            'url': url,
            'status_code': status_code,
            'headers': headers,
            'content_length': len(content),
            'file': filename,
        }
    except Exception as e:
        raise Exception(f"Error fetching URL content: {str(e)}")


def hostip_handler(url):
    domain = url.split("//")[-1].split("/")[0]
    ip_address = get_ip_address(domain)
    if not ip_address:
        raise Exception(f"Unable to resolve domain: {domain}")
    return {
        'domain': domain,
        'ip_address': ip_address
    }


def invoke_cached(cache_key, handler_func, ttl=60):
    def wrapper(*args, **kwargs):
        key = cache_key
        _cached = cache_read(key)
        if _cached:
            _cached = json.loads(_cached)
            if ttl > 0 and time.time() - _cached["timestamp"] < ttl:
                print(f"Cache hit for key {key}")
                return _cached["data"]
            else:
                print(f"!!!!Cache expired for key {key}")

        if inspect.iscoroutinefunction(handler_func):
            result = asyncio.run(handler_func(*args, **kwargs))
        else:
            result = handler_func(*args, **kwargs)

        payload = json.dumps({"data": result, "timestamp": time.time()})
        cache_write(key, payload, ttl)
        print(f"Cache set for key {key}")
        return result
    return wrapper


def scan_domain_sync(domain, use_tls=True, force=False, checks=None):
    if '://' in domain:
        domain = domain.split("://", 1)[1].split("/")[0]

    schema = "https" if use_tls else "http"
    url = f"{schema}://{domain}"
    scan_result = {
        'domain': domain,
        'url': url,
    }

    cache_ttl = 0 if force else WEBCHECK_CACHE_TTL_SEC
    scan_started_at = time.time() * 1000

    # # move old files to new structure
    # old_content_file = f"{WEBCHECK_DATA_DIR}/webcheck/scan_{domain}_content.txt"
    # new_content_file = f"{WEBCHECK_DATA_DIR}/webcheck/{domain}/content.txt"
    # if Path(old_content_file).exists() and not Path(new_content_file).exists():
    #     Path(new_content_file).parent.mkdir(parents=True, exist_ok=True)
    #     Path(old_content_file).rename(new_content_file)
    #
    # old_result_file = f"{WEBCHECK_DATA_DIR}/webcheck/scan_{domain}.json"
    # new_result_file = f"{WEBCHECK_DATA_DIR}/webcheck/{domain}/scan_result.json"
    # if Path(old_result_file).exists() and not Path(new_result_file).exists():
    #     Path(new_result_file).parent.mkdir(parents=True, exist_ok=True)
    #     Path(old_result_file).rename(new_result_file)

    # skip if already scanned
    # if Path(new_result_file).exists() and not force:
    #    print(f"[+] Scan result for {domain} already exists, skipping...")
    #    return

    # first get IP address
    #ip_address = get_ip_address(domain)
    #scan_result['ip_address'] = ip_address
    #if not ip_address:
    #    scan_result['error'] = f"Unable to resolve domain: {domain}"
    #    print(scan_result)
    #    exit(1)


    # Host based handlers
    host_handlers = {
        'ip': hostip_handler,
        #'ports': check_host_ports,
        'ping': ping_handler,
        'dns': dns_handler,
        'server_location': server_location_handler,
        #'traceroute': trace_route_handler,
        'whois': whois_handler,
        'mx': mail_config_handler,
        'rank': rank_handler,
        # 'ssl_qualys': qualys_sslchecker_handler, # long running, handled separately
    }
    for handler_name, handler_func in host_handlers.items():
        if checks and handler_name not in checks:
            #print(f"Skipping {handler_name} as it's not in the checks list")
            continue
        print(f"Handling {handler_name}")
        try:
            # if asyncio.iscoroutinefunction(handler_func):
            #     result = asyncio.run(handler_func(domain))
            # else:
            #     result = handler_func(domain)
            result = invoke_cached(f"{domain}/{handler_name}", handler_func, ttl=cache_ttl)(domain)
            scan_result[handler_name] = result
        except Exception as e:
            scan_result[handler_name] = {'error': str(e)}

    # URL based handlers
    url_handlers = {
        'status': status_handler,
        'content': webcontent_handler,
        'http_headers': http_headers_handler,
        'http_security': http_security_handler,
        'ssl': ssl_handler,
        'hsts': hsts_handler,
        'firewall': firewall_handler,
        'redirects': redirects_handler,
        'robotstxt': robots_handler,
        'securitytxt': security_txt_handler,
        'sitemap': sitemap_handler,
        'social_tags': social_tags_handler,
        'page': page_handler,
        'screenshot': screenshot_handler,
        'wappalyzer': wappalyzer_handler,
        'carbon': carbon_handler,
    }
    for handler_name, handler_func in url_handlers.items():
        if checks and handler_name not in checks:
            #print(f"Skipping {handler_name} as it's not in the checks list")
            continue
        print(f"Handling {handler_name}")
        try:
            # if asyncio.iscoroutinefunction(handler_func):
            #     result = asyncio.run(handler_func(url))
            # else:
            #     result = handler_func(url)
            result = invoke_cached(f"{domain}/{handler_name}", handler_func, ttl=cache_ttl)(url)
            scan_result[handler_name] = result
        except Exception as e:
            print(f"Error in handler {handler_name}: {str(e)}")
            scan_result[handler_name] = {'error': str(e)}


    scan_ended_at = time.time() * 1000
    scan_metadata = {
        'status': 'completed',
        'message': 'Scan completed successfully. Took {} ms'.format(int(scan_ended_at - scan_started_at)),
        'started_at': int(scan_started_at),
        'ended_at': int(scan_ended_at),
        'duration_ms': int(scan_ended_at - scan_started_at),
    }
    scan_result['scan'] = scan_metadata

    # cleanup
    clear_url_cache()

    # dump the result to file
    #print(json.dumps(scan_result, indent=2))
    filename = f"{WEBCHECK_DATA_DIR}/webcheck/{domain}/scan_result.json"
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(scan_result, f, indent=2)

    # add to scan history
    add_scanhistory("domain", domain)

    return scan_result



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Web Module")
    parser.add_argument("domain", type=str, help="The target domain")
    parser.add_argument("--checks", type=str, help="Comma separated list of checks to perform", default="")
    parser.add_argument("--notls", action="store_true", help="Use TLS or not", default=False)
    parser.add_argument("--force", action="store_true", help="Force re-scan even if cached result exists", default=False)
    args = parser.parse_args()

    domain = str(args.domain).strip()
    checks = str(args.checks).strip().split(",") if args.checks else None
    use_tls = not args.notls
    force = args.force

    domains = []
    # if domain starts with "@", it refers to a file with list of domains
    if domain.startswith("@"):
        filename = domain[1:]
        with open(filename, "r", encoding="utf-8") as f:
            domains = [line.strip() for line in f if line.strip()]
    else:
        domains.append(domain)

    print(f"Scanning {len(domains)} domains")
    #print("Domains: ", domains)
    for d in domains:
        try:
            scan_domain_sync(d, use_tls=use_tls, force=force, checks=checks)
        except Exception as e:
            print("Error scanning domain {}: {}".format(d, str(e)))
