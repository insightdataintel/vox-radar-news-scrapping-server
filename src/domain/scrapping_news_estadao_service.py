import json
import datetime
from flask import request
import pandas as pd
import datetime
from src.config.enum import Log

from src.integration.s3.s3 import S3
from src.integration.sqs.sqs import Sqs
from src.repository.adapters.postgres.view_estadao_log_repository import ViewEstadaoLogRepository
from src.types.sigarp_save_data_estadao_queue_dto import SigarpSaveDataEstadaoQueueDTO
from src.types.voxradar_news_save_data_queue_dto import VoxradarNewsSaveDataQueueDTO
from src.types.voxradar_news_scrapping_estadao_queue_dto import VoxradarNewsScrappingEstadaoQueueDTO

from ..config.envs import Envs
from ..config.constants import Constants
from .base.base_service import BaseService
from ..types.sigarp_capture_data_estadao_scrapping_queue_dto import SigarpCaptureDataEstadaoScrappingQueueDTO
from ..types.return_service import ReturnService
import xlrd

from ..integration.selenium.selenium import Selenium

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
from bs4 import BeautifulSoup
import unicodedata
import pandas as pd
import numpy as np
import requests
import logging
import pickle
import time
import os


def month_convert(data_text):  
    data_text = data_text.lower()
    
    meses={"janeiro":"01",
        "fevereiro":"02",
        "março":"03",
        "abril":"04",
        "maio":"05",
        "junho":"06",
        "julho":"07",
        "agosto":"08",
        "setembro":"09",
        "outubro":"10",
        "novembro":"11",
        "dezembro":"12"}

    for i in meses.keys():
        if i in data_text:
            data_text=data_text.replace(i,meses[i]) 

    meses={"jan":"01",
           "fev":"02",
           "mar":"03",
           "abr":"04",
           "mai":"05",
           "jun":"06",
           "jul":"07",
           "ago":"08",
           "set":"09",
           "out":"10",
           "nov":"11",
           "dez":"12"}

    for i in meses.keys():
        if i in data_text:
            data_text=data_text.replace(i,meses[i])
    
    return data_text

class ScrappingNewsEstadaoService(BaseService):
    # s3: S3
    sqs: Sqs

    def __init__(self):
        super().__init__()
        # self.log_repository = ViewEstadaoLogRepository()
        # self.s3 = S3()
        self.sqs = Sqs()

    def exec(self, body:str) -> ReturnService:
        print(f'\n----- Scrapper | Init - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")} -----\n')
        estadao_dict = {'title': [], 'data': [], 'body_news': [], 'link': [],'category': [],'image': []}
        
        voxradar_news_scrapping_estadao_queue_dto:VoxradarNewsScrappingEstadaoQueueDTO = self.__parse_body(body)

        url_news = voxradar_news_scrapping_estadao_queue_dto.url

        # for url in url_news:    
        page = requests.get(url_news).text
        # if page is False:
        #     continue        
        soup = BeautifulSoup(page, 'html.parser')         
        #Pegando o título
        try:
            title = soup.find_all("h1")[0].text.replace('"', '').replace("'", "")
        except Exception as e:
            self.logger.error(f"Não foi possível recuperar alguma informação do site Estadão, o erro encontrado foi | {e}")
            title = " "
            pass                 
        #
        #Stardandizing Date
        try:
            data = soup.find("meta", attrs={'name': 'date'})
            data = str(data).split("content=")[1].split(" ")[0].replace('"','')
            data = data.replace("T", " ")
        except:
            data = soup.find("script", type="application/ld+json")
            data = str(data).split("datePublished")[1].split(",")[0].replace('":','').replace('"','').replace(' ','')
            data = data.replace('T', ' ')    
        #
        #Pick body's news
        try:
            body_news=[x.text for x in soup.find("div","n--noticia__content content").find_all('p') if len(x.text)>2]   
            body_new=""
            for x in body_news:
                if x.replace(" ","")[-1]==",":
                    body_new=body_new+x
                else:
                    body_new=body_new+x+' \n '
        except:
            try:
                body_news = [x.text for x in soup.find("div", class_ = "pw-container").find_all("p") if len(x.text)>2]
                body_new = ''
                for x in body_news:
                    if x.replace(" ","")[-1]==",":
                        body_new=body_new+x
                    else:
                        body_new=body_new+x+' \n '

                body_new = body_new.replace('Leia mais','')
                #body_new = unicodedata.normalize('NFD', body_new).encode('ascii', 'ignore').decode("utf-8")
            
            except:
                body_news = [x.text for x in soup.find("div", class_ = "styles__Container-sc-1ehbu6v-0 cNWinE content").find_all("p") if len(x.text)>2]
                body_new = ''
                for x in body_news:
                    if x.replace(" ","")[-1]==",":
                        body_new=body_new+x
                    else:
                        body_new=body_new+x+' \n '

                body_new = body_new.replace('Leia mais','').replace('Continua após a publicidade','').replace('Leia também','')
                #body_new = unicodedata.normalize('NFD', body_new).encode('ascii', 'ignore').decode("utf-8")


        # except Exception:
        #     logger.error(f"Não foi possível recuperar a notícia do link: {url} | O erro encontrado foi: ")
        #     continue           
        #
        # Pick category news
        #   
        try:
            category_news = soup.find("meta", attrs={'property': 'og:title'})
            category_news = str(category_news).split(" - ")[1].split(" - ")[0].lower().replace('"','')
            category_news = unicodedata.normalize('NFD', category_news).encode('ascii', 'ignore')\
                    .decode("utf-8")
        except:
            category_news = url_news.replace("www.","http://").split("//")[1].split(".")[0].replace('"','')

        #
        #
        # Pick image from news
        #
        ass = soup.find("meta", property="og:image")
        image_new = str(ass).split("content=")[1].split(" ")[0].replace('"','')
        #
        #
        #
        #
        estadao_dict["title"].append(title)
        estadao_dict["data"].append(data)
        estadao_dict["body_news"].append(body_new)
        estadao_dict["link"].append(url_news)
        estadao_dict["category"].append(category_news)
        estadao_dict["image"].append(image_new)#adicionar isto para o scrapper
        

        print(estadao_dict)

        self.__send_queue(title, 'domain', 'source', body_new, data, category_news, image_new, url_news)
    
        #"transform to dataframe"

        ##scrapper title | body | news | date:time | category -- 

        #print(voxradar_news_scrapping_estadao_queue_dto.url)

        return ReturnService(True, 'Sucess')

    def __parse_body(self, body:str) -> VoxradarNewsScrappingEstadaoQueueDTO:
        body = json.loads(body)
        return VoxradarNewsScrappingEstadaoQueueDTO(body.get('url'))
    
    def __send_queue(self, title: str, domain: str, source: str, content: str, date: str, category: str, image: str, url: str):
        message_queue:VoxradarNewsSaveDataQueueDTO = VoxradarNewsSaveDataQueueDTO(title, domain, source, content, date, category, image, url)
        
        #self.log(None, 'Send to queue {} | {}'.format(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_ESTADAO'], message_queue.to_json()), Log.INFO)

        self.sqs.send_message_queue(Envs.AWS['SQS']['QUEUE']['VOXRADAR_NEWS_SAVE_DATA'], message_queue.__str__())


