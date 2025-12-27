import argparse
import json
import time

from webcheck.conf import WEBCHECK_DATA_DIR
from webcheck.util.mongodb_helper import mongodb_get_last_scans_by_type
from webcheck.util.mongodb_queue import JobQueue, mongodb_queue_handler, MongoDBQueue
from webcheckcli import scan_domain_sync

domains_scanned: set[str] = set()
domains_failed: set[str] = set()

job_queue_handler = mongodb_queue_handler
job_queue = None

def get_queue() -> JobQueue:
    global job_queue
    if not job_queue:
        job_queue = job_queue_handler()
    return job_queue


def add_to_queue(domain, depth=0):
    get_queue().enqueue(( domain, depth))

def get_job_from_queue():
    job = get_queue().dequeue()
    print(f"Next job: {job}")
    return job

def get_queue_size():
    return get_queue().count()

def mark_job_done(job_id: str):
    if isinstance(get_queue(), MongoDBQueue):
        get_queue().mark_done(job_id)

def mark_job_failed(job_id: str, reason: str = "scan error"):
    if isinstance(get_queue(), MongoDBQueue):
        get_queue().mark_failed(job_id, reason)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Webcheck Worker for Domain Scanning and Crawling")
    parser.add_argument("--domain", type=str, required=False, help="Domain name to scan or @filename for list of domains")
    parser.add_argument("--worker_id", type=str, required=False, help="Worker ID")
    parser.add_argument("--loop", action="store_true", help="Run in continuous loop mode")
    parser.add_argument("--noscan", action="store_true", help="Does not perform scans, only manages the queue")
    parser.add_argument("--checks", type=str, required=False, help="Comma-separated list of checks to perform")
    parser.add_argument("--notls", action="store_true", help="Disable TLS for scans")
    parser.add_argument("--force", action="store_true", help="Force re-scan even if results exist")
    parser.add_argument("--crawl", action="store_true", help="Enable crawling of linked domains")
    parser.add_argument("--crawl-max-depth", type=int, default=0, help="Maximum crawl depth")
    parser.add_argument("--crawl-max-domains", type=int, default=0, help="Maximum number of domains to crawl (0 for unlimited)")
    parser.add_argument("--crawl-interval", type=int, default=0, help="Interval in seconds between crawl scans")

    args = parser.parse_args()

    last_scans = mongodb_get_last_scans_by_type("domain", limit=25)
    print(last_scans)
    last_scanned_domains = [entry["target"] for entry in last_scans]
    print("Last scanned domains:", last_scanned_domains)

    loop = args.loop
    worker_id = args.worker_id
    if worker_id is None:
        worker_id = "worker_" + str(int(time.time()))
    domain = args.domain
    checks = str(args.checks).strip().split(",") if args.checks else None
    use_tls = not args.notls
    force = args.force
    crawl = args.crawl
    crawl_max_depth = args.crawl_max_depth
    crawl_max_domains = args.crawl_max_domains
    crawl_interval = args.crawl_interval
    no_scan = args.noscan

    # if domain starts with "@", it refers to a file with list of domains
    if domain and domain.startswith("@"):
        filename = domain[1:]
        with open(filename, "r", encoding="utf-8") as f:
            domains = [line.strip() for line in f if line.strip()]
        print(f"Initialized {len(domains)} domains")
        for d in domains:
            add_to_queue(d, 0)
    elif domain and len(domain) > 0:
        # split by comma
        domains = [d.strip() for d in domain.split(",") if d.strip()]
        for d in domains:
            add_to_queue(d, 0)

    if no_scan:
        print("[+] No-scan mode enabled, exiting after queue initialization.")
        exit(0)

    #print("Domains: ", domains)
    print(f"Starting Webcheck Worker with ID: {worker_id}")
    i = 0
    should_continue = True
    while should_continue:
        queue_size = get_queue_size()
        # get next domain
        job = get_job_from_queue()
        if not job:
            # nothing left in queue
            if not loop:
                print("[+] No more domains in queue, exiting ...")
                break

            print("[+] No more domains in queue, waiting ...")
            time.sleep(15)
            continue

        i += 1
        job_id = job.get("_id")
        d, depth = job.get("payload")
        if not d:
            print("[!] Invalid job payload, skipping ...")
            continue

        print(f"\n[#{i}] Scanning domain: {d} (Queued: {queue_size}, Scanned: {len(domains_scanned)}, Failed: {len(domains_failed)})")
        scan_result = {}
        try:
            scan_result = scan_domain_sync(d, use_tls=use_tls, force=force, checks=checks)
            domains_scanned.add(d)
            mark_job_done(job_id)

        except Exception as e:
            print("Error scanning domain {}: {}".format(d, str(e)))
            domains_failed.add(d)
            mark_job_failed(job_id, str(e))
            #continue

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
        stats = {
            'queued': queue_size,
            'scanned': len(domains_scanned),
            'failed': len(domains_failed),
        }
        print(f"\n[+] Worker progress: {json.dumps(stats, indent=2)}")
        stats_file = f"{WEBCHECK_DATA_DIR}/worker_{worker_id}_progress.json"
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)

        if crawl_max_domains > 0 and len(domains_scanned) >= crawl_max_domains:
            print(f"[+] Reached max crawl domains limit of {crawl_max_domains}, stopping further scans.")
            should_continue = False
            break

        # time interval between scans
        if queue_size > 0 and crawl_interval > 0:
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