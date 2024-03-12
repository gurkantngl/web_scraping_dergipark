from datetime import datetime
from bson.json_util import dumps
from pymongo import MongoClient
from elasticsearch import Elasticsearch
import time

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