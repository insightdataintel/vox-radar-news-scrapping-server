import json
import datetime
from flask import request
import datetime
from src.integration.sqs.sqs import Sqs
from src.types.voxradar_news_save_data_queue_dto import VoxradarNewsSaveDataQueueDTO
from src.types.voxradar_news_scrapping_r7_internacional_queue_dto import VoxradarNewsScrappingR7InternacionalQueueDTO
from src.utils.utils import Utils
from ..config.envs import Envs
from .base.base_service import BaseService
from ..types.return_service import ReturnService
from bs4 import BeautifulSoup
import unicodedata
import requests


class ScrappingNewsR7InternacionalService(BaseService):

    sqs: Sqs

    def __init__(self):
        super().__init__()
        # self.log_repository = ViewEstadaoLogRepository()
        # self.s3 = S3()
        self.sqs = Sqs()

    def exec(self, body:str) -> ReturnService:
        self.logger.info(f'\n----- Scrapping News R7 Internacional Service | Init - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")} -----\n')
        r7_dict = {'title': [], 'domain':[],'source':[],'date': [], 'body_news': [], 'link': [],'category': [],'image': []}
        voxradar_news_scrapping_r7_internacional_queue_dto:VoxradarNewsScrappingR7InternacionalQueueDTO = self.__parse_body(body)
        url_news = voxradar_news_scrapping_r7_internacional_queue_dto.url
        headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:2.0b10) Gecko/20100101 Firefox/4.0b10"}
        page = requests.get(url_news,headers=headers).text
        soup = BeautifulSoup(page, 'html.parser')     
    #
    #title
    #
        try:
            title = soup.find("meta", attrs={'property': 'og:title'})
            title = str(title).split("content=")[1].split("property=")[0].replace('"','')
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar o título da notícia do Folha de São Paulo: {url_news} | {e}")     
            title = ""
    #
    #Stardandizing Date
    #
        try:
            try:
                date = soup.find("meta", attrs={'property': 'article:published_time'})
                date = str(date).split('meta content=')[1].split("property=")[0].replace(':"','').replace('"','').split("+")[0]
                date = date.replace('T', ' ') 
            except:
                date = soup.find("div", class_= "dataPublicacaoPost float-left mr-5")
                date = str(date).split('Atualizado em')[1].split("<")[0].replace(':"','').replace('"','').split("+")[0].replace('h',':').replace('-','')
                date = date.split()
                date[1] = Utils.month_convert(date[1])
                date = "-".join(date)+':00'+'-03:00'
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar a data da notícia do Folha de São Paulo: {url_news} | {e}")
            date = ""    
    #
    #Pick body's news
    #
    #
        try: 
            body_new = ''
            mode = ['article', 'div']
            classk = ['toolkit-media-content','offset-md-2 col-md-8 postagem','entry-content materia','entry-content','single-container','texto',\
                    'td_block_wrap tdb_single_content tdi_87 td-pb-border-top conteudo-post td_block_template_8 td-post-content tagdiv-type',\
                    'mvp-post-soc-out right relative']

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
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar o corpo da notícia do Folha de São Paulo: {url_news} | {e}")
            return ReturnService(False, 'Did not collect the body of the News')

    # Pick category news
    # 
        category_news = 'tecnologia e ciencia'

        #
        #
        #
    # Pick image from news
        #
        try:
            ass = soup.find("meta", property="og:image")
            image_new = str(ass).split("content=")[1].split(" ")[0].replace('"','')
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar imagens da notícia do Folha de São Paulo: {url_news} | {e}")     
            image_new = ""
        #
        domain = url_news.split("://")[1].split("/")[0]
        source = domain.split(".")[0]        #
        #
        r7_dict["title"].append(title)
        r7_dict["domain"].append(domain)
        r7_dict["source"].append(source)
        r7_dict["date"].append(date)
        r7_dict["body_news"].append(body_new)
        r7_dict["link"].append(url_news)
        r7_dict["category"].append(category_news)
        r7_dict["image"].append(image_new)
        

        print(r7_dict)

        self.__send_queue(title, domain, source, body_new, date, category_news, image_new, url_news)

        return ReturnService(True, 'Sucess')

    def __parse_body(self, body:str) -> VoxradarNewsScrappingR7InternacionalQueueDTO:
        body = json.loads(body)
        return VoxradarNewsScrappingR7InternacionalQueueDTO(body.get('url'))
    
    def __send_queue(self, title: str, domain: str, source: str, content: str, date: str, category: str, image: str, url: str):
        message_queue:VoxradarNewsSaveDataQueueDTO = VoxradarNewsSaveDataQueueDTO(title, domain, source, content, date, category, image, url)
        
        #self.log(None, 'Send to queue {} | {}'.format(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_FOLHA'], message_queue.to_json()), Log.INFO)

        self.sqs.send_message_queue(Envs.AWS['SQS']['QUEUE']['VOXRADAR_NEWS_SAVE_DATA'], message_queue.__str__())



