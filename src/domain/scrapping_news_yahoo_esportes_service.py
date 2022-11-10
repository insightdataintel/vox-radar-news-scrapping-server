import json
import datetime
from flask import request
import datetime
from src.integration.sqs.sqs import Sqs
from src.types.voxradar_news_save_data_queue_dto import VoxradarNewsSaveDataQueueDTO
from src.types.voxradar_news_scrapping_yahoo_esportes_queue_dto import VoxradarNewsScrappingYahooEsportesQueueDTO
from src.utils.utils import Utils
from ..config.envs import Envs
from .base.base_service import BaseService
from ..types.return_service import ReturnService
from bs4 import BeautifulSoup
import unicodedata
import requests


class ScrappingNewsYahooEsportesService(BaseService):

    sqs: Sqs

    def __init__(self):
        super().__init__()
        # self.log_repository = ViewEstadaoLogRepository()
        # self.s3 = S3()
        self.sqs = Sqs()

    def exec(self, body:str) -> ReturnService:
        self.logger.info(f'\n----- Scrapping News Yahoo Esportes Service | Init - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")} -----\n')
        yahoo_dict = {'title': [], 'domain':[],'source':[],'date': [], 'body_news': [], 'link': [],'category': [],'image': []}
        voxradar_news_scrapping_yahoo_financas_queue_dto:VoxradarNewsScrappingYahooEsportesQueueDTO = self.__parse_body(body)
        url_news = voxradar_news_scrapping_yahoo_financas_queue_dto.url
        page = requests.get(url_news).text
        soup = BeautifulSoup(page, 'html.parser')   
    #
    #title
    #
        try:
            title = soup.find("meta",property="og:title")
            title = str(title).split("content=")[1].split("property=")[0].split('itemprop=')[0].replace('- @aredacao','').replace('"','')
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar o título da notícia do Yahoo Esportes: {url_news} | {e}")     
            title = ""
    #
    #Stardandizing Date
    #
        try:
            date = soup.find_all("script")
            date = str(date).split('"datePublished":')[1].split(',')[0].replace('T', ' ').replace('Z', '').replace('"','').split('+')[0].strip()
            date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
            delta = datetime.timedelta(hours=3)
            date = date - delta
            date = "%s-3:00"%(str(date.strftime('%Y-%m-%d %H:%M:%S')))  
            #
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar a data da notícia do Yahoo Esportes: {url_news} | {e}")
            date = ""    
    #
    #Pick body's news
    #
    #
        try:



            mode = ['div']
            classk = ['caas-body']
            paragraf = ['p']
            body_new = ''

            for i in range(0,len(mode)):
                for j in range(0,len(classk)):
                    try:
                        yes = soup.find(mode[i],class_= classk[j])
                        if(len(yes)>0):
                            break
                    except:
                        None

                        

            for k in range(0,len(paragraf)):
                try:
                    body_news = [x.text for x in soup.find(mode[i], class_ = classk[j]).find_all(paragraf[k]) if len(x.text)>20]
                    if(len(body_news)>0):
                        break
                except:
                    body_news = [x.text for x in soup.find(mode[i], id = 'textContent').find_all(paragraf[k]) if len(x.text)>20]
                    if(len(body_news)>0):
                        break



            no_text = ['Cartola','Leia outras','podcast','Foto','clique aqui','Assine o Premiere','VÍDEOS:','o app do Yahoo Mail','Assine agora a newsletter']
            for x in body_news:
                for item in no_text:
                    if item in x:
                        x = ''
                if x=='':
                    pass
                else:
                    body_new = body_new+x+' \n' ##


        except Exception as e:
            self.logger.error(f"Não foi possível encontrar o corpo da notícia do Yahoo Esportes: {url_news} | {e}")
            return ReturnService(False, 'Did not collect the body of the News')
                

    # Pick category news
    # 

   

        category_news = url_news.replace("www.",'').replace("https://",'')
        category_news = category_news.split('.yahoo')[0]
            

        #
        #
        #
    # Pick image from news
        #
        try:
            ass = soup.find("meta", property="og:image")
            image_new = str(ass).split("content=")[1].split(" ")[0].replace('"','')
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar imagens da notícia do Yahoo Esportes: {url_news} | {e}")     
            image_new = "" #
        # #
        domain = url_news.split(".com")[0]+'.com'
        try:
            source = url_news.split("www.")[1].split(".com")[0]               
        except:
            source = url_news.split("https://")[1].split(".com")[0]       
        #
        #
        yahoo_dict["title"].append(title)
        yahoo_dict["domain"].append(domain)
        yahoo_dict["source"].append(source)
        yahoo_dict["date"].append(date)
        yahoo_dict["body_news"].append(body_new)
        yahoo_dict["link"].append(url_news)
        yahoo_dict["category"].append(category_news)
        yahoo_dict["image"].append(image_new)
        

        print(yahoo_dict)

        self.__send_queue(title, domain, source, body_new, date, category_news, image_new, url_news)

        return ReturnService(True, 'Sucess')

    def __parse_body(self, body:str) -> VoxradarNewsScrappingYahooEsportesQueueDTO:
        body = json.loads(body)
        return VoxradarNewsScrappingYahooEsportesQueueDTO(body.get('url'))
    
    def __send_queue(self, title: str, domain: str, source: str, content: str, date: str, category: str, image: str, url: str):
        message_queue:VoxradarNewsSaveDataQueueDTO = VoxradarNewsSaveDataQueueDTO(title, domain, source, content, date, category, image, url)
        
        #self.log(None, 'Send to queue {} | {}'.format(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_FOLHA'], message_queue.to_json()), Log.INFO)

        self.sqs.send_message_queue(Envs.AWS['SQS']['QUEUE']['VOXRADAR_NEWS_SAVE_DATA'], message_queue.__str__())



