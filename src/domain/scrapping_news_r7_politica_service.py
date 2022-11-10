import json
import datetime
from flask import request
import datetime
from src.integration.sqs.sqs import Sqs
from src.types.voxradar_news_save_data_queue_dto import VoxradarNewsSaveDataQueueDTO
from src.types.voxradar_news_scrapping_r7_politica_queue_dto import VoxradarNewsScrappingR7PoliticaQueueDTO
from src.utils.utils import Utils
from ..config.envs import Envs
from .base.base_service import BaseService
from ..types.return_service import ReturnService
from bs4 import BeautifulSoup
import unicodedata
import requests


class ScrappingNewsR7PoliticaService(BaseService):

    sqs: Sqs

    def __init__(self):
        super().__init__()
        # self.log_repository = ViewEstadaoLogRepository()
        # self.s3 = S3()
        self.sqs = Sqs()

    def exec(self, body:str) -> ReturnService:
        self.logger.info(f'\n----- Scrapping News R7 Política Service | Init - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")} -----\n')
        r7_dict = {'title': [], 'domain':[],'source':[],'date': [], 'body_news': [], 'link': [],'category': [],'image': []}
        voxradar_news_scrapping_r7_politica_queue_dto:VoxradarNewsScrappingR7PoliticaQueueDTO = self.__parse_body(body)
        url_news = voxradar_news_scrapping_r7_politica_queue_dto.url
        page = requests.get(url_news).text
        soup = BeautifulSoup(page, 'html.parser')   
    #
    #title
    #
        try:
            title = soup.find("meta", attrs={'property': 'og:title'})
            title = str(title).split("content=")[1].split("property=")[0].replace('"','')      
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar o título da notícia do Folha de São Paulo: {url_news} | {e}")     
            title = ""
    #
    #Stardandizing Date
    #
        try:
            date = soup.find("meta", attrs={'property': 'article:published_time'})
            date = str(date).split('meta content=')[1].split("property=")[0].replace(':"','').replace('"','').split("+")[0]
            date = date.replace('T', ' ') 
            date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            date = "%s:%.3f-3:00"%(str(date.strftime('%Y-%m-%d %H:%M')),float("%.3f" % (date.second + date.microsecond / 1e6)))  
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar a data da notícia do Folha de São Paulo: {url_news} | {e}")
            date = ""    
    #
    #Pick body's news
    #
    #
        try:
            try:
                body_news = [x.text for x in soup.find("article", class_ = "toolkit-media-content").find_all("p") if len(x.text)>20]
                body_new = ''
                for x in body_news:
                    if x.replace(" ","")[-1]==",":
                        body_new=body_new+x
                    else:
                        body_new=body_new+x+' \n '##

                body_new = body_new.replace('Leia mais','').replace('Continua após a publicidade','').replace('Leia também','').replace('— Foto: Getty Images', '')

            except:
                body_news = [x.text for x in soup.find("div", class_ = "entry-content").find_all("p") if len(x.text)>20]
                body_new = ''
                for x in body_news:
                    if x.replace(" ","")[-1]==",":
                        body_new=body_new+x
                    else:
                        body_new=body_new+x+' \n '##

                body_new = body_new.replace('Leia mais','').replace('Continua após a publicidade','').replace('Leia também','').replace('— Foto: Getty Images', '')    
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar o corpo da notícia do Folha de São Paulo: {url_news} | {e}")
            return ReturnService(False, 'Did not collect the body of the News')

    # Pick category news
    # 
        try:
            category_news = soup.find("meta", attrs={'property': 'article:section'})
            category_news = str(category_news).split("meta content=")[1].split('property=')[0].replace('"','').lower()
        #
        except:
            category_news = soup.find("div", class_="content container")
            category_news = str(category_news).split("category-")[1].split('tag-')[0].replace('"','').lower()

        category_news = Utils.translate_portuguese_english(category_news)

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
        domain = url_news.split("://")[1].split("/")[0]
        source = url_news.split("://")[1].split(".")[1]
        #
        #
        r7_dict["title"].append(title)
        r7_dict["domain"].append(domain)
        r7_dict["source"].append(source)
        r7_dict["date"].append(date)
        r7_dict["body_news"].append(body_new)
        r7_dict["link"].append(url_news)
        r7_dict["category"].append(category_news)
        r7_dict["image"].append(image_new)
        

        print(r7_dict)

        self.__send_queue(title, domain, source, body_new, date, category_news, image_new, url_news)

        return ReturnService(True, 'Sucess')

    def __parse_body(self, body:str) -> VoxradarNewsScrappingR7PoliticaQueueDTO:
        body = json.loads(body)
        return VoxradarNewsScrappingR7PoliticaQueueDTO(body.get('url'))
    
    def __send_queue(self, title: str, domain: str, source: str, content: str, date: str, category: str, image: str, url: str):
        message_queue:VoxradarNewsSaveDataQueueDTO = VoxradarNewsSaveDataQueueDTO(title, domain, source, content, date, category, image, url)
        
        #self.log(None, 'Send to queue {} | {}'.format(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_FOLHA'], message_queue.to_json()), Log.INFO)

        self.sqs.send_message_queue(Envs.AWS['SQS']['QUEUE']['VOXRADAR_NEWS_SAVE_DATA'], message_queue.__str__())



