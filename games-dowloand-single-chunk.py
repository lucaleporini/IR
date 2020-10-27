# -*- coding: utf-8 -*-
__project__ = 'bgg'
__author__ = 'Luca Leporini'
__email__ = 'luca.leporini1@studenti.unimi.it'
__institution__ = 'Università degli Studi di Milano'
__date__ = '20 ago 2020'
__comment__ = '''
    Class for massive download of data from bgg
    '''
import json
import os
from multiprocessing import Process
import requests
import time

# ORIGINAL CODE
# URL = "https://api.geekdo.com/xmlapi2/thing?id={}&marketplace=1&comments=1&stats=1"

URL = "https://www.boardgamegeek.com/xmlapi2/thing?id={}&marketplace=1&comments=1&stats=1"


def bgg_single_id_request(id, destination_folder):
    fgc = destination_folder
    if not os.path.isdir(fgc):
        os.mkdir(fgc)
    query = URL.format(id)
    print(id, query)
    r = requests.get(query)
    out_file = os.sep.join([fgc, "{}.xml".format(id)])
    with open(out_file, 'w', encoding="utf-8") as out:
        out.write(r.text)


def bgg_single_chunk_request(input_chunk, destination_folder):
    print('{}: starting'.format(input_chunk[0][1]))
    keys = [k for k, w in input_chunk]
    fgc = destination_folder  # os.sep.join([destination_folder, game_class])
    if not os.path.isdir(fgc):
        os.mkdir(fgc)
    for k in keys:
        query = URL.format(k)
        print(k, query)
        r = requests.get(query)
        out_file = os.sep.join([fgc, "{}.xml".format(k)])
        with open(out_file, 'w', encoding="utf-8") as out:
            out.write(r.text)
        time.sleep(4)
    print('{}: finishing'.format(input_chunk[0][1]))


if __name__ == '__main__':
    start = time.time()
    temp_folder = 'data/boardgames-temp'
    first_id_chunck = "203420"
    id_to_search = "224783"
    out_folder = 'data/boardgames-data'
    game_file = 'data/boardgames.json'
    chunk = 200
    with open(game_file, 'r') as in_file:
        games = list(json.load(in_file).items())
    chunks, page = [], 0
    while page < len(games) + chunk:
        ck = games[page:page+chunk]
        page += chunk
        try:
            if ck[0][0] == first_id_chunck:
                chunks.append(ck)
        except:
            print("list out of range")

    p = Process(target=bgg_single_id_request(id_to_search, temp_folder))
    p.start()
    p.join()
    print("Executed in", time.time() - start, "seconds")
