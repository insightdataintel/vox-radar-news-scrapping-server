import datetime
from src.integration.sqs.sqs import Sqs
from src.types.voxradar_news_scrapping_estadao_queue_dto import VoxradarNewsScrappingEstadaoQueueDTO
from ..config.envs import Envs
from .base.base_service import BaseService
from ..types.return_service import ReturnService
from bs4 import BeautifulSoup
import numpy as np
import requests

class SelectNewsEstadaoService(BaseService):
    sqs: Sqs

    def __init__(self):
        super().__init__()
        # self.log_repository = ViewEstadaoLogRepository()
        # self.s3 = S3()
        self.sqs = Sqs()

    def exec(self) -> ReturnService:
        self.logger.info(f'\n----- Select News Estadao Service | Init - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")} -----\n')
        
        # self.log(None, f"Iniciando scrapping estado de {sigarp_capture_data_estadao_scrapping_queue_dto.state}, cidade de {sigarp_capture_data_estadao_scrapping_queue_dto.city}, ano {sigarp_capture_data_estadao_scrapping_queue_dto.year}", Log.INFO)

        url = "https://www.estadao.com.br/ultimas"
        
        page = requests.get(url).text

        soup = BeautifulSoup(page, 'html.parser')    
        #//Taking links from url
        try:
            domain = url.split(".")[1]+".com"
            links = soup.find_all('a', href=True)
            links = [link["href"] for link in links if domain in link["href"][:len(url)] ]
            len_link = [len(link.split("/")) for link in links]
            len_max = np.array(len_link).max()
            links_news = [link for link in links if len(link.split("/"))==len_max]
            links_filtered = []
            blocking = ['portal_estadao_selo_acesso', 'einvestidor.', 'emais.', 'paladar.']  
            for link in links_news:
                present = False
                for word in blocking:
                    if word in link:
                        present = True
                if present is False:
                    links_filtered.append(link)
        except Exception as e:
            self.logger.error(f"Não foi possível encontrar os Links na página inicial do site Estadão | {e}")
            return ReturnService(False, "Error")
        
        links_filtered = list(set(links_filtered))
        print(links_filtered)
        for link in links_filtered:
            self.__send_queue(link)

        return ReturnService(True, 'Sucess')

    def __send_queue(self, url:str):
        message_queue:VoxradarNewsScrappingEstadaoQueueDTO = VoxradarNewsScrappingEstadaoQueueDTO(url)
        
        #self.log(None, 'Send to queue {} | {}'.format(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_ESTADAO'], sigarp_save_data_estadao_dto.to_json()), Log.INFO)

        self.sqs.send_message_queue(Envs.AWS['SQS']['QUEUE']['VOXRADAR_NEWS_SCRAPPING_ESTADAO'], message_queue.__str__())


