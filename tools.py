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

def jsonFormat(values, website=False):
    lst = values.strip().split('\n')
    
    def appendW(val):
        return f"'www.{val}'"
    
    def appendComma(val):
        return f'"{val}"'
        
    func = appendW if website else appendComma
    
    return',\n'.join(map(func, lst))

def parseId_get_country(id):
    country = None
    try:
        if '@' in id:
            id = id.split('@')[-1]
            
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
        if '@' in id:
            id = id.split('@')[-1]

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
    metric_files = ['rerun_cmp.py', 'rerun_rnk.py', 'rerun_lst.py', 'manual_cmp_webshots.py']
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

def format_couch_multi_query(ids):
    
    id_list = ids.split(',')
    formatted = ','.join(list(map(lambda id: f'"{id}"', id_list)))
    array_format = f'[{formatted}]'

    return array_format

def payload_builder(ids, metric='comp', date=None, override_t_time=None, retailer=None, mode='rerun', country=None, company=None):
    if not date:
        date = get_date()
    # evaluate country from the first id
    # company_code = parseId_get_db(ids[0])

    if metric == 'comp':
        return comparison_payload(ids, mode, date)

    if metric == 'rank':
        try:
            if override_t_time:
                t_time = override_t_time
            return ranking_payload(ids, mode, date, t_time, company, retailer, country)
        except:
            return {
                "error": "missing params",
                "hint": "keywords, mode, date, trigger time, company, retailer, country are the parameters"
            }

    return {}



def comparison_payload(ids, mode, date):
    data_points_list = ids.strip().split('\n')
    country = parseId_get_country(data_points_list[0])
    t_time = trigger_time(country)
    company_code = parseId_get_db(data_points_list[0])
    payload = {
    "version": "1.0",
    "request": {
        "task_name": f"Comparisons-Rerun-{date}-{t_time}",
        "user_uuid": "1Q2W3E4R5T6Y7U8I9O0P",
        "data": {
            "company": company_code,
            "run_mode": mode,
            "schedule_time": t_time,
            "schedule_date": date,
            "retailers": [],
            "data_points": data_points_list
        }
        }   
    }

    return payload

def ranking_payload(keywords_or_ids, mode, date, override_t_time, company, retailer, country):

    def get_data_points_list(values:list, retailer):
        data_points_list = []
        for val in values:
            data_points_list.append({
                "keyword": val,
                "retailer": retailer
            })
        return data_points_list

    values = keywords_or_ids.strip().split('\n')
    data_points_list = get_data_points_list(values, retailer)

    t_time = trigger_time(country)
    if override_t_time:
        t_time = override_t_time


    payload = {
    "version": "1.0",
    "request": {
        "task_name": f"Rankings-Rerun-{date}-{t_time}",
        "user_uuid": "1Q2W3E4R5T6Y7U8I9O0P",
        "data": {
            "company": company,
            "run_mode": mode,
            "schedule_time": t_time,
            "schedule_date": date,
            "retailers": [],
            "data_points": data_points_list
        }
    }
    }

    return payload

def psy_format(ids):
    list = ids.strip().split('\n')
    return ':'.join(list)