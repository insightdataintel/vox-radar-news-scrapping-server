import json
import datetime
from flask import request
import datetime
from src.integration.sqs.sqs import Sqs
from src.types.voxradar_news_save_data_queue_dto import VoxradarNewsSaveDataQueueDTO
from src.types.voxradar_news_scrapping_cnn_brasil_business_queue_dto import VoxradarNewsScrappingCNNBrasilBusinessQueueDTO
from src.utils.utils import Utils
from ..config.envs import Envs
from .base.base_service import BaseService
from ..types.return_service import ReturnService
from bs4 import BeautifulSoup
import unicodedata
import requests


class ScrappingNewsCNNBrasilBusinessService(BaseService):

    sqs: Sqs

    def __init__(self):
        super().__init__()
        # self.log_repository = ViewEstadaoLogRepository()
        # self.s3 = S3()
        self.sqs = Sqs()

    def exec(self, body:str) -> ReturnService:
        self.logger.info(f'\n----- Scrapping News CNN BRasil Service | Init - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")} -----\n')
        cnnbrasil_dict = {'title': [], 'domain':[],'source':[],'date': [], 'body_news': [], 'link': [],'category': [],'image': []}
        voxradar_news_scrapping_cnnbrasil_queue_dto:VoxradarNewsScrappingCNNBrasilBusinessQueueDTO = self.__parse_body(body)
        url_news = voxradar_news_scrapping_cnnbrasil_queue_dto.url
        page = requests.get(url_news).text
        soup = BeautifulSoup(page, 'html.parser')   
    #
    #title
    #
        title = soup.find('meta', property='og:title')
        title = str(title).split('content="')[1].split('" property="')[0]
    #
    #Stardandizing Date
    #
        
        date = soup.find_all("script", type="application/ld+json")
        date = str(date).split('datePublished":')[1].split(', ')[0].split(',"')[0].split('<span')[0].replace('T', ' ').replace('Z', '').\
                replace('"','').replace('h',':').replace('-04:00','').split('+')[0].\
                replace('min','').strip()
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M")
        date = "%s-3:00"%(str(date.strftime('%Y-%m-%d %H:%M:%S')))
    #
    #Pick body's news
    #
    #

        mode = ['div']
        classk = ['post__content']
        paragraf = ['p']
        body_new = ''

        for i in range(0,len(mode)):
            for j in range(0,len(classk)):
                try:
                    yes = soup.find(mode[i], class_ = classk[j])
                    if(len(yes)>0):
                        break
                except:
                    None

                    

        for k in range(0,len(paragraf)):
            try:
                body_news = [x.text for x in soup.find(mode[i],class_ = classk[j]).find_all(paragraf[k]) if len(x.text)>90]
                if(len(body_news)>0):
                    break
            except:
                body_news = [x.text for x in soup.find(mode[i], id = 'textContent').find_all(paragraf[k]) if len(x.text)>90]
                if(len(body_news)>0):
                    break

        body_new = ''

        no_text = ['Cartola','Leia outras','podcast','Foto','clique aqui','Assine o Premiere','VÍDEOS:',\
                    'o app do Yahoo Mail','Assine agora a newsletter','via Getty Images','Fonte: ','O seu endereço de e-mail',\
                    'email protected','Comunicação Social da Polícia','email','Portal iG','nossas newsletters',\
                    'WhatsApp:  As regras de privacidade','de 700 caracteres [0]','pic.twitter.com','(@','Leia também',\
                        '(Reportagem', 'Entre para o grupo do Money Times','Entre agora para o nosso grupo no Telegram!',\
                            'Ilustração: ','Continue lendo no','CONTINUA DEPOIS DA PUBLICIDADE','Assine o 247, apoie por Pix','Leia Também',\
                                'aproveite a tarifa gratuita','Descarregue a nossa App gratuita','Os jogos (e as apostas)',\
                                'Salve meu nome, e-mail neste navegador para a próxima vez que eu comentar','Redatora do portal, possui ',\
                                'Receba diariamente o RD em seu Whatsapp','Confira outras notícias ']
        for x in body_news:
            for item in no_text:
                if item in x:
                    x = ''
            if x=='':
                None
            else:
                body_new = body_new+x+'\n' ##

    #    
    # Pick category news
    #   
        category_news = url_news.replace('https://www.','').split('/')[1]

                
        #
        #
        #
    # Pick image from news
        #
        try:
            ass = soup.find("meta", property='og:image')
            image_new = str(ass).split("content=")[1].split("property=")[0].replace('"','').replace(";",'')
        except:
            image_new = 'None'
        # # #
        # #
        domain = url_news.split(".com")[0]+'.com'
        try:
            source = url_news.split("www.")[1].split(".com")[0]               
        except:
            source = url_news.split("https://")[1].split(".com")[0]               
               
        #
        #
        cnnbrasil_dict["title"].append(title)
        cnnbrasil_dict["domain"].append(domain)
        cnnbrasil_dict["source"].append(source)
        cnnbrasil_dict["date"].append(date)
        cnnbrasil_dict["body_news"].append(body_new)
        cnnbrasil_dict["link"].append(url_news)
        cnnbrasil_dict["category"].append(category_news)
        cnnbrasil_dict["image"].append(image_new)
        

        print(cnnbrasil_dict)

        self.__send_queue(title, domain, source, body_new, date, category_news, image_new, url_news)

        return ReturnService(True, 'Sucess')

    def __parse_body(self, body:str) -> VoxradarNewsScrappingCNNBrasilBusinessQueueDTO:
        body = json.loads(body)
        return VoxradarNewsScrappingCNNBrasilBusinessQueueDTO(body.get('url'))
    
    def __send_queue(self, title: str, domain: str, source: str, content: str, date: str, category: str, image: str, url: str):
        message_queue:VoxradarNewsSaveDataQueueDTO = VoxradarNewsSaveDataQueueDTO(title, domain, source, content, date, category, image, url)
        
        #self.log(None, 'Send to queue {} | {}'.format(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_FOLHA'], message_queue.to_json()), Log.INFO)

        self.sqs.send_message_queue(Envs.AWS['SQS']['QUEUE']['VOXRADAR_NEWS_SAVE_DATA'], message_queue.__str__())



