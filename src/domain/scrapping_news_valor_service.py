from fnmatch import translate
import json
import datetime
from flask import request
import datetime
from src.integration.sqs.sqs import Sqs
from src.types.voxradar_news_save_data_queue_dto import VoxradarNewsSaveDataQueueDTO
from src.types.voxradar_news_scrapping_valor_queue_dto import VoxradarNewsScrappingValorQueueDTO
from src.utils.utils import Utils
from ..config.envs import Envs
from .base.base_service import BaseService
from ..types.return_service import ReturnService
from bs4 import BeautifulSoup
import unicodedata
import requests


class ScrappingNewsValorService(BaseService):
    # s3: S3
    sqs: Sqs

    def __init__(self):
        super().__init__()
        # self.log_repository = ViewEstadaoLogRepository()
        # self.s3 = S3()
        self.sqs = Sqs()

    def exec(self, body:str) -> ReturnService:
        self.logger.info(f'\n----- Scrapping News Valor Service | Init - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")} -----\n')
        valor_dict = {'title': [], 'domain':[],'source':[],'data': [], 'body_news': [], 'link': [],'category': [],'image': []}
        voxradar_news_scrapping_valor_queue_dto:VoxradarNewsScrappingValorQueueDTO = self.__parse_body(body)
        url_news = voxradar_news_scrapping_valor_queue_dto.url
        page = requests.get(url_news).text
        soup = BeautifulSoup(page, 'html.parser')   

        #title
        #
        title = soup.find("meta", attrs={'property': 'og:title'})
        title = str(title).split("content=")[1].split("property=")[0].replace('"','')
        if (title==""):
            self.logger.error(f"It is cannot possible to retrieve data from Valor")
            title = " "
            pass                 
        #
        #Stardandizing Date
        try:
            data = soup.find("meta", attrs={'name': 'date'})
            data = str(data).split("content=")[1].split(" ")[0].replace('"','')
            data = data.replace("T", " ")
        except:
            data = soup.find_all("script")
            data = str(data).split("ISSUED:")[1].split(",")[0].replace(':"','').replace('"','').replace(' ','')
            data = data.replace('T', ' ')   
            data = datetime.datetime.strptime(data, "%Y-%m-%d %H:%M:%S.%fZ")
            delta = datetime.timedelta(hours=3)
            data = data - delta
            data = "%s:%.3f-3:00"%(str(data.strftime('%Y-%m-%d %H:%M')),float("%.3f" % (data.second + data.microsecond / 1e6)))  
        #
        #Pick body's news
            
        
        body_news = [x.text for x in soup.find("div", class_ = "mc-article-body").find_all("p") if len(x.text)>2]
        body_new = ''
        words_to_extract = "Foto:"
        for x in body_news:
            if words_to_extract in x:
                body_new = body_new+x.replace(words_to_extract,"")+'\n'
            
            elif x.replace(" ","")[-1]==",":
                body_new=body_new+x
            else:
                body_new=body_new+x+' \n '##


        body_new = body_new.replace('Leia mais','').replace('Continua após a publicidade','').replace('Leia também','').replace('— Foto: Getty Images', '')
  
        # Pick category news
        #   
        try:
            category_news = soup.find("meta", attrs={'property': 'og:title'})
            category_news = str(category_news).split(" - ")[1].split(" - ")[0].lower().replace('"','')
            category_news = unicodedata.normalize('NFD', category_news).encode('ascii', 'ignore')\
                    .decode("utf-8")
        except:
            category_news = soup.find_all("script")
            category_news = str(category_news).split('editoria_path":')[1].split(",")[0].replace(':"','').replace('"','').replace(' ','').replace("\\", "")
            category_news = unicodedata.normalize('NFD', category_news).encode('ascii', 'ignore')\
                                                                                    .decode("utf-8")
        category_news = Utils.translate_portuguese_english(category_news)


        # Pick image from news
        #
        ass = soup.find("meta", property="og:image")
        image_new = str(ass).split("content=")[1].split(" ")[0].replace('"','')
        #
        #
        # Pick domain
        #
        domain = url_news.split("://")[1].split("/")[0]
        source = url_news.split("://")[1].split(".")[1]
        #
        #
        valor_dict["title"].append(title)
        valor_dict["domain"].append(domain)
        valor_dict["source"].append(source)
        valor_dict["data"].append(data)
        valor_dict["body_news"].append(body_new)
        valor_dict["link"].append(url_news)
        valor_dict["category"].append(category_news)
        valor_dict["image"].append(image_new)


   

        return ReturnService(True, 'Sucess')

    def __parse_body(self, body:str) -> VoxradarNewsScrappingValorQueueDTO:
        body = json.loads(body)
        return VoxradarNewsScrappingValorQueueDTO(body.get('url'))
    
    def __send_queue(self, title: str, domain: str, source: str, content: str, date: str, category: str, image: str, url: str):
        message_queue:VoxradarNewsSaveDataQueueDTO = VoxradarNewsSaveDataQueueDTO(title, domain, source, content, date, category, image, url)
        
        #self.log(None, 'Send to queue {} | {}'.format(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_VALOR'], message_queue.to_json()), Log.INFO)

        self.sqs.send_message_queue(Envs.AWS['SQS']['QUEUE']['VOXRADAR_NEWS_SAVE_DATA'], message_queue.__str__())


