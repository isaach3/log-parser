import pandas as pd
from requests_html import HTMLSession
import concurrent.futures
from multiprocessing import cpu_count
import time
from random import randrange
import csv

s = HTMLSession()
s.headers.update({"User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.2 Safari/605.1.15'})

def save_to_csv(lst, keys, cat):
    try:
        with open(f'{cat}.csv','a',encoding='utf-8-sig') as f:
            dict_writer = csv.DictWriter(f,keys)
            dict_writer.writerow(lst)
    except Exception as e:
        print('Unable to save CSV')
        print(e)

def get_response(url):
    r = s.get(url)
    time.sleep(1 + (0.1*randrange(5,10)))
    if r.status_code == 200:
        return r
    print('bad response')

def nav_news(url):
    r = get_response(url)
    r.html.render()
    time.sleep(1 + (0.1*randrange(5,10)))
    res = dict.fromkeys(['title','sub-title','publisher','author','date','text','keywords','href'])
    res['title'] = r.html.find('div.article_header',first=True).find('h3',first=True).text.strip()
    res['sub-title'] = r.html.find('div.article_header',first=True).find('span.stit',first=True).text.strip()
    header = r.html.find('div.write',first=True).text.strip().split('l')
    time.sleep(1 + (0.1*randrange(5,10)))
    try:
        res['publisher'] = header[0]
        if header[1]:
            res['author'] = header[1].split()[0]
        if header[2]:
            res['date'] = header[2][4:]
    except IndexError as e:
        print(header)
        raise e
    content = r.html.find('div.cont_class_2 > p, div.cont_class_2 > div, div.cont_class_2 > span')
    
    text = ''
    for c in content:
        if c.text:
            text += (c.text.strip() + ' ')
    if not text:
        text = r.html.find('div.cont_class_2',first=True).text
    res['text'] = text
    keyword_content = r.html.find('div.keyword > a')
    keywords = []
    for keyword in keyword_content:
        if keyword.text:
            keywords.append(keyword.text)
    res['keywords'] = keywords
    res['href'] = url
    time.sleep(1 + (0.1*randrange(5,10)))
    return res

def news():
    print('news')
    news_urls = pd.read_csv('news_links.csv')['URL'].unique()[9811:]
    print(len(news_urls))
    keys = ['title','sub-title','publisher','author','date','text','keywords','href']
    # with open('news.csv','w',encoding='utf-8-sig') as f:
    #     dict_writer = csv.DictWriter(f,keys)
    #     dict_writer.writeheader()
    with concurrent.futures.ProcessPoolExecutor(max_workers=cpu_count()-2) as executor:
        for res in executor.map(nav_news,news_urls):
            if res:
                save_to_csv(res,keys,'news')

def nav_jobs(url):
    r = get_response(url)
    try:
        r.html.render()
    except:
        print(url)
    time.sleep(1 + (0.1*randrange(5,10)))
    res = dict.fromkeys(['company','대표자','사원수','주요분야','자본금','주요업종','매출액','소재지역','홈페이지','담당업무','근무지역','고용형태','근무부서','복리후생','급여조건','모집인원','경력사항','나이제한','최종학력','우대사항','접수기간','상세설명','keywords','href'])
    
    company_info = r.html.find('div.comp_info',first=True)
    res['company'] = company_info.find('span.tit',first=True).text.strip()
    details = company_info.find('ul.job',first=True).find('li')
    for idx,key in enumerate(['대표자','사원수','주요분야','자본금','주요업종','매출액','소재지역','홈페이지']):
        if details[idx] and len(details[idx].text.strip().split(':')) > 1:
            if key == '사원수':
                res[key] = details[idx].text.strip().split(':')[1][:-1].strip()
            else:
                res[key] = details[idx].text.strip().split(':')[1]
    tables = r.html.find('div.viewinfo_set')

    recr_details = tables[0].find('li')
    for idx,key in enumerate(['담당업무','근무지역','고용형태','근무부서','복리후생','급여조건','모집인원']):
        if recr_details[idx]:
            if key == '모집인원':
                res[key] = recr_details[idx].text.strip()[4:][:-1]
            else:
                res[key] = recr_details[idx].text.strip()[4:]

    qual_details = tables[1].find('li')
    for idx,key in enumerate(['경력사항','나이제한','최종학력','우대사항']):
        if qual_details[idx]:
            res[key] = qual_details[idx].text.strip()[4:]
    time.sleep(1 + (0.1*randrange(5,10)))
    res['접수기간'] = tables[2].find('li',first=True).text.strip()[4:]
    res['상세설명'] = tables[3].text.strip()

    keyword_content = r.html.find('div.keyword > a')
    keywords = []
    for keyword in keyword_content:
        if keyword.text:
            keywords.append(keyword.text)
    res['keywords'] = keywords
    res['href'] = url
    return res

def jobs():
    print('jobs')
    job_urls = pd.read_csv('job_links.csv')['URL'].unique()[4466:]
    print(len(job_urls))
    keys = ['company','대표자','주요분야','주요업종','소재지역','사원수','자본금','매출액','홈페이지','담당업무','근무지역','고용형태','근무부서','복리후생','급여조건','모집인원','경력사항','나이제한','최종학력','우대사항','접수기간','상세설명','keywords','href']
    # with open('jobs.csv','w',encoding='utf-8-sig') as f:
    #     dict_writer = csv.DictWriter(f,keys)
    #     dict_writer.writeheader()
    with concurrent.futures.ProcessPoolExecutor(max_workers=cpu_count()-2) as executor:
        for res in executor.map(nav_jobs,job_urls):
            if res:
                save_to_csv(res,keys,'jobs')

# def nav_qna(url):
#     print('.',end='')
#     sys.stdout.flush()
#     return

# def nav_free(url):
#     print('.',end='')
#     sys.stdout.flush()
#     return

# def nav_agr(url):
#     print('.',end='')
#     sys.stdout.flush()
#     return

# def nav_soc_news(url):
#     print('.',end='')
#     sys.stdout.flush()
#     return

# def social():
#     print('social')
#     qna_urls = pd.read_csv('qna.csv')['URL'].unique()
#     keys = []
#     qna_lst = []
#     print('qna')
#     with concurrent.futures.ProcessPoolExecutor(max_workers=cpu_count()-2) as executor:
#         for res in executor.map(nav_qna,qna_urls):
#             qna_lst.append(res)
#     save_to_csv(qna_lst,keys,'qna')

#     free_urls = pd.read_csv('free.csv')['URL'].unique()
#     keys = []
#     free_lst = []
#     print('free')
#     with concurrent.futures.ProcessPoolExecutor(max_workers=cpu_count()-2) as executor:
#         for res in executor.map(nav_free,free_urls):
#             free_lst.append(res)
#     save_to_csv(free_lst,keys,'free')

#     agr_urls = pd.read_csv('agr.csv')['URL'].unique()
#     keys = []
#     agr_lst = []
#     print('agr')
#     with concurrent.futures.ProcessPoolExecutor(max_workers=cpu_count()-2) as executor:
#         for res in executor.map(nav_agr,agr_urls):
#             agr_lst.append(res)
#     save_to_csv(agr_lst,keys,'agr')
    
#     soc_news_urls = pd.read_csv('soc_news.csv')['URL'].unique()
#     keys = []
#     soc_news_lst = []
#     print('soc_news')
#     with concurrent.futures.ProcessPoolExecutor(max_workers=cpu_count()-2) as executor:
#         for res in executor.map(nav_soc_news,soc_news_urls):
#             soc_news_lst.append(res)
#     save_to_csv(soc_news_lst,keys,'agr')
#     return

if __name__ == '__main__':
    # jobs()
    news()
    # social()


