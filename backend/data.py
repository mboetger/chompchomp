import os
import datetime
import hashlib
import re
from urllib.parse import unquote
from pydantic import BaseModel
from pymongo import MongoClient
import numpy

buckets = ['url', 'extract', 'sentiment', 'keywords', 'scan', 'tech', 'headers']

# Set up MongoDB connection details from environment variables, with defaults
mongo_host = os.getenv('MONGO_HOST', 'localhost')
mongo_port = int(os.getenv('MONGO_PORT', 27017))
mongo_db_name = os.getenv('MONGO_DB', 'chompchomp')

# Connect to MongoDB
client = MongoClient(host=mongo_host, port=mongo_port)
db = client[mongo_db_name]

regex = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
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
    db.urls.update_one({'url': url}, 
                        {'$set': {'date': datetime.datetime.today()}}, 
                        upsert=True)

def sanitize(data):
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict):
                sanitize(v)
            elif isinstance(v, str):
                data[k] = v.strip()
            elif isinstance(v, numpy.float64):
                data[k] = str(v)
            elif isinstance(v, numpy.float32):
                data[k] = str(v) 
    elif isinstance(data, list): 
        for d in data:
            sanitize(d)
    elif isinstance(data, str):
        data = data.strip()
    elif isinstance(data, numpy.float64):
        data = str(data)
    elif isinstance(data, numpy.float32):
        data = str(data)  

def save_extraction(url, data):
    sanitize(data)
    db.urls.update_one(
        {'url': url}, 
        {'$set': { 'extract': data }},        
        upsert=True
    )


def save_sentiment(url, sentiment):
    sanitize(sentiment)
    db.urls.update_one(
        {'url': url}, 
        {'$set': {'sentiment': sentiment }},
        upsert=True
    )


def save_keywords(url, keywords):  
    sanitize(keywords)  
    db.urls.update_one(
        {'url': url}, 
        {'$set': {'keywords': keywords}},
        upsert=True
    )


def save_scan(url, report):
    tech = report['tech']
    if tech:
        sanitize(tech)
        db.urls.update_one(
            {'url': url}, 
            {'$set': { 'tech': tech}},
            upsert=True
        )
    headers = report['headers']
    if headers:
        sanitize(headers)
        db.urls.update_one(
            {'url': url}, 
            {'$set': {'headers': headers}},
            upsert=True
        )


def save_whois(domain, whois_info):
    print('unsupported')


def save_summary(url, summary):
    summary = sanitize(summary)
    db.urls.update_one(
        {'url': url}, 
        {'$set': {'summary': summary}},
        upsert=True
    )


class Url(BaseModel):
    url: str


def validate_url_item(item: Url):
    url = unquote(item.url)
    if not validate_url(url):
        return {"message": "Invalid URL"}
    return url

def get_url_data(id: str):    
    return db.urls.find_one({'_id': id})    

class Generator(BaseModel):
    url: str
    xpath: str

def validate_generator(generator: Generator):    
    generator.url = unquote(generator.url)
    if validate_url(generator.url):
        return {"message": "Invalid URL"}
    generator.xpath = unquote(generator.xpath)    
    return generator

def get_generator(id):
    return db.generators.find_one({'_id': id})

def get_generators():
    results = {}
    for doc in db.generators.find({'status': 'active'}):
        results[doc['_id']] = doc
    return results

def save_draft_generator(url, xpath):
    gen = db.generators.update_one(
        {'url': url},
        {'$set': {'url': url, 'xpath': xpath, 'status': 'draft'}},
        upsert=True
    )
    return {'_id': gen.upserted_id}


def save_generator(url, xpath):
    gen = db.generators.update_one(
        {'url': url},
        {'$set': {'url': url, 'xpath': xpath, 'status': 'active'}},
        upsert=True
    )
    return {'Message': 'Generator saved'}
