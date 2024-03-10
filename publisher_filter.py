from datetime import datetime
from bson.json_util import dumps
from pymongo import MongoClient
from elasticsearch import Elasticsearch

client = MongoClient('127.0.0.1',27017)
db = client.Yazlab2
collection_name = db["Articles"]

es = Elasticsearch('http://localhost:9200')

publisher = "Computers and Informatics"

result = es.search(index='your_elasticsearch_index', body={
   "query": {
        "bool": {
            "must": [
                {
                    "match": {
                        "publisher": publisher
                    }
                }
            ]
        }
       
   }
})

for hit in result['hits']['hits']:
    try:
        print(hit['_source']['publisher'])
    except KeyError:
        continue