import json
import datetime
from flask import request
import datetime
from src.integration.sqs.sqs import Sqs
from src.types.voxradar_news_save_data_queue_dto import VoxradarNewsSaveDataQueueDTO
from src.types.voxradar_news_scrapping_dinheiro_rural_queue_dto import VoxradarNewsScrappingDinheiroRuralQueueDTO
from src.utils.utils import Utils
from ..config.envs import Envs
from .base.base_service import BaseService
from ..types.return_service import ReturnService
from bs4 import BeautifulSoup
import unicodedata
import requests


class ScrappingNewsDinheiroRuralService(BaseService):

    sqs: Sqs

    def __init__(self):
        super().__init__()
        # self.log_repository = ViewEstadaoLogRepository()
        # self.s3 = S3()
        self.sqs = Sqs()

    def exec(self, body:str) -> ReturnService:
        self.logger.info(f'\n----- Scrapping News Dinheiro Rural Service | Init - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")} -----\n')
        dinheirorural_dict = {'title': [], 'domain':[],'source':[],'date': [], 'body_news': [], 'link': [],'category': [],'image': []}
        voxradar_news_scrapping_dinheiro_rural_queue_dto:VoxradarNewsScrappingDinheiroRuralQueueDTO = self.__parse_body(body)
        url_news = voxradar_news_scrapping_dinheiro_rural_queue_dto.url
        headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:2.0b10) Gecko/20100101 Firefox/4.0b10"}
        page = requests.get(url_news,headers=headers).text
        soup = BeautifulSoup(page, 'html.parser')     
    #
    #title
    #
        title = soup.find("meta", attrs={'property': 'og:title'})
        title = str(title).split("content=")[1].split("property=")[0].replace('"','')

    #
    #Stardandizing Date
    #
        date = soup.find("span", class_='css-1d56udz')
        date = str(date).split('css-1d56udz">')[1].split("<!--")[0].replace(':"','').replace('"','').split("+")[0]
        horas = date.split('-')[1].replace("h",":").replace("min","")
        aux0 = date.split('-')[0]
        aux1 = aux0.split('/')
        aux1_dia = aux1[0]
        aux1_mes = aux1[1]
        aux1_ano = '20'+aux1[2]
        aux = aux1_dia+'/'+aux1_mes+'/'+aux1_ano + '-' + horas
        date = datetime.datetime.strptime(aux, "%d/%m/%Y - %H:%M")
        date = "%s-3:00"%(str(date.strftime('%Y-%m-%d %H:%M:%S')))  

            #
    #Pick body's news
    #
# 

        body_new = ''
        mode = ['div']
        classk = ['css-1q1yem4']
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
            if 'Contato: ' in x:
                None
            else:
                x.replace("\n","")
                body_new=body_new+x+' \n '##       
                
                
   



    # Pick category news
    #   
        category_news = soup.find('a',class_= 'css-x99x62')
        category_news = str(category_news).split('categoria/')[1].split('">')[0]
       


        #
        #
        #
    # Pick image from news
        #
        ass = soup.find("meta", property="og:image")
        image_new = str(ass).split("content=")[1].split(" ")[0].replace('"','')
        #
        #
        domain = url_news.split("://")[1].split("/")[0]
        source = domain.split(".")[1]       #
        #
        dinheirorural_dict["title"].append(title)
        dinheirorural_dict["domain"].append(domain)
        dinheirorural_dict["source"].append(source)
        dinheirorural_dict["date"].append(date)
        dinheirorural_dict["body_news"].append(body_new)
        dinheirorural_dict["link"].append(url_news)
        dinheirorural_dict["category"].append(category_news)
        dinheirorural_dict["image"].append(image_new)
        

        print(dinheirorural_dict)

        self.__send_queue(title, domain, source, body_new, date, category_news, image_new, url_news)

        return ReturnService(True, 'Sucess')

    def __parse_body(self, body:str) -> VoxradarNewsScrappingDinheiroRuralQueueDTO:
        body = json.loads(body)
        return VoxradarNewsScrappingDinheiroRuralQueueDTO(body.get('url'))
    
    def __send_queue(self, title: str, domain: str, source: str, content: str, date: str, category: str, image: str, url: str):
        message_queue:VoxradarNewsSaveDataQueueDTO = VoxradarNewsSaveDataQueueDTO(title, domain, source, content, date, category, image, url)
        
        #self.log(None, 'Send to queue {} | {}'.format(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_FOLHA'], message_queue.to_json()), Log.INFO)

        self.sqs.send_message_queue(Envs.AWS['SQS']['QUEUE']['VOXRADAR_NEWS_SAVE_DATA'], message_queue.__str__())



