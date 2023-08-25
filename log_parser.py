import csv
import os
import re
import sys
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count

def reader(filename):
    with open(filename,'r') as f:
        log = f.read()
        log = log.split('\n')
    return log
        
def save_to_csv(lst,filename):
    keys = ['IP','Remote Log Name','User Identifier','Timestamp','Method','Path','URL','Category','Version','Content Type','Status','Bytes','Referer','Referer Category','Referer Content Type','User Agent','Device','Identified Hostname','Direct Access']
    try:
        with open(f'{filename}.csv','a',encoding='utf-8-sig') as f:
            dict_writer = csv.DictWriter(f,keys,lineterminator='\n')
            dict_writer.writerows(lst)
    except Exception as e:
        print('Unable to save CSV')
        print(e)

def get_cat(url):
    if str(url).startswith('https://www.lafent.com/') or url.startswith('http://www.lafent.com/'):
        cats = {
            'inews':'news',
            'magazine':'magzine',
            'jobse':'jobs',
            'mtrial':'material',
            'photo':'photos',
            'sns':'social media',
            'help':'help',
            'search':'search',
        }
        for key,cat in cats.items():
                if str(url).lower().startswith(f'https://www.lafent.com/{key}') or str(url).lower().startswith(f'http://www.lafent.com/{key}'):
                    return cat
    return

def get_content_type(url):
    url = str(url).lower()
    if url.startswith('https://www.lafent.com/') or url.startswith('http://www.lafent.com/'):
        if '.html' in url:
            return 'html'
        if '.php' in url:
            return 'php'
        if '.pdf' in url or url.endswith('pdf'):
            return 'pdf'
        if '.jpg' in url or url.endswith('jpg'):
            return 'jpg'
        if '.png' in url or url.endswith('png'):
            return 'png'
        if '.gif' in url or url.endswith('gif'):
            return 'gif'
        if '.js' in url:
            return 'js'
        if '.css' in url:
            return 'css'
        if '.woff' in url:
            return 'font'
        if 'robots.txt' in url:
            return 'robots.txt'
        if '.txt' in url:
            return 'txt'
    return

def get_device(user_agent):
    devices = ['iphone','android','windows','macintosh']
    bots = ['http:','https:','bot','spider','crawl','yeti','lwp-trivial','cortex','mediapartners-google','the knowledge ai']
    for bot in bots:
        if bot in str(user_agent).lower():
            return 'bot'
    for device in devices:
            if device in str(user_agent).lower():
                return device
    return

def check_empty(field):
    if str(field) == '-' or str(field) == '\"-\"':
        return None
    return field

def parse(log,filename):
    lst = []
    for line in log:
        if line:
            pattern = r'^(?P<ips>(?:(?:\S+)(?:,\s*\S+)*)) (?P<identd>\S+) (?P<user>\S+) \[(?P<timestamp>[^\]]+)\] "(?P<method>\S+) (?P<path>\S+)(?: (?P<version>\S+))?" (?P<status>\d+) (?P<bytes>\d+) "(?P<referer>.*?)" "(?P<user_agent>.*?)"'
            match = re.match(pattern,line)
            if match:
                found_host = True
                ips = [ip.strip() for ip in match.group("ips").split(",")]
                if ips[0] == 'unknown':
                    found_host = False
                    ips = ips[1:]
                if len(ips) > 1:
                    device = 'bot'
                else:
                    device = None
                    ips = ips[0]
                ips = check_empty(ips)
                identd = check_empty(match.group("identd"))
                user = check_empty(match.group("user"))
                timestamp = datetime.strptime(match.group("timestamp"),'%d/%b/%Y:%H:%M:%S %z')
                method = match.group("method")
                path = match.group("path")
                url = f'https://www.lafent.com{path}'
                cat = get_cat(url)
                content_type = get_content_type(url)
                version = match.group("version")
                status = match.group("status")
                bytes = match.group("bytes")
                referer = check_empty(match.group("referer"))
                dir_acc = True
                ref_cat = None
                ref_content_type = None
                if referer:
                    dir_acc = False
                    ref_cat = get_cat(referer)
                    ref_content_type = get_content_type(referer)
                user_agent = check_empty(match.group("user_agent"))
                if not device and user_agent:
                    device = get_device(user_agent)
                lst.append({
                    'IP':ips,
                    'Remote Log Name':identd,
                    'User Identifier':user,
                    'Timestamp':timestamp,
                    'Method':method,
                    "Path":path,
                    "URL":url,
                    "Category":cat,
                    "Version":version,
                    "Content Type":content_type,
                    "Status":status,
                    "Bytes":bytes,
                    "Referer":referer,
                    "Referer Category":ref_cat,
                    "Referer Content Type":ref_content_type,
                    "User Agent":user_agent,
                    "Device":device,
                    "Identified Hostname":found_host,
                    "Direct Access":dir_acc
                })
            else:
                with open('invalid_paths.txt','a',encoding='utf-8-sig') as sys.stdout:
                    print(line)
    save_to_csv(lst,filename)

def init_dir(filename):
    keys = ['IP','Remote Log Name','User Identifier','Timestamp','Method','Path','URL','Category','Version','Content Type','Status','Bytes','Referer','Referer Category','Referer Content Type','User Agent','Device','Identified Hostname','Direct Access']
    with open(f'{filename}.csv','w',encoding='utf-8-sig') as f:
        dict_writer = csv.DictWriter(f,keys)
        dict_writer.writeheader()

def process_log_file(f):
    log = reader(f)
    init_dir(f)
    try:
        parse(log,f)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    with ProcessPoolExecutor(max_workers=cpu_count()-2) as executor:
        log_files = [f for f in os.listdir() if str(f).startswith('access_log')]
        executor.map(process_log_file, log_files)
