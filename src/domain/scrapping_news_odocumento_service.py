import json
import datetime
from flask import request
import datetime
from src.integration.sqs.sqs import Sqs
from src.types.voxradar_news_save_data_queue_dto import VoxradarNewsSaveDataQueueDTO
from src.types.voxradar_news_scrapping_odocumento_queue_dto import VoxradarNewsScrappingODocumentoQueueDTO
from src.utils.utils import Utils
from ..config.envs import Envs
from .base.base_service import BaseService
from ..types.return_service import ReturnService
from bs4 import BeautifulSoup
import unicodedata
import requests


class ScrappingNewsODocumentoService(BaseService):

    sqs: Sqs

    def __init__(self):
        super().__init__()
        # self.log_repository = ViewEstadaoLogRepository()
        # self.s3 = S3()
        self.sqs = Sqs()

    def exec(self, body:str) -> ReturnService:
        self.logger.info(f'\n----- Scrapping News O Documento Service | Init - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")} -----\n')
        odocumento_dict = {'title': [], 'domain':[],'source':[],'date': [], 'body_news': [], 'link': [],'category': [],'image': []}
        voxradar_news_scrapping_odocumento_queue_dto:VoxradarNewsScrappingODocumentoQueueDTO = self.__parse_body(body)
        url_news = voxradar_news_scrapping_odocumento_queue_dto.url
        page = requests.get(url_news).text
        soup = BeautifulSoup(page, 'html.parser')   
    #
    #title
    #
        try:
            title = soup.find("meta",property="og:title")
            title = str(title).split("content=")[1].split("property=")[0].split('itemprop=')[0].replace('- @aredacao','').replace('"','')
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar o título da notícia do Folha de São Paulo: {url_news} | {e}")     
            title = ""
    #
    #Stardandizing Date
    #
        try:
            date = soup.find("meta",property="article:published_time")
            date = str(date).split('content="')[1].split('property=')[0].replace('T', ' ').replace('Z', '').replace('"','').split('+')[0].strip()
            date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            delta = datetime.timedelta(hours=4)
            date = date - delta
            date = "%s-3:00"%(str(date.strftime('%Y-%m-%d %H:%M:%S'))) 
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar a data da notícia do Folha de São Paulo: {url_news} | {e}")
            date = ""    
    #
    #Pick body's news
    #
    #
        try:
            mode = ['div']
            classk = ['mvp-content-body']
            paragraf = ['p']
            body_new = ''

            for i in range(0,len(mode)):
                for j in range(0,len(classk)):
                    try:
                        yes = soup.find(mode[i],id= classk[j])
                        if(len(yes)>0):
                            break
                    except:
                        None

                        

            for k in range(0,len(paragraf)):
                try:
                    body_news = [x.text for x in soup.find(mode[i], id = classk[j]).find_all(paragraf[k]) if len(x.text)>20]
                    if(len(body_news)>0):
                        break
                except:
                    body_news = [x.text for x in soup.find(mode[i], id = 'textContent').find_all(paragraf[k]) if len(x.text)>20]
                    if(len(body_news)>0):
                        break



            no_text = ['Cartola','Leia outras','podcast','Foto','clique aqui','Assine o Premiere','VÍDEOS:',\
                        'o app do Yahoo Mail','Assine agora a newsletter','via Getty Images','Fonte: ','O seu endereço de e-mail',\
                        'email protected','Comunicação Social da Polícia','email','Portal iG']
            for x in body_news:
                for item in no_text:
                    if item in x:
                        x = ''
                if x=='':
                    pass
                else:
                    body_new = body_new+x+' \n' ##
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar o corpo da notícia do Folha de São Paulo: {url_news} | {e}")
            body_new = ""

    # Pick category news
    # 
        category_news = soup.find('span',class_='mvp-post-cat left')
        category_news = str(category_news).split('">')[1].split('</span>')[0].lower()
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
            image_new = "" #
        # #
        domain = url_news.split(".com")[0]+'.com'
        try:
            source = url_news.split("www.")[1].split(".com")[0]               
        except:
            source = url_news.split("https://")[1].split(".com")[0]       
        #
        #
        odocumento_dict["title"].append(title)
        odocumento_dict["domain"].append(domain)
        odocumento_dict["source"].append(source)
        odocumento_dict["date"].append(date)
        odocumento_dict["body_news"].append(body_new)
        odocumento_dict["link"].append(url_news)
        odocumento_dict["category"].append(category_news)
        odocumento_dict["image"].append(image_new)
        

        print(odocumento_dict)

        self.__send_queue(title, domain, source, body_new, date, category_news, image_new, url_news)

        return ReturnService(True, 'Sucess')

    def __parse_body(self, body:str) -> VoxradarNewsScrappingODocumentoQueueDTO:
        body = json.loads(body)
        return VoxradarNewsScrappingODocumentoQueueDTO(body.get('url'))
    
    def __send_queue(self, title: str, domain: str, source: str, content: str, date: str, category: str, image: str, url: str):
        message_queue:VoxradarNewsSaveDataQueueDTO = VoxradarNewsSaveDataQueueDTO(title, domain, source, content, date, category, image, url)
        
        #self.log(None, 'Send to queue {} | {}'.format(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_FOLHA'], message_queue.to_json()), Log.INFO)

        self.sqs.send_message_queue(Envs.AWS['SQS']['QUEUE']['VOXRADAR_NEWS_SAVE_DATA'], message_queue.__str__())



