# Author: Andra Waagmeester

from wikidataintegrator import wdi_core, wdi_login, wdi_property_store
import os
from SPARQLWrapper import SPARQLWrapper, JSON
import pprint
from time import gmtime, strftime
import copy
import pprint
import requests
import datetime
from rdflib import Graph
import sys
from SPARQLWrapper import SPARQLWrapper, JSON


wikipathways = Graph()
pwid = sys.argv[1]

wdi_property_store.wd_properties['P2410'] = {
        'datatype': 'string',
        'name': 'Wikipathways ID',
        'domain': ['pathways'],
        'core_id': 'True'
    }


## Downloading data from Wikipathways
#
# This bot extracts Wikipathways content from its RDF representation. This is available through its SPARQL endpoint or through regularly
# updated RDF data files available at: http://data.wikipathways.org/current/rdf/
# The data downloads are preferred over the SPARQL endpoint, since the endpoint is updated infrequently and at times unstable.
# There are two ways to load the RDF:
# 1. Loading it directly in memory with the Python rdflib library (i.e. graph.parse("<rdf file>")
# 2. Loading it in a local sparql endpoint on the server where this python scripts run. Currently, blazegraph is used as prefered
#    RDF infrastructure: https://www.blazegraph.com/download/
#####

"""
# Direct loading into memory
start = datetime.datetime.now()
print(str(start))
wikipathways.parse("/tmp/wikipathways.ttl",format="turtle")
end = datetime.datetime.now()
print(str(end))
delta = end-start
print(str(delta))
"""

# Initiating variables
prep = dict()

# Stating SPARQL endpoints
wikidata_sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql")
wikipathways_sparql = SPARQLWrapper("http://127.0.0.1:9999/blazegraph/namespace/Wikipathways/sparql")

# Login Wikidata
# logincreds = wdi_login.WDLogin(user=os.environ['wd_user'], pwd=os.environ['wikidataApi'])
logincreds = wdi_login.WDLogin(user=os.environ["wd_user"], pwd=os.environ["pwd"])


# Defining references
refStatedIn = wdi_core.WDItemID(value="Q7999828", prop_nr='P248', is_reference=True)
timeStringNow = strftime("+%Y-%m-%dT00:00:00Z", gmtime())
refRetrieved = wdi_core.WDTime(timeStringNow, prop_nr='P813', is_reference=True)
refWikiPathways = wdi_core.WDString(pwid, prop_nr='P2410', is_reference=True)
wikipathways_reference = [refStatedIn, refRetrieved, refWikiPathways]

def get_PathwayElements(pathway="", datatype="GeneProduct", sparqlend = "" ):
    query =  """PREFIX wp:      <http://vocabularies.wikipathways.org/wp#>
           PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
           PREFIX dcterms: <http://purl.org/dc/terms/>

           select distinct ?pathway (str(?label) as ?geneProduct) ?id where {
            ?metabolite a wp:"""
    query += datatype
    query += """  ;
                    rdfs:label ?label ;"""
    if datatype == "Metabolite":
        query += "   wp:bdbPubChem ?id ;"
    if datatype == "GeneProduct":
        query += "   wp:bdbEntrezGene ?id ;"
    query += """
                    dcterms:isPartOf ?pathway .
            ?pathway a wp:Pathway ;
                   dcterms:identifier
            """
    query += "\"" + pathway +"\"^^xsd:string .}"

    print(query)
    #qres = wikipathways.query(query)
    sparqlend.setQuery(query)
    sparqlend.setReturnFormat(JSON)
    results = wikipathways_sparql.query().convert()
    pprint.pprint(results)
    ids = []
    for result in results["results"]["bindings"]:
        print(result["id"]["value"])
        ids.append("\"" + result["id"]["value"].replace("http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID", "").replace("http://identifiers.org/ncbigene/", "") + "\"")
    pprint.pprint(ids)


    # TODO: Check for existence of the ids in wikidata
    wd_query = "SELECT DISTINCT * WHERE {VALUES ?id {"
    wd_query += " ".join(ids)
    if datatype == "Metabolite":
        wd_query += "} ?item wdt:P662 ?id . }"
    if datatype == "GeneProduct":
        wd_query += "} ?item wdt:P351 ?id . }"

    wikidata_sparql.setQuery(wd_query)
    print(wd_query)

    wikidata_sparql.setReturnFormat(JSON)
    results = wikidata_sparql.query().convert()
    for result in results["results"]["bindings"]:
        if "P527" not in prep.keys():
            prep["P527"] = []
        prep["P527"].append(wdi_core.WDItemID(result["item"]["value"].replace("http://www.wikidata.org/entity/", ""), prop_nr='P527', references=[copy.deepcopy(wikipathways_reference)]))
    pprint.pprint(results)




get_PathwayElements(pathway=pwid,datatype="Metabolite", sparqlend=wikipathways_sparql)
get_PathwayElements(pathway=pwid, datatype="GeneProduct", sparqlend=wikipathways_sparql)



# P703 = found in taxon, Q15978631 = "Homo sapiens"
prep["P703"] = [wdi_core.WDItemID(value="Q15978631", prop_nr='P703', references=[copy.deepcopy(wikipathways_reference)])]


query = """
    PREFIX wp:    <http://vocabularies.wikipathways.org/wp#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT DISTINCT ?pathway ?pwId ?pwLabel
WHERE {
   VALUES ?pwId {"""
query += "\""+pwid+"\"^^xsd:string}"
query += """
   ?pathway a wp:Pathway ;
            dc:title ?pwLabel ;
            dcterms:identifier ?pwId ;
            wp:organismName "Homo sapiens"^^xsd:string .
}"""
print(query)
wikipathways_sparql.setQuery(query)
wikipathways_sparql.setReturnFormat(JSON)
wikidata_sparql.setReturnFormat(JSON)
results = wikipathways_sparql.query().convert()
for result in results["results"]["bindings"]:
    print(result["pwId"]["value"])

    # P31 = instance of
    prep["P31"] = [wdi_core.WDItemID(value="Q28864279",prop_nr="P31", references=[copy.deepcopy(wikipathways_reference)])]

    # P2410 = WikiPathways ID
    prep["P2410"] = [wdi_core.WDString(pwid, prop_nr='P2410', references=[copy.deepcopy(wikipathways_reference)])]

    # P2888 = exact match
    prep["P2888"] = [wdi_core.WDUrl("http://identifiers.org/wikipathways/"+result["pwId"]["value"], prop_nr='P2888', references=[copy.deepcopy(wikipathways_reference)])]

    # P2699 = URL
    prep["P2699"] = [wdi_core.WDUrl("http://www.wikipathways.org/instance/" + result["pwId"]["value"], prop_nr='P2699',
                                    references=[copy.deepcopy(wikipathways_reference)])]

    query = """
    PREFIX wp:    <http://vocabularies.wikipathways.org/wp#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
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
    wdPage.set_description("human biological pathway", lang="en")

    wd_json_representation = wdPage.get_wd_json_representation()

    pprint.pprint(wd_json_representation)
    wdPage.write(logincreds)
    sys.exit()





