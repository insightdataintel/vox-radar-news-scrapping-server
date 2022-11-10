import json
import datetime
from flask import request
import datetime
from src.integration.sqs.sqs import Sqs
from src.types.voxradar_news_save_data_queue_dto import VoxradarNewsSaveDataQueueDTO
from src.types.voxradar_news_scrapping_opopular_queue_dto import VoxradarNewsScrappingOPopularQueueDTO
from src.utils.utils import Utils
from ..config.envs import Envs
from .base.base_service import BaseService
from ..types.return_service import ReturnService
from bs4 import BeautifulSoup
import unicodedata
import requests


class ScrappingNewsOPopularService(BaseService):

    sqs: Sqs

    def __init__(self):
        super().__init__()
        # self.log_repository = ViewEstadaoLogRepository()
        # self.s3 = S3()
        self.sqs = Sqs()

    def exec(self, body:str) -> ReturnService:
        self.logger.info(f'\n----- Scrapping News O Popular Service | Init - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")} -----\n')
        opopular_dict = {'title': [], 'domain':[],'source':[],'date': [], 'body_news': [], 'link': [],'category': [],'image': []}
        voxradar_news_scrapping_opopular_queue_dto:VoxradarNewsScrappingOPopularQueueDTO = self.__parse_body(body)
        url_news = voxradar_news_scrapping_opopular_queue_dto.url
        headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:2.0b10) Gecko/20100101 Firefox/4.0b10"}
        page = requests.get(url_news,headers=headers).text
        soup = BeautifulSoup(page, 'html.parser')     
    #
    #title
    #
        try:
            title = soup.find("title")
            title = str(title).split("<title>")[1].split("</title")[0].replace('- @aredacao','').replace('"','')
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar o título da notícia do Folha de São Paulo: {url_news} | {e}")     
            title = ""
    #
    #Stardandizing Date
    #
        try:
            date = soup.find("time",class_='inner-date')
            date = str(date).split('datetime=')[1].split('itemprop')[0].replace('"','')
            date = date.replace('T',' ').split('+')[0]
 
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar a data da notícia do Folha de São Paulo: {url_news} | {e}")
            date = ""    
    #
    #Pick body's news
    #
    #
        try: 
            body_new = soup.find('section', itemprop='articleBody').text.strip()     
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar o corpo da notícia do Folha de São Paulo: {url_news} | {e}")
            return ReturnService(False, 'Did not collect the body of the News')

    # Pick category news
    # 
        category_news = soup.find('div',class_='retracts-tag')
        category_news = str(category_news).split('title="')[1].split('viewbox=')[0].replace('"','').strip()
    


        #
        #
        #
    # Pick image from news
        #
        try:
            ass = soup.find("meta", property="og:image")
            image_new = str(ass).split("content=")[1].split(" ")[0].replace('"','')
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar imagens da notícia do Folha de São Paulo: {url_news} | {e}")     
            image_new = ""
        #
        domain = url_news.split(".br/")[0]+'.br'
        source = url_news.split("https://")[1].split(".com")[0]    
       
        #
        opopular_dict["title"].append(title)
        opopular_dict["domain"].append(domain)
        opopular_dict["source"].append(source)
        opopular_dict["date"].append(date)
        opopular_dict["body_news"].append(body_new)
        opopular_dict["link"].append(url_news)
        opopular_dict["category"].append(category_news)
        opopular_dict["image"].append(image_new)
        

        print(opopular_dict)

        self.__send_queue(title, domain, source, body_new, date, category_news, image_new, url_news)

        return ReturnService(True, 'Sucess')

    def __parse_body(self, body:str) -> VoxradarNewsScrappingOPopularQueueDTO:
        body = json.loads(body)
        return VoxradarNewsScrappingOPopularQueueDTO(body.get('url'))
    
    def __send_queue(self, title: str, domain: str, source: str, content: str, date: str, category: str, image: str, url: str):
        message_queue:VoxradarNewsSaveDataQueueDTO = VoxradarNewsSaveDataQueueDTO(title, domain, source, content, date, category, image, url)
        
        #self.log(None, 'Send to queue {} | {}'.format(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_FOLHA'], message_queue.to_json()), Log.INFO)

        self.sqs.send_message_queue(Envs.AWS['SQS']['QUEUE']['VOXRADAR_NEWS_SAVE_DATA'], message_queue.__str__())



