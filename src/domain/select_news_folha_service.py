import datetime
from src.integration.sqs.sqs import Sqs
from src.types.voxradar_news_scrapping_folha_queue_dto import VoxradarNewsScrappingFolhaQueueDTO
from ..config.envs import Envs
from .base.base_service import BaseService
from ..types.return_service import ReturnService
from bs4 import BeautifulSoup
import requests

class SelectNewsFolhaService(BaseService):
    sqs: Sqs

    def __init__(self):
        super().__init__()
        # self.log_repository = ViewValorLogRepository()
        # self.s3 = S3()
        self.sqs = Sqs()
        

    def exec(self) -> ReturnService:
        self.logger.info(f'\n----- Select News Folha Service | Init - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")} -----\n')
        
        # self.log(None, f"Iniciando scrapping estado de {sigarp_capture_data_folha_scrapping_queue_dto.state}, cidade de {sigarp_capture_data_folha_scrapping_queue_dto.city}, ano {sigarp_capture_data_estadao_scrapping_queue_dto.year}", Log.INFO)

            
        url = "https://www.folha.uol.com.br/"
        
        page = requests.get(url).text

            
        soup = BeautifulSoup(page, 'html.parser')
        links_filtered = []    
        #//Taking links from url
        try:
            domain = url.split(".")[1]+".com"
            links = soup.find_all('a', class_=["c-headline__url","c-main-headline__url"])
            for item in links:
                aux = str(item).split("href=")[1].split(" ")[0].split('>')[0].replace(">","").replace('"','')
                links_filtered.append(aux)
        
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar os Links na página inicial do site Folha | {e}")
        
        links_filtered = list(set(links_filtered))
        print(links_filtered)
        for link in links_filtered:
            self.__send_queue(link)

        return ReturnService(True, 'Sucess')

        
    def __send_queue(self, url:str):
        message_queue:VoxradarNewsScrappingFolhaQueueDTO = VoxradarNewsScrappingFolhaQueueDTO(url)
        
        #self.log(None, 'Send to queue {} | {}'.format(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_FOLHA'], sigarp_save_data_folha_dto.to_json()), Log.INFO)

        self.sqs.send_message_queue(Envs.AWS['SQS']['QUEUE']['VOXRADAR_NEWS_SCRAPPING_FOLHA'], message_queue.__str__())

