from celery import group
from fastapi import FastAPI

from data import Url, Generator, get_key, get_generator, get_generators, save_generator, save_draft_generator, validate_generator, validate_url_item, validate_url_id, get_url_data
from tasks import workflow, get_links, scrape, extract, keywords, sentiment, summarize, scan
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

@app.get("/generator/{item_id}")   
async def generator(item_id: str):    
    return get_generator(unquote(item_id) )

@app.get("/generators")
async def generator_list():
    return get_generators()    

@app.post("/generator")
async def create_generator(generator: Generator):   
    validate_generator(generator)
    return save_generator(generator.url, generator.xpath)

@app.post("/test/generator")
async def test_generator(generator: Generator):   
    generator = validate_generator(generator)
    return get_links((generator.url, generator.xpath))    

@app.post("/draft/generator")
async def draft_generator(generator: Generator):   
    generator = validate_generator(generator)
    return save_draft_generator(generator.url, generator.xpath)

@app.post("/workflow")
async def start_workflow():      
    workflow.s().delay().forget()
    return {"message": "Workflow started"}


