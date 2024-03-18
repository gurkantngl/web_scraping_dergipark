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
        
        not_found = collection_name.find_one({"not_found": {"$exists": True}})
        if not_found is not None:
            return render(request, "not_found.html", {"not_found": not_found["not_found"]})
        
        types = list(set([doc['type'] for doc in collection_name.find({}, {'_id': 0, 'type': 1}) if 'type' in doc]))
        types.insert(0, "")
        
        authors = list(set([author for document in collection_name.find() for author in document.get("authors", [])]))
        authors.insert(0, "")
        
        keywords = list(set([keyword for document in collection_name.find() for keyword in document.get("keywords", [])]))
        keywords.insert(0, "")
        
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

        return render(request, "article_page.html", {"articles": articles, "keywords": keywords, "authors": authors, "types": types, "keyword": input_words})

    else:
        return HttpResponse("Error")

def filter(request):
    if request.method == "POST":
        keyword = request.POST.get("keyword", "")
        author = request.POST.get("author", "")
        type_value = request.POST.get("type", "")
        min_date = request.POST.get("min_date", "")
        max_date = request.POST.get("max_date", "")
        
        body = {
            "query": {
                "bool": {
                    "must" : []
                }
            }
        }
        
        if len(keyword) != 0:
            print("keyword filtresi")
            query = {
                    "bool": {
                        "filter": [
                            {
                                "term": {
                                    "keywords.keyword": keyword
                                }
                            }
                        ]
                    }
                }
            
            body["query"]["bool"]["must"].append(query)
        
        if len(author) != 0:
            print("author filtresi")
            query = {
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
            
            body["query"]["bool"]["must"].append(query)
        
        if len(type_value) != 0:
            print("type filtresi")
            query = {
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
            
            body["query"]["bool"]["must"].append(query)
            
        if len(min_date) != 0 and len(max_date) != 0:
            print("tarih filtresi")
            query = {
                    "range": {
                        "date": {
                            "gte": min_date,
                            "lte": max_date
                        }
                    }
                }
            
            body["query"]["bool"]["must"].append(query)
                
        client = MongoClient('127.0.0.1',27017)
        db = client.Yazlab2
        collection_name = db["Articles"]
        es = Elasticsearch('http://localhost:9200')        
        
        for document in collection_name.find():
            document_id = document.pop('_id') 
            es.index(index='filter_index', id=document_id, body=dumps(document))
                
        time.sleep(1)
        
        result = es.search(index='filter_index', body=body)
        
        for hit in result['hits']['hits']:
            print(type(hit['_source']))
        
        articles = result["hits"]["hits"]
        articles = [article["_source"] for article in articles]

        response = es.indices.delete(index="filter_index", ignore=[400, 404])        
        
        types = list(set([doc['type'] for doc in collection_name.find({}, {'_id': 0, 'type': 1}) if 'type' in doc]))
        types.insert(0, "")
        
        authors = list(set([author for document in collection_name.find() for author in document.get("authors", [])]))
        authors.insert(0, "")
        
        keywords = list(set([doc['keyword'] for doc in collection_name.find({}, {'_id': 0, 'keyword': 1}) if 'keyword' in doc]))
        keywords.insert(0, "")
        
        return render(request, 'article_page.html', {"articles": articles, "keywords": keywords, "authors": authors, "types": types})  

def sort(request):
    if request.method == 'POST':
        sortSelect = request.POST.get('sortSelect', '')
        incdec = request.POST.get('incdec', '')
        keyword = request.POST.get('keyword', '')
        
        client = MongoClient("127.0.0.1", 27017)
        db = client.Yazlab2
        collection_name = db["Articles"]
        es = Elasticsearch("http://localhost:9200")
        
        for document in collection_name.find():
            document_id = document.pop("_id")
            es.index(index="index", id=document_id, body=dumps(document))
        time.sleep(1)
        
        result = es.search(
            index="index",
            body={
                "query": {
                    "bool": {"filter": [{"term": {"keyword.keyword": keyword}}]}
                },
                "size": 10000,
            },
        )
        
        articles = result["hits"]["hits"]
        articles = [article["_source"] for article in articles]

        response = es.indices.delete(index="index", ignore=[400, 404])
        
        types = list(set([doc['type'] for doc in collection_name.find({}, {'_id': 0, 'type': 1}) if 'type' in doc]))
        types.insert(0, "")
        
        authors = list(set([author for document in collection_name.find() for author in document.get("authors", [])]))
        authors.insert(0, "")
        
        keywords = list(set([keyword for document in collection_name.find() for keyword in document.get("keywords", [])]))
        keywords.insert(0, "")
        
        if sortSelect == "Tarihe Göre":
            if incdec == "Artan":
                articles = sorted(articles, key=lambda x: x['date'])
                return render(request, 'article_page.html', {"articles": articles, "keywords": keywords, "authors": authors, "types": types})

            else:
                articles = sorted(articles, key=lambda x: x['date'], reverse=True)
                return render(request, 'article_page.html', {"articles": articles, "keywords": keywords, "authors": authors, "types": types})
            
        else:
            if incdec == "Artan":
                articles = sorted(articles, key=lambda x: x['citation'])
                return render(request, 'article_page.html', {"articles": articles, "keywords": keywords, "authors": authors, "types": types})

            else:
                articles = sorted(articles, key=lambda x: x['citation'], reverse=True)
                return render(request, 'article_page.html', {"articles": articles, "keywords": keywords, "authors": authors, "types": types})