import json
import datetime
from flask import request
import datetime
from src.integration.sqs.sqs import Sqs
from src.types.voxradar_news_save_data_queue_dto import VoxradarNewsSaveDataQueueDTO
from src.types.voxradar_news_scrapping_maisgoias_queue_dto import VoxradarNewsScrappingMaisGoiasQueueDTO
from src.utils.utils import Utils
from ..config.envs import Envs
from .base.base_service import BaseService
from ..types.return_service import ReturnService
from bs4 import BeautifulSoup
import unicodedata
import requests


class ScrappingNewsMaisGoiasService(BaseService):

    sqs: Sqs

    def __init__(self):
        super().__init__()
        # self.log_repository = ViewEstadaoLogRepository()
        # self.s3 = S3()
        self.sqs = Sqs()

    def exec(self, body:str) -> ReturnService:
        self.logger.info(f'\n----- Scrapping News Mais Goias Service | Init - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")} -----\n')
        maisgoias_dict = {'title': [], 'domain':[],'source':[],'date': [], 'body_news': [], 'link': [],'category': [],'image': []}
        voxradar_news_scrapping_maisgoias_queue_dto:VoxradarNewsScrappingMaisGoiasQueueDTO = self.__parse_body(body)
        url_news = voxradar_news_scrapping_maisgoias_queue_dto.url
        headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:2.0b10) Gecko/20100101 Firefox/4.0b10"}
        page = requests.get(url_news,headers=headers).text
        soup = BeautifulSoup(page, 'html.parser')     
    #
    #title
    #
        title = soup.find("meta", attrs={'property': 'og:title'})
        title = str(title).split("content=")[1].split("property=")[0].replace('- @aredacao','').replace('"','')
            #
    #Stardandizing Date
    #
        date = soup.find("script", type="application/ld+json")
        date = str(date).split('datePublished":')[1].split(',"dateModified')[0].replace('"','')
        date = "%s-3:00"%(date)  
 
    #
    #Pick body's news
    #
    # 
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
                body_news = [x.text for x in soup.find(mode[i], class_ = classk[j]).find_all(paragraf[k]) if len(x.text)>90]
                if(len(body_news)>0):
                    break
            except:
                None

        body_new = ''
        jump_text = ('Saiba Mais','Contato: ')

        for x in body_news:
            if 'Clique Aqui' in x:
                None
            else:
                x.replace("\n","")
                body_new=body_new+x+' \n '##  
   



    # Pick category news
    #   
        category_news = soup.find_all('script')
        category_news = str(category_news).split('"category":')[1].split(',')[0].replace('"','')

        #
        #
        #
    # Pick image from news
        #
        ass = soup.find("picture")
        image_new = str(ass).split("quality=90,format=auto/")[1].split('media=')[0].replace('"','')
        #
        #
        domain = url_news.split(".br/")[0]+'.br/'
        source = url_news.split("www.")[1].split(".com")[0]
        #
        maisgoias_dict["title"].append(title)
        maisgoias_dict["domain"].append(domain)
        maisgoias_dict["source"].append(source)
        maisgoias_dict["date"].append(date)
        maisgoias_dict["body_news"].append(body_new)
        maisgoias_dict["link"].append(url_news)
        maisgoias_dict["category"].append(category_news)
        maisgoias_dict["image"].append(image_new)
        

        print(maisgoias_dict)

        self.__send_queue(title, domain, source, body_new, date, category_news, image_new, url_news)

        return ReturnService(True, 'Sucess')

    def __parse_body(self, body:str) -> VoxradarNewsScrappingMaisGoiasQueueDTO:
        body = json.loads(body)
        return VoxradarNewsScrappingMaisGoiasQueueDTO(body.get('url'))
    
    def __send_queue(self, title: str, domain: str, source: str, content: str, date: str, category: str, image: str, url: str):
        message_queue:VoxradarNewsSaveDataQueueDTO = VoxradarNewsSaveDataQueueDTO(title, domain, source, content, date, category, image, url)
        
        #self.log(None, 'Send to queue {} | {}'.format(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_FOLHA'], message_queue.to_json()), Log.INFO)

        self.sqs.send_message_queue(Envs.AWS['SQS']['QUEUE']['VOXRADAR_NEWS_SAVE_DATA'], message_queue.__str__())



