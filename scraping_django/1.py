from elasticsearch import Elasticsearch
from pymongo import MongoClient
from bson.json_util import dumps

client = MongoClient('127.0.0.1',27017)

db = client.Yazlab2

collection_name = db["Articles"]

# Elasticsearch'e bağlanın
es = Elasticsearch('http://localhost:9200')

#Her veri atıldığnda çalışacak sadece :D:D:D:D
# MongoDB koleksiyonundaki belgeleri alın ve Elasticsearch endeksine ekleyin
for document in collection_name.find():
    document_id = document.pop('_id')  # _id alanını belgeden çıkarın
    es.index(index='your_elasticsearch_index', id=document_id, body=dumps(document))

result = es.search(index='your_elasticsearch_index', body={
   "query": {
       "match_all": {}
   }
})  
print(result)
#response = es.delete_by_query(index='your_elasticsearch_index', body={"query": {"match_all": {}}})

# Silinen belgelerin sayısını yazdırın
#print("Silinen Belgelerin Sayısı:", response['deleted'])
# Sonuçları yazdırın
