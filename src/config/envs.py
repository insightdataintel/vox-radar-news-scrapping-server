import os
import json

from ..utils.utils import Utils
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv()
 
file = open('src/config/queues.json')
data = json.load(file)

voxradar_news_scrapping_estadao = data['VOXRADAR_NEWS_SCRAPPING_ESTADAO'] + Utils.get_queue_suffix_by_environment(os.environ.get('ENVIRONMENT'))
voxradar_news_scrapping_folha = data['VOXRADAR_NEWS_SCRAPPING_FOLHA'] + Utils.get_queue_suffix_by_environment(os.environ.get('ENVIRONMENT'))
voxradar_news_scrapping_valor = data['VOXRADAR_NEWS_SCRAPPING_VALOR'] + Utils.get_queue_suffix_by_environment(os.environ.get('ENVIRONMENT'))
voxradar_news_scrapping_folha_emcimadahora = data['VOXRADAR_NEWS_SCRAPPING_FOLHA_EMCIMADAHORA'] + Utils.get_queue_suffix_by_environment(os.environ.get('ENVIRONMENT'))
voxradar_news_save_data = data['VOXRADAR_NEWS_SAVE_DATA'] + Utils.get_queue_suffix_by_environment(os.environ.get('ENVIRONMENT'))

file.close()

class Envs:
  ENVIRONMENT = os.environ.get('ENVIRONMENT'),
  DATABASE = {
    "LOGGING": os.environ.get('DATABASE_LOGGING'),
    "READ": {
      "NAME": os.environ.get('DATABASE_READ_NAME'),
      "USER": os.environ.get('DATABASE_READ_USER'),
      "PASSWORD": os.environ.get('DATABASE_READ_PASSWORD'),
      "HOST": os.environ.get('DATABASE_READ_HOST'),
      "PORT": os.environ.get('DATABASE_READ_PORT'),
    },
    "WRITE": {
      "NAME": os.environ.get('DATABASE_WRITE_NAME'),
      "USER": os.environ.get('DATABASE_WRITE_USER'),
      "PASSWORD": os.environ.get('DATABASE_WRITE_PASSWORD'),
      "HOST": os.environ.get('DATABASE_WRITE_HOST'),
      "PORT": os.environ.get('DATABASE_WRITE_PORT'),
    }
  }
  ROLLBAR = {
    "KEY": os.environ.get('ROLLBAR_KEY')
  }
  AWS = {
    "ACCOUNT_ID": os.environ.get('AWS_ACCOUNT_ID'),
    "SQS": {
      "KEY": os.environ.get('AWS_SQS_KEY'),
      "SECRET": os.environ.get('AWS_SQS_SECRET'),
      "REGION": os.environ.get('AWS_SQS_REGION'),
      "URL": os.environ.get('AWS_SQS_URL'),
      "QUEUE": {
        "VOXRADAR_NEWS_SCRAPPING_ESTADAO": voxradar_news_scrapping_estadao,
        "VOXRADAR_NEWS_SCRAPPING_FOLHA": voxradar_news_scrapping_folha,
        "VOXRADAR_NEWS_SCRAPPING_VALOR": voxradar_news_scrapping_valor,
        "VOXRADAR_NEWS_SCRAPPING_FOLHA_EMCIMADAHORA": voxradar_news_scrapping_folha_emcimadahora,
        "VOXRADAR_NEWS_SAVE_DATA": voxradar_news_save_data
      }
    },
    "S3": {
      "KEY": os.environ.get('AWS_S3_KEY'),
      "SECRET": os.environ.get('AWS_S3_SECRET')
    }
  }
  REDIS = {
    "HOST": os.environ.get('REDIS_HOST'),
    "PORT": os.environ.get('REDIS_PORT'),
    "HAS_AUTHENTICATION": os.environ.get('REDIS_HAS_AUTHENTICATION'),
    "PASSWORD": os.environ.get('REDIS_PASSWORD')
  }
