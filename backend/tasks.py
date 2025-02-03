from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from celery import Celery, group, subtask
from extractnet import Extractor

from textblob import TextBlob

from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

from urllib.parse import urlparse


import datetime
import hashlib
import json
import os

import random
import redis
import webtech
import whois
import yake

SUMMARY_LANGUAGE = "english"
SUMMARY_SENTENCES_COUNT = 5
stemmer = Stemmer(SUMMARY_LANGUAGE)
summarizer = Summarizer(stemmer)
summarizer.stop_words = get_stop_words(SUMMARY_LANGUAGE)

llamacpp_server_url = os.getenv('LLAMACPP_SERVER_URL', 'http://localhost:8080')

user_agents = [    
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
]

# Set up Celery broker and backend URLs from environment variables, with defaults
broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
backend_url = os.getenv('CELERY_BACKEND_URL', 'redis://localhost:6379/0')

# Initialize Celery app with broker and backend URLs
app = Celery('tasks', broker=broker_url, backend=backend_url)
app.conf.broker_transport_options = {'visibility_timeout': 3600}  # 1 hour.

# Set up Redis connection details from environment variables, with defaults
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = os.getenv('REDIS_PORT', 6379)
redis_db = os.getenv('REDIS_DB', 1)

# Connect to Redis for more persistent saves
r = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

wt = webtech.WebTech(options={'json': True})  

kw_model = yake.KeywordExtractor(top=10, stopwords=None)  # Set up YAKE keyword extractor

def get_options(): # Get Chrome options for headless browsing
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # adding argument to disable the AutomationControlled flag 
    options.add_argument("--disable-blink-features=AutomationControlled") 

    # exclude the collection of enable-automation switches 
    options.add_experimental_option("excludeSwitches", ["enable-automation"]) 

    # turn-off userAutomationExtension 
    options.add_experimental_option("useAutomationExtension", False) 
    user_agent = random.choice(user_agents)
    options.add_argument(f'user-agent={user_agent}')

    proxy_url = os.getenv('PROXY_URL') # IP:PORT or HOST:PORT
    if proxy_url:
        options.add_argument(f'--proxy-server={proxy_url}')
    return options

def setup_driver():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=get_options())
    # changing the property of the navigator value for webdriver to undefined 
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

# Define a Celery task to scrape a webpage and return its source
@app.task(default_retry_delay=10, max_retries=3, soft_time_limit=30, time_limit=100)
def scrape(url):
    results = {}
    driver = setup_driver()
    try:        
        driver.get(url)
        page_source = driver.page_source
        if page_source:
            results[url] = page_source
            key = get_key('url', url)
            with r.pipeline() as pipe:  # Start a pipeline (transaction)
                pipe.hset(key, 'url', url)
                today = datetime.datetime.today()
                pipe.hset(key, 'date', int(today.timestamp()))
                pipe.execute()
    finally:
        driver.close()
    return results

# Define a Celery task to get links from a webpage using a specified XPath
@app.task(default_retry_delay=4, max_retries=2, soft_time_limit=10, time_limit=30)
def get_links(target_xpath):
    target, xpath = target_xpath
    urls = set()
    driver = setup_driver()
    try:    
        driver.get(target)
        elements = driver.find_elements(By.XPATH, xpath)            
        for element in elements:           
            url = element.get_attribute("href")
            urls.add(url)
    finally:
        driver.close()
    return list(urls)

def date_to_string(date):
    if date is None:
        return ''
    return date.strftime('%Y-%m-%d %H:%M:%S')

# Define a Celery task to extract structured data from a webpage's content
@app.task
def extract(scraped):
    results = {}
    for url, content in scraped.items():
        if content is None:
            continue
        
        data = Extractor().extract(content)
        if not data.get('content'):
            continue
    
        key = get_key('extract', url)
        with r.pipeline() as pipe:  # Start a pipeline (transaction)
            pipe.hset(key, 'rawAuthor', data.get('rawAuthor', ''))            
            pipe.hset(key, 'rawDate', data.get('rawDate', ''))
            pipe.hset(key, 'title', data.get('title', ''))
            pipe.hset(key, 'content', data.get('content', ''))            
            pipe.execute()
        
        results[url] = data.get('content', '')
    return results

def get_key(prefix, url):
    return prefix + ":" + hashlib.md5(url.encode()).hexdigest()

def remove_http(url):
    if url.startswith('http://'):
        return url[7:]
    if url.startswith('https://'):
        return url[8:]
    return url

@app.task()
def sentiment(extracted_data):
    results = {}
    for url, content in extracted_data.items():                
        sentiment = TextBlob(content).sentiment                        
        key = get_key('sentiment', url)
        with r.pipeline() as pipe:            
            pipe.hset(key, 'polarity', str(sentiment.polarity))
            pipe.hset(key, 'subjectivity', str(sentiment.subjectivity))
            pipe.execute()

        results[url] = True
    return results

@app.task()
def keywords(extracted_data):
    results = {}    
    for url, content in extracted_data.items():        
        keywords = kw_model.extract_keywords(content)                       
        
        key = get_key('keywords', url) 
        with r.pipeline() as pipe:  # Start a pipeline (transaction)
            for k,v in keywords:                
                pipe.hset(key, k, v)
            pipe.execute()               
        results[url] = True    
    return results

@app.task
def scan(data):
    results = {}
    for url, _data in data.items():
        report = wt.start_from_url(url)        
        key = get_key('tech', url) 
        tech = report['tech']
        if tech:
            with r.pipeline() as pipe:  # Start a pipeline (transaction)            
                for item in tech:                               
                    version = item['version']
                    if version is None:
                        version = ''
                    pipe.hset(key, item['name'], version)                  
                    pipe.execute()        
        key = get_key('headers', url) 
        headers = report['headers']
        if headers:           
            with r.pipeline() as pipe:  # Start a pipeline (transaction)            
                for item in headers:                                  
                    pipe.hset(key, item['name'], item['value'])                     
                    pipe.execute()      
        results[url] = True
    return results

@app.task
def ask_whois(data):
    results = {}    
    for url, _data in data.items():
        domain = urlparse(url).netloc
        key = get_key('whois', domain)
        whois_info = whois.whois(domain)
        print(whois_info)        
        with r.pipeline() as pipe:  # Start a pipeline (transaction)            
            pipe.hset(key, 'report', json.dumps(whois_info))
            pipe.execute()
        results[url] = True
    return results

@app.task
def summarize(extracted_data):    
    results = {}    
    for url, content in extracted_data.items():    
        key = get_key('url', url) 
        summary = ''
        parser = PlaintextParser.from_string(content, Tokenizer(SUMMARY_LANGUAGE))
        for sentence in summarizer(parser.document, SUMMARY_SENTENCES_COUNT):            
            summary += str(sentence) + ' '        
        with r.pipeline() as pipe:  # Start a pipeline (transaction)                  
            pipe.hset(key, 'summary', summary)                
            pipe.execute()
        results[url] = True
    return results        

@app.task
def workflow():
    process_url = (
        scrape.s() | 
        group(
            extract.s() | 
            group(
                keywords.s(), 
                sentiment.s(),  
                summarize.s(),                       
            ),
            scan.s(),
            #ask_whois.s(),
        )
    )
    keys = r.keys('generator:*')
    for key in keys:
        url = r.hget(key, 'url').decode()
        xpath = r.hget(key, 'xpath').decode()
        (get_links.s((url, xpath)) | dmap.s(process_url)).delay().forget()

def clone_signature(sig, args=(), kwargs=(), **opts):
    if sig.subtask_type and sig.subtask_type != "chain":
        raise NotImplementedError(
            "Cloning only supported for Tasks and chains, not %s" % sig.subtask_type
        )
    clone = sig.clone()
    if hasattr(clone, "tasks"):
        t = clone.tasks[0]
    else:
        t = clone
    args, kwargs, opts = t._merge(args=args, kwargs=kwargs, options=opts)
    t.update(args=args, kwargs=kwargs, options=opts)
    return clone

@app.task()
def dmap(it, cb):
    callback = subtask(cb)
    grp = group(clone_signature(callback, [arg, ]) for arg in it)
    return grp()

