import requests
import zipfile
import csv
import os
from urllib.parse import urlparse
from io import StringIO

from webcheck.conf import WEBCHECK_DATA_DIR

# https://s3-us-west-1.amazonaws.com/umbrella-static/index.html
UMBRELLA_FILE_URL = 'https://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip'
UMBRELLA_FILE_PATH = f'{WEBCHECK_DATA_DIR}/top-1m.csv'

TRANCO_FILE_PATH = f"{WEBCHECK_DATA_DIR}/tranco-1m.csv"

def find_domain_in_rank_list(rank_list_path, domain):
    with open(rank_list_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=['rank', 'domain'])
        for row in reader:
            if row['domain'] == domain:
                return row['rank']
    return None


def umbrella_rank_handler(domain):
    # try:
    #     domain = urlparse(url).hostname
    # except Exception as e:
    #     raise ValueError('Invalid URL')
    
    # if not os.path.exists(TEMP_FILE_PATH):
    #     print('Downloading Umbrella rank list')
    #     response = requests.get(FILE_URL, stream=True)
    #     response.raise_for_status()
    #
    #     print('Extracting Umbrella rank list')
    #     with zipfile.ZipFile(response.raw) as zip_ref:
    #         zip_ref.extractall(f'{WEBCHECK_DATA_DIR}/cache/')
    #
    # with open(TEMP_FILE_PATH, 'r', newline='', encoding='utf-8') as csvfile:
    #     reader = csv.DictReader(csvfile, fieldnames=['rank', 'domain'])
    #
    #     for row in reader:
    #         if row['domain'] == domain:
    #             print('Domain found in Umbrella rank list with rank:', row['rank'])
    #             return {
    #                 'domain': domain,
    #                 'rank': row['rank'],
    #                 'isFound': True
    #             }
    #
    #     return {
    #         'skipped': f'Skipping, as {domain} is not present in the Umbrella top 1M list.',
    #         'domain': domain,
    #         'isFound': False
    #     }
    rank = find_domain_in_rank_list(UMBRELLA_FILE_PATH, domain)
    if rank:
        return {
            'domain': domain,
            'rank': rank,
            'isFound': True
        }
    else:
        return {
            'domain': domain,
            'isFound': False
        }


def tranco_rank_handler(domain):
    rank = find_domain_in_rank_list(TRANCO_FILE_PATH, domain)
    if rank:
        return {
            'domain': domain,
            'rank': rank,
            'isFound': True
        }
    else:
        return {
            'domain': domain,
            'isFound': False
        }


def tranco_rank_api_handler(domain):
    try:
        auth = None
        if os.environ.get('TRANCO_API_KEY'):
            auth = (os.environ.get('TRANCO_USERNAME'), os.environ.get('TRANCO_API_KEY'))

        response = requests.get(
            f"https://tranco-list.eu/api/ranks/domain/{domain}",
            timeout=5.0,
            auth=auth
        )

        if not response.json() or not response.json().get('ranks') or len(response.json().get('ranks', [])) == 0:
            return {'skipped': f"Skipping, as {domain} isn't ranked in the top 100 million sites yet."}

        return response.json()
    except Exception as error:
        return {'error': f"Unable to fetch rank, {str(error)}"}


def rank_handler(domain):

    return {
        'umbrella': umbrella_rank_handler(domain),
        'tranco': tranco_rank_handler(domain),
        #'tranco_api': tranco_rank_api_handler(url)
    }