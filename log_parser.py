import csv
import os

filename = 'access_log.20220801'

def reader(filename):
    with open(filename,'r') as f:
        log = f.read()
        log = log.split('\n')
    return log
        
def save_to_csv(lst,filename):
    keys = ['IP','Remote Log Name','User Identifier','Datetime','Request','Requested URL','Status Code','Size','Referrer','User Agent']
    try:
        with open(f'{filename}.csv','a',encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f,keys,lineterminator='\n')
            dict_writer.writerows(lst)
    except Exception as e:
        print('Unable to save CSV')
        print(e)

def parse(log,filename):
    lst = []
    for line in log:
        if line:
            try:
                line = line.split(' ')
                ip = line[0]
                identd = line[1]
                rehg = line[2]
                datetime = line[3] + line[4]
                request = ''.join([line[5],line[6]]) + ' ' + line[7]
                requested_url = 'http://www.lafent.com' + request[request.find('/'):request.find(line[7])]
                requested_url = requested_url.strip()
                status = line[8]
                size = line[9]
                referrer = line[10]
                user_agent = ''.join([l for l in line[11:]])
                lst.append({
                    'IP':ip,
                    'Remote Log Name':identd,
                    'User Identifier':rehg,
                    'Datetime':datetime,
                    'Request':request,
                    'Requested URL':requested_url,
                    'Status Code':status,
                    'Size':size,
                    'Referrer':referrer,
                    'User Agent':user_agent
                })
            except Exception as e:
                print(line)
                print(e)
    save_to_csv(lst,filename)

def init_dir(filename):
    keys = ['IP','Remote Log Name','User Identifier','Datetime','Request','Requested URL','Status Code','Size','Referrer','User Agent']
    with open(f'{filename}.csv','w',encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f,keys)
        dict_writer.writeheader() 

if __name__ == '__main__':
    for f in os.listdir(os.getcwd()):
        if str(f).startswith('access_log'):
            print(f)
            log = reader(f)
            init_dir(f)
            parse(log,f)