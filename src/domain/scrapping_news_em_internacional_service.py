import json
import datetime
from flask import request
import datetime
from src.integration.sqs.sqs import Sqs
from src.types.voxradar_news_save_data_queue_dto import VoxradarNewsSaveDataQueueDTO
from src.types.voxradar_news_scrapping_em_internacional_queue_dto import VoxradarNewsScrappingEmInternacionalQueueDTO
from src.utils.utils import Utils
from ..config.envs import Envs
from .base.base_service import BaseService
from ..types.return_service import ReturnService
from bs4 import BeautifulSoup
import unicodedata
import requests


class ScrappingNewsEmInternacionalService(BaseService):

    sqs: Sqs

    def __init__(self):
        super().__init__()
        # self.log_repository = ViewEstadaoLogRepository()
        # self.s3 = S3()
        self.sqs = Sqs()

    def exec(self, body:str) -> ReturnService:
        self.logger.info(f'\n----- Scrapping News Em Internacional Service | Init - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")} -----\n')
        em_dict = {'title': [], 'domain':[],'source':[],'date': [], 'body_news': [], 'link': [],'category': [],'image': []}
        voxradar_news_scrapping_eminternacional_queue_dto:VoxradarNewsScrappingEmInternacionalQueueDTO = self.__parse_body(body)
        url_news = voxradar_news_scrapping_eminternacional_queue_dto.url
        page = requests.get(url_news).text
        soup = BeautifulSoup(page, 'html.parser')   
    #
    #title
    #
        title = soup.find("meta",property="og:title")
        title = str(title).split("content=")[1].split("property=")[0].split('itemprop=')[0].replace('- @aredacao','').replace('"','')
    #
    #Stardandizing Date
    #
        date = soup.find_all("script")
        date = str(date).split('"datePublished":')[1].split(',')[0].replace('T', ' ').replace('Z', '').replace('"','').split('+')[0].strip()
        #
    #
    #Pick body's news
    #
    #



        mode = ['div']
        classk = ['rs_read_this2']
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
            body_news = [x.text.strip().replace('\xa0', '  ') for x in soup.find(mode[i], id = classk[j]).find_all(paragraf[k]) if len(x.text)>20]
        body_news_extract = [x.text.strip().replace('\xa0', '  ') for x in soup.find(mode[i], id = classk[j]).find_all('div') if len(x.text)>20]

        aux_extract = body_news_extract[1]
        aux = []
        for i in range(1,len(body_news)):
            aux.append(body_news[i].replace(aux_extract,'').strip())


        no_text = ['Cartola','Leia outras','podcast','Foto','clique aqui','Assine o Premiere','VÍDEOS:','LEIA MAIS']
        space_text = ['  ']
        for x in aux:
            if item in space_text:
                if item in x:
                    x.replace(item,'\n')    
            for item in no_text:
                if item in x:
                    x = ''

            if x=='':
                pass
            else:
                body_new = body_new+x+' \n' ##

                
    # Pick category news
    #   

   
        category_news =soup.find("meta",property="article:section")
        category_news = str(category_news).split("content=")[1].split("property=")[0].split('itemprop=')[0].replace('- @aredacao','').replace('"','').lower()
            

        #
        #
        #
    # Pick image from news
        #
        ass = soup.find("meta", property="og:image")
        image_new = str(ass).split("content=")[1].split(" ")[0].replace('"','').replace(";",'')
        # #
        # #
        domain = url_news.split(".com")[0]+'.com'
        try:
            source = url_news.split("www.")[1].split(".com")[0]               
        except:
            source = url_news.split("https://")[1].split(".com")[0]       
        #
        #
        em_dict["title"].append(title)
        em_dict["domain"].append(domain)
        em_dict["source"].append(source)
        em_dict["date"].append(date)
        em_dict["body_news"].append(body_new)
        em_dict["link"].append(url_news)
        em_dict["category"].append(category_news)
        em_dict["image"].append(image_new)
        

        print(em_dict)

        self.__send_queue(title, domain, source, body_new, date, category_news, image_new, url_news)

        return ReturnService(True, 'Sucess')

    def __parse_body(self, body:str) -> VoxradarNewsScrappingEmInternacionalQueueDTO:
        body = json.loads(body)
        return VoxradarNewsScrappingEmInternacionalQueueDTO(body.get('url'))
    
    def __send_queue(self, title: str, domain: str, source: str, content: str, date: str, category: str, image: str, url: str):
        message_queue:VoxradarNewsSaveDataQueueDTO = VoxradarNewsSaveDataQueueDTO(title, domain, source, content, date, category, image, url)
        
        #self.log(None, 'Send to queue {} | {}'.format(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_FOLHA'], message_queue.to_json()), Log.INFO)

        self.sqs.send_message_queue(Envs.AWS['SQS']['QUEUE']['VOXRADAR_NEWS_SAVE_DATA'], message_queue.__str__())



