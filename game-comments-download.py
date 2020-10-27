import xmltodict, json
import os
import requests
import time
from threading import Thread
import threading
from os import listdir
from os.path import isfile, join
import random as rand

URL = "https://api.geekdo.com/xmlapi2/thing?id={}&marketplace=1&comments=1&stats=1&pagesize=100&page={}"
num_thread = 2 # number of active thread to execute request API


def bgg_one_request(id_game, destination_folder):
    fgc = destination_folder
    if not os.path.isdir(fgc):
        os.mkdir(fgc)

    # Iterazioni sulle pagine per raccogliere tutti i commenti di un determinato gioco
    stop_condition = False
    num_page = 1
    root_game = None
    while not stop_condition:
        query = URL.format(id_game, num_page)
        print("ID:", id_game, "- PAGE:", num_page, query)
        r = requests.get(query)
        json_str = json.dumps(xmltodict.parse(r.text), indent=4)
        next_page = json.loads(json_str)

        # Non sono più presenti commenti
        if "comment" not in next_page["items"]["item"]["comments"].keys():
            stop_condition = True
        else:

            if root_game is None:
                root_game = next_page
            else:
                try:
                    root_game["items"]["item"]["comments"]["comment"] = root_game["items"]["item"]["comments"][
                                                                            "comment"] + \
                                                                        next_page["items"]["item"]["comments"][
                                                                            "comment"]
                except:
                    if next_page["items"]["item"]["comments"]["comment"] is type(dict):
                        root_game["items"]["item"]["comments"]["comment"] = root_game["items"]["item"]["comments"][
                                                                                "comment"] + \
                                                                            [next_page["items"]["item"]["comments"][
                                                                                 "comment"]]
        num_page += 1
        time.sleep(4)

    out_file = os.sep.join([fgc, "{}.json".format(id_game)])
    with open(out_file, 'w', encoding="utf-8") as out:
        json.dump(root_game, out)


class WorkerThread (Thread):
    def __init__(self, input_chunk, destination_folder):
        Thread.__init__(self)
        self.chuck = input_chunk
        self.folder = destination_folder

    def run(self):
        print(threading.current_thread().name, self.chuck)
        bgg_chunk_request(self.chuck, self.folder)


def bgg_chunk_request(input_chunk, destination_folder):
    start = time.time()
    TAG = threading.current_thread().name
    if not os.path.isdir(destination_folder):
        os.mkdir(destination_folder)
    if not os.path.isdir(destination_folder+"/blacklist"):
            os.mkdir(destination_folder+"/blacklist")

    keys = [k for k, w in input_chunk]
    game_class = "".join(keys[:2]) # come nome del file si considerano i primi due id di gioco nel chunk
    # chunk_result = None

    files = [f.split(".")[0] for f in listdir(out_folder) if isfile(join(out_folder, f))]
    blacklist = []
    while len(keys) != 0:

        id_game = keys.pop(0)
        # Iterazioni sulle pagine per raccogliere tutti i commenti di un determinato gioco
        stop_condition = False
        error = False
        num_page = 1
        root_game = None
        # files = [f.split(".")[0] for f in listdir(out_folder) if isfile(join(out_folder, f))]

        # SCANSIONE DI TUTTE LE PAGINE DI COMMENTI
        if id_game not in files:
            num_retries = 0  # tentativi di ottenimento di una nuova pagina di commento (BACKOFF TIMER)
            while not stop_condition:
                query = URL.format(id_game, num_page)
                print(TAG, "ID:", id_game, "- PAGE:", num_page, query)
                stop_connection = False

                try:
                    r = requests.get(query)
                    json_str = json.dumps(xmltodict.parse(r.text), indent=4)
                    next_page = json.loads(json_str)
                except Exception as e:
                    print(TAG, str(e))
                    print(TAG, " - ERROR", id_game, num_page)
                    stop_connection = True
                    num_page -= 1
                    time.sleep(rand.randint(8, 13) + (num_retries*4))
                    num_retries += 1

                if not stop_connection:
                    try:
                        if "comments" not in next_page["items"]["item"]:
                            # questo gioco non presenta commenti e valutazione
                            print(TAG, "GIOCO", id_game,
                                  "NON PRESENTA COMMENTI E VALUTAZIONE ***********************************************")
                            root_game = next_page
                            stop_condition = True
                        else:
                            if "comment" not in next_page["items"]["item"]["comments"].keys():
                                # Non sono più presenti commenti
                                stop_condition = True
                            else:
                                if root_game is None:
                                    root_game = next_page
                                else:
                                    try:
                                        root_game["items"]["item"]["comments"]["comment"] = root_game["items"]["item"]["comments"]["comment"] + \
                                                                                            next_page["items"]["item"]["comments"]["comment"]
                                    except:
                                        if type(next_page["items"]["item"]["comments"]["comment"]) is dict:
                                            root_game["items"]["item"]["comments"]["comment"] = root_game["items"]["item"]["comments"][
                                                                                                    "comment"] + \
                                                                                                [next_page["items"]["item"]["comments"][
                                                                                                    "comment"]]
                    except Exception as e:
                        # controllo della formattazione
                        print(TAG, "ERROR FORMATTAZIONE: ", id_game)
                        print(TAG, str(e))
                        print(next_page)
                        num_page -= 1 # ripetere la pagina non andata a buon fine
                        time.sleep(rand.randint(8, 13) + (num_retries*4))
                        num_retries += 1

                if num_retries > 3:
                    if id_game not in blacklist:
                        blacklist.append(id_game)
                        keys.append(id_game)  # inserisco il gioco in keys e verrà ripetuto
                    print(TAG, "ERROR RETRIES EXCEED --> ADD", id_game, " TO KEYS")
                    stop_condition = True
                    error = True

                num_page += 1
                time.sleep(4)

            # GAME COMPLETATO
            if not error: # controllo se non si sono verificati errori e salvo il gioco
                print(TAG, " - GAME COMPLETED: ", id_game)
                print(TAG, " - REMAINING GAMES:", len(keys))
                print("###############################################################################################")
                # SCRITTURA FILE JSON
                out_file = os.sep.join([destination_folder, "{}.json".format(id_game)])
                with open(out_file, 'w', encoding="utf-8") as out:
                    json.dump(root_game, out)
        else:
            print(TAG, "GAME ALREADY COMPLETED: ", id_game, " - REMAINING GAMES:", len(keys))

    if len(blacklist) > 0:
        print(TAG, "BLACKLIST:", blacklist)
        out_file = os.sep.join([destination_folder+"/blacklist", "{}.json".format(game_class)])
        with open(out_file, 'w') as log:
            log.write("\t".join(blacklist))

    print(TAG, " - Executed in", time.time() - start, "seconds")


if __name__ == '__main__':
    # versione singolo id
    # out_folder = 'boardgames-temp'
    # id_to_search = "193738"
    # p = Process(target=bgg_one_request(id_to_search, out_folder))
    # p.start()
    # p.join()

    # versione con chunk
    out_folder = 'boardgames-temp'
    game_file = 'bgg/data/boardgames.json'
    chunk = 200
    with open(game_file, 'r') as in_file:
        games = list(json.load(in_file).items())
    chunks, page = [], 0
    while page < len(games) + chunk:
        ck = games[page:page + chunk]
        if len(ck) > 0:
            chunks.append(ck)
        page += chunk
    threads = []

    for i in range(1, 202, num_thread):
        print("CHUNK: ", i, "--", i+num_thread, "------------------------------------------------------------------------------")
        for chunk in chunks[i:i+num_thread]:
            t = WorkerThread(chunk, out_folder)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()


