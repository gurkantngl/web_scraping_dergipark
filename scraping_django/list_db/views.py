from django.shortcuts import render
from elasticsearch import Elasticsearch
from pymongo import MongoClient
from bson.json_util import dumps
import time

def list_db(request):
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
            "match_all": {}
        },
        "size": 10000
    })
    
    articles = result['hits']['hits']
    articles = [article['_source'] for article in articles]
    print("length: ",len(articles))
    
    response = es.indices.delete(index='index', ignore=[400, 404])
    print("response: ",response)

    return render(request, 'article_page.html', {'articles': articles})