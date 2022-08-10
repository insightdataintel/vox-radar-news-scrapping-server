import re
from src.config.constants import Constants
import requests
from urllib.parse import urlparse
import pytz
from datetime import datetime, timedelta
import os.path
import unicodedata
import regex
import feedparser
from bs4 import BeautifulSoup
import numpy as np

class Utils:

  @classmethod
  def remove_accent_chars_regex(self, text: str):
    return regex.sub(r'\p{Mn}', '', unicodedata.normalize('NFKD', text))
  
  @classmethod
  def get_extension(self, file_name:str):
    return os.path.splitext(file_name)[1]

  @classmethod
  def remove_extension(self, file_name:str):
    extension = os.path.splitext(file_name)[1]
    return file_name.replace(extension,'')

  @classmethod
  def get_datetime_now(self):
    return datetime.now(pytz.timezone(Constants.TIMEZONE[0]['SAO_PAULO']['TIMEZONE']))

  @classmethod
  def has_numbers(self, input_string):
    return any(char.isdigit() for char in input_string)

  @classmethod
  def only_numbers(self, input_string):
    return re.sub(r"\D", '', input_string)

  @classmethod
  def transform_number(self, number_text:str) -> int:
    only_text = re.sub(r"[^A-Za-z]+", '', number_text).strip().lower()
    only_number = re.sub(r"\D", '', number_text)
    if(only_text == "mil"):
      return int(only_number) * 1000
    else:
      return int(only_number)

  @classmethod
  def format_date_br_to_universal(self, date:str) -> str:
    if not date:
      return None

    try:
      date_parsed = datetime.strptime(date, '%d/%m/%Y').date()
      if date_parsed.year > 1900:
        return date_parsed.strftime('%Y-%m-%d')
      else:
        print(f'This is the incorrect date string format | {date}')
        return None

    except Exception:
      print(f'This is the incorrect date string format | {date}')
      return None

  @classmethod
  def format_date_universal_to_br(self, date:str) -> str:
    try:
      date_parsed = datetime.strptime(date, '%Y-%m-%d').date()
      if date_parsed.year > 1900:
        return date_parsed.strftime('%d/%m/%Y')
      else:
        print(f'This is the incorrect date string format | {date}')
        return None

    except Exception:
      print(f'This is the incorrect date string format | {date}')
      return None

  @classmethod
  def getQueueSuffixByEnvironment(self, environment: str) -> str:
    if environment == Constants.ENVIRONMENT['LOCAL']:
      return '_LOCAL'
    if environment == Constants.ENVIRONMENT['DEVELOP']:
      return '_DEVELOP'
    else:
      return ''

  @classmethod
  def remove_duplicate(self, list:list, key:str) -> list:
    memo = set()
    res = []
    for sub in list:
      if sub[key] not in memo:
        res.append(sub)
        memo.add(sub[key])

    return res

  @classmethod
  def to_int(self, value) -> int:
    if not value:
      return None
    else:
      return int(value)

  @classmethod
  def to_float(self, value) -> float:
    if not value:
      return None
    else:
      return float(str(value).replace(',','.'))

  @classmethod
  def check_int(self, value):
    if value:
      return re.match(r"[-+]?\d+(\.0*)?$", str(value)) is not None
    return None

  @classmethod
  def truncate_text(self, text:str, size:int):
    if(len(text) > size):
      return text[0:size] + '...'
    else:
      return text

  @classmethod
  def remove_links(self, text:str):
    return re.sub(r'http\S+', '', text)

  @classmethod
  def get_datetime_now(self):
    return datetime.now(pytz.timezone(Constants.TIMEZONE[0]['SAO_PAULO']['TIMEZONE']))

  @classmethod
  def normalize_url(self, url:str):
    decoded = self.decode_url(url)
    return decoded.rstrip("/")

  @classmethod
  def decode_url(self, url:str):
    parsed = urlparse(url)
    return parsed.scheme + '://' + parsed.netloc + parsed.path
  
  @classmethod
  def get_domain_url(self, url:str):
    parsed = urlparse(url)
    return parsed.netloc

  @classmethod
  def get_long_url(self, short_url):
    try:
        r = requests.get(short_url)
    except requests.exceptions.RequestException:
        return (short_url, None)

    if r.status_code != 200:
        long_url = None
    else:
        long_url = r.url

    return long_url

  @classmethod
  def get_urls_from_text(self, text):    
    links = re.findall(r'(https?://\S+)', text)
    long_links = [self.get_long_url(link) for link in links]
    return long_links

  @classmethod
  def has_numbers(self, input_string):
    return any(char.isdigit() for char in input_string)

  @classmethod
  def only_numbers(self, input_string):
    return re.sub(r"\D", '', input_string)

  @classmethod
  def get_queue_suffix_by_environment(self, environment: str) -> str:
    if environment == Constants.ENVIRONMENT['LOCAL']:
      return '_LOCAL'
    if environment == Constants.ENVIRONMENT['DEVELOP']:
      return '_DEVELOP'
    else:
      return ''

  @classmethod
  def transform_number(self, number_text:str) -> int:
    only_text = re.sub(r"[^A-Za-z]+", '', number_text).strip().lower()
    only_number = re.sub(r"\D", '', number_text)
    if(only_text == "mil"):
      return int(only_number) * 1000
    else:
      return int(only_number)

  @classmethod
  def subtract_day_from_datetime(datetime:datetime, days:int) -> datetime:
    _days = timedelta(days)
    return datetime - _days

  @classmethod
  def translate_portuguese_english(self, word:str)->str:
    word = word.lower()
        
    translate = {"poder":"power", 
                "opinião":"opinion",
                "educação":"education",
                "maternar":"maternity",
                "televisao":"television",
                "painel":"panel",
                "ilustrada":"illustrated",
                "cotidiano":"daily",
                "mundo":"world",
                "mercado":"market",
                "empresas":"companies",
                "mercados":"market",
                "financas":"finance",
                "carreira":"career",
                "brasil":"brazil",
                "politica":"politics",
                "política":"politics", 
                "legislacao":"law",
                "eu-e":"me and",
                "inovacao":"inovation",
                "internacional":"international",
                "nacional":"national",
                "economia":"economy"
                }

    return (translate.get(word))
  
  @classmethod
  def extract_links_from_rss(self, url:str)->str:
    
    links_filtered = []   
    links = feedparser.parse(url)
     
    for e in links.entries:
        
        links_filtered.append(e.link)

    return(links_filtered)

  @classmethod
  def extract_links_from_rss_ge(self, url:str)->str:
    
    links_filtered = []   
    links = feedparser.parse(url)
     
    for e in links.entries:
        if '/jogo/' in e.link:
          None
        else:
          links_filtered.append(e.link)

    return(links_filtered)    

  @classmethod
  def extract_links_from_rss_oglobo(self, url:str)->str:
    
    links_filtered = []   
    links = feedparser.parse(url)
    no_text = ['/stories/','/jogo/']     

    for e in links.entries:
      for item in no_text:
          if item in e.link:
              e.link = ''
      if e.link =='':
          None
      else:
          links_filtered.append(e.link)

    return(links_filtered)    

  @classmethod
  def extract_links_from_page(self, url:str)->str:


      headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:2.0b10) Gecko/20100101 Firefox/4.0b10"}
      page = requests.get(url,headers=headers).text
      soup = BeautifulSoup(page, 'html.parser')  
      
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
              if link[len(link)-1]=="/":
                  pass
              else:
                  links_filtered.append(link)

      links_filtered = list(set(links_filtered))
      return(links_filtered)

  @classmethod
  def extract_links_from_page_v2(self, url:str)->str:

    headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:2.0b10) Gecko/20100101 Firefox/4.0b10"}
    page = requests.get(url,headers=headers).text
    soup = BeautifulSoup(page, 'html.parser')  
    
    domain = url.split(".")[1]+".com"
    links = soup.find_all('a', href=True)
    links = [link["href"] for link in links if domain in link["href"][:len(url)] ]
    len_link = [len(link.split("/")) for link in links]
    len_max = np.array(len_link).max()
    links_news = [link for link in links if len(link.split("/"))==len_max]
    links_filtered = []
    blocking = ['portal_estadao_selo_acesso', 'einvestidor.', 'emais.', 'paladar.','/cadastro/alterar-senha','/pagina/'] 
    for link in links_news:
        present = False
        for word in blocking:
            if word in link:
                present = True
        if present is False:
            # if link[len(link)-1]=="/":
            #     pass
            # else:
            links_filtered.append(link)

    links_filtered = list(set(links_filtered))
    return(links_filtered)      

  @classmethod
  def extract_links_from_page_v3(self, url:str)->str:

    headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:2.0b10) Gecko/20100101 Firefox/4.0b10"}
    page = requests.get(url,headers=headers).text
    soup = BeautifulSoup(page, 'html.parser')   

    domain0 = 'https://www.'
    domain = url.split(".")[1]+".com"
    links = soup.find('div', class_='list-news').find_all('a', href=True)
    linkos = []
    for link in links:
        new_link = str(link).split('href=')[1].split('rel')[0].replace('"','').replace(' ','')
        linkos.append(domain0+domain+'.br'+new_link)
    return(linkos)

  @classmethod
  def extract_links_from_page_oantagonista(self, url:str)->str:

    headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:2.0b10) Gecko/20100101 Firefox/4.0b10"}
    page = requests.get(url,headers=headers).text
    soup = BeautifulSoup(page, 'html.parser')   

    links = soup.find_all('div', class_='content_post')
    linkos = []
    for link in links:
        new_link = str(link).split('href=')[1].split('title')[0].replace('"','').replace(' ','')
        linkos.append(new_link)
    return(linkos)

  @classmethod
  def extract_links_from_page_metropoles(self, url:str)->str:

    headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:2.0b10) Gecko/20100101 Firefox/4.0b10"}
    page = requests.get(url,headers=headers).text
    soup = BeautifulSoup(page, 'html.parser')   
    
    links = soup.find_all('div', class_='column is-full is-full')
    linkos = []
    for link in links:
        new_link = str(link).split('href=')[1].split('onclick')[0].replace('"','').replace(' ','')
        linkos.append(new_link)
    return(linkos)

  @classmethod
  def extract_links_from_page_broadcast_agro(self, url:str)->str:

    headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:2.0b10) Gecko/20100101 Firefox/4.0b10"}
    page = requests.get(url,headers=headers).text
    soup = BeautifulSoup(page, 'html.parser')   
    
    domain0 = 'http://www.'
    domain = url.split(".")[1]+".com"
    links = soup.find_all('div', class_='materia')
    linkos = []
    for link in links:
        new_link = str(link).split('href=')[1].split('target')[0].replace('"','').replace(' ','')
        linkos.append(domain0+domain+'.br'+new_link)
    return(linkos)


  @classmethod
  def extract_links_from_page_dinheiro_rural(self, url:str)->str:

    headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:2.0b10) Gecko/20100101 Firefox/4.0b10"}
    page = requests.get(url,headers=headers).text
    soup = BeautifulSoup(page, 'html.parser')   
    
    links = soup.find_all('div', class_='wrapper-title no-image')
    linkos = []
    for link in links:
        new_link = str(link).split('href=')[1].split('title')[0].replace('"','').replace(' ','')
        linkos.append(new_link)
    return(linkos)


  @classmethod
  def extract_links_from_page_istoe(self, url:str)->str:

    headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:2.0b10) Gecko/20100101 Firefox/4.0b10"}
    page = requests.get(url,headers=headers).text
    soup = BeautifulSoup(page, 'html.parser')   
    
    links = soup.find('div', class_='c-box-principal').find_all('a',class_='link-category')
    linkos = []
    for link in links:
        new_link = str(link).split('href=')[1].split('title')[0].replace('"','').replace(' ','')
        linkos.append(new_link)
    return(linkos)


  @classmethod
  def request_link(self, url:str)->str:

    headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:2.0b10) Gecko/20100101 Firefox/4.0b10"}
    page = requests.get(url,headers=headers).text
    soup = BeautifulSoup(page, 'html.parser')   
    return soup


  @classmethod
  def extract_links_from_page_aredacao(self, url:str)->str:

    soup = Utils.request_link(url)
    
    links = soup.find_all('li', class_='listaNoticia')
    linkos = []
    for link in links:
        new_link = str(link).split('href=')[1].split('style=')[0].replace('"','').replace(' ','')
        linkos.append(new_link)
    return(linkos)


  @classmethod
  def extract_links_from_page_maisgoias(self, url:str)->str:

    soup = Utils.request_link(url)
    
    links = soup.find_all('article', class_='cardHor')
    linkos = []
    for link in links:
        new_link = str(link).split('href=')[1].split('>')[0].replace('"','').replace(' ','')
        linkos.append(new_link)
    return(linkos)


  @classmethod
  def extract_links_from_page_jornalahora(self, url:str)->str:

    soup = Utils.request_link(url)
    
    links = soup.find('div', class_='wpb_wrapper').find_all('a',class_='td-image-wrap')
    linkos = []
    for link in links:
        new_link = str(link).split('href=')[1].split('rel="bookmark"')[0].replace('"','').replace(' ','')
        linkos.append(new_link)
    return(linkos)


  @classmethod
  def extract_links_from_page_tribunadoplanalto(self, url:str)->str:

    soup = Utils.request_link(url)
    
    links = soup.find_all('div', class_='col-12 separator')
    linkos = []
    for link in links:
      aux = link.find('a',class_='fix-thumb-image')
      new_link = str(aux).split('href=')[1].split('">')[0].replace('"','').replace(' ','')
      linkos.append(new_link)
    return(linkos)


  @classmethod
  def extract_links_from_page_diariodamanha(self, url:str)->str:

    soup = Utils.request_link(url)
    
    links = soup.find_all('div', class_='col-md-4 col-12')
    linkos = []
    for link in links:
      aux = link.find('a',href = True)
      new_link = str(aux).split('href=')[1].split('">')[0].replace('"','').replace(' ','')
      linkos.append(new_link)
    return(linkos)


  @classmethod
  def extract_links_from_page_folhaz(self, url:str)->str:

    soup = Utils.request_link(url)
    links = soup.find_all('div', class_='post-details')
    linkos = []
    for link in links:
      aux = link.find('a',class_= 'more-link button')
      new_link = str(aux).split('href=')[1].split('">')[0].replace('"','').replace(' ','')
      linkos.append(new_link)
    return(linkos)
    

  @classmethod
  def extract_links_from_page_sagres(self, url:str)->str:

    soup = Utils.request_link(url)
    links = soup.find_all('h3', class_='entry-title td-module-title')
    linkos = []
    for link in links:
      aux = link.find('a',href = True)
      new_link = str(aux).split('href=')[1].split('rel="bookmark"')[0].replace('"','').replace(' ','')
      linkos.append(new_link)
    return(linkos)


  @classmethod
  def extract_links_from_page_ohoje(self, url:str)->str:

    soup = Utils.request_link(url)
    links = soup.find_all('div', class_='news list-editor')
    linkos = []
    for link in links:
      aux = link.find('a',href = True)
      new_link = str(aux).split('href=')[1].split('><div')[0].replace('"','').replace(' ','')
      linkos.append(new_link)
    return(linkos)


  @classmethod
  def extract_links_from_page_jornalopcao(self, url:str)->str:

    soup = Utils.request_link(url)
    links = soup.find_all('div', class_='template-part-component-feed-post has-thumb')
    linkos = []
    for link in links:
      aux = link.find('a',class_='main_link')
      new_link = str(aux).split('href=')[1].split('>')[0].replace('"','').replace(' ','')
      linkos.append(new_link)
    return(linkos)

  @classmethod
  def extract_links_from_page_opopular(self, url:str)->str:

    soup = Utils.request_link(url)
    links = soup.find("ul", {"class": "row news"}).find_all("li")
    linkos = []
    for link in links:
      new_link = link.find("a")['href']
      linkos.append("https://opopular.com.br"+new_link)
    return(linkos)    


  @classmethod
  def extract_links_from_page_globo(self, url:str)->str:

    soup = Utils.request_link(url)
    links = soup.find_all('a', class_='post__link')
    linkos = []
    for link in links:
      new_link = str(link).split('data-tracking-label=')[1].split('data-tracking-view=')[0].replace('"','').replace(' ','')
      linkos.append(new_link)
    return(linkos)    


  @classmethod
  def extract_links_from_page_uol_esporte(self, url:str)->str:

    soup = Utils.request_link(url)
    links = soup.find_all('div', class_='thumbnails-wrapper')
    linkos = []
    no_text = ['/amp-stories/','/jogo/']
    for link in links:
      new_link = str(link).split('href=')[1].split('>')[0].replace('"','').replace(' ','')
      for item in no_text:
        if item in new_link:
            new_link = ''
    if new_link == '':
      None
    else:
      linkos.append(new_link)
    return(linkos)    

  @classmethod
  def extract_links_from_page_terra(self, url:str)->str:

    soup = Utils.request_link(url)
    links = soup.find_all('a', class_='card-news__text--title main-url')
    linkos = []
    no_text = ['/amp-stories/','/jogo/','/story/', 'noopener']
    for link in links:
      new_link = str(link).split('href=')[1].split('id=')[0].split('target=')[0].replace('"','').replace(' ','')
      for item in no_text:
        if item in new_link:
            new_link = ''
    if new_link == '':
      None
    else:
      linkos.append(new_link)
    return(linkos)    




  @classmethod
  def month_convert(texto_horario):  
    texto_horario = texto_horario.lower()
    
    meses={"janeiro":"01",
        "fevereiro":"02",
        "março":"03",
        "abril":"04",
        "maio":"05",
        "junho":"06",
        "julho":"07",
        "agosto":"08",
        "setembro":"09",
        "outubro":"10",
        "novembro":"11",
        "dezembro":"12"}

    for i in meses.keys():
        if i in texto_horario:
            texto_horario=texto_horario.replace(i,meses[i]) 

    meses={"jan":"01",
           "fev":"02",
           "mar":"03",
           "abr":"04",
           "mai":"05",
           "jun":"06",
           "jul":"07",
           "ago":"08",
           "set":"09",
           "out":"10",
           "nov":"11",
           "dez":"12"}

    for i in meses.keys():
        if i in texto_horario:
            texto_horario=texto_horario.replace(i,meses[i])
    
    return texto_horario
