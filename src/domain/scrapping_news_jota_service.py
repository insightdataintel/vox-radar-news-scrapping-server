import json
import datetime
from flask import request
import datetime
from src.integration.sqs.sqs import Sqs
from src.types.voxradar_news_save_data_queue_dto import VoxradarNewsSaveDataQueueDTO
from src.types.voxradar_news_scrapping_jota_queue_dto import VoxradarNewsScrappingJotaQueueDTO
from src.utils.utils import Utils
from ..config.envs import Envs
from .base.base_service import BaseService
from ..types.return_service import ReturnService
from bs4 import BeautifulSoup
import unicodedata
import requests


class ScrappingNewsJotaService(BaseService):

    sqs: Sqs

    def __init__(self):
        super().__init__()
        # self.log_repository = ViewEstadaoLogRepository()
        # self.s3 = S3()
        self.sqs = Sqs()

    def exec(self, body:str) -> ReturnService:
        self.logger.info(f'\n----- Scrapping News Jota Service | Init - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")} -----\n')
        jota_dict = {'title': [], 'domain':[],'source':[],'date': [], 'body_news': [], 'link': [],'category': [],'image': []}
        voxradar_news_scrapping_jota_queue_dto:VoxradarNewsScrappingJotaQueueDTO = self.__parse_body(body)
        url_news = voxradar_news_scrapping_jota_queue_dto.url
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
        date = soup.find("div", class_= "jota-article__date")
        date = str(date).split('datetime=')[1].split(">")[0].replace('"','').replace('h',':').replace('T', ' ') 
            #
    #Pick body's news
    #
# 
                
        body_new = ''
        mode = ['article', 'div']
        classk = ['toolkit-media-content','container','offset-md-2 col-md-8 postagem','entry-content materia','entry-content','jota-article__content','single-container','texto',\
                'td_block_wrap tdb_single_content tdi_87 td-pb-border-top conteudo-post td_block_template_8 td-post-content tagdiv-type',\
                'mvp-post-soc-out right relative','post_content']

        for i in range(0,len(mode)):
            for j in range(0,len(classk)):
                try:
                    yes = soup.find(mode[i],class_= classk[j])
                    if(len(yes)>0):
                        break
                except:
                    None

                    
        body_news = [x.text for x in soup.find(mode[i], class_ = classk[j]).find_all("p") if len(x.text)>90]
        body_new = ''
        for x in body_news:
            if x.replace(" ","")[-1]==",":
                body_new=body_new+x
            else:
                body_new=body_new+x+' \n '##

        body_new = body_new.replace('Leia mais','').replace('Continua após a publicidade','').replace('Leia também','').replace('— Foto: Getty Images', '')
        body_new = body_new.split('Foto destaque:')[0]

                    
                    
   



    # Pick category news
    #   
        chars = ['<','>','span','/span','/']
        category_news = soup.find("header", class_="jota-article__header")
        category_news = str(category_news).split('p class="jota-article__term"')[1].split("</p>")[0].replace("<","")
        for c in chars:
            category_news = category_news.replace(c,'')

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
        jota_dict["title"].append(title)
        jota_dict["domain"].append(domain)
        jota_dict["source"].append(source)
        jota_dict["date"].append(date)
        jota_dict["body_news"].append(body_new)
        jota_dict["link"].append(url_news)
        jota_dict["category"].append(category_news)
        jota_dict["image"].append(image_new)
        

        print(jota_dict)

        self.__send_queue(title, domain, source, body_new, date, category_news, image_new, url_news)

        return ReturnService(True, 'Sucess')

    def __parse_body(self, body:str) -> VoxradarNewsScrappingJotaQueueDTO:
        body = json.loads(body)
        return VoxradarNewsScrappingJotaQueueDTO(body.get('url'))
    
    def __send_queue(self, title: str, domain: str, source: str, content: str, date: str, category: str, image: str, url: str):
        message_queue:VoxradarNewsSaveDataQueueDTO = VoxradarNewsSaveDataQueueDTO(title, domain, source, content, date, category, image, url)
        
        #self.log(None, 'Send to queue {} | {}'.format(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_FOLHA'], message_queue.to_json()), Log.INFO)

        self.sqs.send_message_queue(Envs.AWS['SQS']['QUEUE']['VOXRADAR_NEWS_SAVE_DATA'], message_queue.__str__())



