from datetime import datetime
from bson.json_util import dumps
from pymongo import MongoClient
from elasticsearch import Elasticsearch

client = MongoClient('127.0.0.1',27017)
db = client.Yazlab2
collection_name = db["Articles"]

es = Elasticsearch()

publisher = "Computers and Informatics"

# index oluşturma
for document in collection_name.find():
    document_id = document.pop('_id')
    es.index(index='publisher_filter', id=document_id, body=dumps(document))

# filtreleme
result = es.search(index='publisher_filter', body={
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

# sonuçları yazdırma
for hit in result['hits']['hits']:
    try:
        print(hit['_source']['publisher'])
    except KeyError:
        continue

# indexi temizleme
response = es.indices.delete(index='publisher_filter', ignore=[400, 404])
print(response)