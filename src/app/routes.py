from distutils.debug import DEBUG
import json
import os
import argparse
from flask import Flask, jsonify, request
from flask_cors import CORS
from logzero import logger
from src.domain.estadao_select_news_service import EstadaoSelectNewsService
from ..domain.estadao_scrapper_news_service import EstadaoScrapperNewsService
from src.domain.folha_scrapper_news_service import FolhaScrapperNewsService
from src.domain.folha_select_news_service import FolhaSelectNewsService
from src.domain.valor_scrapper_news_service import ValorScrapperNewsService
from src.domain.valor_select_news_service import ValorSelectNewsService

from src.types.return_service import ReturnService
from ..domain.example import ExampleService


class RouteApp():
    
    def create_app(config=None):
        app = Flask(__name__)

        # See http://flask.pocoo.org/docs/latest/config/
        app.config.update(dict(ENV='development', DEBUG=True))
        app.config.update(config or {})

        # Setup cors headers to allow all domains
        # https://flask-cors.readthedocs.io/en/latest/
        CORS(app)

        @app.route("/health")
        def health():
            logger.info("/health")
            return "I'm ok"

        @app.route("/example", methods=['POST'])
        def example():
            logger.info("/example")
            logger.info(request.get_json())

            ExampleService().exec(json.dumps(request.get_json()))
            return "I'm ok"

        @app.route("/estadao-select-news")
        def estadao_select_news():
            logger.info("/estadao")
            #1 extract links
            EstadaoSelectNewsService().exec()
            return "I'm ok"

        @app.route("/estadao-scrapper-news",methods=['POST'])
        def estadao_scrapper_news():
            logger.info("/estadao")
            #2 scrapper news
            EstadaoScrapperNewsService().exec(json.dumps(request.get_json()))
            return "I'm ok"

        @app.route("/valor-select-news")
        def valor_select_news():
            logger.info("/valor")
            #1 extract links
            ValorSelectNewsService().exec()
            return "I'm ok"

        @app.route("/valor-scrapper-news",methods=['POST'])
        def valor_scrapper_news():
            logger.info("/valor")
            #2 scrapper news
            ValorScrapperNewsService().exec(json.dumps(request.get_json()))
            return "I'm ok"

        @app.route("/folha-select-news")
        def folha_select_news():
            logger.info("/folha")
            #1 extract links
            FolhaSelectNewsService().exec()
            return "I'm ok"

        @app.route("/folha-scrapper-news",methods=['POST'])
        def folha_scrapper_news():
            logger.info("/folha")
            #2 scrapper news
            FolhaScrapperNewsService().exec(json.dumps(request.get_json()))
            return "I'm ok"
            
        return app
