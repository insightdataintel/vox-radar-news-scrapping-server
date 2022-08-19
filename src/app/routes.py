from distutils.debug import DEBUG
import json
import os
import argparse
from flask import Flask, jsonify, request
from flask_cors import CORS
from logzero import logger
from src.domain.scrapping_news_aredacao_service import ScrappingNewsARedacaoService
from src.domain.scrapping_news_broadcast_agro_service import ScrappingNewsBroadcastAgroService
from src.domain.scrapping_news_campo_grande_news_service import ScrappingNewsCampoGrandeNewsService
from src.domain.scrapping_news_correio24horas_service import ScrappingNewsCorreio24horasService
from src.domain.scrapping_news_correiobraziliense_service import ScrappingNewsCorreioBrazilienseService
from src.domain.scrapping_news_diariodamanha_service import ScrappingNewsDiariodaManhaService
from src.domain.scrapping_news_dinheiro_rural_service import ScrappingNewsDinheiroRuralService
from src.domain.scrapping_news_em_cultura_service import ScrappingNewsEmCulturaService
from src.domain.scrapping_news_em_economia_service import ScrappingNewsEmEconomiaService
from src.domain.scrapping_news_em_educacao_service import ScrappingNewsEmEducacaoService
from src.domain.scrapping_news_em_gerais_service import ScrappingNewsEmGeraisService
from src.domain.scrapping_news_em_internacional_service import ScrappingNewsEmInternacionalService
from src.domain.scrapping_news_em_nacional_service import ScrappingNewsEmNacionalService
from src.domain.scrapping_news_em_politica_service import ScrappingNewsEmPoliticaService
from src.domain.scrapping_news_em_saude_service import ScrappingNewsEmSaudeService
from src.domain.scrapping_news_em_tecnologia_service import ScrappingNewsEmTecnologiaService
from src.domain.scrapping_news_folha_uol_emcimadahora_service import ScrappingNewsFolhaEmcimadahoraService
from src.domain.scrapping_news_folhaz_service import ScrappingNewsFolhaZService
from src.domain.scrapping_news_gazeta_do_povo_service import ScrappingNewsGazetadoPovoService
from src.domain.scrapping_news_globo_g1_service import ScrappingNewsGloboG1Service
from src.domain.scrapping_news_globo_ge_service import ScrappingNewsGloboGeService
from src.domain.scrapping_news_globo_service import ScrappingNewsGloboService
from src.domain.scrapping_news_globo_valor_service import ScrappingNewsGloboValorService
from src.domain.scrapping_news_gshow_service import ScrappingNewsGShowService
from src.domain.scrapping_news_ig_service import ScrappingNewsIgService
from src.domain.scrapping_news_istoe_dinheiro_service import ScrappingNewsIstoeDinheiroService
from src.domain.scrapping_news_istoe_service import ScrappingNewsIstoeService
from src.domain.scrapping_news_jornalahora_service import ScrappingNewsJornalAHoraService
from src.domain.scrapping_news_jornalopcao_service import ScrappingNewsJornalOpcaoService
from src.domain.scrapping_news_jota_service import ScrappingNewsJotaService
from src.domain.scrapping_news_jovempan_service import ScrappingNewsJovemPanService
from src.domain.scrapping_news_lance_service import ScrappingNewsLanceService
from src.domain.scrapping_news_maisgoias_service import ScrappingNewsMaisGoiasService
from src.domain.scrapping_news_metropoles_service import ScrappingNewsMetropolesService
from src.domain.scrapping_news_mix_vale_service import ScrappingNewsMixValeService
from src.domain.scrapping_news_money_times_service import ScrappingNewsMoneyTimesService
from src.domain.scrapping_news_ndmais_service import ScrappingNewsNdmaisService
from src.domain.scrapping_news_o_globo_service import ScrappingNewsOGloboService
from src.domain.scrapping_news_oantagonista_service import ScrappingNewsOAntagonistaService
from src.domain.scrapping_news_odocumento_service import ScrappingNewsODocumentoService
from src.domain.scrapping_news_ohoje_service import ScrappingNewsOHojeService
from src.domain.scrapping_news_opopular_service import ScrappingNewsOPopularService
from src.domain.scrapping_news_opovo_noticias_service import ScrappingNewsOpovoNoticiasService
from src.domain.scrapping_news_otempo_supernoticia_service import ScrappingNewsOtemposupernoticiaService
from src.domain.scrapping_news_portal_holanda_service import ScrappingNewsPortalHolandaService
from src.domain.scrapping_news_r7_agronegocios_service import ScrappingNewsR7AgronegociosService
from src.domain.scrapping_news_r7_brasilia_service import ScrappingNewsR7BrasiliaService
from src.domain.scrapping_news_r7_economia_service import ScrappingNewsR7EconomiaService
from src.domain.scrapping_news_r7_educacao_service import ScrappingNewsR7EducacaoService
from src.domain.scrapping_news_r7_internacional_service import ScrappingNewsR7InternacionalService
from src.domain.scrapping_news_r7_politica_service import ScrappingNewsR7PoliticaService
from src.domain.scrapping_news_r7_saude_service import ScrappingNewsR7SaudeService
from src.domain.scrapping_news_r7_tecnologiaeciencia_service import ScrappingNewsR7TecnologiaecienciaService
from src.domain.scrapping_news_revista_forum_service import ScrappingNewsRevistaForumService
from src.domain.scrapping_news_sagres_service import ScrappingNewsSagresService
from src.domain.scrapping_news_terra_economia_service import ScrappingNewsTerraEconomiaService
from src.domain.scrapping_news_terra_eleicoes_service import ScrappingNewsTerraEleicoesService
from src.domain.scrapping_news_terra_esportes_service import ScrappingNewsTerraEsportesService
from src.domain.scrapping_news_terra_noticias_service import ScrappingNewsTerraNoticiasService
from src.domain.scrapping_news_tribunadoplanalto_service import ScrappingNewsTribunadoPlanaltoService
from src.domain.scrapping_news_uol_economia_service import ScrappingNewsUolEconomiaService
from src.domain.scrapping_news_uol_esporte_service import ScrappingNewsUolEsporteService
from src.domain.scrapping_news_uol_noticias_service import ScrappingNewsUolNoticiasService
from src.domain.scrapping_news_yahoo_esportes_service import ScrappingNewsYahooEsportesService
from src.domain.scrapping_news_yahoo_financas_service import ScrappingNewsYahooFinancasService
from src.domain.scrapping_news_yahoo_noticias_service import ScrappingNewsYahooNoticiasService
from src.domain.select_news_aredacao_service import SelectNewsARedacaoService
from src.domain.select_news_broadcast_agro_service import SelectNewsBroadcastAgroService
from src.domain.select_news_correio24horas_service import SelectNewsCorreio24horasService
from src.domain.select_news_correiobraziliense_service import SelectNewsCorreioBrazilienseService
from src.domain.select_news_diariodamanha_service import SelectNewsDiariodaManhaService
from src.domain.select_news_dinheiro_rural_service import SelectNewsDinheiroRuralService
from src.domain.select_news_em_cultura_service import SelectNewsEmCulturaService
from src.domain.select_news_em_economia_service import SelectNewsEmEconomiaService
from src.domain.select_news_em_educacao_service import SelectNewsEmEducacaoService
from src.domain.select_news_em_gerais_service import SelectNewsEmGeraisService
from src.domain.select_news_em_internacional_service import SelectNewsEmInternacionalService
from src.domain.select_news_em_nacional_service import SelectNewsEmNacionalService
from src.domain.select_news_em_politica_service import SelectNewsEmPoliticaService
from src.domain.select_news_em_saude_service import SelectNewsEmSaudeService
from src.domain.select_news_em_tecnologia_service import SelectNewsEmTecnologiaService
from src.domain.select_news_estadao_service import SelectNewsEstadaoService
from src.domain.select_news_folha_uol_emcimadahora_service import SelectNewsFolhaEmcimadahoraService
from src.domain.select_news_folhaz_service import SelectNewsFolhaZService
from src.domain.select_news_globo_g1_service import SelectNewsGloboG1Service
from src.domain.select_news_globo_ge_service import SelectNewsGloboGeService
from src.domain.select_news_globo_service import SelectNewsGloboService
from src.domain.select_news_globovalor_service import SelectNewsGloboValorService
from src.domain.select_news_gshow_service import SelectNewsGShowService
from src.domain.select_news_ig_service import SelectNewsIgService
from src.domain.select_news_istoe_service import SelectNewsIstoeService
from src.domain.select_news_jornalahora_service import SelectNewsJornalAHoraService
from src.domain.select_news_jornalopcao_service import SelectNewsJornalOpcaoService
from src.domain.select_news_jota_service import SelectNewsJotaService
from src.domain.select_news_lance_service import SelectNewsLanceService
from src.domain.select_news_maisgoias_service import SelectNewsMaisGoiasService
from src.domain.select_news_metropoles_service import SelectNewsMetropolesService
from src.domain.select_news_mix_vale_service import SelectNewsMixValeService
from src.domain.select_news_money_times_service import SelectNewsMoneyTimesService
from src.domain.select_news_ndmais_service import SelectNewsNdmaisService
from src.domain.select_news_o_globo_service import SelectNewsOGloboService
from src.domain.select_news_oantagonista_service import SelectNewsOAntagonistaService
from src.domain.select_news_odocumento_service import SelectNewsODocumentoService
from src.domain.select_news_ohoje_service import SelectNewsOHojeService
from src.domain.select_news_opopular_service import SelectNewsOPopularService
from src.domain.select_news_opovonoticias_service import SelectNewsOpovoNoticiasService
from src.domain.select_news_otempo_supernoticia_service import SelectNewsOtemposupernoticiaService
from src.domain.select_news_campo_grande_news_service import SelectNewsCampoGrandeNewsService
from src.domain.select_news_gazeta_do_povo_service import SelectNewsGazetadoPovoService
from src.domain.select_news_portal_holanda_service import SelectNewsPortalHolandaService
from src.domain.select_news_istoe_dinheiro_service import SelectNewsIstoeDinheiroService
from src.domain.select_news_jovempan_service import SelectNewsJovemPanService
from src.domain.select_news_r7_agronegocios_service import SelectNewsR7AgronegociosService
from src.domain.select_news_r7_brasilia_service import SelectNewsR7BrasiliaService
from src.domain.select_news_r7_economia_service import SelectNewsR7EconomiaService
from src.domain.select_news_r7_educacao_service import SelectNewsR7EducacaoService
from src.domain.select_news_r7_internacional_service import SelectNewsR7InternacionalService
from src.domain.select_news_r7_politica_service import SelectNewsR7PoliticaService
from src.domain.select_news_r7_saude_service import SelectNewsR7SaudeService
from src.domain.select_news_r7_tecnologiaeciencia_service import SelectNewsR7TecnologiaecienciaService
from src.domain.select_news_revista_forum_service import SelectNewsRevistaForumService
from src.domain.select_news_sagres_service import SelectNewsSagresService
from src.domain.select_news_terra_economia_service import SelectNewsTerraEconomiaService
from src.domain.select_news_terra_eleicoes_service import SelectNewsTerraEleicoesService
from src.domain.select_news_terra_esportes_service import SelectNewsTerraEsportesService
from src.domain.select_news_terra_noticia_service import SelectNewsTerraNoticiasService
from src.domain.select_news_tribunadoplanalto_service import SelectNewsTribunadoPlanaltoService
from src.domain.select_news_uol_economia_service import SelectNewsUolEconomiaService
from src.domain.select_news_uol_esporte_service import SelectNewsUolEsporteService
from src.domain.select_news_uol_noticias_service import SelectNewsUolNoticiasService
from src.domain.select_news_yahoo_esportes_service import SelectNewsYahooEsportesService
from src.domain.select_news_yahoo_financas_service import SelectNewsYahooFinancasService
from src.domain.select_news_yahoo_noticias_service import SelectNewsYahooNoticiasService
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


        @app.route("/select-news-globoge")
        def select_news_globoge():
            logger.info("/globoge")
            SelectNewsGloboGeService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-globoge",methods=['POST'])
        def scrapping_news_globoge():
            logger.info("/globoge")
            ScrappingNewsGloboGeService().exec(json.dumps(request.get_json()))
            return "I'm ok" 

        @app.route("/select-news-oglobo")
        def select_news_oglobo():
            logger.info("/oglobo")
            SelectNewsOGloboService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-oglobo",methods=['POST'])
        def scrapping_news_oglobo():
            logger.info("/oglobo")
            ScrappingNewsOGloboService().exec(json.dumps(request.get_json()))
            return "I'm ok" 

        @app.route("/select-news-gshow")
        def select_news_gshow():
            logger.info("/gshow")
            SelectNewsGShowService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-gshow",methods=['POST'])
        def scrapping_news_gshow():
            logger.info("/gshow")
            ScrappingNewsGShowService().exec(json.dumps(request.get_json()))
            return "I'm ok" 

        @app.route("/select-news-globo")
        def select_news_globo():
            logger.info("/globo")
            SelectNewsGloboService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-globo",methods=['POST'])
        def scrapping_news_globo():
            logger.info("/globo")
            ScrappingNewsGloboService().exec(json.dumps(request.get_json()))
            return "I'm ok" 


        @app.route("/select-news-uolesporte")
        def select_news_uolesporte():
            logger.info("/uolesporte")
            SelectNewsUolEsporteService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-uolesporte",methods=['POST'])
        def scrapping_news_uolesporte():
            logger.info("/uolesporte")
            ScrappingNewsUolEsporteService().exec(json.dumps(request.get_json()))
            return "I'm ok" 

        @app.route("/select-news-terra-noticias")
        def select_news_terranoticias():
            logger.info("/terra-noticias")
            SelectNewsTerraNoticiasService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-terra-noticias",methods=['POST'])
        def scrapping_news_terra_noticias():
            logger.info("/terra-noticias")
            ScrappingNewsTerraNoticiasService().exec(json.dumps(request.get_json()))
            return "I'm ok"      

        @app.route("/select-news-terra-economia")
        def select_news_terraeconomia():
            logger.info("/terra-economia")
            SelectNewsTerraEconomiaService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-terra-economia",methods=['POST'])
        def scrapping_news_terra_economia():
            logger.info("/terra-economia")
            ScrappingNewsTerraEconomiaService().exec(json.dumps(request.get_json()))
            return "I'm ok"         


        @app.route("/select-news-terra-eleicoes")
        def select_news_terraeleicoes():
            logger.info("/terra-eleicoes")
            SelectNewsTerraEleicoesService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-terra-eleicoes",methods=['POST'])
        def scrapping_news_terra_eleicoes():
            logger.info("/terra-eleicoes")
            ScrappingNewsTerraEleicoesService().exec(json.dumps(request.get_json()))
            return "I'm ok"


        @app.route("/select-news-terra-esportes")
        def select_news_terraesportes():
            logger.info("/terra-esportes")
            SelectNewsTerraEsportesService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-terra-esportes",methods=['POST'])
        def scrapping_news_terra_esportes():
            logger.info("/terra-esportes")
            ScrappingNewsTerraEsportesService().exec(json.dumps(request.get_json()))
            return "I'm ok"


        @app.route("/select-news-ig")
        def select_news_ig():
            logger.info("/ig")
            SelectNewsIgService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-ig",methods=['POST'])
        def scrapping_news_ig():
            logger.info("/ig")
            ScrappingNewsIgService().exec(json.dumps(request.get_json()))
            return "I'm ok"


        @app.route("/select-news-mixvale")
        def select_news_mixvale():
            logger.info("/mixvale")
            SelectNewsMixValeService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-mixvale",methods=['POST'])
        def scrapping_news_mixvale():
            logger.info("/mixvale")
            ScrappingNewsMixValeService().exec(json.dumps(request.get_json()))
            return "I'm ok"

        @app.route("/select-news-emgerais")
        def select_news_emgerais():
            logger.info("/emgerais")
            SelectNewsEmGeraisService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-emgerais",methods=['POST'])
        def scrapping_news_emgerais():
            logger.info("/emgerais")
            ScrappingNewsEmGeraisService().exec(json.dumps(request.get_json()))
            return "I'm ok"


        @app.route("/select-news-empolitica")
        def select_news_empolitica():
            logger.info("/empolitica")
            SelectNewsEmPoliticaService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-empolitica",methods=['POST'])
        def scrapping_news_empolitica():
            logger.info("/empolitica")
            ScrappingNewsEmPoliticaService().exec(json.dumps(request.get_json()))
            return "I'm ok"


        @app.route("/select-news-emeconomia")
        def select_news_emeconomia():
            logger.info("/emeconomia")
            SelectNewsEmEconomiaService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-emeconomia",methods=['POST'])
        def scrapping_news_emeconomia():
            logger.info("/emeconomia")
            ScrappingNewsEmEconomiaService().exec(json.dumps(request.get_json()))
            return "I'm ok"

        @app.route("/select-news-emnacional")
        def select_news_emnacional():
            logger.info("/emnacional")
            SelectNewsEmNacionalService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-emnacional",methods=['POST'])
        def scrapping_news_emnacional():
            logger.info("/emnacional")
            ScrappingNewsEmNacionalService().exec(json.dumps(request.get_json()))
            return "I'm ok"


        @app.route("/select-news-eminternacional")
        def select_news_eminternacional():
            logger.info("/eminternacional")
            SelectNewsEmInternacionalService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-eminternacional",methods=['POST'])
        def scrapping_news_eminternacional():
            logger.info("/eminternacional")
            ScrappingNewsEmInternacionalService().exec(json.dumps(request.get_json()))
            return "I'm ok"


        @app.route("/select-news-emeducacao")
        def select_news_emeducacao():
            logger.info("/emeducacao")
            SelectNewsEmEducacaoService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-emeducacao",methods=['POST'])
        def scrapping_news_emeducacao():
            logger.info("/emeducacao")
            ScrappingNewsEmEducacaoService().exec(json.dumps(request.get_json()))
            return "I'm ok"


        @app.route("/select-news-emtecnologia")
        def select_news_emtecnologia():
            logger.info("/emtecnologia")
            SelectNewsEmTecnologiaService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-emtecnologia",methods=['POST'])
        def scrapping_news_emtecnologia():
            logger.info("/emtecnologia")
            ScrappingNewsEmTecnologiaService().exec(json.dumps(request.get_json()))
            return "I'm ok"



        @app.route("/select-news-emsaude")
        def select_news_emsaude():
            logger.info("/emsaude")
            SelectNewsEmSaudeService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-emsaude",methods=['POST'])
        def scrapping_news_emsaude():
            logger.info("/emsaude")
            ScrappingNewsEmSaudeService().exec(json.dumps(request.get_json()))
            return "I'm ok"



        @app.route("/select-news-emcultura")
        def select_news_emcultura():
            logger.info("/emcultura")
            SelectNewsEmCulturaService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-emcultura",methods=['POST'])
        def scrapping_news_emcultura():
            logger.info("/emcultura")
            ScrappingNewsEmCulturaService().exec(json.dumps(request.get_json()))
            return "I'm ok"


        @app.route("/select-news-yahoo-noticias")
        def select_news_yahoo_noticias():
            logger.info("/yahoo-noticias")
            SelectNewsYahooNoticiasService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-yahoo-noticias",methods=['POST'])
        def scrapping_news_yahoo_noticias():
            logger.info("/yahoo-noticias")
            ScrappingNewsYahooNoticiasService().exec(json.dumps(request.get_json()))
            return "I'm ok"


        @app.route("/select-news-yahoo-financas")
        def select_news_yahoo_financas():
            logger.info("/yahoo-financas")
            SelectNewsYahooFinancasService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-yahoo-financas",methods=['POST'])
        def scrapping_news_yahoo_financas():
            logger.info("/yahoo-financas")
            ScrappingNewsYahooFinancasService().exec(json.dumps(request.get_json()))
            return "I'm ok"


        @app.route("/select-news-yahoo-esportes")
        def select_news_yahoo_esportes():
            logger.info("/yahoo-esportes")
            SelectNewsYahooEsportesService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-yahoo-esportes",methods=['POST'])
        def scrapping_news_yahoo_esportes():
            logger.info("/yahoo-esportes")
            ScrappingNewsYahooEsportesService().exec(json.dumps(request.get_json()))
            return "I'm ok"


        @app.route("/select-news-ndmais")
        def select_news_ndmais():
            logger.info("/ndmais")
            SelectNewsNdmaisService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-ndmais",methods=['POST'])
        def scrapping_news_ndmais():
            logger.info("/ndmais")
            ScrappingNewsNdmaisService().exec(json.dumps(request.get_json()))
            return "I'm ok"


        @app.route("/select-news-lance")
        def select_news_lance():
            logger.info("/lance")
            SelectNewsLanceService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-lance",methods=['POST'])
        def scrapping_news_lance():
            logger.info("/lance")
            ScrappingNewsLanceService().exec(json.dumps(request.get_json()))
            return "I'm ok"

        @app.route("/select-news-odocumento")
        def select_news_odocumento():
            logger.info("/odocumento")
            SelectNewsODocumentoService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-odocumento",methods=['POST'])
        def scrapping_news_odocumento():
            logger.info("/odocumento")
            ScrappingNewsODocumentoService().exec(json.dumps(request.get_json()))
            return "I'm ok"


        @app.route("/select-news-revistaforum")
        def select_news_revistaforum():
            logger.info("/revistaforum")
            SelectNewsRevistaForumService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-revistaforum",methods=['POST'])
        def scrapping_news_revistaforum():
            logger.info("/revistaforum")
            ScrappingNewsRevistaForumService().exec(json.dumps(request.get_json()))
            return "I'm ok"


        @app.route("/select-news-portal-holanda")
        def select_news_portalholanda():
            logger.info("/portal-holanda")
            SelectNewsPortalHolandaService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-portal-holanda",methods=['POST'])
        def scrapping_news_portalholanda():
            logger.info("/portal-holanda")
            ScrappingNewsPortalHolandaService().exec(json.dumps(request.get_json()))
            return "I'm ok"


        @app.route("/select-news-gazeta-do-povo")
        def select_news_gazetadopovo():
            logger.info("/gazeta-do-povo")
            SelectNewsGazetadoPovoService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-gazeta-do-povo",methods=['POST'])
        def scrapping_news_gazetadopovo():
            logger.info("/gazeta-do-povo")
            ScrappingNewsGazetadoPovoService().exec(json.dumps(request.get_json()))
            return "I'm ok"


        @app.route("/select-news-jovempan")
        def select_news_jovempan():
            logger.info("/jovempan")
            SelectNewsJovemPanService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-jovempan",methods=['POST'])
        def scrapping_news_jovempan():
            logger.info("/jovempan")
            ScrappingNewsJovemPanService().exec(json.dumps(request.get_json()))
            return "I'm ok"

        @app.route("/select-news-campo-grande-news")
        def select_news_campograndenews():
            logger.info("/campo-grande-news")
            SelectNewsCampoGrandeNewsService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-campo-grande-news",methods=['POST'])
        def scrapping_news_campograndenews():
            logger.info("/campo-grande-news")
            ScrappingNewsCampoGrandeNewsService().exec(json.dumps(request.get_json()))
            return "I'm ok"            

        @app.route("/select-news-istoe-dinheiro")
        def select_news_istoe_dinheiro():
            logger.info("/istoe-dinheiro")
            SelectNewsIstoeDinheiroService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-istoe-dinheiro",methods=['POST'])
        def scrapping_news_istoe_dinheiro():
            logger.info("/istoe-dinheiro")
            ScrappingNewsIstoeDinheiroService().exec(json.dumps(request.get_json()))
            return "I'm ok"   

        @app.route("/select-news-money-times")
        def select_news_money_times():
            logger.info("/money-times")
            SelectNewsMoneyTimesService().exec()
            return "I'm ok"
        
        @app.route("/scrapping-news-money-times",methods=['POST'])
        def scrapping_news_money_times():
            logger.info("/money-times")
            ScrappingNewsMoneyTimesService().exec(json.dumps(request.get_json()))
            return "I'm ok"   





        return app
