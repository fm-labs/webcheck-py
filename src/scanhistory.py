import csv
import time

HISTORY_CSV = "data/scanhistory.csv"

def add_scanhistory(scanner: str, target: str):
    """
    Add a scan entry to the scan history CSV file.

    :param scanner: The scanner type (e.g., 'domain', 'url', 'host').
    :param target: The target that was scanned (e.g., domain name, URL, IP).
    :return:
    """
    timestamp = time.time()
    with open(HISTORY_CSV, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([scanner, target, int(timestamp * 1000)])  # store timestamp in milliseconds


def get_scanhistory(limit: int = 100) -> list[dict]:
    """
    Retrieve the scan history from the CSV file.

    :return: A list of dictionaries with keys 'scanner' and 'target'.
    """
    history = []
    try:
        with open(HISTORY_CSV, mode='r', newline='') as file:
            reader = csv.reader(file)
            i = 0
            for row in reader:
                if len(row) >= 2:
                    history.append({'scanner': row[0], 'target': row[1], 'timestamp': row[2]})
                else:
                    print("Malformed scan history entry:", row)

                i = i + 1
                if limit > 0 and i >= limit:
                    break
    except FileNotFoundError:
        pass  # No history file yet
    return history


def get_last_scans_by_type(scanner: str, limit: int = 10) -> list[str]:
    """
    Retrieve the last scanned targets of a specific scanner type.

    :param scanner: The scanner type to filter by.
    :param limit: The maximum number of entries to return.
    :return: A list of target strings.
    """
    history = get_scanhistory()
    filtered = [entry['target'] for entry in history if entry['scanner'] == scanner]

    # remove duplicates while preserving order
    seen = set()
    filtered = [x for x in filtered if not (x in seen or seen.add(x))]

    return filtered[-limit:]