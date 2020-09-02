import time
from os import listdir
from os.path import isfile, join
import re
from xml.dom import minidom
import csv


data_path = "bgg/data/boardgames-data"
files = [f for f in listdir(data_path) if isfile(join(data_path, f)) and re.match(r'[0-9]+_+[0-9]+\.xml', f)]

# blacklist = ["20342038453_200.xml"]

start = time.time()
missing_ids = []
for f in files:
    #if f in blacklist:
     #   break
    print("\n"+f)
    mydoc = minidom.parse(join(data_path, f))
    items = mydoc.getElementsByTagName('item')
    ids = [i.attributes['id'].value for i in items]
    with open(join(data_path, f.replace("xml", "tsv"))) as tsv_file:
        reader = csv.reader(tsv_file, delimiter='\t')
        ids_check = next(reader)

    for id in ids:
        if id not in ids_check:
            missing_ids.append(id)
    print(missing_ids)

print("\nMISSING IDS #########################################################################\n")
print(missing_ids)
print("Executed in", time.time() - start, "seconds")