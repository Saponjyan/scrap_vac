# pip install selenium, webdriver_manager, pyvirtualdisplay, bs4,lxml,requests
# sudo apt-get install xvfb 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
from bs4 import BeautifulSoup
import csv
from time import sleep
from pyvirtualdisplay import Display
import logging
import json
from utils import setup_logging

display = Display(visible=0, size=(1920, 1200))  
display.start()
options = webdriver.ChromeOptions()
# options.add_argument("--window-size=1920,1200")
options.add_argument('--no-sandbox')
options.add_argument('start-maximized')
options.add_argument('enable-automation')
options.add_argument('--disable-infobars')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-browser-side-navigation')
options.add_argument("--remote-debugging-port=9222")
options.add_argument('--disable-gpu')
options.add_argument("--log-level=3")
driver = webdriver.Chrome( options=options)
ac = ActionChains(driver) 
dataname = (datetime.now()).date()


setup_logging()
with open("DreamParser-parser_glassdoor/src/parser/urls.json","r", encoding="utf-8") as json_data:
    urls = json.load(json_data)
alllinks={}# id, link c левой стороны

def scan(cont,alllink):
        # поскольку на сайте не указывается конкретное время публикации вакансии, проставляем везде дату текущего дня
    today = datetime.now()
    date = today.date()
        # закрываем высплывающие окна, которые могут появиться, кликнув на основную часть страницы 
    try:
        ac.move_by_offset(1, 1).click().perform()                                                                                                                                                                                                                                                                                                                                
    except Exception as ex:
            #print(repr(ex))
        sleep(0.1)
        # забираем весь html страницы    
    sleep(1)
    soup=BeautifulSoup(driver.page_source,"lxml")
    sleep(2)
        # получаем id с правой стороны
    try:
        idd_right = soup.find("article",class_="scrollable active css-1d88wr9 ead8scz0").get("data-id")
    except Exception as ex:
        logging.info("response ERROR")
        # название компании
    try:
        employerName = soup.find("div",class_="css-87uc0g").text[:-3]
    except:
        employerName = ''
        # имя вакансии
    try:
        jobTitle = soup.find("div",class_="css-1vg6q84 e1tk4kwz4").text
    except:
        jobTitle = ''

        # месторасположение
    try:
        location = (soup.find("div",class_="css-56kyx5 e1tk4kwz5").text).split(',')[0]
    except:
        location = ''

        # зарплата
    try:
        detailSalary = driver.find_element(By.XPATH,("/html/body/div[2]/div/div/"
            "div/div/div[2]/section/div/div/article/div/div[1]/div/div/div[1]/div[3]"
            "/div[1]/div[4]/span")).text
    except:
        detailSalary = ''
        # ссылка

    link = alllink[idd_right]

        # страна
    country = cont
        # текст вакансии
    try:    
        text2 = soup.find("div",class_="jobDescriptionContent").text
    except:
        text2 = ''
        # сайт
    source = "GLASSDOOR"
        # опис комп
    try:
        company_field = driver.find_element(By.XPATH,("/html/body/div[2]/div/div/div/"
            "div/div[2]/section/div/div/article/div/div[2]/div[1]/div[3]/div/div/"
            "div[1]/div/div[4]/span[2]")).text

    except:
        company_field = ''
        #skills
    try:
        skils = driver.find_element(By.XPATH,("/html/body/div[2]/div/div/div/"
                                        "div/div[2]/section/div/div/article/div/"
                                "div[2]/div[1]/div[1]/div/div[1]/div/ul[2]")).text

    except:
        skils = ''

        #job_type
    job_type = ''
    job_types = soup.find("div",
                    class_="jobDescriptionContent desc").find_all("p")
    for jobs in job_types:
        # z = i.text.split(":")
        if jobs.text.split(":")[0] == "Job Type":
            job_type = jobs.text.split(":")[1]
        
        # сразу возвращаем df   
    return ([jobTitle, employerName, country, location, 
                detailSalary, source, link,date, company_field,
                text2, skils, job_type])

def main():

    data=[]
    data.append(['title',  'company', 'country',
                                'location', 'salary', 'source',
                                'link', 'date', 'company_field',
                                'description', 'skills', 'job_type'])
    # цикл по ссылкам
    for country, url in urls.items():
        driver.get(url)
        sleep(3)
        # избавляемся от всплывающих окон
        try:
            ac.move_by_offset(1, 1).click().perform() 
            sleep(1)
        except Exception as ex:
            sleep(0.1)       

        # забираем весь html страницы
        soup=BeautifulSoup(driver.page_source,"lxml")
        sleep(2)
        
        # находим количество страниц и если нет вакансий по запросу пропускаем
        try:
            last_page = soup.find("div",class_="paginationFooter")
            last_page = int(last_page.text.split()[-1]) 
        except Exception as ex:
            last_page=1
            logging.info("response ERROR")
            #continue

        # цикл по страницам
        for j in range(last_page): 
            soup=BeautifulSoup(driver.page_source,"lxml")
            sleep(2)
            # вакансии что бы в цыкле по xpath проходить по номеру
            vacancy = soup.find_all("li",class_="react-job-listing")
            
            # по id находим присвоиваем ссылки        
            for v in vacancy:
                alllinks[v.get("data-id")]="https://www.glassdoor.com" + v.find("a").get("href")
            # цыкл по вакансиям   
            for i in range(1,len(vacancy)+1): 
                try:
                    sleep(2)
                    button= driver.find_element(By.XPATH,(f'/html/body/div[2]/div/div/'
                    f'div/div/div[2]/section/article/div[1]/ul/li[{i}]/div[2]/a'))
                    sleep(1)
                    button.click()
                except Exception as ex:
                    logging.info("click ERROR")

                try:
                    data.append(scan(country,alllinks)) # передаем страну
                    #print(data[-1])
                except Exception as ex:
                    logging.info("global append ERROR")
                    
            try:                                         
                next_page = driver.find_element(By.XPATH,('/html/body/div[2]/div/'
                'div/div/div/div[2]/section/article/div[2]/div/div[1]/button[4]'))
                sleep(2) 
                next_page.click() # переход на следующую страницу
                
            except Exception as ex:
                logging.info("next page ERROR")

    with open(f'glassdoor_{dataname}.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerows(data)
    driver.quit()

if __name__ == "__main__":
    main()