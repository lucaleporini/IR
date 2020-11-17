import json
import pprint
from os import listdir
from os.path import isfile, join
import os


if __name__ == '__main__':
    input_folder = 'data/boardgames-temp'
    game_file = 'data/boardgames.json'
    out_folder = 'data/boardgames-data'
    chunk = 200
    with open(game_file, 'r') as in_file:
        games = list(json.load(in_file).items())
    chunks, page = [], 0
    while page < len(games) + chunk:
        ck = games[page:page+chunk]
        if len(ck) > 0:
            chunks.append(ck)
        page += chunk
    files = [f.split(".")[0] for f in listdir(input_folder) if isfile(join(input_folder, f))]

    tot_items = 0
    for chunk in chunks:
        tot_items += len(chunk)
    print(tot_items)
    print(len(files))

    blacklist = []
    id_games = []
    bgg_result = None
    tot_comments = 0
    chunk_count = 0
    for chunk in chunks:
        if chunk_count != 0:
            for id_game, name_game in chunk:
                if id_game in files:
                    id_games.append((id_game, name_game))
                    # load json file
                    with open(input_folder+'/{}.json'.format(id_game), 'r', encoding="utf-8") as f:
                        json_game = json.load(f)
                    if bgg_result is None:
                        bgg_result = json_game
                        bgg_result["items"]["item"] = [json_game["items"]["item"]]
                    else:
                        bgg_result["items"]["item"].append(json_game["items"]["item"])
                else:
                    blacklist.append(id_game)
        chunk_count += 1
        print("BLACKLIST:", len(blacklist))

    # with open('boardgames-temp/result/174430161936_200.json', 'r', encoding="utf-8") as f:
    #     json_chunk = json.load(f)
    # bgg_result["items"]["item"] += json_chunk["items"]["item"]
    # id_games += chunks[0]

    print(len(bgg_result["items"]["item"]))
    print(len(id_games))
    print(blacklist)

    out_file = os.sep.join([out_folder, "bgg-data.json"])
    with open(out_file, 'w', encoding="utf-8") as out:
        json.dump(bgg_result, out)
    with open(os.sep.join([out_folder, "bgg-data-index.json"]), 'w') as log:
        json.dump({id: name for id, name in id_games}, log)
    with open(os.sep.join([out_folder, "bgg-data-blacklist.tsv"]), 'w') as log:
        log.write("\t".join(blacklist))

