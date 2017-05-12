__author__ = 'andra'

# This is a maintenance bot which removes all occurences where a protein is incorrectly being encoded by another protein

import time
import sys
import os
from wikidataintegrator import wdi_core, wdi_login, wdi_property_store
from SPARQLWrapper import SPARQLWrapper, JSON

logincreds = wdi_login.WDLogin(user=os.environ["wd_user"], pwd=os.environ["pwd"])

wikidata_sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql")


# SPARQL query to get all Wikidata items with properties for a Wikipathways ID and a URL
# both are redundant to each other, so the URL property is removed.
query = """
SELECT ?item ?itemLabel WHERE {
  ?item wdt:P2699 ?url ;
        wdt:P2410 ?WPID .
  }
"""
wikidata_sparql.setQuery(query)
wikidata_sparql.setReturnFormat(JSON)
results = wikidata_sparql.query().convert()
for result in results["results"]["bindings"]:
    data2add = [wdi_core.WDBaseDataType.delete_statement(prop_nr='P2699')]
    wdPage = wdi_core.WDItemEngine(result["item"]["value"].replace("http://www.wikidata.org/entity/", ""), data=data2add, server="www.wikidata.org",
                                           domain="pathways")
    wdPage.write(logincreds)
