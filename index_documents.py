import itertools
import functools
import logging
import os
import re
from argparse import ArgumentParser
from multiprocessing import Pool
from pathlib import Path

from elasticsearch import Elasticsearch, RequestError, helpers

DOC_ID_REGEX = re.compile(r"<docid>(?P<docid>\d+)</docid>")
es = Elasticsearch(hosts=[{'host': 'localhost', 'port': 9200}])


def worker(args):
    documents_paths, doc_modifier = args
    parsed_docs = xml_reader(documents_paths, doc_modifier)
    elastic_docs = map(as_elastic_index, parsed_docs)

    success, errors = helpers.bulk(es, elastic_docs, yield_ok=False, chunk_size=250, stats_only=True)
    return success, errors

def as_elastic_index(doc):
    return {
        "_index": "biocaddie",
        "_id": doc['docid'],
        "_source": doc
    }


def xml_to_json(xml_iterator):
    result = {}

    for line in xml_iterator:
        line: str = line.strip()
        if line.startswith('<docid>'):
            match = DOC_ID_REGEX.match(line)
            result['docid'] = match.group('docid')
        elif line.startswith('<body>'):
            body = line[6:-7].strip().replace("  ", " ")
            result['body'] = body

    return result


def xml_reader(documents_paths, doc_modifier=None):
    documents_read = 0

    for documents_path in documents_paths:
        with open(documents_path) as file:
            json_doc = xml_to_json(file)
        
        documents_read += 1
        if documents_read % 250 == 0:
            logging.info(f"Worker {os.getpid()} read {documents_read} documents")
        
        if doc_modifier is not None:
            json_doc = doc_modifier(json_doc)

        yield json_doc


def split_docs(documents_paths, workers):
    results = []
    documents_paths = list(documents_paths)
    for start in range(workers):
        result = documents_paths[start::workers]
        results.append(result)

    return results


def main(documents_directory, workers):
    logger = logging.getLogger('main')
    logger.setLevel(logging.INFO)
    logger.propagate = False
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter("%(asctime)s|%(message)s"))
    logger.addHandler(sh)

    logger.info("Reading documents")
    documents_directory = Path(documents_directory)
    documents_paths = documents_directory.glob('*')
    splited_docs = split_docs(documents_paths, workers)

    doc_modifier = None # Replace with function (dict) -> dict
    modifiers = itertools.repeat(doc_modifier, workers)
    workers_args = zip(splited_docs, modifiers)

    logger.info("Executing indexing")
    with Pool(workers) as pool:
        results = pool.map(worker, workers_args)
    
    tuple_sum = lambda acc, val: (acc[0]+val[0], acc[1]++val[1])
    sucesses, errors =functools.reduce(tuple_sum, results, (0,0))
    logger.info(f"Sucesses: {sucesses}, Errors: {errors}")

if __name__ == "__main__":
    argp = ArgumentParser("Elastic Indexer")
    argp.add_argument('dir', nargs='?', default='../docs')
    # Don't use more then default=1, otherwise it behaves funky
    argp.add_argument('-w', '--workers', default=1) 
    args = argp.parse_args()

    create_index_body = {
        'settings': {
            'number_of_shards': 1,
            'number_of_replicas': 1
        },

        'mappings': {
            'properties': {
                'docid': {'type': 'text'},
                'body': {'type': 'text'},
            }
        }
    }
    try:
        es.indices.create(index='biocaddie', body=create_index_body)
    except RequestError:
        print("Index already exists")

    logging.basicConfig(level=logging.WARN) # Change to INFO for more logging
    main(args.dir, args.workers)
