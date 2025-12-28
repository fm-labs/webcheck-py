import argparse
import asyncio
import inspect
import json
import time
from pathlib import Path

from scanhistory import add_scanhistory
from webcheck.carbon import carbon_handler
from webcheck.conf import WEBCHECK_DATA_DIR, WEBCHECK_CACHE_TTL_SEC, USE_MONGODB
from webcheck.content import webcontent_handler
from webcheck.dns import dns_records_handler
from webcheck.firewall import firewall_handler
from webcheck.hsts import hsts_handler
from webcheck.http_headers import http_headers_handler
from webcheck.http_security import http_security_handler
from webcheck.ip import hostip_handler
from webcheck.mail_config import mail_config_handler
from webcheck.page import page_handler
from webcheck.ping import ping_handler
from webcheck.rank import rank_handler
from webcheck.redirects import redirects_handler
from webcheck.robotstxt import robots_handler
from webcheck.screenshot import screenshot_handler
from webcheck.securitytxt import security_txt_handler
from webcheck.server_location import server_location_handler
from webcheck.sitemap import sitemap_handler
from webcheck.social_tags import social_tags_handler
from webcheck.ssl import ssl_handler
from webcheck.status import status_handler
from webcheck.util.cache_helper import cache_read, cache_write
from webcheck.util.content_helper import clear_url_cache, reverse_domain_path
from webcheck.util.mongodb_helper import mongodb_upsert_domain_scan
from webcheck.util.mongodb_queue import JobQueue, SimpleInMemoryQueue
from webcheck.wappalyzer import wappalyzer_handler
from webcheck.whois import whois_handler


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


# Host based handlers
HOST_HANDLERS = {
    'ip': (hostip_handler, 60 * 24),
    #'ports': (check_host_ports, None),
    'ping': (ping_handler, None),
    'dns': (dns_records_handler, None),
    'server_location': (server_location_handler, None),
    #'traceroute': (trace_route_handler, None),
    'whois': (whois_handler, None),
    'mx': (mail_config_handler, None),
    'rank': (rank_handler, None),
    # 'ssl_qualys': (qualys_sslchecker_handler, None), # long running, handled separately
}

URL_HANDLERS = {
    'status': (status_handler, 60 * 24),  # cache for 24 hours
    'content': (webcontent_handler, None),
    'http_headers': (http_headers_handler, None),
    'http_security': (http_security_handler, None),
    'ssl': (ssl_handler, None),
    'hsts': (hsts_handler, None),
    'firewall': (firewall_handler, None),
    'redirects': (redirects_handler, None),
    'robotstxt': (robots_handler, None),
    'securitytxt': (security_txt_handler, None),
    'sitemap': (sitemap_handler, None),
    'social_tags': (social_tags_handler, None),
    'page': (page_handler, None),
    'screenshot': (screenshot_handler, None),
    'wappalyzer': (wappalyzer_handler, None),
    'carbon': (carbon_handler, None),
}

def should_scan_domain(domain: str):
    # implement any logic to decide whether to scan the domain
    return True

def scan_domain_sync(domain, use_tls=True, force=False, checks=None):
    if '://' in domain:
        domain = domain.split("://", 1)[1].split("/")[0]

    schema = "https" if use_tls else "http"
    url = f"{schema}://{domain}"
    scan_result = {
        'domain': domain,
        'url': url,
    }

    scan_started_at = time.time() * 1000

    # skip if already scanned
    # if Path(new_result_file).exists() and not force:
    #    print(f"[+] Scan result for {domain} already exists, skipping...")
    #    return

    # Host based handlers
    for handler_name, handler in HOST_HANDLERS.items():
        if checks and handler_name not in checks:
            #print(f"Skipping {handler_name} as it's not in the checks list")
            continue
        try:
            handler_func = handler[0]
            handler_ttl = handler[1] if handler[1] else WEBCHECK_CACHE_TTL_SEC
            handler_ttl = 0 if force else handler_ttl
            print(f"[host-check] {handler_name} ({handler_ttl})")
            result = invoke_cached(f"{reverse_domain_path(domain)}/{handler_name}", handler_func, ttl=handler_ttl)(domain)
            scan_result[handler_name] = result
        except Exception as e:
            scan_result[handler_name] = {'error': str(e)}

    # URL based handlers
    for handler_name, handler in URL_HANDLERS.items():
        if checks and handler_name not in checks:
            #print(f"Skipping {handler_name} as it's not in the checks list")
            continue
        try:
            handler_func = handler[0]
            handler_ttl = handler[1] if handler[1] else WEBCHECK_CACHE_TTL_SEC
            handler_ttl = 0 if force else handler_ttl
            print(f"[page-check] {handler_name} ({handler_ttl})")
            result = invoke_cached(f"{reverse_domain_path(domain)}/{handler_name}", handler_func, ttl=handler_ttl)(url)
            scan_result[handler_name] = result

            if handler_name == 'status' and 'error' in result:
                print("[!!] Status check failed, skipping further URL-based checks: ", result['error'])
                break

        except Exception as e:
            print(f"Error in handler {handler_name}: {str(e)}")
            scan_result[handler_name] = {'error': str(e)}

            if handler_name == 'status':
                print("[!!] Status check failed, skipping further URL-based checks.", str(e))
                break


    scan_ended_at = time.time() * 1000
    scan_metadata = {
        'type': 'domain',
        'target': domain,
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
    save_scan_result(domain, scan_result)

    # add to scan history
    add_scanhistory("domain", domain)

    return scan_result


domains_queued: set[tuple[str,int]] = set()
domains_scanned: set[str] = set()
domains_failed: set[str] = set()

job_queue_handler = SimpleInMemoryQueue
job_queue = None

def get_queue() -> JobQueue:
    global job_queue
    if not job_queue:
        job_queue = job_queue_handler()
    return job_queue

def add_to_queue(domain, depth=0):
    global domains_queued
    global domains_scanned
    if domain not in domains_scanned:
        domains_queued.add((domain, depth))
    else:
        print(f"Domain {domain} already scanned, skipping adding to queue.")

def get_next_from_queue(max_depth=-1):
    global domains_queued
    if len(domains_queued) > 0:
        domain, depth = domains_queued.pop()
        if max_depth < 0 or depth <= max_depth:
            return domain, depth
    return None, None

def save_scan_result(domain, scan_result):
    filename = f"{WEBCHECK_DATA_DIR}/webcheck/{domain}/scan_result.json"
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(scan_result, f, indent=2)
    print(f"Saving scan result to {filename}")

    if USE_MONGODB:
        print("Upserting scan data for domain:", domain)
        mongodb_upsert_domain_scan(domain, scan_result)
    else:
        print("Skipping MongoDB upsert as USE_MONGODB is False.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Webcheck CLI")
    parser.add_argument("domain", type=str, help="The target domain")
    parser.add_argument("--checks", type=str, help="Comma separated list of checks to perform", default="")
    parser.add_argument("--notls", action="store_true", help="Use TLS or not", default=False)
    parser.add_argument("--force", action="store_true", help="Force re-scan even if cached result exists", default=False)
    parser.add_argument("--crawl", action="store_true", help="Crawl linked domains", default=False)
    parser.add_argument("--crawl-max-depth", type=int, help="Max domain depth", default=0)
    parser.add_argument("--crawl-max-domains", type=int, help="Max domains to scan", default=-1)
    parser.add_argument("--crawl-interval", type=int, help="Interval between scans in sec", default=0)
    args = parser.parse_args()

    #last_scans = mongodb_get_last_scans_by_type("domain", limit=25)
    #print(last_scans)
    #last_scanned_domains = [entry["target"] for entry in last_scans]
    #print("Last scanned domains:", last_scanned_domains)

    domain = str(args.domain).strip()
    checks = str(args.checks).strip().split(",") if args.checks else None
    use_tls = not args.notls
    force = args.force
    crawl = args.crawl
    crawl_max_depth = args.crawl_max_depth
    crawl_max_domains = args.crawl_max_domains
    crawl_interval = args.crawl_interval

    # if domain starts with "@", it refers to a file with list of domains
    if domain.startswith("@"):
        filename = domain[1:]
        with open(filename, "r", encoding="utf-8") as f:
            domains = [line.strip() for line in f if line.strip()]
        print(f"Initialized {len(domains)} domains")
        for d in domains:
            add_to_queue(d, 0)
    else:
        # split by comma
        domains = [d.strip() for d in domain.split(",") if d.strip()]
        for d in domains:
            add_to_queue(d, 0)

    #print("Domains: ", domains)
    i = 0
    should_continue = True
    while len(domains_queued) > 0 and should_continue:
        # get next domain
        d, depth = get_next_from_queue(crawl_max_depth)
        if not d:
            break

        i += 1
        print(f"\n[#{i}] Scanning domain: {d} (Queued: {len(domains_queued)}, Scanned: {len(domains_scanned)}, Failed: {len(domains_failed)})")

        try:
            scan_result = scan_domain_sync(d, use_tls=use_tls, force=force, checks=checks)
            domains_scanned.add(d)

        except Exception as e:
            print("Error scanning domain {}: {}".format(d, str(e)))
            domains_failed.add(d)
            continue

        try:
            if crawl and depth < crawl_max_depth and 'page' in scan_result:
                # extract links and add to queue
                page_info = scan_result['page']
                domains = page_info.get('parsed', {}).get('linkDomains', [])
                for _d in domains:
                    print("  [+] Found linked domain: {}".format(_d))
                    add_to_queue(_d, depth + 1)
        except Exception as e:
            print("Error during crawling links: {}".format(str(e)))
            continue


        # dump progress stats every 10 scans to console and file
        if i % 10 == 0 or len(domains_queued) == 0:
            stats = {
                'queued': len(domains_queued),
                'scanned': len(domains_scanned),
                'failed': len(domains_failed),
            }
            print(f"\n[+] Scan Progress: {json.dumps(stats, indent=2)}")
            stats_file = f"{WEBCHECK_DATA_DIR}/webcheck/scan_progress.json"
            with open(stats_file, "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=2)

        if crawl_max_domains > 0 and len(domains_scanned) >= crawl_max_domains:
            print(f"[+] Reached max crawl domains limit of {crawl_max_domains}, stopping further scans.")
            should_continue = False
            break

        # time interval between scans
        if len(domains_queued) > 0 and crawl_interval > 0:
            print(f"[+] Waiting for {crawl_interval} seconds before next scan...")
            time.sleep(crawl_interval)

    print("\n[+] Scan completed.")
    print(f"Total Domains Scanned: {len(domains_scanned)}")
    print(f"Total Domains Failed: {len(domains_failed)}")

    # dump failed domains to file
    if len(domains_failed) > 0:
        failed_file = f"{WEBCHECK_DATA_DIR}/webcheck/failed_domains.txt"
        with open(failed_file, "w", encoding="utf-8") as f:
            for d in domains_failed:
                f.write(d + "\n")
        print(f"Failed domains written to {failed_file}")

    # dump scanned domains to file
    if len(domains_scanned) > 0:
        scanned_file = f"{WEBCHECK_DATA_DIR}/webcheck/scanned_domains.txt"
        with open(scanned_file, "w", encoding="utf-8") as f:
            for d in domains_scanned:
                f.write(d + "\n")
        print(f"Scanned domains written to {scanned_file}")