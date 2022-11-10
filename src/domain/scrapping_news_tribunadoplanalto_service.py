import json
import datetime
from flask import request
import datetime
from src.integration.sqs.sqs import Sqs
from src.types.voxradar_news_save_data_queue_dto import VoxradarNewsSaveDataQueueDTO
from src.types.voxradar_news_scrapping_tribunadoplanalto_queue_dto import VoxradarNewsScrappingTribunadoPlanaltoQueueDTO
from src.utils.utils import Utils
from ..config.envs import Envs
from .base.base_service import BaseService
from ..types.return_service import ReturnService
from bs4 import BeautifulSoup
import unicodedata
import requests


class ScrappingNewsTribunadoPlanaltoService(BaseService):

    sqs: Sqs

    def __init__(self):
        super().__init__()
        # self.log_repository = ViewEstadaoLogRepository()
        # self.s3 = S3()
        self.sqs = Sqs()

    def exec(self, body:str) -> ReturnService:
        self.logger.info(f'\n----- Scrapping News Tribuna do Planalto Service | Init - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")} -----\n')
        tribunadoplanalto_dict = {'title': [], 'domain':[],'source':[],'date': [], 'body_news': [], 'link': [],'category': [],'image': []}
        voxradar_news_scrapping_tribunadoplanalto_queue_dto:VoxradarNewsScrappingTribunadoPlanaltoQueueDTO = self.__parse_body(body)
        url_news = voxradar_news_scrapping_tribunadoplanalto_queue_dto.url
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
            date = soup.find("meta",attrs={'property': 'article:published_time'})
            date = str(date).split('meta content=')[1].split('property=')[0].replace('"','')
            date = date.replace('T',' ').split('+')[0]
            date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            delta = datetime.timedelta(hours=3)
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
            classk = ['col-12 col-lg-8 pb-4']
            paragraf = ['p']

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
                    None

            body_new = ''

            for x in body_news:
                if 'LEIA TAMBÉM:' in x:
                    None
                else:
                    x.replace("\n","")
                    body_new=body_new+x+' \n '##         
    

        except Exception as e:
            self.logger.error(f"Não foi possível encontrar o corpo da notícia do Folha de São Paulo: {url_news} | {e}")
            body_new = ""

    # Pick category news
    # 
        category_news = soup.find('div',class_='marcadores py-4')
        category_news = str(category_news).split('rel="category tag">')[1].split('</a>')[0]

        #
        #
        #
    # Pick image from news
        #
        try:
            ass = soup.find("div",class_='d-flex container-fluid single-featured-image')
            image_new = str(ass).split('src="')[1].split('style=')[0].replace('"','')
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar imagens da notícia do Folha de São Paulo: {url_news} | {e}")     
            image_new = "" 
        #
        #
        domain = url_news.split(".com")[0]+'.com'
        source = url_news.split("https://")[1].split(".com")[0]     
        #
        tribunadoplanalto_dict["title"].append(title)
        tribunadoplanalto_dict["domain"].append(domain)
        tribunadoplanalto_dict["source"].append(source)
        tribunadoplanalto_dict["date"].append(date)
        tribunadoplanalto_dict["body_news"].append(body_new)
        tribunadoplanalto_dict["link"].append(url_news)
        tribunadoplanalto_dict["category"].append(category_news)
        tribunadoplanalto_dict["image"].append(image_new)
        

        print(tribunadoplanalto_dict)

        self.__send_queue(title, domain, source, body_new, date, category_news, image_new, url_news)

        return ReturnService(True, 'Sucess')

    def __parse_body(self, body:str) -> VoxradarNewsScrappingTribunadoPlanaltoQueueDTO:
        body = json.loads(body)
        return VoxradarNewsScrappingTribunadoPlanaltoQueueDTO(body.get('url'))
    
    def __send_queue(self, title: str, domain: str, source: str, content: str, date: str, category: str, image: str, url: str):
        message_queue:VoxradarNewsSaveDataQueueDTO = VoxradarNewsSaveDataQueueDTO(title, domain, source, content, date, category, image, url)
        
        #self.log(None, 'Send to queue {} | {}'.format(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_FOLHA'], message_queue.to_json()), Log.INFO)

        self.sqs.send_message_queue(Envs.AWS['SQS']['QUEUE']['VOXRADAR_NEWS_SAVE_DATA'], message_queue.__str__())



