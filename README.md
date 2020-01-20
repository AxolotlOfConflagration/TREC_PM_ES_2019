# TREC_PM_ES_2019
## Prepare environment
### Requirements

* Python3
* Linux (tested only on Linux based operating systems)

### Run ElasticSearch

* Modify file permissions with chmod - `scripts/run_elasticsearch.sh` file.
* Run script: `./scripts/run_elasticsearch.sh`

### Create Python virtual environment

```bash
pip install virtualenv
virtualenv venv
source venv/bin/activate
```

### Download and compile trec_eval

```bash
./scripts/download_trec_eval.sh
```

## Load TREC PM data to ElasticSearch

```bash
python trec_parser.py
python es_indexer.py
```

## Quering ElasticSearch

Example in: `es_reader.py` file.

## Evaluating results with trec_eval

Example in: `es_reader_trec_eval.py` file.