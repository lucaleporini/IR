import mining_tools as min_t
import bgg_tools as bgg_t
import json
from nltk.stem import WordNetLemmatizer

category_params = {
    "type": "boardgamecategory",
    "k": 10
}
max_comments_game = 500
max_users_for_category = 500

lemmatizer = WordNetLemmatizer()
nlp = min_t.nlp


if __name__ == '__main__':

    users = bgg_t.get_list_users_w_top_list()  # dict {username: user}
    games = bgg_t.get_game_list_from_users(users)  # dict {id_game: game}

    selected_categories = bgg_t.select_k_categories(games, category_params)  # array [(id_cat, name)]
    selected_categories_ids = [id for id, name in selected_categories]  # [id_cat]

    # users_categories = {username: [list of cat selected]
    # users_categories_values = {id_cat: {"max_value": xxx, "min_value": xxx}
    users_categories, users_categories_values = bgg_t.users_categorization(users, games, category_params,
                                                                                selected_categories_ids,
                                                                                max_users_for_category)

    # all comments from users by selecting max_comments_game ordered by decreasing length
    bgg_t.games_processing(users_categories, games, max_comments_game)

    count_game = 0
    ao_polarity_category_dict = {id_cat: {} for id_cat in selected_categories_ids}
    for game in games.values():
        count_game += 1
        for comment in game["comments"]:
            spacy_comment = nlp(min_t.pre_processing(comment["value"].lower()))

            sentences = []
            start = 0
            for token in spacy_comment:
                if token.sent_start:
                    sentences.append(spacy_comment[start:token.i])
                    start = token.i
                if token.i == len(spacy_comment) - 1:
                    sentences.append(spacy_comment[start:(token.i + 1)])

            comment_asp_opn_dict = {}
            for sentence in sentences:
                sentence_asp_opn_dict = min_t.extract_aspect_opinion(spacy_comment)
                for k, v in sentence_asp_opn_dict.items():
                    lemma_k = lemmatizer.lemmatize(k)
                    if comment_asp_opn_dict.get(lemma_k) is None:
                        comment_asp_opn_dict[lemma_k] = v
                    else:
                        comment_asp_opn_dict[lemma_k] = set(list(comment_asp_opn_dict[lemma_k]) + v)

            if len(comment_asp_opn_dict) > 0:
                for aspect, opinions in comment_asp_opn_dict.items():
                    for opinion in opinions:
                        polarity = min_t.get_polarity(opinion)
                        for user_cat in users_categories[comment["username"]]:
                            if aspect not in ao_polarity_category_dict[user_cat].keys():
                                ao_polarity_category_dict[user_cat][aspect] = [(opinion, polarity)]
                            else:
                                ao_polarity_category_dict[user_cat][aspect].append((opinion, polarity))

        print("REMAINING GAMES ", len(games.values())-count_game)

    with open("bgg_result/aop_"+category_params["type"]+"_"+
              str(category_params["k"])+"_"+
              str(max_users_for_category)+"_"+str(max_comments_game)+".json", "w") as out_file:
        json.dump(ao_polarity_category_dict, out_file)

