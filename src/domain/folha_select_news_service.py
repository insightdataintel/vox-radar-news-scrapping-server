import json
import datetime
import pandas as pd
import datetime
from src.config.enum import Log

from src.integration.s3.s3 import S3
from src.integration.sqs.sqs import Sqs
from src.repository.adapters.postgres.view_folha_log_repository import ViewFolhaLogRepository
from src.types.sigarp_save_data_folha_queue_dto import SigarpSaveDataFolhaQueueDTO

from ..config.envs import Envs
from ..config.constants import Constants
from .base.base_service import BaseService
from ..types.sigarp_capture_data_folha_scrapping_queue_dto import SigarpCaptureDataFolhaScrappingQueueDTO
from ..types.return_service import ReturnService
import xlrd

from ..integration.selenium.selenium import Selenium

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
from bs4 import BeautifulSoup
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



class FolhaSelectNewsService(BaseService):
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



    def exec(self) -> ReturnService:
        print(f'\n----- Scrapper | Init - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")} -----\n')
        
        # self.log(None, f"Iniciando scrapping estado de {sigarp_capture_data_estadao_scrapping_queue_dto.state}, cidade de {sigarp_capture_data_estadao_scrapping_queue_dto.city}, ano {sigarp_capture_data_estadao_scrapping_queue_dto.year}", Log.INFO)

            
        url = "https://valor.globo.com/"
        
        page = requests_wrapper_text(url)

            
        soup = BeautifulSoup(page, 'html.parser')
        links_filtered = []    
        #//Taking links from url
        try:
            domain = url.split(".")[1]+".com"
            links = soup.find_all('a', class_=["c-headline__url","c-main-headline__url"])
            for item in links:
                aux = str(item).split("href=")[1].split(" ")[0].split('>')[0].replace(">","").replace('"','')
                links_filtered.append(aux)

        except Exception as e:
            logger.error(f"Não foi possível encontrar os Links na página inicial do site Valor | {e}")
        
        print(links_filtered)


        return ReturnService(True, 'Sucess')

        
    def __save_json(self, df, state, city, year, file):
        total = len(df)

        print(f'----- Count rows {total} -----')

        file_name = f'folha/folha_{state}_{city}_{year}_{datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%z")}'.lower()
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
        sigarp_save_data_folha_dto:SigarpSaveDataFolhaQueueDTO = SigarpSaveDataFolhaQueueDTO(files_download)
        
        self.log(None, 'Send to queue {} | {}'.format(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_FOLHA'], sigarp_save_data_folha_dto.to_json()), Log.INFO)

        self.sqs.send_message_queue(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_FOLHA'], sigarp_save_data_folha_dto.to_json())


