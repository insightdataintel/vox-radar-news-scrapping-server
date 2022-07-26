import datetime
from src.integration.sqs.sqs import Sqs
from src.types.voxradar_news_scrapping_otempo_supernoticia_queue_dto import VoxradarNewsScrappingOtemposupernoticiaQueueDTO
from src.utils.utils import Utils
from ..config.envs import Envs
from .base.base_service import BaseService
from ..types.return_service import ReturnService

class SelectNewsOtemposupernoticiaService(BaseService):
    sqs: Sqs

    def __init__(self):
        super().__init__()
        # self.log_repository = ViewValorLogRepository()
        # self.s3 = S3()
        self.sqs = Sqs()
        

    def exec(self) -> ReturnService:
        self.logger.info(f'\n----- Select News Otempo Supernoticia Service | Init - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")} -----\n')
        
        # self.log(None, f"Iniciando scrapping estado de {sigarp_capture_data_estadao_scrapping_queue_dto.state}, cidade de {sigarp_capture_data_estadao_scrapping_queue_dto.city}, ano {sigarp_capture_data_estadao_scrapping_queue_dto.year}", Log.INFO)

            
        url = "https://www.otempo.com.br/super-noticia/"
        
        links_filtered = Utils.extract_links_from_page(url)
                    
        print(links_filtered)
        for link in links_filtered:
            self.__send_queue(link)

        return ReturnService(True, 'Sucess')

        
    def __send_queue(self, url:str):
        message_queue:VoxradarNewsScrappingOtemposupernoticiaQueueDTO = VoxradarNewsScrappingOtemposupernoticiaQueueDTO(url)
        
        #self.log(None, 'Send to queue {} | {}'.format(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_VALOR'], sigarp_save_data_valor_dto.to_json()), Log.INFO)

        self.sqs.send_message_queue(Envs.AWS['SQS']['QUEUE']['VOXRADAR_NEWS_SCRAPPING_VALOR'], message_queue.__str__())



