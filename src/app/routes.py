from distutils.debug import DEBUG
import json
import os
import argparse
from flask import Flask, jsonify, request
from flask_cors import CORS
from logzero import logger
from src.domain.scrapping_news_aredacao_service import ScrappingNewsARedacaoService
from src.domain.scrapping_news_broadcast_agro_service import ScrappingNewsBroadcastAgroService
from src.domain.scrapping_news_correio24horas_service import ScrappingNewsCorreio24horasService
from src.domain.scrapping_news_correiobraziliense_service import ScrappingNewsCorreioBrazilienseService
from src.domain.scrapping_news_diariodamanha_service import ScrappingNewsDiariodaManhaService
from src.domain.scrapping_news_dinheiro_rural_service import ScrappingNewsDinheiroRuralService
from src.domain.scrapping_news_folha_uol_emcimadahora_service import ScrappingNewsFolhaEmcimadahoraService
from src.domain.scrapping_news_folhaz_service import ScrappingNewsFolhaZService
from src.domain.scrapping_news_globo_g1_service import ScrappingNewsGloboG1Service
from src.domain.scrapping_news_globo_valor_service import ScrappingNewsGloboValorService
from src.domain.scrapping_news_istoe_service import ScrappingNewsIstoeService
from src.domain.scrapping_news_jornalahora_service import ScrappingNewsJornalAHoraService
from src.domain.scrapping_news_jornalopcao_service import ScrappingNewsJornalOpcaoService
from src.domain.scrapping_news_jota_service import ScrappingNewsJotaService
from src.domain.scrapping_news_maisgoias_service import ScrappingNewsMaisGoiasService
from src.domain.scrapping_news_metropoles_service import ScrappingNewsMetropolesService
from src.domain.scrapping_news_oantagonista_service import ScrappingNewsOAntagonistaService
from src.domain.scrapping_news_ohoje_service import ScrappingNewsOHojeService
from src.domain.scrapping_news_opopular_service import ScrappingNewsOPopularService
from src.domain.scrapping_news_opovo_noticias_service import ScrappingNewsOpovoNoticiasService
from src.domain.scrapping_news_otempo_supernoticia_service import ScrappingNewsOtemposupernoticiaService
from src.domain.scrapping_news_r7_agronegocios_service import ScrappingNewsR7AgronegociosService
from src.domain.scrapping_news_r7_brasilia_service import ScrappingNewsR7BrasiliaService
from src.domain.scrapping_news_r7_economia_service import ScrappingNewsR7EconomiaService
from src.domain.scrapping_news_r7_educacao_service import ScrappingNewsR7EducacaoService
from src.domain.scrapping_news_r7_internacional_service import ScrappingNewsR7InternacionalService
from src.domain.scrapping_news_r7_politica_service import ScrappingNewsR7PoliticaService
from src.domain.scrapping_news_r7_saude_service import ScrappingNewsR7SaudeService
from src.domain.scrapping_news_r7_tecnologiaeciencia_service import ScrappingNewsR7TecnologiaecienciaService
from src.domain.scrapping_news_sagres_service import ScrappingNewsSagresService
from src.domain.scrapping_news_tribunadoplanalto_service import ScrappingNewsTribunadoPlanaltoService
from src.domain.scrapping_news_uol_economia_service import ScrappingNewsUolEconomiaService
from src.domain.scrapping_news_uol_noticias_service import ScrappingNewsUolNoticiasService
from src.domain.select_news_aredacao_service import SelectNewsARedacaoService
from src.domain.select_news_broadcast_agro_service import SelectNewsBroadcastAgroService
from src.domain.select_news_correio24horas_service import SelectNewsCorreio24horasService
from src.domain.select_news_correiobraziliense_service import SelectNewsCorreioBrazilienseService
from src.domain.select_news_diariodamanha_service import SelectNewsDiariodaManhaService
from src.domain.select_news_dinheiro_rural_service import SelectNewsDinheiroRuralService
from src.domain.select_news_estadao_service import SelectNewsEstadaoService
from src.domain.select_news_folha_uol_emcimadahora_service import SelectNewsFolhaEmcimadahoraService
from src.domain.select_news_folhaz_service import SelectNewsFolhaZService
from src.domain.select_news_globog1_service import SelectNewsGloboG1Service
from src.domain.select_news_globovalor_service import SelectNewsGloboValorService
from src.domain.select_news_istoe_service import SelectNewsIstoeService
from src.domain.select_news_jornalahora_service import SelectNewsJornalAHoraService
from src.domain.select_news_jornalopcao_service import SelectNewsJornalOpcaoService
from src.domain.select_news_jota_service import SelectNewsJotaService
from src.domain.select_news_maisgoias_service import SelectNewsMaisGoiasService
from src.domain.select_news_metropoles_service import SelectNewsMetropolesService
from src.domain.select_news_oantagonista_service import SelectNewsOAntagonistaService
from src.domain.select_news_ohoje_service import SelectNewsOHojeService
from src.domain.select_news_opopular_service import SelectNewsOPopularService
from src.domain.select_news_opovonoticias_service import SelectNewsOpovoNoticiasService
from src.domain.select_news_otempo_supernoticia_service import SelectNewsOtemposupernoticiaService
from src.domain.select_news_r7_agronegocios_service import SelectNewsR7AgronegociosService
from src.domain.select_news_r7_brasilia_service import SelectNewsR7BrasiliaService
from src.domain.select_news_r7_economia_service import SelectNewsR7EconomiaService
from src.domain.select_news_r7_educacao_service import SelectNewsR7EducacaoService
from src.domain.select_news_r7_internacional_service import SelectNewsR7InternacionalService
from src.domain.select_news_r7_politica_service import SelectNewsR7PoliticaService
from src.domain.select_news_r7_saude_service import SelectNewsR7SaudeService
from src.domain.select_news_r7_tecnologiaeciencia_service import SelectNewsR7TecnologiaecienciaService
from src.domain.select_news_sagres_service import SelectNewsSagresService
from src.domain.select_news_tribunadoplanalto_service import SelectNewsTribunadoPlanaltoService
from src.domain.select_news_uol_economia_service import SelectNewsUolEconomiaService
from src.domain.select_news_uol_noticias_service import SelectNewsUolNoticiasService
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

        @app.route("/select-news-folha-uol-emcimadahora")
        def select_news_folha_uol_emcimadahora():
            logger.info("/folha-uol-emcimadahora")
            SelectNewsFolhaEmcimadahoraService().exec()
            return "I'm ok"

        @app.route("/scrapping-news-folha-uol-emcimadahora",methods=['POST'])
        def scrapping_news_folha_uol_emcimadahora():
            logger.info("/folha-uol-emcimadahora")
            ScrappingNewsFolhaEmcimadahoraService().exec(json.dumps(request.get_json()))
            return "I'm ok"

        @app.route("/select-news-uol-economia")
        def select_news_uol_economia():
            logger.info("/uol-economia")
            SelectNewsUolEconomiaService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-uol-economia",methods=['POST'])
        def scrapping_news_uol_economia():
            logger.info("/uol-economia")
            ScrappingNewsUolEconomiaService().exec(json.dumps(request.get_json()))
            return "I'm ok"

        @app.route("/select-news-uol-noticias")
        def select_news_uol_noticias():
            logger.info("/uol-noticias")
            SelectNewsUolNoticiasService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-uol-noticias",methods=['POST'])
        def scrapping_news_uol_noticias():
            logger.info("/uol-noticias")
            ScrappingNewsUolNoticiasService().exec(json.dumps(request.get_json()))
            return "I'm ok"
        
        @app.route("/select-news-globo-valor")
        def select_news_globo_valor():
            logger.info("/globo-valor")
            SelectNewsGloboValorService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-globo-valor",methods=['POST'])
        def scrapping_news_globo_valor():
            logger.info("/globo-valor")
            ScrappingNewsGloboValorService().exec(json.dumps(request.get_json()))
            return "I'm ok"
                        
        @app.route("/select-news-globo-g1")
        def select_news_globo_g1():
            logger.info("/globo-g1")
            SelectNewsGloboG1Service().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-globo-g1",methods=['POST'])
        def scrapping_news_globo_g1():
            logger.info("/globo-g1")
            ScrappingNewsGloboG1Service().exec(json.dumps(request.get_json()))
            return "I'm ok"     

        @app.route("/select-news-r7-politica")
        def select_news_r7_politica():
            logger.info("/r7-politica")
            SelectNewsR7PoliticaService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-r7-politica",methods=['POST'])
        def scrapping_news_r7_politica():
            logger.info("/r7-politica")
            ScrappingNewsR7PoliticaService().exec(json.dumps(request.get_json()))
            return "I'm ok"                                  
            
        @app.route("/select-news-r7-economia")
        def select_news_r7_economia():
            logger.info("/r7-economia")
            SelectNewsR7EconomiaService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-r7-economia",methods=['POST'])
        def scrapping_news_r7_economia():
            logger.info("/r7-economia")
            ScrappingNewsR7EconomiaService().exec(json.dumps(request.get_json()))
            return "I'm ok"    

        @app.route("/select-news-r7-agronegocios")
        def select_news_r7_agronegocios():
            logger.info("/r7-agronegocios")
            SelectNewsR7AgronegociosService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-r7-agronegocios",methods=['POST'])
        def scrapping_news_r7_agronegocios():
            logger.info("/r7-agronegocios")
            ScrappingNewsR7AgronegociosService().exec(json.dumps(request.get_json()))
            return "I'm ok"  
                        
        @app.route("/select-news-r7-tecnologiaeciencia")
        def select_news_r7_tecnologiaeciencia():
            logger.info("/r7-tecnologiaeciencia")
            SelectNewsR7TecnologiaecienciaService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-r7-tecnologiaeciencia",methods=['POST'])
        def scrapping_news_r7_tecnologiaeciencia():
            logger.info("/r7-tecnologiaeciencia")
            ScrappingNewsR7TecnologiaecienciaService().exec(json.dumps(request.get_json()))
            return "I'm ok"  


        @app.route("/select-news-r7-saude")
        def select_news_r7_saude():
            logger.info("/r7-saude")
            SelectNewsR7SaudeService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-r7-saude",methods=['POST'])
        def scrapping_news_r7_saude():
            logger.info("/r7-saude")
            ScrappingNewsR7SaudeService().exec(json.dumps(request.get_json()))
            return "I'm ok"  

        @app.route("/select-news-r7-brasilia")
        def select_news_r7_brasilia():
            logger.info("/r7-brasilia")
            SelectNewsR7BrasiliaService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-r7-brasilia",methods=['POST'])
        def scrapping_news_r7_brasilia():
            logger.info("/r7-brasilia")
            ScrappingNewsR7BrasiliaService().exec(json.dumps(request.get_json()))
            return "I'm ok"              

        @app.route("/select-news-r7-internacional")
        def select_news_r7_internacional():
            logger.info("/r7-internacional")
            SelectNewsR7InternacionalService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-r7-internacional",methods=['POST'])
        def scrapping_news_r7_internacional():
            logger.info("/r7-internacional")
            ScrappingNewsR7InternacionalService().exec(json.dumps(request.get_json()))
            return "I'm ok"              

        @app.route("/select-news-r7-educacao")
        def select_news_r7_educacao():
            logger.info("/r7-educacao")
            SelectNewsR7EducacaoService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-r7-educacao",methods=['POST'])
        def scrapping_news_r7_educacao():
            logger.info("/r7-educacao")
            ScrappingNewsR7EducacaoService().exec(json.dumps(request.get_json()))
            return "I'm ok"      

        @app.route("/select-news-jota")
        def select_news_jota():
            logger.info("/jota")
            SelectNewsJotaService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-jota",methods=['POST'])
        def scrapping_news_jota():
            logger.info("/jota")
            ScrappingNewsJotaService().exec(json.dumps(request.get_json()))
            return "I'm ok"  


        @app.route("/select-news-otempo-supernoticia")
        def select_news_otempo_supernoticia():
            logger.info("/otempo-supernoticia")
            SelectNewsOtemposupernoticiaService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-otempo-supernoticia",methods=['POST'])
        def scrapping_news_otempo_supernoticia():
            logger.info("/otempo-supernoticia")
            ScrappingNewsOtemposupernoticiaService().exec(json.dumps(request.get_json()))
            return "I'm ok"  

        @app.route("/select-news-opovo-noticias")
        def select_news_opovo_noticias():
            logger.info("/opovo-noticias")
            SelectNewsOpovoNoticiasService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-opovo-noticias",methods=['POST'])
        def scrapping_news_opovo_noticias():
            logger.info("/opovo-noticias")
            ScrappingNewsOpovoNoticiasService().exec(json.dumps(request.get_json()))
            return "I'm ok"  

        @app.route("/select-news-correio24horas")
        def select_news_correio24horas():
            logger.info("/correio24horas")
            SelectNewsCorreio24horasService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-correio24horas",methods=['POST'])
        def scrapping_news_correio24horas():
            logger.info("/correio24horas")
            ScrappingNewsCorreio24horasService().exec(json.dumps(request.get_json()))
            return "I'm ok"  

        @app.route("/select-news-correio-braziliense")
        def select_news_correio_braziliense():
            logger.info("/correio-braziliense")
            SelectNewsCorreioBrazilienseService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-correio-braziliense",methods=['POST'])
        def scrapping_news_correio_braziliense():
            logger.info("/correio-braziliense")
            ScrappingNewsCorreioBrazilienseService().exec(json.dumps(request.get_json()))
            return "I'm ok" 


        @app.route("/select-news-oantagonista")
        def select_news_oantagonista():
            logger.info("/oantagonista")
            SelectNewsOAntagonistaService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-oantagonista",methods=['POST'])
        def scrapping_news_oantagonista():
            logger.info("/oantagonista")
            ScrappingNewsOAntagonistaService().exec(json.dumps(request.get_json()))
            return "I'm ok" 

        @app.route("/select-news-metropoles")
        def select_news_metropoles():
            logger.info("/metropoles")
            SelectNewsMetropolesService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-metropoles",methods=['POST'])
        def scrapping_news_metropoles():
            logger.info("/metropoles")
            ScrappingNewsMetropolesService().exec(json.dumps(request.get_json()))
            return "I'm ok"             


        @app.route("/select-news-broadcast-agro")
        def select_news_broadcast_agro():
            logger.info("/broadcast-agro")
            SelectNewsBroadcastAgroService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-broadcast-agro",methods=['POST'])
        def scrapping_news_broadcast_agro():
            logger.info("/broadcast-agro")
            ScrappingNewsBroadcastAgroService().exec(json.dumps(request.get_json()))
            return "I'm ok"             

        @app.route("/select-news-dinheiro-rural")
        def select_news_dinheiro_rural():
            logger.info("/dinheiro-rural")
            SelectNewsDinheiroRuralService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-dinheiro-rural",methods=['POST'])
        def scrapping_news_dinheiro_rural():
            logger.info("/dinheiro-rural")
            ScrappingNewsDinheiroRuralService().exec(json.dumps(request.get_json()))
            return "I'm ok"             

        @app.route("/select-news-istoe")
        def select_news_istoe():
            logger.info("/istoe")
            SelectNewsIstoeService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-istoe",methods=['POST'])
        def scrapping_news_istoe():
            logger.info("/istoe")
            ScrappingNewsIstoeService().exec(json.dumps(request.get_json()))
            return "I'm ok"   


        @app.route("/select-news-aredacao")
        def select_news_aredacao():
            logger.info("/aredacao")
            SelectNewsARedacaoService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-aredacao",methods=['POST'])
        def scrapping_news_aredacao():
            logger.info("/aredacao")
            ScrappingNewsARedacaoService().exec(json.dumps(request.get_json()))
            return "I'm ok"   

        @app.route("/select-news-maisgoias")
        def select_news_maisgoias():
            logger.info("/maisgoias")
            SelectNewsMaisGoiasService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-maisgoias",methods=['POST'])
        def scrapping_news_maisgoias():
            logger.info("/maisgoias")
            ScrappingNewsMaisGoiasService().exec(json.dumps(request.get_json()))
            return "I'm ok"             


        @app.route("/select-news-jornalahora")
        def select_news_jornalahora():
            logger.info("/jornalahora")
            SelectNewsJornalAHoraService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-jornalahora",methods=['POST'])
        def scrapping_news_jornalahora():
            logger.info("/jornalahora")
            ScrappingNewsJornalAHoraService().exec(json.dumps(request.get_json()))
            return "I'm ok" 
            
        @app.route("/select-news-tribunadoplanalto")
        def select_news_tribunadoplanalto():
            logger.info("/tribunadoplanalto")
            SelectNewsTribunadoPlanaltoService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-tribunadoplanalto",methods=['POST'])
        def scrapping_news_tribunadoplanalto():
            logger.info("/tribunadoplanalto")
            ScrappingNewsTribunadoPlanaltoService().exec(json.dumps(request.get_json()))
            return "I'm ok"   

        @app.route("/select-news-diariodamanha")
        def select_news_diariodamanha():
            logger.info("/diariodamanha")
            SelectNewsDiariodaManhaService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-diariodamanha",methods=['POST'])
        def scrapping_news_diariodamanha():
            logger.info("/diariodamanha")
            ScrappingNewsDiariodaManhaService().exec(json.dumps(request.get_json()))
            return "I'm ok"             


        @app.route("/select-news-folhaz")
        def select_news_folhaz():
            logger.info("/folhaz")
            SelectNewsFolhaZService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-folhaz",methods=['POST'])
        def scrapping_news_folhaz():
            logger.info("/folhaz")
            ScrappingNewsFolhaZService().exec(json.dumps(request.get_json()))
            return "I'm ok"             


        @app.route("/select-news-sagres")
        def select_news_sagres():
            logger.info("/sagres")
            SelectNewsSagresService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-sagres",methods=['POST'])
        def scrapping_news_sagres():
            logger.info("/sagres")
            ScrappingNewsSagresService().exec(json.dumps(request.get_json()))
            return "I'm ok"             

        @app.route("/select-news-ohoje")
        def select_news_ohoje():
            logger.info("/ohoje")
            SelectNewsOHojeService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-ohoje",methods=['POST'])
        def scrapping_news_ohoje():
            logger.info("/ohoje")
            ScrappingNewsOHojeService().exec(json.dumps(request.get_json()))
            return "I'm ok"       

        @app.route("/select-news-jornalopcao")
        def select_news_jornalopcao():
            logger.info("/jornalopcao")
            SelectNewsJornalOpcaoService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-jornalopcao",methods=['POST'])
        def scrapping_news_jornalopcao():
            logger.info("/jornalopcao")
            ScrappingNewsJornalOpcaoService().exec(json.dumps(request.get_json()))
            return "I'm ok"  


        @app.route("/select-news-opopular")
        def select_news_opopular():
            logger.info("/opopular")
            SelectNewsOPopularService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-opopular",methods=['POST'])
        def scrapping_news_opopular():
            logger.info("/opopular")
            ScrappingNewsOPopularService().exec(json.dumps(request.get_json()))
            return "I'm ok"  




        return app
