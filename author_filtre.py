from datetime import datetime
from bson.json_util import dumps
from pymongo import MongoClient
from elasticsearch import Elasticsearch

client = MongoClient('127.0.0.1',27017)
db = client.Yazlab2
collection_name = db["Articles"]

es = Elasticsearch('http://localhost:9200')

author = "Makbule Damla Yılmaz"

result = es.search(index='author_filter', body={
   "query": {
        "bool": {
            "filter": [
                {
                    "terms": {
                        "authors": [author]
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