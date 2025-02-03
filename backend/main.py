import datetime
import hashlib
import os
import re
import redis

from celery import group
from fastapi import FastAPI
from pydantic import BaseModel
from tasks import workflow, get_links, scrape, extract, keywords, sentiment, summarize, scan
from urllib.parse import unquote


# Set the broker URL from the environment variable 'BROKER_URL' or use the default value.
broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
backend_url = os.getenv('CELERY_BACKEND_URL', 'redis://localhost:6379/0')

app = FastAPI()

def isValidMd5(to_test): 
    return re.fullmatch('^[a-f0-9]{32}$', to_test) is not None

buckets = ['url','extract', 'sentiment', 'keywords','scan', 'tech', 'headers']

# Set up Redis connection details from environment variables, with defaults
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = os.getenv('REDIS_PORT', 6379)
redis_db = os.getenv('REDIS_DB', 1)

# Connect to Redis for more persistent saves
r = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

def get_key(prefix, url):       
    if isValidMd5(url):                
        return prefix + ":" + url
    else:              
        hash_url = hashlib.md5(url.encode()).hexdigest()        
        return prefix + ":" + hash_url

regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

def validate_url(url):
    return re.match(regex, url) is not None

class Item(BaseModel):
    url: str    

@app.get("/url/{item_id}")
async def read_item(item_id: str):
    url = unquote(item_id)
    data = {}
    for bucket in buckets:
        key = get_key(bucket, url)        
        data[bucket] = r.hgetall(key)
    return data

@app.get("/urls")
async def read_items():
    url = unquote(item_id)
    data = {}
    for bucket in buckets:
        key = get_key(bucket, url)        
        data[bucket] = r.hgetall(key)
    return data

@app.post("/url")
async def create_item(item: Item):       
    if validate_url(item.url):
        return {"message": "Invalid URL"}    
    url = unquote(item.url)    
    
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

    process_url.delay(url).forget()
    return {"message": "Item created",
            "id": get_key('url', url)}

@app.get("/generator/{item_id}")   
async def generator(item_id: str):
    url = unquote(item_id) 
    key = get_key('generator', url)        
    return r.hgetall(key)

@app.get("/generators")
async def generator_list():
    results = {}
    keys = r.keys('generator:*')
    for key in keys:
        results[key] = r.hgetall(key)
    return results

@app.post("/generator/{item_id}/{xpath}")
async def create_generator(item_id: str, xpath: str):   
    if validate_url(item_id):
        return {"message": "Invalid URL"}
    
    url = unquote(item_id)
    key = get_key('generator', url)            
    with r.pipeline() as pipe:  # Start a pipeline (transaction)
        pipe.hset(key, 'url', url)           
        pipe.hset(key, 'xpath', unquote(xpath))           
        pipe.execute()
    return {"message": "Generator created"}

@app.post("/test/generator/{item_id}/{xpath}")
async def test_generator(item_id: str, xpath: str):   
    if validate_url(item_id):
        return {"message": "Invalid URL"}
    
    url = unquote(item_id)
    xpath = unquote(xpath)
    return get_links((url, xpath))    

@app.post("/draft/generator/{item_id}/{xpath}")
async def draft_generator(item_id: str, xpath: str):   
    if validate_url(item_id):
        return {"message": "Invalid URL"}
    
    url = unquote(item_id)
    key = get_key('draft', url)            
    with r.pipeline() as pipe:  # Start a pipeline (transaction)
        pipe.hset(key, 'url', url)           
        pipe.hset(key, 'xpath', unquote(xpath))           
        pipe.execute()
    return {"message": "Draft generator created"}

@app.post("/workflow")
async def start_workflow():      
    workflow.s().delay().forget()
    return {"message": "Workflow started"}


