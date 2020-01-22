# TREC_PM_ES_2019
## Prepare environment
### Requirements

* Python3
* Linux (tested only on Linux based operating systems)

### Run ElasticSearch

* Modify file permissions with chmod - `scripts/run_elasticsearch.sh` file.
* Run script: `./scripts/run_elasticsearch.sh`

*Or*

* Run `sh scripts/get_elastic.sh`
* Run `sh scripts/run_elastic.sh`

### Create Python virtual environment

```bash
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Load bioCaddie data to ElasticSearch

First download this file: [bioCaddie data](https://drive.google.com/open?id=1dnOAgOd_-IC2flZBXMJm0STPy9SATbd2) and unpack this in your system. The unpacked folder contains about 3.1 GB of data. You can have these files in any direcotry, but by default the script uses the directory `../docs/` when current woring directory in the project root directory. The `docs` should contain XML files with names like `1`,`2`, `3`,... and so on. 

Now just run the Python script:
```bash
python index_documents.py <documents-directory>
```
The parameter `<documents-directory>` is optional. It is only required if you placed the data in other place then described above.

This scripts creates index of name: `biocaddie`. Use it to query the indexed documents.

Wait few minutes (on my machine it was around 2-3 minutes). The output should look like this:
```
2020-01-22 20:32:28,098|Reading documents
2020-01-22 20:32:30,267|Executing indexing
2020-01-22 20:34:46,869|Sucesses: 794992, Errors: 0
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

qrels for Trec Eval are in directory `data`. 
These files are taken from official [Trec2018](https://trec.nist.gov/data/precmed2018.html) website.
