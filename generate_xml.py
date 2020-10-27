
from os import listdir
from os.path import isfile, join
import os

import xml.etree.ElementTree as ET
from pprint import pprint

if __name__ == '__main__':
    data_path = 'data/boardgames-temp'
    out_folder = 'data/boardgames-data'
    data_id = '20342038453_200'
    files = [f for f in listdir(data_path) if isfile(join(data_path, f))]
    root = None
    for f in files:
        if root is None:
            tree = ET.parse(join(data_path, f))
            root = tree.getroot()
        else:
            try:
                print(ET.parse(join(data_path, f)).getroot()[0].attrib)
                root.append(ET.parse(join(data_path, f)).getroot()[0])
            except:
                print(f)
            # root.append(ET.parse(join(data_path, f)).getroot()[0])
        # root = tree.getroot()
    print(len(root))

    out_file = os.sep.join([out_folder, "{}.xml".format(data_id)])
    # with open(out_file, 'w', encoding="utf-8") as out:
    #     out.write(ET.tostring(root, encoding='utf8').decode('utf8'))

    tree.write(out_file)


   # print(ET.tostring(root, encoding='utf8').decode('utf8'))

