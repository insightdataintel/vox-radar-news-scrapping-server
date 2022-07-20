import datetime
from src.integration.sqs.sqs import Sqs
from src.types.voxradar_news_scrapping_folha_queue_dto import VoxradarNewsScrappingFolhaQueueDTO
from ..config.envs import Envs
from .base.base_service import BaseService
from ..types.return_service import ReturnService
from bs4 import BeautifulSoup
import requests
import discord
import os
from dotenv import load_dotenv
import asyncio
from discord.ext import commands






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

###ainda estamos com problemas....
        # TOKEN = 'OTkzNTAyNzM0NTAwMjQ5NjYw.G-6Gwu.9KLt62IcPtmlNG9CebPQibQK4PmXWFIngl4t2g'
        # TOKEN2 = 'OTkzNjAwMDQzNjE5NzE3MTQw.GuRHBE.bt5RrnkeN8qjQBIfvESCF2MzScFduw6a9yVWuk'
        # GUILD = 993563167584170075
        # client = discord.Client()

        # @client.event
        # async def on_ready():  #  Called when internal cache is loaded
        #     print('We have logged in as {0.user}'.format(client))

        #     #async def on_message():
        #     channel = client.get_channel(GUILD) #  Gets channel from internal cache
        #     await channel.send("hello world testing from server") #  Sends message to channel      

        # client.run(TOKEN)
        

        return ReturnService(True, 'Sucess')

        
    def __send_queue(self, url:str):
        message_queue:VoxradarNewsScrappingFolhaQueueDTO = VoxradarNewsScrappingFolhaQueueDTO(url)
        
        #self.log(None, 'Send to queue {} | {}'.format(Envs.AWS['SQS']['QUEUE']['SIGARP_SAVE_DATA_FOLHA'], sigarp_save_data_folha_dto.to_json()), Log.INFO)

        self.sqs.send_message_queue(Envs.AWS['SQS']['QUEUE']['VOXRADAR_NEWS_SCRAPPING_FOLHA'], message_queue.__str__())

