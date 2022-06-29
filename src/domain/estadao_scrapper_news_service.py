import json
import datetime
import pandas as pd
import datetime
from src.config.enum import Log

from src.integration.s3.s3 import S3
from src.integration.sqs.sqs import Sqs
from src.repository.adapters.postgres.view_estadao_log_repository import ViewEstadaoLogRepository
from src.types.sigarp_save_data_estadao_queue_dto import SigarpSaveDataEstadaoQueueDTO
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

logging.basicConfig(filename='arquivos/logger.log', level=logging.INFO, filemode='a', 
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()

def requests_wrapper_text(url):

    try:
        page = requests.get(url).text
        return page
    # Set of try of identify erros case doesn't get a request
    # Realizando um conjunto de tentativas de identificar errors caso não consiga fazer o Requests
    except requests.exceptions.Timeout:
        # Tentando mais uma vez entrar no site caso tenha dado Timeout
        # Trying one more time to get in the site case doesn't has timeout
        try:
            page = requests.get(url).text
            return page
        except requests.exceptions.Timeout:
            logger.error(f"Time out error: {url}") 
            return False
    except requests.exceptions.TooManyRedirects:
        logger.error(f"Too manyredirects: {url}")
        return False
    except requests.exceptions.ConnectionError as errc:
        logger.error(f"Connection Error: {errc} | no link: {url}")
        return False                         
    except requests.exceptions.RequestException as e:
        logger.error(f"Request Exception, link: {url} | {e}")
        return False   

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



class EstadaoScrapperNewsService(BaseService):
    # s3: S3
    sqs: Sqs
    selenium:Selenium = None
    # state_dict = {
    #     'AC': 1, 'AL': 2, 'AM': 3, 'AP': 4,
    #     'BA': 5, 'CE': 6, 'DF': 7, 'ES': 8,
    #     'GO': 9, 'MA': 10, 'MG': 11, 'MS': 12,
    #     'MT': 13, 'PA': 14, 'PB': 15, 'PE': 16,
    #     'PI': 17, 'PR': 18, 'RJ': 19, 'RN': 20,
    #     'RO': 21, 'RR': 22, 'RS': 23, 'SC': 24,
    #     'SE': 25, 'SP': 26, 'TO': 27
    # }

    #Configuração do Logger: Nível Informação, dando append nelas com data padronizada, o nome da função que se refere a informação
    #E também a mensagem de erro.



    def __init__(self):
        super().__init__()
        # self.log_repository = ViewEstadaoLogRepository()
        # self.selenium = Selenium('estadao')
        # self.s3 = S3()
        # self.sqs = Sqs()



    def exec(self,body:str) -> ReturnService:
        print(f'\n----- Scrapper | Init - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")} -----\n')
        estadao_dict = {'title': [], 'data': [], 'body_news': [], 'link': [],'category': [],'image': []}
        
        voxradar_news_scrapping_estadao_queue_dto:VoxradarNewsScrappingEstadaoQueueDTO = self.__parse_body(body)

        url_news = voxradar_news_scrapping_estadao_queue_dto.url

        # for url in url_news:    
        page = requests_wrapper_text(url_news)
        # if page is False:
        #     continue        
        soup = BeautifulSoup(page, 'html.parser')         
        #Pegando o título
        try:
            title = soup.find_all("h1")[0].text.replace('"', '').replace("'", "")
        except Exception as e:
            logger.error(f"Não foi possível recuperar alguma informação do site Estadão, o erro encontrado foi | {e}")
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

    

        #"transform to dataframe"

        ##scrapper title | body | news | date:time | category -- 

        #print(voxradar_news_scrapping_estadao_queue_dto.url)

        return ReturnService(True, 'Sucess')

    def __parse_body(self, body:str) -> VoxradarNewsScrappingEstadaoQueueDTO:
        body = json.loads(body)
        return VoxradarNewsScrappingEstadaoQueueDTO(body.get('url'))


    def __save_json(self, df, state, city, year, file):
        total = len(df)

        print(f'----- Count rows {total} -----')

        file_name = f'estadao/estadao_{state}_{city}_{year}_{datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%z")}'.lower()
        self.s3.upload_file(file, Constants.S3['BUCKET']['SIGARP'], f'{file_name}_full.xlsx')

        result = df.to_json(orient='records')
        dataParsed = json.loads(result)
        count = 1
        list_chunk = 1
        files_list = []
        list_line = []
        chunk_num = 1

        for line in dataParsed:
            list_line.append(line)

            if(list_chunk == Constants.CHUNK[0]['JSON'] or count == total):
                print(f'Saving data {list_chunk}')
                chunk_file_name = f'{file_name}_{chunk_num}.json'
                self.s3.upload_file(json.dumps(list_line, ensure_ascii=False), Constants.S3['BUCKET']['SIGARP'], chunk_file_name)
                files_list.append(chunk_file_name)
                list_line = []
                list_chunk = 1
                chunk_num += 1

            count += 1
            list_chunk += 1
        
        return files_list
    
    def __send_queue(self, files_download:list):
        sigarp_save_data_estadao_dto:SigarpSaveDataEstadaoQueueDTO = SigarpSaveDataEstadaoQueueDTO(files_download)
        
        self.log(None, 'Send to queue {} | {}'.format(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_ESTADAO'], sigarp_save_data_estadao_dto.to_json()), Log.INFO)

        self.sqs.send_message_queue(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_ESTADAO'], sigarp_save_data_estadao_dto.to_json())


