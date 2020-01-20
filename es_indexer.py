from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError
from elasticsearch.helpers import bulk
from pathlib import Path
import json

es = Elasticsearch(hosts=[{'host': 'localhost', 'port': 9200}])
print(es.indices.get_alias('*'))

create_trec_index_body = {
    "settings" : {
        "number_of_shards": 1,
        "number_of_replicas": 1
    },

    'mappings': {
            'properties': {
                'ArticleTitle': {'type': 'text'},
                'AbstractText': {'type': 'text'},
                'MeshTerms': {'type': 'text'},
                'SubstanceNames': {'type': 'text'},
                'DocID': {'type': 'text'},
            }}
}

try:
    es.indices.create(index = 'trec', body = create_trec_index_body)
except RequestError:
    print("Index already exists")

print("Indicies:")
print(es.indices.get_alias('*'))

directory = Path('./results/jsons')
files = directory.glob('*.json')

for file_path in files:
    print('Indexing file', str(file_path))
    with open(file_path) as file:
        documents = json.load(file)

    for doc in documents:
        es.index(index='trec', id=doc["DocID"], body=doc)

def as_elastic_document(document):
    return {
        "_index": "trec",
        "_type": "document",
        "_id": document['DocID'],
        "doc": document
        }

def bulk_index(documents):
    body = map(as_elastic_document, documents)
    bulk(es, body)