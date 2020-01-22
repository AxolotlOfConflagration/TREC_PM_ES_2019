from elasticsearch import Elasticsearch

es = Elasticsearch(hosts=['localhost'])

### Search for all documents with 'trec' index 
raw_result = es.search(
    index="trec",
    body={
        "query": {
            "match_all": {}
        }
    }
)

### Search and display titles of documents connected to melanoma
raw_result = es.search(
    index="trec",
    body={
        "query": {
            "match":{
                "ArticleTitle": "melanoma"
            }
        }
    }
)

for res in raw_result["hits"]["hits"]:
    print(res["_source"]["ArticleTitle"])

### Other properties
# 'ArticleTitle': {'type': 'text'}
# 'AbstractText': {'type': 'text'}
# 'MeshTerms': {'type': 'text'}
# 'SubstanceNames': {'type': 'text'}
# 'DocID': {'type': 'text'}