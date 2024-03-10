from elasticsearch import Elasticsearch
from pymongo import MongoClient
from bson.json_util import dumps
import time

client = MongoClient('127.0.0.1',27017)
db = client.Yazlab2
collection_name = db["Articles"]
es = Elasticsearch(
                   ['http://localhost:9200'],
                   http_auth=('elastic', 'HjpNEqc4I5NcOarsrJRN'),
)

for document in collection_name.find():
    document_id = document.pop('_id')
    es.index(index='your_elasticsearch_index', id=document_id, body=dumps(document))

time.sleep(3)

result = es.search(index='your_elasticsearch_index', body={
   "query": {
       "match_all": {}
   }
})  
print(result)

response = es.indices.delete(index='your_elasticsearch_index', ignore=[400, 404])
print(response)