# -*- coding: utf-8 -*-
import pprint

__project__ = 'bgg'
__author__ = 'Luca Leporini'
__email__ = 'luca.leporini1@studenti.unimi.it'
__institution__ = 'Università degli Studi di Milano'
__date__ = 'set 2020'
__comment__ = '''
    Class for massive download of data from bgg
    '''

import xmltodict, json
import os
import requests
import time
from threading import Thread
import threading
from os import listdir
from os.path import isfile, join
import random as rand
import numpy as np
from matplotlib import pyplot as plt

URL = "https://api.geekdo.com/xmlapi2/user?name={}&buddies=1&guilds=1&hot=1&top=1&page={}"
num_thread = 2 # number of active thread to execute request API


def plot_users(users, t_min, t_max):
    print("NUMERO UTENTI:", len(users.keys()))
    print("NUM COMMENTI MEDIO:", np.mean([list(users.values())]))
    print("NUM COMMENTI MASSIMO:", np.max([list(users.values())]))
    print("NUM COMMENTI MINIMO:", np.min([list(users.values())]))
    plt.plot(range(0, len([i for i in list(users.values()) if t_min <= i <= t_max])),
             sorted([i for i in list(users.values()) if t_min <= i <= t_max], reverse=True))
    plt.show()


def create_list_users():
    if os.path.exists("data/boardgames-data/bgg-data-users-index.json"):
        with open('data/boardgames-data/bgg-data-users-index.json', 'r', encoding="utf-8") as f:
            users = json.load(f)
        return users

    with open('data/boardgames-data/bgg-data-cleaned.json', 'r', encoding="utf-8") as f:
        data = json.load(f)

    users = {}
    for item in data["items"]:
        if int(item["totalcomments"]) > 0:
            for comment in item["comments"]:
                if comment["username"] not in users.keys():
                    users[comment["username"]] = 1
                else:
                    users[comment["username"]] += 1
    # plot_users(data, 3, 1200)
    with open("data/boardgames-data/bgg-data-users-index.json", 'w') as f:
        json.dump(users, f)
    return users


# WorkerThread to download boardgames in parallel
class WorkerThread (Thread):
    def __init__(self, input_chunk, destination_folder, files):
        Thread.__init__(self)
        self.chuck = input_chunk
        self.folder = destination_folder
        #to remove
        self.files = files

    def run(self):
        print(threading.current_thread().name, "STARTING.....................................")
        bgg_users_chunk_download(self.chuck, self.folder, self.files)


def bgg_users_chunk_download(input_chunk, destination_folder, files):
    TAG = threading.current_thread().name

    if not os.path.isdir(destination_folder):
        os.mkdir(destination_folder)
    if not os.path.isdir(destination_folder + "/blacklist"):
        os.mkdir(destination_folder + "/blacklist")

    users = [k for k, w in input_chunk]
    user_class = "".join(users[:2])
    blacklist = []

    while len(users) != 0:
        username = users.pop(0)
        num_page = 1
        stop_condition = False
        error = False
        root_user = None
        num_retries = 0  # tentativi di ottenimento di una nuova pagina (BACKOFF TIMER)

        if username not in files:
            while not stop_condition:
                query = URL.format(username, num_page)
                print(TAG, "user:", username, "- PAGE:", num_page, query)
                stop_connection = False
                try:
                    r = requests.get(query)
                    json_str = json.dumps(xmltodict.parse(r.text), indent=4)
                    next_page = json.loads(json_str)
                except Exception as e:
                    stop_connection = True
                    num_page -= 1
                    time.sleep(rand.randint(1, 4) + (num_retries * 4))
                    num_retries += 1

                if not stop_connection:
                    try:
                        if root_user is None:
                            root_user = next_page["user"]
                        else:
                            if "giuld" in next_page["user"]["guilds"].keys():
                                root_user["guilds"]["guild"] += next_page["user"]["guilds"]["guild"]
                            if "buddy" in next_page["user"]["buddies"].keys():
                                root_user["buddies"]["buddy"] += next_page["user"]["buddies"]["buddy"]

                        if "guild" not in next_page["user"]["guilds"].keys() and \
                                "buddy" not in next_page["user"]["buddies"].keys():
                            stop_condition = True

                    except Exception as e:
                        num_page -= 1  # ripetere la pagina non andata a buon fine
                        num_retries += 1
                        time.sleep(rand.randint(1, 4) + (num_retries * 4))  # backoff timer

                        if "div" in next_page.keys():
                            if next_page["div"]["#text"] == "invalid Get list data":
                                num_retries = 3

                if num_retries >= 3:
                    if username not in blacklist:
                        print(TAG, "ERROR RETRIES EXCEED --> ADD", username, " TO USERS")
                        blacklist.append(username)
                        users.append(username)
                    stop_condition = True
                    error = True

                num_page += 1
                time.sleep(4)

            if not error:
                print(TAG, "USER COMPLETED", username, "---", "REMAINING USERS:", len(users))
                out_file = os.sep.join([destination_folder, "{}.json".format(username)])
                with open(out_file, 'w', encoding="utf-8") as out:
                    json.dump(root_user, out)

        else:
            print(TAG, "USER ALREADY COMPLETED", username, "---", "REMAINING USERS:", len(users))

    if len(blacklist) > 0:
        print(TAG, "USER BLACKLIST:", blacklist)
        out_file = os.sep.join([destination_folder+"/blacklist", "{}.json".format(user_class)])
        with open(out_file, 'w') as log:
            log.write("\t".join(blacklist))


if __name__ == '__main__':
    out_folder = 'data/boardgames-temp'
    files_extended = [f for f in listdir(out_folder) if isfile(join(out_folder, f))]
    files = [x.split(".")[0] if len(x.split(".")) == 2 else '.'.join(x.split(".")[:-1]) for x in files_extended]

    chunk = 200
    users_file = create_list_users()
    users = list(users_file.items())

    chunks, page = [], 0
    while page < len(users) + chunk:
        ck = users[page:page + chunk]
        if len(ck) > 0:
            chunks.append(ck)
        page += chunk

    threads = []
    for i in range(1, len(chunks), num_thread):
        for chunk in chunks[i:i + num_thread]:
            t = WorkerThread(chunk, out_folder, files)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
