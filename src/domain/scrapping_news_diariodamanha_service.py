import json
import datetime
from flask import request
import datetime
from src.integration.sqs.sqs import Sqs
from src.types.voxradar_news_save_data_queue_dto import VoxradarNewsSaveDataQueueDTO
from src.types.voxradar_news_scrapping_diariodamanha_queue_dto import VoxradarNewsScrappingDiariodaManhaQueueDTO
from src.utils.utils import Utils
from ..config.envs import Envs
from .base.base_service import BaseService
from ..types.return_service import ReturnService
from bs4 import BeautifulSoup
import unicodedata
import requests


class ScrappingNewsDiariodaManhaService(BaseService):

    sqs: Sqs

    def __init__(self):
        super().__init__()
        # self.log_repository = ViewEstadaoLogRepository()
        # self.s3 = S3()
        self.sqs = Sqs()

    def exec(self, body:str) -> ReturnService:
        self.logger.info(f'\n----- Scrapping News Diario da Manha Service | Init - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")} -----\n')
        diariodamanha_dict = {'title': [], 'domain':[],'source':[],'date': [], 'body_news': [], 'link': [],'category': [],'image': []}
        voxradar_news_scrapping_diariodamanha_queue_dto:VoxradarNewsScrappingDiariodaManhaQueueDTO = self.__parse_body(body)
        url_news = voxradar_news_scrapping_diariodamanha_queue_dto.url
        headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:2.0b10) Gecko/20100101 Firefox/4.0b10"}
        page = requests.get(url_news,headers=headers).text
        soup = BeautifulSoup(page, 'html.parser')     
    #
    #title
    #
        title = soup.find("title")
        title = str(title).split("<title>")[1].split("|")[0].replace('- @aredacao','').replace('"','')
            #
    #Stardandizing Date
    #
        date = soup.find("meta",attrs={'property': 'article:published_time'})
        date = str(date).split('meta content=')[1].split('property=')[0].replace('"','')
        date = date.replace('T',' ').split('+')[0]
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        delta = datetime.timedelta(hours=4)
        date = date - delta
        date = "%s-3:00"%(str(date.strftime('%Y-%m-%d %H:%M:%S')))   
 
    #
    #Pick body's news
    #
    # 
        mode = ['div']
        classk = ['content-single']
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
            if 'Leia também:' in x:
                None
            else:
                x.replace("\n","")
                body_new=body_new+x+' \n '##        
   


    # Pick category news
    #   
        category_news = soup.find('span',class_='categoria')
        category_news = str(category_news).split('categoria">')[1].split('</span>')[0]

        #
        #
        #
    # Pick image from news
        #
        ass = soup.find("figure",class_='img-responsive img-post placeholder mt-3')
        image_new = str(ass).split('data-large=')[1].split('>')[0].replace('"','')
        #
        #
        domain = url_news.split(".com")[0]+'.com'
        source = url_news.split("www.")[1].split(".com")[0]       
        #
        diariodamanha_dict["title"].append(title)
        diariodamanha_dict["domain"].append(domain)
        diariodamanha_dict["source"].append(source)
        diariodamanha_dict["date"].append(date)
        diariodamanha_dict["body_news"].append(body_new)
        diariodamanha_dict["link"].append(url_news)
        diariodamanha_dict["category"].append(category_news)
        diariodamanha_dict["image"].append(image_new)
        

        print(diariodamanha_dict)

        self.__send_queue(title, domain, source, body_new, date, category_news, image_new, url_news)

        return ReturnService(True, 'Sucess')

    def __parse_body(self, body:str) -> VoxradarNewsScrappingDiariodaManhaQueueDTO:
        body = json.loads(body)
        return VoxradarNewsScrappingDiariodaManhaQueueDTO(body.get('url'))
    
    def __send_queue(self, title: str, domain: str, source: str, content: str, date: str, category: str, image: str, url: str):
        message_queue:VoxradarNewsSaveDataQueueDTO = VoxradarNewsSaveDataQueueDTO(title, domain, source, content, date, category, image, url)
        
        #self.log(None, 'Send to queue {} | {}'.format(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_FOLHA'], message_queue.to_json()), Log.INFO)

        self.sqs.send_message_queue(Envs.AWS['SQS']['QUEUE']['VOXRADAR_NEWS_SAVE_DATA'], message_queue.__str__())



