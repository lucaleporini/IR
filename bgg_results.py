import json
import pprint

neu_pol_threshold = 0.2
category_type = "boardgamecategory"
result_path = "bgg_result/aop_"+category_type+"_20_500_500.json"
target_aspects_path = "ThematicAspects.json"
games_categories_path = "bgg_download/data/bgg-data-games-categories.json"


def classify_polarity(score):
    if score < - neu_pol_threshold:
        return "NEG"
    elif -neu_pol_threshold < score < neu_pol_threshold:
        return "NEU"
    else:
        return "POS"


if __name__ == '__main__':
    with open(result_path, 'r', encoding="utf-8") as f:
        ao_polarity_category_dict = json.load(f)  # {id_category: {aspect: [(opinion, polarity), ...]}}
    with open(target_aspects_path, 'r', encoding="utf-8") as f:
        target_aspects = json.load(f)  # {target_aspect: [aspects,..]
    with open(games_categories_path, 'r', encoding="utf-8") as f:
        categories = json.load(f)

    result = {}  # {target_aspect: {id_category: {NEG: xxx, NEU: xxx, POS: xxx}}}
    for target_asp, aspects in target_aspects.items():
        result[target_asp] = {}
        for id_cat in ao_polarity_category_dict.keys():
            result[target_asp][id_cat] = {"NEG": 0, "NEU": 0, "POS": 0}
            for aspect, opinions_polarities in ao_polarity_category_dict[id_cat].items():
                if aspect in aspects:
                    for opn, pol in opinions_polarities:
                        pol_classification = classify_polarity(pol)
                        result[target_asp][id_cat][pol_classification] += 1

    # plotting result for each target aspect --> x: selected categories, y: opinions
    # bgg_t.plotting_target_aspects(categories, result)

    for polarity_label in ["NEG", "POS"]:
        print("POLARITY:", polarity_label, "--------------------------------------------------------------------------")
        for target_asp in result.keys():
            target_asp_score = sorted([(id_cat, result[target_asp][id_cat][polarity_label] /
                                        (result[target_asp][id_cat]["NEG"] +
                                         result[target_asp][id_cat]["POS"]))
                                       if (result[target_asp][id_cat]["NEG"] + result[target_asp][id_cat]["POS"]) > 0
                                       else (id_cat, 0)
                                       for id_cat in result[target_asp].keys()],
                                      key=lambda x: x[1], reverse=True)
            print(target_asp)
            pprint.pprint([(categories[category_type][id_cat[0]], id_cat[1]) for id_cat in target_asp_score])


