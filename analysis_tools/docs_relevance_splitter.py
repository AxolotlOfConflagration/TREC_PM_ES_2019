import pandas as pd
import progressbar
import os, json
import re

### TODO

widgets=[
        ' [', progressbar.Timer(), '] ',
        progressbar.Bar(),
        ' (', progressbar.ETA(), ') ',
        ]

def read_data():
    # read qrels
    df_qrels = pd.read_csv("../data/qrels", header=None, sep='\t')
    # read parsed data
    jsonp = '../data/update_json_folder'
    json_files = [pos_json for pos_json in os.listdir(jsonp) if pos_json.endswith('.json')]
    df_jsons_data = pd.DataFrame(columns=['DOCNO', 'TITLE'])

    for js in progressbar.progressbar(json_files, redirect_stdout=True, widgets=widgets):
        with open(os.path.join(jsonp, js)) as json_file:
            index = list(re.findall(r'\d+', js))[0]
            json_text = json.load(json_file)
            docid = json_text['DOCNO']
            title = json_text['TITLE']
            df_jsons_data.loc[index] = [docid, title]
    return df_qrels, df_jsons_data

df_qrels, df_jsons_data = read_data()