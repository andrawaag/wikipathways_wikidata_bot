from wikidataintegrator import wdi_core, wdi_login
import os
from SPARQLWrapper import SPARQLWrapper, JSON
import pprint
from time import gmtime, strftime
import copy

#login_instance = wdi_login.WDLogin("ProteinBoxBot", os.environ['wikidataApi'])

wikipathways_sparql = SPARQLWrapper("http://sparql.wikipathways.org")
wikidata_sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql")

prep = dict()
prep["P703"] = wdi_core.WDItemID(value="Q15978631", prop_nr='P248', is_reference=True)



wikipathways_sparql.setQuery("""
    PREFIX wp:    <http://vocabularies.wikipathways.org/wp#>

SELECT DISTINCT ?pathway ?pwId ?pwLabel
WHERE {

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

    prep["P2410"] = [wdi_core.WDString(result["pwId"]["value"], prop_nr='P2410', references=[copy.deepcopy(wikipathways_reference)])]

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
    wikidata_sparql.setQuery(query)
    wikidata_results = wikidata_sparql.query().convert()
    for wikidata_result in wikidata_results["results"]["bindings"]:
        if 'P2860' not in prep.keys():
            prep["P2860"] = []
        prep['P2860'].append(wdi_core.WDItemID(value=wikidata_result["item"]["value"].replace("http://www.wikidata.org/entity/", ""), prop_nr='P2860',
                                           references=[copy.deepcopy(wikipathways_reference)]))
        #print(pubmed_result["pubmed"]["value"], wikidata_result["item"]["value"])
    pprint.pprint(prep)






