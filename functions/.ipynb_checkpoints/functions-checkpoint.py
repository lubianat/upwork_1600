import requests
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd

import time
    

def make_string_of_qids_for_sparql(array_of_qids):
    string_of_qids_for_sparql = ""
    for qid in array_of_qids:
        string_of_qids_for_sparql += "wd:" + str(qid) + " "
    return(string_of_qids_for_sparql)


def return_instances_of_specific_qid(array_of_qids, instances_of_qid) :
    
    time.sleep(5)

    string_of_qids = make_string_of_qids_for_sparql(array_of_qids)
    SPARQL_QUERY = """
    SELECT DISTINCT ?item ?itemLabel 

    WHERE {
    VALUES ?item """ + "{"+ string_of_qids +"}" + """
    ?item wdt:P31 wd:"""  +   instances_of_qid + "." +  """
   OPTIONAL {?item rdfs:label ?itemLabel. #Create a label (aka name) for the items in WikiData, without using the service query. 
    FILTER(LANG(?itemLabel) = "en").
    }
    }

"""
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery(SPARQL_QUERY)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    results_df = pd.json_normalize(results['results']['bindings'])
    
    results_df = results_df.replace(regex=r'http://www.wikidata.org/entity/(\.*)', value=r'\1')
    results_df = results_df[['item.value', 'itemLabel.value']]
    results_df.columns = ['QID', 'title']
    return(results_df)
