# Pathwaybot
Pathwaybot is a Wikibot developed to add data on biological pathways
 to Wikidata. It is being developed in close collaboration between the
 Wikipathways and Genewiki teams. 
 
 The bot is written in Python (requires v 3) and makes use of the [WikidataIntegrator](https://github.com/SuLab/WikidataIntegrator) developed by in the 
  Genewiki project. In the Genewiki project data on genes, proteins, drugs, and diseases are being actively added and updated to Wikidata
  
  ### Usage
The bot feeds on the [Semantic Web representation of Wikipathways](http://www.wikipathways.org/index.php/Portal:Semantic_Web). 
While the bot is actively being developed, running it requires downloading the 
latest rdf dump from Wikipathways and store that in a local SPARQL endpoint. 

Later in the project this preprocessing step will be integrated into the
Pathwaybot itself to allow more automation in loading pathway content to Wikidata. 

#### Loading WPRDF
The first step is to start a local sparql endpoint. Currently, [Blazegraph](https://www.blazegraph.com/download/) is our Sparql endpoint of choice. 
 
##### Start the SPARQL endpoint 
 ``` java -server -Xmx4g -jar blazegraph.jar```
 
##### Collect the RDF for all pathways
``` python collectWikipathwaysRDF.py ```

##### Load the RDF into the locally running SPARQL endpoint
By default blazegraph initiates in the kb namespace. Create or Switch to the
Wikipathways namespace in blazegraph and load the output from the previous step.

##### Run Pathwaybot
```python Pathwaybot.py <Wikipathway identifier>```.


## TODO
1. Merge the functionalities of collectWikiPathwaysRDF.py into PathwayBot.py to remove the dependancy on 
locally running a SPARQL endpoint

## Wikidata: Pathwaybot account
This bot is primarily developed to be run the [Pathwaybot](https://www.wikidata.org/wiki/User:Pathwaybot) on [Wikidata](http://www.wikidata.org). 
