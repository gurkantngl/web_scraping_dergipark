from elasticsearch import Elasticsearch
from pymongo import MongoClient
from bson.json_util import dumps
import time

client = MongoClient('127.0.0.1',27017)
db = client.Yazlab2
collection_name = db["Articles"]
es = Elasticsearch('http://localhost:9200')


#Her veri atıldığnda çalışacak sadece :D:D:D:D
# MongoDB koleksiyonundaki belgeleri alın ve Elasticsearch endeksine ekleyin
for document in collection_name.find():
    document_id = document.pop('_id')  # _id alanını belgeden çıkarın
    es.index(index='your_elasticsearch_index', id=document_id, body=dumps(document))

time.sleep(1)

result = es.search(index='your_elasticsearch_index', body={
   "query": {
       "match_all": {}
   }
})

print(type(result['hits']['hits']))
# Sonuçları yazdırın
# print("Arama Sonuçları:")
# for hit in result['hits']['hits']:
#     print(type(hit['_source']))

response = es.indices.delete(index='your_elasticsearch_index', ignore=[400, 404])# Silinen belgelerin sayısını yazdırın
print("Silinen Belgelerin Sayısı:", response)
