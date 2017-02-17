# Author: Andra Waagmeester

import requests
import io
import zipfile
from contextlib import closing
from rdflib import Graph

u = requests.get("http://data.wikipathways.org/current/rdf/wikipathways-20170210-rdf-gpml.zip")

temp = Graph()
with closing(u), zipfile.ZipFile(io.BytesIO(u.content)) as archive:
    for member in archive.infolist():
        nt_content = archive.read(member)
        print(nt_content)
        temp.parse(data=nt_content.decode(), format="turtle")

u = requests.get("http://data.wikipathways.org/current/rdf/wikipathways-20170210-rdf-wp.zip")
with closing(u), zipfile.ZipFile(io.BytesIO(u.content)) as archive:
    for member in archive.infolist():
        nt_content = archive.read(member)
        print(nt_content)
        temp.parse(data=nt_content.decode(), format="turtle")

temp.serialize("/tmp/wikipathways.ttl", format="turtle")

