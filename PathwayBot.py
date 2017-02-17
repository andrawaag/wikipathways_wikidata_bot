# Author: Andra Waagmeester

from wikidataintegrator import wdi_core, wdi_login
import os
from SPARQLWrapper import SPARQLWrapper, JSON
import pprint
from time import gmtime, strftime
import copy
import pprint
import requests
from rdflib import Graph
import sys

wikipathways = Graph()
wikipathways.parse("/tmp/wikipathways.ttl",format="turtle")
qres = wikipathways.query(
    """SELECT DISTINCT *
       WHERE {
          ?s ?p ?o .
       }""")
for row in qres:
    print("%s knows %s %s" % row)
sys.exit()

def getWikiPathwaysRDF():
    wpfile= requests.get("http://data.wikipathways.org/current/rdf/wikipathways-20170210-rdf-gpml.zip")
    gpmlfile = requests.get("http://data.wikipathways.org/current/rdf/wikipathways-20170210-rdf-wp.zip")



#login_instance = wdi_login.WDLogin("ProteinBoxBot", os.environ['wikidataApi'])

wikipathways_sparql = SPARQLWrapper("http://sparql.wikipathways.org")
wikidata_sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql")

prep = dict()

# P703 = found in taxon, Q15978631 = "Homo sapiens"
prep["P703"] = [wdi_core.WDItemID(value="Q15978631", prop_nr='P703', is_reference=True)]

wikipathways_sparql.setQuery("""
    PREFIX wp:    <http://vocabularies.wikipathways.org/wp#>

SELECT DISTINCT ?pathway ?pwId ?pwLabel
WHERE {
   VALUES ?pwId {"WP197"^^xsd:string}
   ?pathway a wp:Pathway ;
            dc:title ?pwLabel ;
            dcterms:identifier ?pwId ;
            wp:organismName "Homo sapiens"^^xsd:string .
}
""")
wikipathways_sparql.setReturnFormat(JSON)
wikidata_sparql.setReturnFormat(JSON)
results = wikipathways_sparql.query().convert()
for result in results["results"]["bindings"]:
    print(result["pwId"]["value"])
    refStatedIn = wdi_core.WDItemID(value="Q27612411", prop_nr='P248', is_reference=True)
    timeStringNow = strftime("+%Y-%m-%dT00:00:00Z", gmtime())
    refRetrieved = wdi_core.WDTime(timeStringNow, prop_nr='P813', is_reference=True)
    refWikiPathways = wdi_core.WDString(result["pwId"]["value"], prop_nr='P2410', is_reference=True)
    wikipathways_reference = [refStatedIn, refRetrieved, refWikiPathways]

    # P2410 = WikiPathways ID
    prep["P2410"] = [wdi_core.WDString(result["pwId"]["value"], prop_nr='P2410', references=[copy.deepcopy(wikipathways_reference)])]

    # P2888 = exact match
    prep["P2888"] = [wdi_core.WDUrl("http://identifiers.org/wikipathways/"+result["pwId"]["value"], prop_nr='P2888', references=[copy.deepcopy(wikipathways_reference)])]

    # P2699 = URL
    prep["P2699"] = [wdi_core.WDUrl("http://www.wikipathways.org/instance/" + result["pwId"]["value"], prop_nr='P2888',
                                    references=[copy.deepcopy(wikipathways_reference)])]

    query = """
    select *

    WHERE {
     ?pubmed  a       wp:PublicationReference ;
            dcterms:isPartOf <"""

    query+= result["pathway"]["value"]
    query += """> .}

    """
    wikipathways_sparql.setQuery(query)
    pubmed_results = wikipathways_sparql.query().convert()
    pubmed_citations = []
    for pubmed_result in pubmed_results["results"]["bindings"]:
        pubmed_citations.append("\""+pubmed_result["pubmed"]["value"].replace("http://identifiers.org/pubmed/", "")+"\"")

    query = "SELECT * WHERE { VALUES ?pmid {"
    query += " ".join(pubmed_citations)
    query += "} ?item wdt:P698 ?pmid .}"
    # print(query)
    wikidata_sparql.setQuery(query)
    wikidata_results = wikidata_sparql.query().convert()
    for wikidata_result in wikidata_results["results"]["bindings"]:
        # P2860 = cites
        if 'P2860' not in prep.keys():
            prep["P2860"] = []
        prep['P2860'].append(wdi_core.WDItemID(value=wikidata_result["item"]["value"].replace("http://www.wikidata.org/entity/", ""), prop_nr='P2860',
                                           references=[copy.deepcopy(wikipathways_reference)]))

    pprint.pprint(prep)


    data2add = []
    for key in prep.keys():
        for statement in prep[key]:
            data2add.append(statement)
            print(statement.prop_nr, statement.value)
    # wdPage = wdi_core.WDItemEngine( item_name=result["pwLabel"]["value"], data=data2add, server="www.wikidata.org", domain="genes", fast_run=fast_run, fast_run_base_filter=fast_run_base_filter)
    wdPage = wdi_core.WDItemEngine(item_name=result["pwLabel"]["value"], data=data2add, server="www.wikidata.org",
                                   domain="genes")

    wdPage.set_label(result["pwLabel"]["value"])

    wd_json_representation = wdPage.get_wd_json_representation()

    pprint.pprint(wd_json_representation)





