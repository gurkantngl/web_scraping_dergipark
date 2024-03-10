from elasticsearch import Elasticsearch
from pymongo import MongoClient

es = Elasticsearch(['http://localhost:9200'])
mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['Yazlab2']
mongo_collection = mongo_db['Articles']

index_name = 'your_elasticsearch_index'
mapping = {
    'mappings': {
        'properties': {
            'type': {'type': 'text'},
            'title':{'type':'text'},
            'link' : {'type':'text'},
            'authors' : {
                'type' : 'nested',
                'properties' : {
                    'author' : {'type' : 'text'},
                },
            },
            'date' : {"type":"text"},
            'publisher' : {"type":"text"},
            'doi' : {"type":"text"},
        }
    }
}

es.indices.create(index=index_name, body=mapping, ignore=400)

for document in mongo_collection.find():
    es.index(index=index_name, body=document)

type = 'Araştırma Makalesi'
query = {
    'query': {
        'match': {
            'type': type
        }
    }
}

result = es.search(index=index_name, body=query)
for hit in result['hits']['hits']:
    try:
        print(hit['_source']['type'])
    except KeyError:
        continue
