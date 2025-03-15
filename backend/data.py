from enum import Enum
import os
from datetime import datetime, timedelta
import hashlib
import re
from urllib.parse import unquote
from pydantic import BaseModel
from pymongo import MongoClient, DESCENDING
import numpy
from bson.objectid import ObjectId

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

def should_ask_whois(domain):
    return not db.domains.find_one({'domain': domain, 'date': { "$gte": datetime.today() - timedelta(days=1) }})

def should_scrape(url):
    return not db.urls.find_one({'url': url, 'date': { "$gte": datetime.today() - timedelta(days=1) }})

def save_url(url: str):
    db.urls.update_one({'url': url}, 
                        {'$set': {'date': datetime.today()}}, 
                        upsert=True)

def sanitize(data):
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict):
                sanitize(v)
            elif isinstance(v, numpy.float64):
                data[k] = str(v)
            elif isinstance(v, numpy.float32):
                data[k] = str(v) 
    elif isinstance(data, list): 
        for d in data:
            sanitize(d)
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
    db.domains.update_one(
        {'domain': domain},
        {'date': datetime.today()},
        {'$set': {'whois': whois_info}},
        upsert=True
    )


def save_summary(url, summary):
    db.urls.update_one(
        {'url': url}, 
        {'$set': {'summary': summary}},
        upsert=True
    )

class Url(BaseModel):
    url: str

class OrderBy(str, Enum):    
    published = "date_published"
    scanned = "date_scanned"

def validate_url_item(item: Url):
    url = unquote(item.url)
    if not validate_url(url):
        return {"message": "Invalid URL"}
    return url

def get_url_by_url(url: str):
    return db.urls.find_one({'url': url})

def get_url_data(id: str):    
    results = list(db.urls.aggregate([
        {"$match": {
            "_id": ObjectId(id),
        }},
        {'$sort': {'date': DESCENDING}},
        {'$project': {
            "_id": {"$toString": "$_id"},
            "url": 1,
            "date": 1,
            "extract.title": 1,
            "extract.headline": 1,
            "extract.content": 1,
            "extract.author": 1,
            "extract.date": 1,
            "keywords": 1,
            "sentiment": 1,
            "tech": 1,
            "summary": 1,

        }},
        {'$limit': 1}
    ]))
    return results[0] if results else None

def get_url_list():
    return [
        {
            '$project': {
                "_id": {"$toString": "$_id"},
                "url": 1,
                "date": 1,
                "extract.title": 1,
                "extract.headline": 1,
                "extract.date": 1,
                "summary": 1,
            }
        },        
    ]

def get_urls(date:str =None, query:str =None, sort_by: OrderBy = OrderBy.published):
    pipeline = []
    
    if date:
        if sort_by == OrderBy.scanned:
            begin = datetime.strptime(date, "%Y-%m-%d")
            end = begin + timedelta(days=1)
            pipeline.append({
                "$match": {
                    "date": {
                        "$gte": begin,
                        "$lt": end
                    }
                }
            })
        else:
            pipeline.append({
                "$match": {
                    "extract.date": {
                        "$eq": datetime.strptime(date, "%Y-%m-%d")
                    }
                }
            })
    
    if query:
        keywords = query.split(' ')
        pipeline.append({
            "$match": {
                "keywords.0": {
                    "$exists": True
                },
                "$or": [
                    {"keywords": {"$elemMatch": {"0": {"$regex": word, "$options": "i"}}}} for word in keywords
                ]                
            }
        })
    
    
    pipeline += get_url_list()

    if sort_by == OrderBy.published:
        pipeline += get_sort_by_published()
    else:
        pipeline += get_sort_by_scanned()

    pipeline += [{'$limit': 50}]

    return list(db.urls.aggregate(pipeline))

def get_sort_by_scanned():
    return [
        {
            "$match": {
                "extract": { "$exists": True }
            }
        },
        {
            '$sort': {
                'date': DESCENDING
            }
        },
    ]

def get_sort_by_published(): 
    return [        
        {
            "$match": {
                "extract.date": { "$exists": True }
            }
        },        
        {
            "$match": {
                "extract.date": {
                    "$lte": datetime.utcnow(),
                }
            }
        },        
        {'$sort': {'extract.date': -1}},            
    ]

def get_url_counts():
    return list(db.urls.aggregate([  			
        {
            "$project": {
                "yearMonthDay": { "$dateToString": { "format": "%Y-%m-%d", "date": "$date" } },
            }
        },
        {
            "$group": {
                "_id": "$yearMonthDay",
                "count": {
                    "$sum": 1
                }
            }
        },
        {
            "$sort": {
                "_id": -1
            }
        },
        {'$limit': 100}
    ]))

def get_url_counts_by_date():
    return list(db.urls.aggregate([
        {
            "$match": {
                "extract.date": {
                    "$not": {
                        "$size": 0
                    }
                }
            }
        },
        {
            "$addFields": {
                "dConfidence": {
                    "$toDecimal": "$extract.dateConfidence"
                }
            }
        },
        {
            "$match": {
                "dConfidence": {
                    "$gte": 0.04
                }
            }
        },
        {
            "$group": {
                "_id": "$extract.date",
                "count": {
                    "$sum": 1
                }
            }
        },
        {
            "$match": {
                "_id": {
                    "$lte": datetime.utcnow()
                }
            }
        },
        {
            "$match": {
               "count": {
                    "$gt": 3
                }
            }
        },
        {
            "$sort": {
                "_id": -1
            }
        }
    ]))

def get_urls_with_date():
    return list(db.urls.aggregate([{
        "$group": { 
        "_id": { "hasValue": { "$exists": True } },
        "count": { "$sum": 1 }
    }
  }]))

def get_stats():
    results = {}
    urls = {}
    urls['count'] = db.urls.count_documents({'extract': { '$exists': True }})
    urls['with_date'] = list(db.urls.aggregate([{
        '$match': {
            "extract.date": {
                '$not': {
                '$size': 0
                }
            }
        }
    },
    {
        '$addFields':      
        {
            'dConfidence': {
            '$toDecimal': "$extract.dateConfidence"
            }
        }
    },
    {
        '$match':     
        {
            'dConfidence': {
            '$gte': 0.04
            }
        }
    },
    {
        '$group': {
                '_id': None,     
        'count': {
            '$sum': 1
        }
        }
    }
    ]))[0]['count']    
    results['urls'] = urls
    aggregators = {}
    aggregators['active_count'] = db.aggregators.count_documents({'status': 'active'})
    aggregators['draft_count'] = db.aggregators.count_documents({'status': 'draft'})
    results['aggregators'] = aggregators
    return results

class Aggregator(BaseModel):
    url: str
    xpath: str

def validate_aggregator(aggregator: Aggregator):    
    aggregator.url = unquote(aggregator.url)
    if validate_url(aggregator.url):
        return {"message": "Invalid URL"}

def get_aggregator(id):
    return db.aggregators.find_one({'_id': id})

def get_aggregators():
    results = {}
    for doc in db.aggregators.find({'status': 'active'}):
        results[doc['_id']] = doc
    return results

def save_draft_aggregator(url, xpath):
    gen = db.aggregators.update_one(
        {'url': url},
        {'$set': {'url': url, 'xpath': xpath, 'status': 'draft'}},
        upsert=True
    )
    return {'_id': gen.upserted_id}


def save_aggregator(url, xpath):
    gen = db.aggregators.update_one(
        {'url': url},
        {'$set': {'url': url, 'xpath': xpath, 'status': 'active'}},
        upsert=True
    )
    return {'Message': 'aggregator saved'}
