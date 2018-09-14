# Author: Andra Waagmeester

import requests
import io
import zipfile
from contextlib import closing
from rdflib import Graph
from bs4 import BeautifulSoup, SoupStrainer

#u = requests.get("http://data.wikipathways.org/current/rdf/wikipathways-20171210-rdf-gpml.zip")

temp = Graph()

url = 'http://data.wikipathways.org/current/rdf'
page = requests.get(url).text
files = []
for link in BeautifulSoup(page, "lxml", parse_only=SoupStrainer('a')):
    address = str(link).split("\"")
    if len(address) > 1:
        filename = address[1].replace("./", "/")
        if len(filename) > 1:
            if filename not in files:
                if filename != "./":
                    files.append(url + filename)
    wpids = []
    for file in set(files):
        if "rdf-wp" in file:  # get the most accurate file
            print(file)
            u = requests.get(file)
            with closing(u), zipfile.ZipFile(io.BytesIO(u.content)) as archive:
                for member in archive.infolist():
                    nt_content = archive.read(member)
                    # print(nt_content)
                    temp.parse(data=nt_content.decode(), format="turtle")

temp.serialize("/tmp/wikipathways.ttl", format="turtle")

# u = requests.get("http://data.wikipathways.org/current/rdf/wikipathways-20180910-rdf-wp.zip")
# with closing(u), zipfile.ZipFile(io.BytesIO(u.content)) as archive:
#    for member in archive.infolist():
#        nt_content = archive.read(member)
#        print(nt_content)
#        temp.parse(data=nt_content.decode(), format="turtle")
#        print(len(temp))



