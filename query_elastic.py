import os
import subprocess
import pandas as pd
from tqdm import tqdm
from argparse import ArgumentParser
from elasticsearch import Elasticsearch
from tempfile import NamedTemporaryFile

def main(filename):
    es = Elasticsearch(hosts=['localhost'])

    quries = [
    'protein sequencing bacterial chemotaxis',
    'macrophage inflammatory protein gene biliary atresia',
    'gene tumor protein p53 activation',
    'inflammation oxidative stress human hepatic cells',
    'gene expression genetic deletion cd69 memory augmentation -brain',
    'ldlr gene cardiovascular disease',
    'gene expression photo transduction regulation calcium blind d melanogaster',
    'proteomic regulation calcium blind d melanogaster',
    'ob gene obese m musculus',
    'energy metabolism obese m musculus',
    'htt gene huntington disease',
    'neural brain tissue transgenic mice huntington disease',
    'snca gene parkinson disease',
    'nerve cells substantia nigra mice',
    'nf-κb signaling pathway mg myasthenia gravis patients'
    ]

    df_res = pd.DataFrame(columns=['query_id', 'q0', 'doc_id', 'rank', 'score', 'exp_name'])

    id = 0
    for qid, q in tqdm(enumerate(quries)):
        print(" -- query no: {}".format(qid+1))
        raw_result = es.search(
            index="biocaddie",
            size=1000,
            body={
                "query": {
                    "match":{
                        "body": "{}".format(q)
                    }
                }
            }
        )
        results = raw_result['hits']['hits']
        for id_res, res in enumerate(results):
            df_res.loc[id] = [qid+1, 'Q0', res['_id'], id_res+1, res['_score'], 'ES_TEST']
            id += 1

    df_res.to_csv(path_or_buf='results/query_results/{}'.format(filename), sep='\t', header=False, index=False)


if __name__ == "__main__":
    argp = ArgumentParser("Elastic Reader")
    argp.add_argument('-fn', '--filename', default='default_results') 
    args = argp.parse_args()
    main(args.filename)