import json
import datetime
from flask import request
import datetime
from src.integration.sqs.sqs import Sqs
from src.types.voxradar_news_save_data_queue_dto import VoxradarNewsSaveDataQueueDTO
from src.types.voxradar_news_scrapping_uol_economia_queue_dto import VoxradarNewsScrappingUolEconomiaQueueDTO
from src.utils.utils import Utils
from ..config.envs import Envs
from .base.base_service import BaseService
from ..types.return_service import ReturnService
from bs4 import BeautifulSoup
import unicodedata
import requests


class ScrappingNewsUolEconomiaService(BaseService):

    sqs: Sqs

    def __init__(self):
        super().__init__()
        # self.log_repository = ViewEstadaoLogRepository()
        # self.s3 = S3()
        self.sqs = Sqs()

    def exec(self, body:str) -> ReturnService:
        self.logger.info(f'\n----- Scrapping News Uol Economia | Init - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")} -----\n')
        uol_dict = {'title': [], 'domain':[],'source':[],'date': [], 'body_news': [], 'link': [],'category': [],'image': []}
        voxradar_news_scrapping_uol_economia_queue_dto:VoxradarNewsScrappingUolEconomiaQueueDTO = self.__parse_body(body)
        url_news = voxradar_news_scrapping_uol_economia_queue_dto.url
        page = requests.get(url_news).text
        soup = BeautifulSoup(page, 'html.parser')   

        #title
        #
        title = soup.find("meta", attrs={'property': 'og:title'})
        title = str(title).split("content=")[1].split("property=")[0].replace('"','')
        if (title==""):
            self.logger.error(f"It is cannot possible to retrieve date from Valor")
            title = " "
            pass                 
        #
        #Stardandizing Date
        date = soup.find("script", type="application/ld+json")
        date = str(date).split('datePublished":')[1].split(",")[0].replace(':"','').replace('"','').replace(' ','')
        date = date.replace('T', ' ')   
        #
        #Pick body's news

        body_news = [x.text for x in soup.find("div", class_ = "text").find_all("p") if len(x.text)>90]
        body_new = ''
        for x in body_news:
            if x.replace(" ","")[-1]==",":
                body_new=body_new+x
            else:
                body_new=body_new+x+' \n '##

        body_new = body_new.replace('Leia mais','').replace('Continua após a publicidade','').replace('Leia também','').replace('— Foto: Getty Images', '')

        # Pick category news
        #   
        category_news = soup.find("script", id="js-collection")
        category_news = str(category_news).split('"channel" :')[1].split(",")[0].replace(':"','').replace('"','')

        category_news = Utils.translate_portuguese_english(category_news)

        #
        #
        #
        # Pick image from news
        #
        ass = soup.find("meta", property="og:image")
        image_new = str(ass).split("content=")[1].split(" ")[0].replace('"','')
        #
        #
        domain = url_news.split("://")[1].split("/")[0]
        source = url_news.split("://")[1].split(".")[1]
        #
        #
        uol_dict["title"].append(title)
        uol_dict["domain"].append(domain)
        uol_dict["source"].append(source)
        uol_dict["date"].append(date)
        uol_dict["body_news"].append(body_new)
        uol_dict["link"].append(url_news)
        uol_dict["category"].append(category_news)
        uol_dict["image"].append(image_new)
        

        print(uol_dict)

        self.__send_queue(title, domain, source, body_new, date, category_news, image_new, url_news)

        return ReturnService(True, 'Sucess')

    def __parse_body(self, body:str) -> VoxradarNewsScrappingUolEconomiaQueueDTO:
        body = json.loads(body)
        return VoxradarNewsScrappingUolEconomiaQueueDTO(body.get('url'))
    
    def __send_queue(self, title: str, domain: str, source: str, content: str, date: str, category: str, image: str, url: str):
        message_queue:VoxradarNewsSaveDataQueueDTO = VoxradarNewsSaveDataQueueDTO(title, domain, source, content, date, category, image, url)
        
        #self.log(None, 'Send to queue {} | {}'.format(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_FOLHA'], message_queue.to_json()), Log.INFO)

        self.sqs.send_message_queue(Envs.AWS['SQS']['QUEUE']['VOXRADAR_NEWS_SAVE_DATA'], message_queue.__str__())



