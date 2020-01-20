import os
import subprocess
from elasticsearch import Elasticsearch
from tempfile import NamedTemporaryFile

es = Elasticsearch(hosts=['localhost'])
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

### Prepare files for trec_eval
qrels_fp = ""
treceval_fp = "trec_eval-9.0.7/trec_eval"

result = {}
result["melanoma_query"] = raw_result['hits']['hits']

with NamedTemporaryFile(delete=False, mode='w') as tmp:
    tmp_fn = tmp.name
    for q_id, docs in sorted(result.items()):
        for i, doc in enumerate(docs):
            tmp.write('{q_id} 0 {d_id} {i} {score:.5f} TREC_DEMO\n'.format( \
                q_id=q_id, d_id=doc['_id'], i=i, score=doc['_score']))

if not os.path.exists(treceval_fp):
    platform_name = platform.system()
    treceval_fp ='{}_{}'.format(treceval_fp, platform_name)

cmd = ['./{}'.format(treceval_fp), qrels_fp, tmp_fn]

try:
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    resp = proc.communicate()
    msg_out, msg_err = (msg.decode('utf-8') for msg in resp)
except Exception:
    raise
finally:
    os.remove(tmp_fn)

if msg_err:
    raise OSError(msg_err)

print(msg_out.strip())