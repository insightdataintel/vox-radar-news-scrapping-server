from distutils.debug import DEBUG
import json
import os
import argparse
from flask import Flask, jsonify, request
from flask_cors import CORS
from logzero import logger
from src.domain.select_news_estadao_service import SelectNewsEstadaoService
from ..domain.scrapping_news_estadao_service import ScrappingNewsEstadaoService
from src.domain.scrapping_news_folha_service import ScrappingNewsFolhaService
from src.domain.select_news_folha_service import SelectNewsFolhaService
from src.domain.scrapping_news_valor_service import ScrappingNewsValorService
from src.domain.select_news_valor_service import SelectNewsValorService

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

        @app.route("/select-news-estadao")
        def select_news_estadao():
            logger.info("/estadao")
            SelectNewsEstadaoService().exec()
            return "I'm ok"

        @app.route("/scrapping-news-estadao",methods=['POST'])
        def scrapping_news_estadao():
            logger.info("/estadao")
            ScrappingNewsEstadaoService().exec(json.dumps(request.get_json()))
            return "I'm ok"

        @app.route("/select-news-valor")
        def select_news_valor():
            logger.info("/valor")
            SelectNewsValorService().exec()
            return "I'm ok"

        @app.route("/scrapping-news-valor",methods=['POST'])
        def scrapping_news_valor():
            logger.info("/valor")
            ScrappingNewsValorService().exec(json.dumps(request.get_json()))
            return "I'm ok"

        @app.route("/select-news-folha")
        def select_news_folha():
            logger.info("/folha")
            SelectNewsFolhaService().exec()
            return "I'm ok"

        @app.route("/scrapping-news-folha",methods=['POST'])
        def scrapping_news_folha():
            logger.info("/folha")
            ScrappingNewsFolhaService().exec(json.dumps(request.get_json()))
            return "I'm ok"
            
        return app
