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
    if request.method == "POST":
        input_words = request.POST.get("inputWords", "")

        scrapy_process = Process(target=run_scrapy, args=(input_words,))
        scrapy_process.start()
        scrapy_process.join()

        client = MongoClient("127.0.0.1", 27017)
        db = client.Yazlab2
        collection_name = db["Articles"]
        es = Elasticsearch("http://localhost:9200")
        
        types = list(set([doc['type'] for doc in collection_name.find({}, {'_id': 0, 'type': 1}) if 'type' in doc]))
        authors = list(set([author for document in collection_name.find() for author in document.get("authors", [])]))
        keywords = list(set([doc['keyword'] for doc in collection_name.find({}, {'_id': 0, 'keyword': 1}) if 'keyword' in doc]))
        
        for document in collection_name.find():
            document_id = document.pop("_id")
            es.index(index="index", id=document_id, body=dumps(document))
        time.sleep(1)

        result = es.search(
            index="index",
            body={
                "query": {
                    "bool": {"filter": [{"term": {"keyword.keyword": input_words}}]}
                },
                "size": 10000,
            },
        )

        articles = result["hits"]["hits"]
        articles = [article["_source"] for article in articles]

        response = es.indices.delete(index="index", ignore=[400, 404])

        return render(request, "article_page.html", {"articles": articles, "keywords": keywords, "authors": authors, "types": types})

    else:
        return HttpResponse("Error")

def filter(request):
    if request.method == "POST":
        keyword = request.POST.get("keyword", "")
        author = request.POST.get("author", "")
        type_value = request.POST.get("type", "")
        min_date = request.POST.get("min_date", "")
        max_date = request.POST.get("max_date", "")
        
        print(f"Keyword: {type(keyword)}, Author: {type(author)}, Type: {type(type_value)}, Min Date: {type(min_date)}, Max Date: {type(max_date)}")
        
        return HttpResponse(f"Keyword: {type(keyword)}, Author: {type(author)}, Type: {type(type_value)}, Min Date: {type(min_date)}, Max Date: {type(max_date)}")
   
    
def author_filter():
    client = MongoClient('127.0.0.1',27017)
    db = client.Yazlab2
    collection_name = db["Articles"]

    es = Elasticsearch('http://localhost:9200')

    author = "Elif TAŞDEMİR"

    for document in collection_name.find():
        document_id = document.pop('_id')
        es.index(index='author_filter', id=document_id, body=dumps(document))

    time.sleep(1)

    result = es.search(index='author_filter', body={
    "query": {
            "bool": {
                "filter": [
                    {
                        "term": {
                            "authors.keyword": author
                        }
                    }
                ]
            }
    }
    })

    for hit in result['hits']['hits']:
        try:
            print(hit['_source']['authors'])
        except KeyError:
            continue
        
    #indexi temizleme
    response = es.indices.delete(index='author_filter', ignore=[400, 404])
    print(response)
    
    
def publisher_filter():
    client = MongoClient('127.0.0.1',27017)
    db = client.Yazlab2
    collection_name = db["Articles"]

    es = Elasticsearch('http://localhost:9200')
    publisher = "Türkiye Sağlık Araştırmaları Dergisi"

    # index oluşturma
    for document in collection_name.find():
        document_id = document.pop('_id')
        es.index(index='publisher_filter', id=document_id, body=dumps(document))

    time.sleep(1)

    # filtreleme
    result = es.search(index='publisher_filter', body={
    "query": {
            "bool": {
                "filter": [
                    {
                        "term": {
                            "publisher.keyword": publisher
                        }
                    }
                ]
            }
    }
    })

    # sonuçları yazdırma
    for hit in result['hits']['hits']:
        try:
            print(hit['_source']['publisher'])
        except KeyError:
            continue

    # indexi temizleme
    response = es.indices.delete(index='publisher_filter', ignore=[400, 404])
    print(response)


def date_filter():
    client = MongoClient('127.0.0.1',27017)
    db = client.Yazlab2
    collection_name = db["Articles"]

    es = Elasticsearch('http://localhost:9200')

    start_year = 2010
    end_year = 2024

    for document in collection_name.find():
        document_id = document.pop('_id')
        es.index(index='date_filter', id=document_id, body=dumps(document))

    time.sleep(1)

    result = es.search(index='date_filter', body={
    "query": {
        "range": {
            "date": {
                "gte": start_year,
                "lte": end_year
            }
        }
    }
    })

    # Bulunan belgelerin tarihlerini yazdırma
    for hit in result['hits']['hits']:
        print(hit['_source']['date'])
        
    response = es.indices.delete(index='date_filter', ignore=[400, 404])
    print(response)  
    
def type_filter():
    client = MongoClient('127.0.0.1',27017)
    db = client.Yazlab2
    mongo_collection = db["Articles"]

    es = Elasticsearch('http://localhost:9200')

    type_value = "Araştırma Makalesi"


    for document in mongo_collection.find():
        document_id = document.pop('_id')
        es.index(index='type_filter', id=document_id, body=dumps(document))

    time.sleep(1)

    result = es.search(index='type_filter', body={
    "query": {
            "bool": {
                "filter": [
                    {
                        "term": {
                            "type.keyword": type_value
                        }
                    }
                ]
            }
    }
    })

    for hit in result['hits']['hits']:
        try:
            print(hit['_source']['type'])
        except KeyError:
            continue
        
    # indexi temizleme
    response = es.indices.delete(index='type_filter', ignore=[400, 404])
    print(response)