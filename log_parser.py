import csv
import os
import time 
import re
import sys
from ipaddress import ip_address
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count


# filename = 'access_log.20220801'

def reader(filename):
    with open(filename,'r') as f:
        log = f.read()
        log = log.split('\n')
    return log
        
def save_to_csv(lst,filename):
    keys = ['IP','Remote Log Name','User Identifier','Timestamp','Method','Path','URL','Version','Status','Bytes','Referrer','User Agent']
    try:
        with open(f'{filename}.csv','a',encoding='utf-8-sig') as f:
            dict_writer = csv.DictWriter(f,keys,lineterminator='\n')
            dict_writer.writerows(lst)
    except Exception as e:
        print('Unable to save CSV')
        print(e)

def parse(log,filename):
    lst = []
    for line in log:
        if line:
            line = line.strip('\'')
            pattern = r'^(?P<ips>(?:(?:\S+)(?:,\s*\S+)*)) (?P<identd>\S+) (?P<user>\S+) \[(?P<timestamp>[^\]]+)\] "(?P<method>\S+) (?P<path>\S+)(?: (?P<version>\S+))?" (?P<status>\d+) (?P<bytes>\d+) "(?P<referrer>.*?)" "(?P<user_agent>.*?)"'
            match = re.match(pattern,line)
            if match:
                ips = [ip.strip() for ip in match.group("ips").split(",")]
                identd = match.group("identd")
                user = match.group("user")
                timestamp = datetime.strptime(match.group("timestamp"),'%d/%b/%Y:%H:%M:%S %z')
                method = match.group("method")
                path = match.group("path")
                url = f'https://www.lafent.com{path}'
                version = match.group("version")
                status = match.group("status")
                bytes = match.group("bytes")
                referrer = match.group("referrer")
                user_agent = match.group("user_agent")
                lst.append({
                    'IP':ips,
                    'Remote Log Name':identd,
                    'User Identifier':user,
                    'Timestamp':timestamp,
                    'Method':method,
                    "Path":path,
                    "URL":url,
                    "Version":version,
                    "Status":status,
                    "Bytes":bytes,
                    "Referrer":referrer,
                    "User Agent":user_agent
                })
            else:
                with open('invalid_paths.txt','a',encoding='utf-8-sig') as sys.stdout:
                    print(line)
    save_to_csv(lst,filename)

def init_dir(filename):
    keys = ['IP','Remote Log Name','User Identifier','Timestamp','Method','Path','URL','Version','Status','Bytes','Referrer','User Agent']
    with open(f'{filename}.csv','w',encoding='utf-8-sig') as f:
        dict_writer = csv.DictWriter(f,keys)
        dict_writer.writeheader()

def process_log_file(f):
    log = reader(f)
    init_dir(f)
    parse(log,f)

if __name__ == '__main__':
    with ProcessPoolExecutor(max_workers=cpu_count()-3) as executor:
        log_files = [f for f in os.listdir() if str(f).startswith('access_log')]
        executor.map(process_log_file, log_files)