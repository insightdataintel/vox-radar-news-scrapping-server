import json
import datetime
from flask import request
import datetime
from src.integration.sqs.sqs import Sqs
from src.types.voxradar_news_save_data_queue_dto import VoxradarNewsSaveDataQueueDTO
from src.types.voxradar_news_scrapping_globo_g1_queue_dto import VoxradarNewsScrappingGloboG1QueueDTO
from src.utils.utils import Utils
from ..config.envs import Envs
from .base.base_service import BaseService
from ..types.return_service import ReturnService
from bs4 import BeautifulSoup
import unicodedata
import requests


class ScrappingNewsGloboG1Service(BaseService):

    sqs: Sqs

    def __init__(self):
        super().__init__()
        # self.log_repository = ViewEstadaoLogRepository()
        # self.s3 = S3()
        self.sqs = Sqs()

    def exec(self, body:str) -> ReturnService:
        self.logger.info(f'\n----- Scrapping News Globo G1 Service | Init - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")} -----\n')
        globo_dict = {'title': [], 'domain':[],'source':[],'date': [], 'body_news': [], 'link': [],'category': [],'image': []}
        voxradar_news_scrapping_globo_g1_queue_dto:VoxradarNewsScrappingGloboG1QueueDTO = self.__parse_body(body)
        url_news = voxradar_news_scrapping_globo_g1_queue_dto.url
        page = requests.get(url_news).text
        soup = BeautifulSoup(page, 'html.parser')   
    #
    #title
    #
        title = soup.find("meta", attrs={'property': 'og:title'})
        title = str(title).split("content=")[1].split("property=")[0].replace('"','')         
    #
    #Stardandizing Date
    #
        date = soup.find("time")
        date = str(date).split('datetime=')[1].split("Z")[0].replace(':"','').replace('"','')
        date = date.replace('T', ' ')   
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
        delta = datetime.timedelta(hours=3)
        date = date - delta
        date = "%s:%.3f-3:00"%(str(date.strftime('%Y-%m-%d %H:%M')),float("%.3f" % (date.second + date.microsecond / 1e6)))  
        #
    #
    #Pick body's news
    #
    #
        body_news = [x.text for x in soup.find("div", class_ = "mc-article-body").find_all("p") if len(x.text)>90]
        body_new = ''
        for x in body_news:
            if x.replace(" ","")[-1]==",":
                body_new=body_new+x
            else:
                body_new=body_new+x+' \n '##

        body_new = body_new.replace('Leia mais','').replace('Continua após a publicidade','').replace('Leia também','').replace('— Foto: Getty Images', '')



    # Pick category news
    #   
        category_news = soup.find_all("script")
        category_news = str(category_news).split('editoria_path":')[1].split(",")[0].replace(':"','').replace('"','').replace(' ','').replace("\\", "")

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
        globo_dict["title"].append(title)
        globo_dict["domain"].append(domain)
        globo_dict["source"].append(source)
        globo_dict["date"].append(date)
        globo_dict["body_news"].append(body_new)
        globo_dict["link"].append(url_news)
        globo_dict["category"].append(category_news)
        globo_dict["image"].append(image_new)
        

        print(globo_dict)

        self.__send_queue(title, domain, source, body_new, date, category_news, image_new, url_news)

        return ReturnService(True, 'Sucess')

    def __parse_body(self, body:str) -> VoxradarNewsScrappingGloboG1QueueDTO:
        body = json.loads(body)
        return VoxradarNewsScrappingGloboG1QueueDTO(body.get('url'))
    
    def __send_queue(self, title: str, domain: str, source: str, content: str, date: str, category: str, image: str, url: str):
        message_queue:VoxradarNewsSaveDataQueueDTO = VoxradarNewsSaveDataQueueDTO(title, domain, source, content, date, category, image, url)
        
        #self.log(None, 'Send to queue {} | {}'.format(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_FOLHA'], message_queue.to_json()), Log.INFO)

        self.sqs.send_message_queue(Envs.AWS['SQS']['QUEUE']['VOXRADAR_NEWS_SAVE_DATA'], message_queue.__str__())



