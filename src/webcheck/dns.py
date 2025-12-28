import socket
import asyncio
from urllib.parse import urlparse
from typing import Dict, List, Any, Union

import dns.resolver
from dns.exception import DNSException

from webcheck.conf import DNS_PROVIDERS

COMMON_RECORD_TYPES = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "SRV"]

def make_resolver(provider_name: str | None = None) -> dns.resolver.Resolver:
    """
    Create a dnspython Resolver, optionally bound to one of our public DNS providers.
    If provider_name is None or unknown, system defaults are used.
    """
    resolver = dns.resolver.Resolver()

    if provider_name and provider_name in DNS_PROVIDERS:
        resolver.nameservers = DNS_PROVIDERS[provider_name]["nameservers"]

    return resolver

def get_all_dns_records(domain: str,
                        provider_name: str | None = None,
                        record_types: list[str] | None = None) -> dict[str, list[str]]:
    """
    Query multiple DNS record types for a given domain using a chosen DNS provider.

    Returns: { "A": [...], "MX": [...], ... }
    Missing/empty types are omitted.
    """
    if record_types is None:
        record_types = COMMON_RECORD_TYPES

    resolver = make_resolver(provider_name)
    results: dict[str, list[str]] = {}

    for rtype in record_types:
        try:
            answer = resolver.resolve(domain, rtype)
            results[rtype] = [r.to_text() for r in answer]
        except (dns.resolver.NoAnswer,
                dns.resolver.NXDOMAIN,
                dns.resolver.NoNameservers,
                dns.resolver.LifetimeTimeout,
                DNSException):
            # Just skip this type if there's an issue
            print(f"DNS lookup for {rtype} record on {domain} failed or returned no answer.")
            continue

    return results

async def dns_records_handler(domain: str) -> Dict[str, Any]:
    records = get_all_dns_records(domain)

    # parse txt records into key-value pairs if present
    readable_txt_records = {}
    if 'TXT' in records:
        for record_array in records['TXT']:
            record_strings = [record_array] if isinstance(record_array, str) else record_array
            for record_string in record_strings:
                record_string = record_string.strip('"')
                split_record = record_string.split('=', 1)
                if len(split_record) >= 2:
                    key = split_record[0]
                    value = '='.join(split_record[1:]) if len(split_record) > 1 else ''
                    readable_txt_records[key] = value
                else:
                    readable_txt_records[record_string] = ''

    return {
        'records': records,
        'txt_records': readable_txt_records
    }


async def dns_handler1(domain: str) -> Dict[str, Any]:
    hostname = domain
    
    # Handle URLs by extracting hostname
    if hostname.startswith('http://') or hostname.startswith('https://'):
        hostname = urlparse(hostname).hostname
    
    try:
        # Helper function to safely resolve DNS records
        def safe_resolve(record_type: str, hostname: str) -> List[Any]:
            try:
                if record_type == 'A':
                    return [socket.gethostbyname(hostname)]
                elif record_type == 'AAAA':
                    result = socket.getaddrinfo(hostname, None, socket.AF_INET6)
                    return [addr[4][0] for addr in result]
                elif record_type == 'MX':
                    # Basic implementation - would need dnspython for full MX support
                    return []
                elif record_type == 'TXT':
                    # Basic implementation - would need dnspython for full TXT support
                    return []
                elif record_type == 'NS':
                    # Basic implementation - would need dnspython for full NS support
                    return []
                elif record_type == 'CNAME':
                    return [socket.getfqdn(hostname)]
                elif record_type == 'SOA':
                    # Basic implementation - would need dnspython for full SOA support
                    return []
                elif record_type == 'SRV':
                    # Basic implementation - would need dnspython for full SRV support
                    return []
                elif record_type == 'PTR':
                    # Basic implementation - would need dnspython for full PTR support
                    return []
                else:
                    return []
            except Exception:
                return []
        
        # Perform DNS lookups
        a_record = safe_resolve('A', hostname)
        aaaa_record = safe_resolve('AAAA', hostname)
        mx_record = safe_resolve('MX', hostname)
        txt_record = safe_resolve('TXT', hostname)
        ns_record = safe_resolve('NS', hostname)
        cname_record = safe_resolve('CNAME', hostname)
        soa_record = safe_resolve('SOA', hostname)
        srv_record = safe_resolve('SRV', hostname)
        ptr_record = safe_resolve('PTR', hostname)
        
        return {
            'A': a_record, # a_record[0] if a_record else None,
            'AAAA': aaaa_record,
            'MX': mx_record,
            'TXT': txt_record,
            'NS': ns_record,
            'CNAME': cname_record,
            'SOA': soa_record,
            'SRV': srv_record,
            'PTR': ptr_record
        }
        
    except Exception as error:
        raise Exception(str(error))

handler = dns_records_handler