from datetime import datetime
from bson.json_util import dumps
from pymongo import MongoClient
from elasticsearch import Elasticsearch
import time

client = MongoClient('127.0.0.1',27017)
db = client.Yazlab2
collection_name = db["Articles"]

es = Elasticsearch(
                   ['http://localhost:9200'],
                   basic_auth=('elastic', 'HjpNEqc4I5NcOarsrJRN'),
                   )

start_year = "2000"
end_year = "2024"

for document in collection_name.find():
    document_id = document.pop('_id')
    print(document)
    es.index(index='date_filter', id=document_id, body=dumps(document))

# time.sleep(5)

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
print(result)
    
# response = es.indices.delete(index='date_filter', ignore=[400, 404])
# print(response)