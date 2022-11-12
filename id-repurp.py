from urllib.request import urlopen
from datetime import datetime
import sys
import json

max_age_of_older_version = 365 # days
inactivity_thresh = 365 # days

class Record:
    time = None
    status = 0
    size = 0

    def __init__(self, time, status, size):
        self.time = time
        self.status = status
        self.size = size

    @staticmethod
    def from_json(record):
        time = parse_time(record['time'])
        status = int(record['status'])
        size = int(record['size'])
        return Record(time, status, size)

domain_to_records = {}

def parse_time(time_string):
    return datetime.strptime(time_string, '%Y-%m-%d %H:%M:%S')


def fetch_data_for_domain(domain):
    try:
        url = f'http://archive-api.edoms.com/api/v2/{domain}'
        response = urlopen(url)
        raw_response = response.read()
        data_json = json.loads(raw_response)
        records = []
        for status_change in data_json[domain]['data']:
            for page_change in status_change:
                only = page_change.get('only')
                if only is None:
                    first = page_change.get('first')
                    last =  page_change.get('last')
                    records.append(Record.from_json(first))
                    records.append(Record.from_json(last))
                else:
                    records.append(Record.from_json(only))
        return records
    except ValueError:
        print(f'error: {domain} does not look like a domain name')
        sys.exit(1)

def get_domain_records(domain):
    records = domain_to_records.get(domain)
    if records is None:
        records = fetch_data_for_domain(domain)
        domain_to_records[domain] = records
    return records

def has_bad_status(record):
    return record.status >= 400 and record.status < 600

def get_max_inactivity(domain):
    best_diff = None
    best_first = None
    best_record = None

    records = get_domain_records(domain)
    first_bad = None
    for record in records:
<<<<<<< HEAD
        if has_bad_status(record):
            if first_bad is None:
                first_bad = record
            else:
                diff = record.time - first_bad.time
                if best_diff is None or diff.days > best_diff.days:
                    best_diff = diff
                    best_first = first_bad
                    best_record = record
        else:
            first_bad = None

    print(f'debug: max inactivity from {best_first.time} to {best_record.time}')
    return best_diff.days
=======
        if previous is not None:
            diff = record.time - previous.time
            if best_diff is None or diff.days > best_diff.days:
                best_diff = diff
                best_previous = previous
                best_record = record
        previous = record
    return best_diff.days if best_diff is not None else 0
>>>>>>> 9444e76 (wip)

domain = sys.argv[1]

print(get_max_inactivity(domain))
