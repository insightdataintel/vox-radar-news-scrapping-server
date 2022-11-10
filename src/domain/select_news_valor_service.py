import datetime
from src.integration.sqs.sqs import Sqs
from src.types.voxradar_news_scrapping_valor_queue_dto import VoxradarNewsScrappingValorQueueDTO
from ..config.envs import Envs
from .base.base_service import BaseService
from ..types.return_service import ReturnService
from bs4 import BeautifulSoup
from src.utils.utils import Utils
import requests

class SelectNewsValorService(BaseService):
    sqs: Sqs

    def __init__(self):
        super().__init__()
        # self.log_repository = ViewValorLogRepository()
        # self.s3 = S3()
        self.sqs = Sqs()
        

    def exec(self) -> ReturnService:
        self.logger.info(f'\n----- Select News Valor Service | Init - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")} -----\n')
        
        # self.log(None, f"Iniciando scrapping estado de {sigarp_capture_data_estadao_scrapping_queue_dto.state}, cidade de {sigarp_capture_data_estadao_scrapping_queue_dto.city}, ano {sigarp_capture_data_estadao_scrapping_queue_dto.year}", Log.INFO)

            
        url = "https://valor.globo.com/ultimas-noticias/"    
        soup = Utils.request_link(url)
        links = soup.find_all('div', class_='feed-post-body')
        no_text = ['/amp-stories/','/jogo/','/story/', 'noopener','mail','search','rapidnofollow','noopener ','Notícias</a>','Esportes</a>',\
                'Finanças</a>','Vida e Estilo</a>','Celebridades</a>','Cinema</a>','Mobile</a>','BOVESPA</a>','MERVAL</a>','quote','category/',\
                '/web-stories/','/enquetes/','instagram/','comscore','gbrcomponentes','instagram.','bit.ly','digitalaudit.ivcbrasil','amazonasdireito.com.br','taxonomy',\
                    'videojs.com/','turismo-0','facebook.com','campograndenews','https://twitter.com','ultimas-noticias','#',\
                    'wa.me/','mais-lidas','/ultimas-noticias/tag/','secure.']


        links_filteredauxa = []
        links_filteredauxb  =[]
        links_filtered = []

        try:
            for link in links:
                auxa = link.find('a',href=True)
                links_filteredauxa.append(str(auxa))
            links_filteredauxa = list(set(links_filteredauxa))

            # # # # # # # # 

            links_filteredauxa = str(links).split('href=')
            for i in range(1,len(links_filteredauxa)):
                auxb = links_filteredauxa[i].split('">')[0].replace('"','').strip()
                for item in no_text:
                    if item in links_filteredauxa[i]:
                        auxb = ''
                if auxb== '':
                    None
                else:
                    links_filteredauxb.append(auxb)

            temp = ''
            links_filteredauxb = list(set(links_filteredauxb))
            for i in range(0,len(links_filteredauxb)):
                for j in range(1,len(links_filteredauxb)):
                    if str(links_filteredauxb[i]) in str(links_filteredauxb[j]):
                        temp = links_filteredauxb[j]

                if temp == '':
                    None
                else:            
                    links_filtered.append(temp)

        except Exception as e:
            self.logger.error(f"Não foi possível encontrar os Links na página inicial do site valor | {e}")

        print(links_filtered)
        for link in links_filtered:
            self.__send_queue(link)

        return ReturnService(True, 'Sucess')

        
    def __send_queue(self, url:str):
        message_queue:VoxradarNewsScrappingValorQueueDTO = VoxradarNewsScrappingValorQueueDTO(url)
        
        #self.log(None, 'Send to queue {} | {}'.format(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_VALOR'], sigarp_save_data_valor_dto.to_json()), Log.INFO)

        self.sqs.send_message_queue(Envs.AWS['SQS']['QUEUE']['VOXRADAR_NEWS_SCRAPPING_VALOR'], message_queue.__str__())



