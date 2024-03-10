from datetime import datetime
from bson.json_util import dumps
from pymongo import MongoClient
from elasticsearch import Elasticsearch

client = MongoClient('127.0.0.1',27017)
db = client.Yazlab2
collection_name = db["Articles"]

es = Elasticsearch('http://localhost:9200')

type_value = "Araştırma Makalesi"

result = es.search(index='your_elasticsearch_index', body={
   "query": {
        "bool": {
            "must": [
                {
                    "match": {
                        "type": type_value
                    }
                }
            ]
        }
       
   }
})

# Bulunan belgelerin tarihlerini yazdırma
for hit in result['hits']['hits']:
    try:
        print(hit['_source']['type'])
    except KeyError:
        continue