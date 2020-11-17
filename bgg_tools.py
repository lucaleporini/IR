import spacy
import mining_tools as mt
import json
import pprint
from spacy_langdetect import LanguageDetector




def create_categories_game_dict():
    print("loading dataset games..")
    with open('bgg_download/data/boardgames-data/bgg-data-cleaned.json', 'r', encoding="utf-8") as f:
        data = json.load(f)
    print("dataset loaded")

    categories = {}
    for item in data["items"]:
        for link in item["links"]:
            if link["type"] not in categories.keys():
                categories[link["type"]] = {link["id"]: link["value"]}
            else:
                if link["value"] not in categories[link["type"]]:
                    categories[link["type"]][link["id"]] = link["value"]

    pprint.pprint([(k, len(categories[k])) for k in categories.keys()])
    # pprint.pprint(categories["boardgamecategory"])

    with open("bgg_download/data/boardgames-data/bgg-data-games-categories.json", 'w') as out:
        json.dump(categories, out)


params = {
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