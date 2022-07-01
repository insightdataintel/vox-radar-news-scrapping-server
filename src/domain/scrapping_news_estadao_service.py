import json
import datetime
from flask import request
import datetime
from src.integration.sqs.sqs import Sqs
from src.types.voxradar_news_save_data_queue_dto import VoxradarNewsSaveDataQueueDTO
from src.types.voxradar_news_scrapping_estadao_queue_dto import VoxradarNewsScrappingEstadaoQueueDTO
from src.utils.utils import Utils
from ..config.envs import Envs
from .base.base_service import BaseService
from ..types.return_service import ReturnService
from bs4 import BeautifulSoup
import unicodedata
import requests


class ScrappingNewsEstadaoService(BaseService):
    # s3: S3
    sqs: Sqs

    def __init__(self):
        super().__init__()
        # self.log_repository = ViewEstadaoLogRepository()
        # self.s3 = S3()
        self.sqs = Sqs()

    def exec(self, body:str) -> ReturnService:
        self.logger.info(f'\n----- Scrapping News Estadao Service | Init - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")} -----\n')
        estadao_dict = {'title': [], 'domain':[],'source':[],'data': [], 'body_news': [], 'link': [],'category': [],'image': []}
        voxradar_news_scrapping_estadao_queue_dto:VoxradarNewsScrappingEstadaoQueueDTO = self.__parse_body(body)
        url_news = voxradar_news_scrapping_estadao_queue_dto.url
        page = requests.get(url_news).text
        soup = BeautifulSoup(page, 'html.parser')         

        #title
        #
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

            
            except:
                body_news = [x.text for x in soup.find("div", class_ = "styles__Container-sc-1ehbu6v-0 cNWinE content").find_all("p") if len(x.text)>2]
                body_new = ''
                for x in body_news:
                    if x.replace(" ","")[-1]==",":
                        body_new=body_new+x
                    else:
                        body_new=body_new+x+' \n '

                body_new = body_new.replace('Leia mais','').replace('Continua após a publicidade','').replace('Leia também','')

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
        category_news = Utils.translate_portuguese_english(category_news)

        #
        # Pick image from news
        #
        ass = soup.find("meta", property="og:image")
        image_new = str(ass).split("content=")[1].split(" ")[0].replace('"','')
        #
        #
        domain = url_news.split("://")[1].split(".")[0] 
        source = url_news.split("://")[1].split("/")[0]
        #
        #
        estadao_dict["title"].append(title)
        estadao_dict["domain"].append(domain)
        estadao_dict["source"].append(source)
        estadao_dict["data"].append(data)
        estadao_dict["body_news"].append(body_new)
        estadao_dict["link"].append(url_news)
        estadao_dict["category"].append(category_news)
        estadao_dict["image"].append(image_new)
        

        print(estadao_dict)

        self.__send_queue(title, 'domain', 'source', body_new, data, category_news, image_new, url_news)
    

        return ReturnService(True, 'Sucess')

    def __parse_body(self, body:str) -> VoxradarNewsScrappingEstadaoQueueDTO:
        body = json.loads(body)
        return VoxradarNewsScrappingEstadaoQueueDTO(body.get('url'))
    
    def __send_queue(self, title: str, domain: str, source: str, content: str, date: str, category: str, image: str, url: str):
        message_queue:VoxradarNewsSaveDataQueueDTO = VoxradarNewsSaveDataQueueDTO(title, domain, source, content, date, category, image, url)
        
        #self.log(None, 'Send to queue {} | {}'.format(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_ESTADAO'], message_queue.to_json()), Log.INFO)

        self.sqs.send_message_queue(Envs.AWS['SQS']['QUEUE']['VOXRADAR_NEWS_SAVE_DATA'], message_queue.__str__())


