from django.shortcuts import render
from django.http import HttpResponse
from scrapy.crawler import CrawlerProcess
from scholar.scholar.spiders import articles
from scrapy.utils.project import get_project_settings
from multiprocessing import Process
from elasticsearch import Elasticsearch
from pymongo import MongoClient
from bson.json_util import dumps
import time

def run_scrapy(input_words):
    process = CrawlerProcess(get_project_settings())
    process.crawl(articles.ArticlesSpider, keyword=input_words)
    process.start()
    process.join()

def search(request):
    print("search çalıştı")
    if request.method == 'POST':
        input_words = request.POST.get('inputWords', '')

        scrapy_process = Process(target=run_scrapy, args=(input_words,))
        scrapy_process.start()
        scrapy_process.join()

        client = MongoClient('127.0.0.1',27017)
        db = client.Yazlab2
        collection_name = db["Articles"]
        es = Elasticsearch('http://localhost:9200')
        
        for document in collection_name.find():
            document_id = document.pop('_id')
            es.index(index='index', id=document_id, body=dumps(document))


        time.sleep(1)
        
        result = es.search(index='index', body={
            "query": {
                "bool": {
                    "filter": [
                        {
                            "term": {
                                "keyword.keyword": input_words
                            }
                        }
                    ]
                }
        } ,
            "size": 10000
        })
        
        articles = result['hits']['hits']
        articles = [article['_source'] for article in articles]
        print("length: ",len(articles))
        
        response = es.indices.delete(index='index', ignore=[400, 404])
        print("response: ",response)

        return render(request, 'article_page.html', {'articles': articles})
    
    else:
        return HttpResponse("Error")