from time import sleep
import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import logging
from utils import setup_logging

setup_logging()
#url = 'https://career.habr.com/vacancies?page=1&q=data%20science&qid=3&remote=1&sort=date&type=all'
dataname = (datetime.now()).date()
day=dataname.day # нужно что бы парсить только за вчерашние вакансии

headers=({'user-agent': 
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36'
        '(KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'})
# записиваем ссылки вакансии за сегодня и прошлый день
links=[]
data = []
data.append(['title',  'company', 'country',
            'location', 'salary', 'source', 
            'link', 'date', 'company_field', 
            'description', 'skills', 'job_type'])

def scan(url):
    try:
        response = requests.get(url,headers=headers)
        sleep(1)                  # when time decreases, more links give no information
    except Exception as ex:
        logging.info(url,ex)
    soup = BeautifulSoup(response.text,"lxml")
    try:
        title = soup.find("h1",class_=("page-title__title")).text
    except:
        title = ''
    try:
        company = soup.find("div",class_="vacancy-company").find_all("a")[1].text
    except:
        company = ''
    country = "РФ"
    try:
        location=soup.find_all("span",class_="inline-list")[2].text.split('•')[0]
    except:
        location = ''
    try:
        salary = soup.find("div",class_="basic-salary").text
    except:
        salary = ''
    source = "ХАБР"
    link=url
    date = dataname
    try:
        company_field = soup.find("div",class_="vacancy-company__sub-title").text
    except:
        company_field = ''
    try:
        description = soup.find("div",class_="basic-section--appearance-vacancy-description").text
    except:
        description = ''
    try:
        skills = soup.find("span",class_="inline-list").text
    except:
        skills = ''
    try:
        job_type = soup.find_all("span",class_="inline-list")[2].text.split('•')[1]
    except:
        job_type = ''
    return ([title,  company, country,
            location, salary, source, 
            link, date, company_field, 
            description, skills, job_type])

def main():
    for u in range(1,5):
        url=f'https://career.habr.com/vacancies?page={u}&q=data%20science&qid=3&remote=1&sort=date&type=all'
        response = requests.get(url,headers=headers)
        soup = BeautifulSoup(response.text,"lxml")
        vacancys = soup.find_all("div",class_="section-box")
        for i in vacancys:
            try:
                # записиваем ссылки вакансии за сегодня и прошлый день
                if int(i.find("time").text.split()[0]) > day-2:
                    links.append('https://career.habr.com'+(i.find("div",class_='vacancy-card__title').find('a')).get('href'))
            except:
                sleep(0.1)
    # теперь в links у нас ссылки вакансии
    # пройдемся по ним циклом
    for i in links:
        try:
            data.append(scan(i)) 
        except Exception as ex:
            logging.info(url,ex)
            
    with open(f'Xabr_{dataname}.csv', 'w+', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerows(data)

if __name__ == "__main__":
    main()