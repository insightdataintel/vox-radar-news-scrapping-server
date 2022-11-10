import json
import datetime
from flask import request
import datetime
from src.integration.sqs.sqs import Sqs
from src.types.voxradar_news_save_data_queue_dto import VoxradarNewsSaveDataQueueDTO
from src.types.voxradar_news_scrapping_ebc_queue_dto import VoxradarNewsScrappingEbcQueueDTO
from src.utils.utils import Utils
from ..config.envs import Envs
from .base.base_service import BaseService
from ..types.return_service import ReturnService
from bs4 import BeautifulSoup
import unicodedata
import requests


class ScrappingNewsEbcService(BaseService):

    sqs: Sqs

    def __init__(self):
        super().__init__()
        # self.log_repository = ViewEstadaoLogRepository()
        # self.s3 = S3()
        self.sqs = Sqs()

    def exec(self, body:str) -> ReturnService:
        self.logger.info(f'\n----- Scrapping News Poliarquia Service | Init - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")} -----\n')
        ebc_dict = {'title': [], 'domain':[],'source':[],'date': [], 'body_news': [], 'link': [],'category': [],'image': []}
        voxradar_news_scrapping_ebc_queue_dto:VoxradarNewsScrappingEbcQueueDTO = self.__parse_body(body)
        url_news = voxradar_news_scrapping_ebc_queue_dto.url
        page = requests.get(url_news).text
        soup = BeautifulSoup(page, 'html.parser')   
    #
    #title
    #
        try:
            title = soup.find('meta',property='og:title')
            title = str(title).split("content=")[1].split("property=")[0].split('itemprop=')[0].split('- ISTOÉ DINHEIRO')[0].replace('- @aredacao','').replace('"','')
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar o título da notícia do EBC: {url_news} | {e}")     
            title = ""
    #
    #Stardandizing Date
    #
        try:
        
            date = soup.find("span", property="dc:date")
            date = str(date).split('content="')[1].split('datatype')[0].split(',')[0].split('<span')[0].replace('T', ' ').replace('Z', '').\
            replace('"','').replace('h',':').replace('-04:00','').split('+')[0].\
            replace('min','').strip()
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar a data da notícia do EBC: {url_news} | {e}")
            date = ""    
    #
    #Pick body's news
    #
    #
        try:
            mode = ['div']
            classk = ['td-post-content']
            paragraf = ['p']
            body_new = ''

            for i in range(0,len(mode)):
                for j in range(0,len(classk)):
                    try:
                        yes = soup.find('article')
                        if(len(yes)>0):
                            break
                    except:
                        None

                        

            for k in range(0,len(paragraf)):
                try:
                    body_news = [x.text for x in soup.find('article').find_all(paragraf[k]) if len(x.text)>20]
                    if(len(body_news)>0):
                        break
                except:
                    body_news = [x.text for x in soup.find(mode[i], id = 'textContent').find_all(paragraf[k]) if len(x.text)>20]
                    if(len(body_news)>0):
                        break



            no_text = ['Cartola','Leia outras','podcast','Foto','clique aqui','Assine o Premiere','VÍDEOS:',\
                        'o app do Yahoo Mail','Assine agora a newsletter','via Getty Images','Fonte: ','O seu endereço de e-mail',\
                        'email protected','Comunicação Social da Polícia','email','Portal iG','nossas newsletters',\
                        'WhatsApp:  As regras de privacidade','de 700 caracteres [0]','pic.twitter.com','(@','Leia também',\
                            '(Reportagem', 'Entre para o grupo do Money Times','Entre agora para o nosso grupo no Telegram!',\
                                'Ilustração: ','Continue lendo no']
            for x in body_news:
                for item in no_text:
                    if item in x:
                        x = ''
                if x=='':
                    None
                else:
                    body_new = body_new+x+'\n' ##

            body_new = body_new.strip().replace('\n',' ').replace('(Reuters) –', '')
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar o corpo da notícia do EBC: {url_news} | {e}")
            body_new= ""    
    #    
    # Pick category news
    #   
        category_news = url_news.replace("www.",'').replace('https://','').split('/')[2]

                
        #
        #
        #
    # Pick image from news
        #
        try:
            ass = soup.find("img", class_='img-responsive full')
            image_new = str(ass).split("src=")[1].split("title=")[0].replace('"','').replace(";",'')
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar imagens da notícia do EBC: {url_news} | {e}")     
            image_new = "" 
        # # #
        # #
        domain = url_news.split(".com")[0]+'.com'
        try:
            source = url_news.split("www.")[1].split(".com")[0]               
        except:
            source = url_news.split("https://")[1].split(".com")[0]               
        #
        #
        ebc_dict["title"].append(title)
        ebc_dict["domain"].append(domain)
        ebc_dict["source"].append(source)
        ebc_dict["date"].append(date)
        ebc_dict["body_news"].append(body_new)
        ebc_dict["link"].append(url_news)
        ebc_dict["category"].append(category_news)
        ebc_dict["image"].append(image_new)
        

        print(ebc_dict)

        self.__send_queue(title, domain, source, body_new, date, category_news, image_new, url_news)

        return ReturnService(True, 'Sucess')

    def __parse_body(self, body:str) -> VoxradarNewsScrappingEbcQueueDTO:
        body = json.loads(body)
        return VoxradarNewsScrappingEbcQueueDTO(body.get('url'))
    
    def __send_queue(self, title: str, domain: str, source: str, content: str, date: str, category: str, image: str, url: str):
        message_queue:VoxradarNewsSaveDataQueueDTO = VoxradarNewsSaveDataQueueDTO(title, domain, source, content, date, category, image, url)
        
        #self.log(None, 'Send to queue {} | {}'.format(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_FOLHA'], message_queue.to_json()), Log.INFO)

        self.sqs.send_message_queue(Envs.AWS['SQS']['QUEUE']['VOXRADAR_NEWS_SAVE_DATA'], message_queue.__str__())



