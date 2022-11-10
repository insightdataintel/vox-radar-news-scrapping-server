import json
import datetime
from flask import request
import datetime
from src.integration.sqs.sqs import Sqs
from src.types.voxradar_news_save_data_queue_dto import VoxradarNewsSaveDataQueueDTO
from src.types.voxradar_news_scrapping_jornalopcao_queue_dto import VoxradarNewsScrappingJornalOpcaoQueueDTO
from src.utils.utils import Utils
from ..config.envs import Envs
from .base.base_service import BaseService
from ..types.return_service import ReturnService
from bs4 import BeautifulSoup
import unicodedata
import requests


class ScrappingNewsJornalOpcaoService(BaseService):

    sqs: Sqs

    def __init__(self):
        super().__init__()
        # self.log_repository = ViewEstadaoLogRepository()
        # self.s3 = S3()
        self.sqs = Sqs()

    def exec(self, body:str) -> ReturnService:
        self.logger.info(f'\n----- Scrapping News Jornal Opção Service | Init - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")} -----\n')
        jornalopcao_dict = {'title': [], 'domain':[],'source':[],'date': [], 'body_news': [], 'link': [],'category': [],'image': []}
        voxradar_news_scrapping_jornalopcao_queue_dto:VoxradarNewsScrappingJornalOpcaoQueueDTO = self.__parse_body(body)
        url_news = voxradar_news_scrapping_jornalopcao_queue_dto.url
        headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:2.0b10) Gecko/20100101 Firefox/4.0b10"}
        page = requests.get(url_news,headers=headers).text
        soup = BeautifulSoup(page, 'html.parser')     
    #
    #title
    #
        try:
            title = soup.find("meta",attrs={'property': 'og:title'})
            title = str(title).split("meta content=")[1].split("property=")[0].replace('- Jornal Opção','').replace('"','')
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar o título da notícia do Jornal Opcao: {url_news} | {e}")     
            title = ""
    #
    #Stardandizing Date
    #
        try:
            date = soup.find("p", class_='post-date')
            date = str(date).split('"post-date">')[1].split("</p>")[0].replace(':"','').replace('"','').split("+")[0].replace('-','').replace('às','')
            aux = date.split()
            aux[1] = Utils.month_convert(aux[1])
            date = aux[0]+'-'+aux[1]+'-'+aux[2]+ ' ' + aux[3].replace('h',':')+':00'+'-03:00'
    
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar a data da notícia do Jornal Opcao: {url_news} | {e}")
            date = ""    
    #
    #Pick body's news
    #
    #
        try: 
            mode = ['div']
            classk = ['post-content']
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
                    break
                else:
                    x.replace("\n","")
                    body_new=body_new+x+' \n '##                
   

        except Exception as e:
            self.logger.error(f"Não foi possível encontrar o corpo da notícia do Jornal Opcao: {url_news} | {e}")
            return ReturnService(False, 'Did not collect the body of the News')

    # Pick category news
    # 
        category_news = soup.find('span','text')
        category_news = str(category_news).split('text">')[1].split('</span>')[0]
    


        #
        #
        #
    # Pick image from news
        #
        try:
            ass = soup.find("meta", property="og:image")
            image_new = str(ass).split("content=")[1].split(" ")[0].replace('"','').replace(";",'')
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar imagens da notícia do Jornal Opcao: {url_news} | {e}")     
            image_new = "" 
        #
        #
        domain = url_news.split(".br")[0]+'.br'
        source = url_news.split("www.")[1].split(".com")[0]
       
        #
        jornalopcao_dict["title"].append(title)
        jornalopcao_dict["domain"].append(domain)
        jornalopcao_dict["source"].append(source)
        jornalopcao_dict["date"].append(date)
        jornalopcao_dict["body_news"].append(body_new)
        jornalopcao_dict["link"].append(url_news)
        jornalopcao_dict["category"].append(category_news)
        jornalopcao_dict["image"].append(image_new)
        

        print(jornalopcao_dict)

        self.__send_queue(title, domain, source, body_new, date, category_news, image_new, url_news)

        return ReturnService(True, 'Sucess')

    def __parse_body(self, body:str) -> VoxradarNewsScrappingJornalOpcaoQueueDTO:
        body = json.loads(body)
        return VoxradarNewsScrappingJornalOpcaoQueueDTO(body.get('url'))
    
    def __send_queue(self, title: str, domain: str, source: str, content: str, date: str, category: str, image: str, url: str):
        message_queue:VoxradarNewsSaveDataQueueDTO = VoxradarNewsSaveDataQueueDTO(title, domain, source, content, date, category, image, url)
        
        #self.log(None, 'Send to queue {} | {}'.format(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_FOLHA'], message_queue.to_json()), Log.INFO)

        self.sqs.send_message_queue(Envs.AWS['SQS']['QUEUE']['VOXRADAR_NEWS_SAVE_DATA'], message_queue.__str__())



