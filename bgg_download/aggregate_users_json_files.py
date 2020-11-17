from os import listdir
from os.path import isfile, join
import os
import json


if __name__ == '__main__':
    input_folder = 'data/boardgames-temp'
    users_file = 'data/boardgames-data/bgg-data-users-index.json'
    out_folder = 'data/boardgames-data'

    chunk = 200
    with open(users_file, 'r') as in_file:
        users = list(json.load(in_file).items())
    chunks, page = [], 0
    while page < len(users) + chunk:
        ck = users[page:page+chunk]
        if len(ck) > 0:
            chunks.append(ck)
        page += chunk

    files_extended = [f for f in listdir(input_folder) if isfile(join(input_folder, f))]
    files = [x.split(".")[0] if len(x.split(".")) == 2 else '.'.join(x.split(".")[:-1]) for x in files_extended]

    blacklist = []
    num_users = len(files)
    users_count = 0
    bgg_users_result = None

    for chunk in chunks:
        for username, rip in chunk:
            users_count += 1
            if username in files:
                with open(input_folder + '/{}.json'.format(username), 'r', encoding="utf-8") as f:
                    json_user = json.load(f)
                if bgg_users_result is None:
                    bgg_users_result = [json_user]
                else:
                    bgg_users_result.append(json_user)
            else:
                blacklist.append(username)
            print("REMAINING USERS ", num_users-users_count)

    print("NUM USERS:", len(bgg_users_result))
    print("NUM USERS BLACKLIST:", len(blacklist))

    out_file = os.sep.join([out_folder, "bgg-data-users.json"])
    with open(out_file, 'w', encoding="utf-8") as out:
        json.dump(bgg_users_result, out)
    with open(os.sep.join([out_folder, "bgg-data-users-blacklist.tsv"]), 'w') as log:
        log.write("\t".join(blacklist))
