import spacy
import mining_tools as mt
import json
import pprint
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
from spacy_langdetect import LanguageDetector


# Giochi presenti nelle top/hot list degli utenti ma non presenti nel dataset di giochi
games_blacklist = []


def check_top_hot_list_user(user):
    return "top" in user.keys() or "hot" in user.keys()


def get_list_users_w_top_list():
    if os.path.exists("bgg_result/bgg-users.json"):
        with open('bgg_result/bgg-users.json', 'r', encoding="utf-8") as f:
            data = json.load(f)
        print("SELECTED USERS (w/ top/hot list):", len(data.keys()))
        return data

    with open('bgg_download/data/bgg-data-users-cleaned.json', 'r', encoding="utf-8") as f:
        data = json.load(f)
    result = {user["name"]: user for user in data["users"] if check_top_hot_list_user(user)}
    with open("bgg_result/bgg-users.json", "w") as out_file:
        json.dump(result, out_file)
    print("SELECTED USERS (w/ top/hot list):", len(result.keys()))
    return result


def get_game_list_from_users(users):
    with open('bgg_download/data/bgg-data-cleaned.json', 'r', encoding="utf-8") as f:
        data = json.load(f)
    user_game_list = set()
    for user in users.values():
        if "top" in user.keys():
            user_game_list.update([g["id"] for g in user["top"]])
        if "hot" in user.keys():
            user_game_list.update([g["id"] for g in user["hot"]])
    games = {}
    for id_game in user_game_list:
        if id_game in data.keys():
            games[id_game] = data[id_game]
        else:
            games_blacklist.append(id_game)

    print("SELECTED GAMES:", len(games),
          "-- ( TOT:", len(user_game_list), ", REMOVED:", len(user_game_list)-len(games),")")
    return games


def games_processing(users_categories, games, max_comments):
    c = 0
    for game in games.values():
        num_comments = max_comments if len(game["comments"]) >= max_comments else len(game["comments"])
        game["comments"] = sorted([comment for comment in game["comments"] if comment["username"] in users_categories.keys()],
                                  key=lambda c: len(c["value"]), reverse=True)[:num_comments]
        c += len(game["comments"])
    print("TOTAL COMMENTS: ", c)


def create_categories_game_dict():
    print("loading dataset games..")
    with open('bgg_download/data/bgg-data-cleaned.json', 'r', encoding="utf-8") as f:
        data = json.load(f)
    print("dataset loaded")
    categories = {}
    for item in data.values():
        for link in item["links"]:
            if link["type"] not in categories.keys():
                categories[link["type"]] = {}
            if link["id"] not in categories[link["type"]].keys():
                categories[link["type"]][link["id"]] = {"name": link["value"], "freq": 1}
            else:
                categories[link["type"]][link["id"]]["freq"] += 1

    # pprint.pprint([(k, len(categories_id_name[k].keys())) for k in categories_id_name.keys()])
    # pprint.pprint(categories_id_name["boardgamecategory"])

    with open("bgg_download/data/bgg-data-games-categories.json", 'w') as out:
        json.dump(categories, out)


def select_k_categories(games, category_params):
    categories = {}
    for item in games.values():
        for link in item["links"]:
            if link["type"] == category_params["type"]:
                if link["id"] not in categories.keys():
                    categories[link["id"]] = {"name": link["value"], "freq": 1}
                else:
                    categories[link["id"]]["freq"] += 1
    selected_categories = [(id_cat, desc["name"]) for id_cat, desc in sorted(categories.items(),
                                                                             key=lambda x: x[1]["freq"],
                                                                             reverse=True)][:category_params["k"]]
    return selected_categories


# category type ("category, family, artist, etc.) | k -> selected k categories with higher frequency
def user_category_vector(user, games, category_type, selected_categories):
    user_game_list = set()
    if "top" in user.keys():
        user_game_list.update([g["id"] for g in user["top"]])
    if "hot" in user.keys():
        user_game_list.update([g["id"] for g in user["hot"]])

    user_category_list = {id_cat: 0 for id_cat in selected_categories}
    for id_game in user_game_list:
        if id_game not in games_blacklist:
            for link in games[id_game]["links"]:
                if link["type"] == category_type and link["id"] in selected_categories:
                    user_category_list[link["id"]] += 1

    result = [(cat, val/len(user_game_list)) for cat, val in user_category_list.items()]
    return result


def get_users_categories_dict(users, games, category_params, category_ids, max_users):
    users_category_vector = {id_cat: [] for id_cat in category_ids}
    users_category_vector["username"] = []
    for username in users.keys():
        users_category_vector["username"].append(username)
        user_vector = user_category_vector(users[username], games, category_params["type"], category_ids)
        for id_cat, val in user_vector:
            users_category_vector[id_cat].append(val)

    df = pd.DataFrame(users_category_vector)

    cat_users_favorite = {}
    result = {}
    for id_cat in category_ids:
        cat_df = df[[id_cat, "username"]].sort_values(id_cat, ascending=False)[:max_users]
        cat_users_favorite[id_cat] = {"max_value": cat_df.head(1)[id_cat].iloc[0],
                                      "min_value": cat_df.tail(1)[id_cat].iloc[0]}
        for username in cat_df["username"].to_list():
            if username not in result.keys():
                result[username] = [id_cat]
            else:
                result[username].append(id_cat)
    return result, cat_users_favorite


lang_params = {
    "lang": "en",
    "lang_score": 0.70,
    "min_len": 10
}


def lang_distribution():
    print("loading dataset..")
    with open('bgg_download/data/boardgames-data/bgg-data-cleaned.json', 'r', encoding="utf-8") as f:
        data = json.load(f)
    print("dataset loaded")

    print("loading spacy en model...")
    nlp = spacy.load("en_core_web_lg")
    nlp.add_pipe(LanguageDetector(), name='language_detector', last=True)
    print("model loaded")

    game_lang_dict = {}
    for item in data["items"]:
        for com in item["comments"]:
            comment = nlp(mt.pre_processing(com["value"].lower()))
            comment_lang, comment_lang_score = comment._.language.values()
            if comment_lang not in game_lang_dict.keys():
                game_lang_dict[comment_lang] = 1
            else:
                game_lang_dict[comment_lang] += 1

    with open("bgg_result/games_lang_distr.json", 'w') as out:
        json.dump(game_lang_dict, out)


def plotting_categories_target_aspects(result, categories, category_type):

    for target_asp in result.keys():
        neg_values = [scores["NEG"] for id_cat, scores in result[target_asp].items()]
        pos_values = [scores["POS"] for id_cat, scores in result[target_asp].items()]
        labels = [categories[category_type][id_cat] for id_cat in result[target_asp]]

        N = len(neg_values)
        ind = np.arange(N)
        width_bars = 0.27

        fig = plt.figure()
        ax = fig.add_subplot(111)

        rects1 = ax.bar(ind, neg_values, width_bars, color='r')
        rects2 = ax.bar(ind + width_bars, pos_values, width_bars, color='g')

        ax.set_title(target_asp)
        ax.set_ylabel('Opinions')
        ax.set_xlabel('BGG ' + category_type)
        ax.set_xticks(ind + width_bars)
        ax.set_xticklabels(labels)
        ax.legend((rects1[0], rects2[0]), ('NEG', 'POS'))

        def autolabel(rects):
            for rect in rects:
                h = rect.get_height()
                ax.text(rect.get_x() + rect.get_width() / 2., 1.05 * h, '%d' % int(h),
                        ha='center', va='bottom')

        autolabel(rects1)
        autolabel(rects2)

        plt.xticks(rotation=90)
        plt.show()
