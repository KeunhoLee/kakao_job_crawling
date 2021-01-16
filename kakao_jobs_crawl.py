import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
# from selenium import webdriver
import time
from datetime import datetime

# 메인페이지 소스 가져오가
def get_main_page_src(url):
    req = requests.get(main_url)
    
    job_main_html = req.text
    
    main_soup = bs(job_main_html, 'html.parser')
    
    return main_soup

# 페이지 최대값 가져오기
def get_last_page(soup):
    
    to_last_btn = soup.select('#mArticle > div > div.paging_list > span > a.change_page.btn_lst')
    
    last_page_url = to_last_btn[0]['href']
    
    last_page = int(last_page_url[-1])
    
    return last_page

# 해시태그 가져오기
def get_job_tag(jobs_info):
    result = []
    jobs_info = jobs_info.find_all('a', {'class':'link_tag'})
    
    for job in jobs_info:
        result += [job['data-code']]
        
    str_result = ', '.join(result)
    
    return str_result

# 공고 정보
def get_to_page_jobs(page_num):
    
    pn = page_num
    
    url = f'https://careers.kakao.com/jobs?page={pn}'
    
    req = requests.get(url)
    
    page_html = req.text
    
    return page_html

main_url = 'https://careers.kakao.com/jobs'
main_soup = get_main_page_src(main_url)

max_page = get_last_page(main_soup)

job_df = pd.DataFrame()

for i in range(1,max_page+1):
    time.sleep(2)
    soup = bs(get_to_page_jobs(i), 'html.parser')
    jobs_info = soup.select('#mArticle > div > ul.list_jobs > li > div > div.wrap_info' )
    
    job_title = list(map(lambda x: x.find_all('h4', {'class':'tit_jobs'})[0].get_text(), jobs_info))
    job_due_date = list(map(lambda x: x.select('dl > dd')[0].get_text(), jobs_info))
    job_location = list(map(lambda x: x.select('dl > dd')[1].get_text(), jobs_info))
    job_tags = list(map(lambda x: get_job_tag(x), jobs_info))
    job_url = list(map(lambda x: main_url.replace('/jobs', '') + x.select('a.link_jobs')[0]['href'], jobs_info))
    
    temp_df = pd.DataFrame( {'job_title' : job_title,
                             'job_due_date' : job_due_date,
                             'job_location' : job_location,
                             'job_tags' : job_tags,
                             'job_url' : job_url
                            })
    
    job_df = job_df.append(temp_df, ignore_index = True)

job_df['create_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
job_df['last_modified_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

job_df.to_csv('./test.csv', encoding='utf-8')

