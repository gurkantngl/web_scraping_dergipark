from datetime import datetime
from bson.json_util import dumps
from pymongo import MongoClient
from elasticsearch import Elasticsearch

client = MongoClient('127.0.0.1',27017)
db = client.Yazlab2
mongo_collection = db["Articles"]

es = Elasticsearch('http://localhost:9200')

type_value = "Araştırma Makalesi"


#Her veri atıldığnda çalışacak sadece :D:D:D:D
# MongoDB koleksiyonundaki belgeleri alın ve Elasticsearch endeksine ekleyin
for document in mongo_collection.find():
    document_id = document.pop('_id')
    es.index(index='type_filter', id=document_id, body=dumps(document))


result = es.search(index='type_filter', body={
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

for hit in result['hits']['hits']:
    try:
        print(hit['_source']['type'])
    except KeyError:
        continue
    
#indexi temizleme
response = es.delete_by_query(index='type_filter', body={"query": {"match_all": {}}})
print("Silinen Belgelerin Sayısı:", response['deleted'])