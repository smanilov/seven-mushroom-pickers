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
total_times = {}

def parse_time(time_string):
    return datetime.strptime(time_string, '%Y-%m-%d %H:%M:%S')


def fetch_data_for_domain(domain):
    try:
        url = f'http://archive-api.edoms.com/api/v2/{domain}'
        response = urlopen(url)
        raw_response = response.read()
        data_json = json.loads(raw_response)
        records = []
        first_time = data_json[domain]['header']['first_date']
        first_time = parse_time(first_time) if first_time is not None else 0

        last_time = data_json[domain]['header']['last_date']
        last_time = parse_time(last_time) if last_time is not None else 0

        if first_time == 0 or last_time == 0:
            now = datetime.now()
            total_times[domain] = now - now
        else:
            total_times[domain] = last_time - first_time

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

    return best_diff.days if best_diff is not None else 0

# aka downtime
def get_avg_inactivity(domain):
    records = get_domain_records(domain)
    previous = None

    # get some zero accumulator values somehow
    now = datetime.now()
    total_up = now - now
    total_down = now - now

    for record in records:
        if previous is not None:
            diff = record.time - previous.time
            if has_bad_status(record):
                total_down += diff
            else:
                total_up += diff
        previous = record

    up = total_up.total_seconds()
    down = total_down.total_seconds()
    return down / (down + up) if (down + up) > 0 else None


def report_results(domain):
    max_break = get_max_inactivity(domain)
    lifespan = total_times[domain].days
    break_part = "%.4f" % (max_break / lifespan) if lifespan > 0 else "-"
    downtime = get_avg_inactivity(domain)
    downtime = "%.4f" % downtime if downtime is not None else "-"
    print('domain\t' +\
          'max_break (days)\t' +\
          'lifespan (days)\t' +\
          'break_part (fract)\t' +\
          'downtime (fract)')
    print(f'{domain}\t' + \
          f'{max_break}\t' + \
          f'{lifespan}\t' + \
          f'{break_part}\t' + \
          f'{downtime}')


domain = sys.argv[1]
report_results(domain)
