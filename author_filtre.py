from datetime import datetime
from bson.json_util import dumps
from pymongo import MongoClient
from elasticsearch import Elasticsearch
import time

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