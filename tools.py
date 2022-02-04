import datetime
import re, json


def rerunFormat(values, prefix=None):
    dictionary = values.strip().strip('"').split('\n')
    wPrefix = None
    if prefix:
        wPrefix = list(map(lambda val: f'{prefix}@{val}', dictionary))
    else:
        wPrefix = list(map(lambda val: f'{get_date()}@{trigger_time(parseId_get_country(val))}@{val}', dictionary))
    return ','.join(wPrefix)

def sqlFormat(values, website=False):
    dictionary = values.strip().split('\n')
    
    def appendW(val):
        return f"'www.{val}'"
    
    def appendComma(val):
        return f"'{val}'"
        
    func = appendW if website else appendComma
    
    return',\n'.join(map(func, dictionary))

def parseId_get_country(id):
    country = None
    try:
        db_time_rgx = r'^([\d|\w]\d\d)([A-Z]{2})'
        matches = re.search(db_time_rgx, id)
        if matches:
            country = matches.group(2)
    except:
        pass    
    return country

def parseId_get_db(id):
    db = None
    try:
        db_time_rgx = r'^([\d|\w]\d\d)([A-Z]{2})'
        matches = re.search(db_time_rgx, id)
        if matches:
            db = matches.group(1)
    except:
        pass    
    return db

def trigger_time(country):
    try:
        with open('trigger-time-config.json', 'r') as json_file:
            lines = json_file.read()
            _json = json.loads(str(lines))
            return _json[country]
    except:
        return '22:00:00'
        
def get_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def get_metric(num):
    metric_files = ['rerun_cmp.py', 'rerun_rnk.py', 'rerun_list.py', 'manual_cmp_webshots.py']
    try:
        return metric_files[num]
    except:
        # if error return default rerun_cmp.py
        return metric_files[0]

def get_status(num):
    status = ['CRAWL_FAILED', 'CRAWL_FINISHED', 'CREATED']
    try:
        return status[num]
    except:
        return status[0]

def get_commands(metric, status, ids, db=None):
    
    metric_types = ['comp', 'rank', 'list', 'web']
    metric_code = 0
    if isinstance(metric, str):
        metric_code = metric_types.index(metric)
    else:
        metric_code = metric

    if metric_code >= 3:
        return f'python {get_metric(metric_code)} -c {db} -i {ids}'
    return f'python {get_metric(metric_code)} -s {get_status(status)} -l {ids}'

    