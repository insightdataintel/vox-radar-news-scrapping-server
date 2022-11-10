import json
import datetime
from flask import request
import datetime
from src.integration.sqs.sqs import Sqs
from src.types.voxradar_news_save_data_queue_dto import VoxradarNewsSaveDataQueueDTO
from src.types.voxradar_news_scrapping_correiobraziliense_queue_dto import VoxradarNewsScrappingCorreioBrazilienseQueueDTO
from src.utils.utils import Utils
from ..config.envs import Envs
from .base.base_service import BaseService
from ..types.return_service import ReturnService
from bs4 import BeautifulSoup
import unicodedata
import requests


class ScrappingNewsCorreioBrazilienseService(BaseService):

    sqs: Sqs

    def __init__(self):
        super().__init__()
        # self.log_repository = ViewEstadaoLogRepository()
        # self.s3 = S3()
        self.sqs = Sqs()

    def exec(self, body:str) -> ReturnService:
        self.logger.info(f'\n----- Scrapping News Correio Braziliense Service | Init - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")} -----\n')
        correiobrz_dict = {'title': [], 'domain':[],'source':[],'date': [], 'body_news': [], 'link': [],'category': [],'image': []}
        voxradar_news_scrapping_correiobraziliense_queue_dto:VoxradarNewsScrappingCorreioBrazilienseQueueDTO = self.__parse_body(body)
        url_news = voxradar_news_scrapping_correiobraziliense_queue_dto.url
        headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:2.0b10) Gecko/20100101 Firefox/4.0b10"}
        page = requests.get(url_news,headers=headers).text
        soup = BeautifulSoup(page, 'html.parser')     
    #
    #title
    #
        try:
            title = soup.find("meta", attrs={'property': 'og:title'})
            title = str(title).split("content=")[1].split("property=")[0].replace('"','')
            title = title.encode('iso-8859-1').decode('utf-8')

        except Exception as e:
            self.logger.error(f"Não foi possível encontrar o título da notícia do Correrio Braziliense: {url_news} | {e}")     
            title = ""
    #
    #Stardandizing Date
    #
        try:
            date = soup.find("meta", attrs={'property': 'article:published_time'})
            date = str(date).split('meta content=')[1].split("property=")[0].replace(':"','').replace('"','').split("+")[0]
            aux = date.split('-')
            aux_ano = aux[0]
            aux_mes = aux[1]
            aux_dia = aux[2]
            aux_hora = aux[3].replace('03', '')
            date = aux_ano+'-'+aux_mes+'-'+aux_dia+ ' ' + aux_hora + '-03'

        except Exception as e:
            self.logger.error(f"Não foi possível encontrar a data da notícia do Correrio Braziliense: {url_news} | {e}")
            date = ""    
    #
    #Pick body's news
    #
# 
        try:
            body_new = ''
            mode = ['article']
            classk = ['article']
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
                    body_news = [x.text for x in soup.find(mode[i], class_ = classk[j]).find_all(paragraf[k],class_='texto') if len(x.text)>20]
                    if(len(body_news)>0):
                        break
                except:
                    None

            body_new = ''

            for x in body_news:
                if 'Saiba Mais' in x:
                    None
                elif x.replace(" ","")[-1]==",":
                    body_new=body_new+x
                else:
                    body_new=body_new+x+' \n '##

            body_new = body_new.replace('Leia mais','').replace('Continua após a publicidade','').replace('Leia também','').replace('— Foto: Getty Images', '')
            body_new = body_new.split('Foto destaque:')[0]
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar o corpo da notícia do Correrio Braziliense: {url_news} | {e}")
            return ReturnService(False, 'Did not collect the body of the News')            
   



    # Pick category news
    #   
        category_news = url_news.replace("www.",'').replace("https://",'')
        category_news = category_news.split('/')[1]

        #
        #
        #
    # Pick image from news
        #
        try:
            ass = soup.find("meta", property="og:image")
            image_new = str(ass).split("content=")[1].split(" ")[0].replace('"','')
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar imagens da notícia do Correrio Braziliense: {url_news} | {e}")     
            image_new = "" 
        #
        #
        domain = url_news.split("://")[1].split("/")[0]
        source = domain.split(".")[1]       #
        #
        correiobrz_dict["title"].append(title)
        correiobrz_dict["domain"].append(domain)
        correiobrz_dict["source"].append(source)
        correiobrz_dict["date"].append(date)
        correiobrz_dict["body_news"].append(body_new)
        correiobrz_dict["link"].append(url_news)
        correiobrz_dict["category"].append(category_news)
        correiobrz_dict["image"].append(image_new)
        

        print(correiobrz_dict)

        self.__send_queue(title, domain, source, body_new, date, category_news, image_new, url_news)

        return ReturnService(True, 'Sucess')

    def __parse_body(self, body:str) -> VoxradarNewsScrappingCorreioBrazilienseQueueDTO:
        body = json.loads(body)
        return VoxradarNewsScrappingCorreioBrazilienseQueueDTO(body.get('url'))
    
    def __send_queue(self, title: str, domain: str, source: str, content: str, date: str, category: str, image: str, url: str):
        message_queue:VoxradarNewsSaveDataQueueDTO = VoxradarNewsSaveDataQueueDTO(title, domain, source, content, date, category, image, url)
        
        #self.log(None, 'Send to queue {} | {}'.format(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_FOLHA'], message_queue.to_json()), Log.INFO)

        self.sqs.send_message_queue(Envs.AWS['SQS']['QUEUE']['VOXRADAR_NEWS_SAVE_DATA'], message_queue.__str__())



