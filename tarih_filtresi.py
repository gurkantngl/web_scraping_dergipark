from datetime import datetime
from bson.json_util import dumps
from pymongo import MongoClient
from elasticsearch import Elasticsearch

client = MongoClient('127.0.0.1',27017)
db = client.Yazlab2
collection_name = db["Articles"]

es = Elasticsearch('http://localhost:9200')

start_year = 2019
end_year = 2020

result = es.search(index='your_elasticsearch_index', body={
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
    try:
        print(hit['_source']['date'])
    except KeyError:
        continue