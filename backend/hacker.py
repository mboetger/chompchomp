"""
This script uses Celery to orchestrate a series of tasks for scraping and extracting news links from Hacker News.

Modules:
    celery: Celery is an asynchronous task queue/job queue based on distributed message passing.
    tasks: Custom module containing task definitions for scraping, extracting, and getting news links.
    os: Provides a way of using operating system dependent functionality.

Functions:
    group: Celery function to create a group of tasks that can be executed in parallel.

Environment Variables:
    BROKER_URL: URL for the message broker (default: 'redis://localhost:6379/0').

Celery Configuration:
    broker_url: URL for the message broker.
    backend: URL for the result backend.
    broker_transport_options: Dictionary containing transport options for the broker (e.g., visibility_timeout).

Task Flow:
    1. Get links from Hacker News using the get_links function.
    2. For each link, create a chain of tasks: scrap followed by extract.
    3. Execute the group of chained tasks in parallel and immediately forget the results.
"""
from celery import Celery, group
from tasks import scrape, extract, get_links, keywords, sentiment, scan, ask_whois, summarize
import os
import sys

# Set the broker URL from the environment variable 'BROKER_URL' or use the default value.
broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
backend_url = os.getenv('CELERY_BACKEND_URL', 'redis://localhost:6379/0')

# Initialize the Celery application with the broker and backend URLs.
app = Celery('news', broker=broker_url, backend=backend_url)

# Configure the broker transport options, setting the visibility timeout to 1 hour.
app.conf.broker_transport_options = {'visibility_timeout': 3600}  # 1 hour.

targets = {}
base_url = 'https://news.ycombinator.com/?p='
xpath = '//*[@class="titleline"]/a'

# Populate the targets dictionary using a loop
for i in range(31):
    if i == 0:
        targets['https://news.ycombinator.com/'] = xpath
    else:
        targets[f'{base_url}{i}'] = xpath

# Create a group of tasks where each task is a chain of 'scrap' followed by 'extract'.
# The 'scrap' task scrapes the content of the link, and the 'extract' task extracts the necessary information.
# The 'get_links' function fetches the list of links from the specified target URL using the given XPath.
# The group of chained tasks is executed in parallel and the results are immediately forgotten.
def main(targets=targets):
    links = group(get_links.s(item) for item in targets.items())
    for links_list in links.delay().get():
        for link in links_list:
            (scrape.s(link) | 
                group(
                    extract.s() | 
                    group(
                        keywords.s(), 
                        sentiment.s(),  
                        summarize.s(),                       
                    ),
                    scan.s(),
                    #ask_whois.s(),
                )).delay().forget()
    
if __name__ == "__main__":
    if '-t' in sys.argv or '--test' in sys.argv:
        first_key = next(iter(targets))
        first_value = targets[first_key]
        main({first_key: first_value})        
    if '-w' in sys.argv or '--wayback' in sys.argv:
        first_key = next(iter(targets))
        first_value = targets[first_key]
        print('Wayback Machine')
    else:
        main(targets)





