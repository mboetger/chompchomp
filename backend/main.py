from celery import group
from fastapi import FastAPI

from data import Url, Aggregator, get_stats, get_urls, get_key, get_aggregator, get_aggregators, save_aggregator, save_draft_aggregator, validate_aggregator, validate_url_item, validate_url_id, get_url_data
from tasks import wayback, workflow, get_links, scrape, extract, keywords, sentiment, summarize, scan
from urllib.parse import unquote

app = FastAPI()

@app.get("/url/{item_id}")
async def read_item(item_id: str):
    id = unquote(item_id)    
    return get_url_data(id)    

@app.post("/url")
async def create_item(item: Url):       
    url = validate_url_item(item)          
    (scrape.s() | 
    group(
        extract.s() | 
        group(
            keywords.s(), 
            sentiment.s(),  
            summarize.s(),                       
        ),
        scan.s(),
        #ask_whois.s(),
    )).delay(url).forget()
    return {"message": "Item created",
            "id": get_key('url', url)}

@app.get("/urls")
async def url_list():
    return get_urls()

@app.get("/stats")
async def stats():
    return get_stats()

@app.get("/aggregator/{item_id}")   
async def aggregator(item_id: str):    
    return get_aggregator(unquote(item_id) )

@app.get("/aggregators")
async def aggregator_list():
    return get_aggregators()    

@app.post("/aggregator")
async def create_aggregator(aggregator: Aggregator):   
    validate_aggregator(aggregator)
    return save_aggregator(unquote(aggregator.url), unquote(aggregator.xpath))

@app.post("/test/aggregator")
async def test_aggregator(aggregator: Aggregator):   
    validate_aggregator(aggregator)
    return get_links((unquote(aggregator.url), unquote(aggregator.xpath)))    

@app.post("/draft/aggregator")
async def draft_aggregator(aggregator: Aggregator):   
    validate_aggregator(aggregator)
    return save_draft_aggregator(unquote(aggregator.url), unquote(aggregator.xpath))

@app.post("/workflow")
async def start_workflow():      
    workflow.s().delay().forget()
    return {"message": "Workflow started"}

@app.post("/wayback")
async def start_wayback():      
    wayback.s().delay().forget()
    return {"message": "Wayback started"}


