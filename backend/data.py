import redis
import os
import datetime
import hashlib
import re
from urllib.parse import unquote
from pydantic import BaseModel
import json

buckets = ['url','extract', 'sentiment', 'keywords','scan', 'tech', 'headers']

# Set up Redis connection details from environment variables, with defaults
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = os.getenv('REDIS_PORT', 6379)
redis_db = os.getenv('REDIS_DB', 1)

# Connect to Redis for more persistent saves
r = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

def validate_url(url):
    return is_valid_md5(url) or re.match(regex, url) is not None

def validate_url_id(item_id):
    return is_valid_md5(item_id)

def is_valid_md5(to_test): 
    return re.fullmatch('^[a-f0-9]{32}$', to_test) is not None

def get_key(prefix, url):       
    if is_valid_md5(url):                
        return prefix + ":" + url
    else:              
        hash_url = hashlib.md5(url.encode()).hexdigest()        
        return prefix + ":" + hash_url

def save_url(url: str):
    key = get_key('url', url)
    with r.pipeline() as pipe:  # Start a pipeline (transaction)
        pipe.hset(key, 'url', url)
        today = datetime.datetime.today()
        pipe.hset(key, 'date', int(today.timestamp()))
        pipe.execute()

def save_extraction(url, data):
    key = get_key('extract', url)
    with r.pipeline() as pipe:  # Start a pipeline (transaction)
        pipe.hset(key, 'rawAuthor', data.get('rawAuthor', ''))            
        pipe.hset(key, 'rawDate', data.get('rawDate', ''))
        pipe.hset(key, 'title', data.get('title', ''))
        pipe.hset(key, 'content', data.get('content', ''))            
        pipe.execute()
        
def save_sentiment(url, sentiment):
    key = get_key('sentiment', url)
    with r.pipeline() as pipe:            
        pipe.hset(key, 'polarity', str(sentiment.polarity))
        pipe.hset(key, 'subjectivity', str(sentiment.subjectivity))
        pipe.execute()        

def save_keywords(url, keywords):            
    key = get_key('keywords', url) 
    with r.pipeline() as pipe:  # Start a pipeline (transaction)
        for k,v in keywords:                
            pipe.hset(key, k, v)
        pipe.execute()        

def save_scan(url, report):
    tech = report['tech']
    if tech:
        key = get_key('tech', url) 
        with r.pipeline() as pipe:  # Start a pipeline (transaction)            
            for item in tech:                               
                version = item['version']
                if version is None:
                    version = ''
                pipe.hset(key, item['name'], version)                  
                pipe.execute()                
    headers = report['headers']
    if headers:           
        key = get_key('headers', url) 
        with r.pipeline() as pipe:  # Start a pipeline (transaction)            
            for item in headers:                                  
                pipe.hset(key, item['name'], item['value'])                     
                pipe.execute()      

def save_whois(domain, whois_info):
    print(whois_info) 
    key = get_key('whois', domain)       
    with r.pipeline() as pipe:  # Start a pipeline (transaction)            
        pipe.hset(key, 'report', json.dumps(whois_info))
        pipe.execute()

def save_summary(url, summary):
    key = get_key('url', url) 
    with r.pipeline() as pipe:  # Start a pipeline (transaction)                  
        pipe.hset(key, 'summary', summary)                
        pipe.execute()

class Url(BaseModel):
    url: str    

def validate_url_item(item: Url):
    url = unquote(item.url)    
    if not validate_url(url):
        return {"message": "Invalid URL"}     
    return url

def get_url_data(url: str):
    data = {}
    for bucket in buckets:
        key = get_key(bucket, url)
        data[bucket] = r.hgetall(key)
    return data

class Generator(BaseModel):
    url: str  
    xpath: str  

def validate_generator(generator: Generator):
    url = unquote(generator.url)
    if validate_url(url):
        return {"message": "Invalid URL"}
    xpath = unquote(generator.xpath)
    return url, xpath

def get_generator(url):
    key = get_key('generator', url)        
    return r.hgetall(key)

def get_generators():
    results = {}
    keys = r.keys('generator:*')
    for key in keys:
        results[key] = r.hgetall(key)
    return results

def save_draft_generator(url, xpath):
    return save_generic_generator('draft', url, xpath)

def save_generator(url, xpath):
    return save_generic_generator('generator', url, xpath)

def save_generic_generator(bucket, url, xpath):
    key = get_key(bucket, url)            
    with r.pipeline() as pipe:  # Start a pipeline (transaction)
        pipe.hset(key, 'url', url)           
        pipe.hset(key, 'xpath', xpath)           
        pipe.execute()
    return {id: key}
