import requests
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd

import time
    

def return_data_about_humans(array_of_qids) :
    time.sleep(1)

    string_of_qids = make_string_of_qids_for_sparql(array_of_qids)
    SPARQL_QUERY = """
    SELECT DISTINCT ?item ?itemLabel ?birth ?death ?birthplaceLabel  ?coordinate 

    WHERE {
    VALUES ?item """ + "{"+ string_of_qids +"}" + """
    ?item wdt:P31 wd:Q5.
    OPTIONAL{?item wdt:P569 ?birth.} 
    OPTIONAL{?item wdt:P570 ?death.}
    OPTIONAL{?item wdt:P19 ?birthplace.
            ?birthplace wdt:P625 ?coordinate.} 

    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    }


    """
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery(SPARQL_QUERY)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    results_df = pd.json_normalize(results['results']['bindings'])

    results_df = results_df.replace(regex=r'http://www.wikidata.org/entity/(\.*)', value=r'\1')
    results_df = results_df[['item.value', 'itemLabel.value', 'birth.value', 'birthplaceLabel.value', 'coordinate.value', 'death.value']]

    results_df.columns = ['wikidata_id', 'label', 'birth_date', 'birthplace', 'birthplace_coordinate', 'death_date']

    return(results_df)


def make_string_of_qids_for_sparql(array_of_qids):
    string_of_qids_for_sparql = ""
    for qid in array_of_qids:
        string_of_qids_for_sparql += "wd:" + str(qid) + " "
    return(string_of_qids_for_sparql)


def add_ids_and_urls_to_dataframe(links_df):
    titles = "|".join(links_df["*"])
    query = "https://en.wikipedia.org/w/api.php?action=query&prop=pageprops&ppprop=wikibase_item&redirects=1&titles="+titles+"&format=json"
    wdi = requests.get(query)

    urls_dict = {}
    urls_id = {}
    wikidata_ids = {}

    for i in wdi.json()['query']['pages']:
        link = (wdi.json()['query']['pages'][i])
        hyperlink_title = link["title"]
        hyperlink_url = "https://en.wikipedia.org/wiki/" + link["title"]
        hyperlink_page_id = link["pageid"]

        wikidata_id = link['pageprops']['wikibase_item']

        urls_dict[hyperlink_title] = hyperlink_url
        urls_id[hyperlink_title] = hyperlink_page_id
        wikidata_ids[hyperlink_title] = wikidata_id

    links_df["page_url"] = links_df["*"].map(urls_dict)
    links_df["page_id"] = links_df["*"].map(urls_id)
    links_df["wikidata_id"] = links_df["*"].map(wikidata_ids)
    
    return(links_df)
