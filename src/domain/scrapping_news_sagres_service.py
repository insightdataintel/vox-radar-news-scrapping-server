import json
import datetime
from flask import request
import datetime
from src.integration.sqs.sqs import Sqs
from src.types.voxradar_news_save_data_queue_dto import VoxradarNewsSaveDataQueueDTO
from src.types.voxradar_news_scrapping_sagres_queue_dto import VoxradarNewsScrappingSagresQueueDTO
from src.utils.utils import Utils
from ..config.envs import Envs
from .base.base_service import BaseService
from ..types.return_service import ReturnService
from bs4 import BeautifulSoup
import unicodedata
import requests


class ScrappingNewsSagresService(BaseService):

    sqs: Sqs

    def __init__(self):
        super().__init__()
        # self.log_repository = ViewEstadaoLogRepository()
        # self.s3 = S3()
        self.sqs = Sqs()

    def exec(self, body:str) -> ReturnService:
        self.logger.info(f'\n----- Scrapping News Sagres Service | Init - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")} -----\n')
        sagres_dict = {'title': [], 'domain':[],'source':[],'date': [], 'body_news': [], 'link': [],'category': [],'image': []}
        voxradar_news_scrapping_sagres_queue_dto:VoxradarNewsScrappingSagresQueueDTO = self.__parse_body(body)
        url_news = voxradar_news_scrapping_sagres_queue_dto.url
        headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:2.0b10) Gecko/20100101 Firefox/4.0b10"}
        page = requests.get(url_news,headers=headers).text
        soup = BeautifulSoup(page, 'html.parser')     
    #
    #title
    #
        title = soup.find("meta",attrs={'property':'og:title'})
        title = str(title).split("meta content=")[1].split("property=")[0].replace('- Sagres Online','').replace('"','').replace("'","")
            #
    #Stardandizing Date
    #
        date = soup.find("meta",attrs={'property': 'article:published_time'})
        date = str(date).split('meta content=')[1].split('property=')[0].replace('"','')
        date = date.replace('T',' ').split('+')[0]
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        delta = datetime.timedelta(hours=3)
        date = date - delta
        date = "%s-3:00"%(str(date.strftime('%Y-%m-%d %H:%M:%S')))  
 
    #
    #Pick body's news
    #
    # 
        mode = ['div']
        classk = ['td-ss-main-content']
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
            if 'Telefone:' in x:
                break
            else:
                x.replace("\n","")
                body_new=body_new+x+' \n '##              
   


    # Pick category news
    #   
        category = soup.find_all('li',class_='entry-category') 
        category_news = ''
        for categor in category:
            category_news = category_news +" %s"%(str(categor).split('/">')[1].split('</a>')[0])
    


        #
        #
        #
    # Pick image from news
        #
        ass = soup.find("meta", property="og:image")
        image_new = str(ass).split("content=")[1].split(" ")[0].replace('"','').replace(";",'')
        #
        #
        domain = url_news.split(".br/")[0]+'.br'
        source = url_news.split("https://")[1].split(".com")[0]          
        #
        sagres_dict["title"].append(title)
        sagres_dict["domain"].append(domain)
        sagres_dict["source"].append(source)
        sagres_dict["date"].append(date)
        sagres_dict["body_news"].append(body_new)
        sagres_dict["link"].append(url_news)
        sagres_dict["category"].append(category_news)
        sagres_dict["image"].append(image_new)
        

        print(sagres_dict)

        self.__send_queue(title, domain, source, body_new, date, category_news, image_new, url_news)

        return ReturnService(True, 'Sucess')

    def __parse_body(self, body:str) -> VoxradarNewsScrappingSagresQueueDTO:
        body = json.loads(body)
        return VoxradarNewsScrappingSagresQueueDTO(body.get('url'))
    
    def __send_queue(self, title: str, domain: str, source: str, content: str, date: str, category: str, image: str, url: str):
        message_queue:VoxradarNewsSaveDataQueueDTO = VoxradarNewsSaveDataQueueDTO(title, domain, source, content, date, category, image, url)
        
        #self.log(None, 'Send to queue {} | {}'.format(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_FOLHA'], message_queue.to_json()), Log.INFO)

        self.sqs.send_message_queue(Envs.AWS['SQS']['QUEUE']['VOXRADAR_NEWS_SAVE_DATA'], message_queue.__str__())



