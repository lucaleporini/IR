import json
import pprint

if __name__ == '__main__':
    print("loading dataset..")
    with open('bgg_download/data/boardgames-data/bgg-data-cleaned.json', 'r', encoding="utf-8") as f:
        data_games = json.load(f)
    with open('bgg_download/data/boardgames-data/bgg-data-users-cleaned.json', 'r', encoding="utf-8") as f:
        data_users = json.load(f)
    with open('bgg_download/data/boardgames-data/bgg-data-users-index.json', 'r', encoding="utf-8") as f:
        data_users_index = json.load(f)
    with open('bgg_download/data/boardgames-data/bgg-data-games-categories.json', 'r', encoding="utf-8") as f:
        data_categories = json.load(f)
    print("dataset loaded")

    category_type = 'boardgamecategory'
    categories = data_categories[category_type].items()

    # category_id = '1028'

    category_scores = {}
    for category_id, category_name in categories:
        # giochi appartenenti alla categoria selezionata
        games_of_selected_category = []
        for game in data_games["items"]:
            for link in game["links"]:
                if link["type"] == category_type and link["id"] == category_id:
                    games_of_selected_category.append(game["id"])

        # utenti che presentano nella propria top list almeno un gioco appartente alla categoria selezionata
        selected_users = []
        for user in data_users["users"]:
            if "top" in user.keys():
                for game in user["top"]:
                    if game["id"] in games_of_selected_category and user["name"] not in selected_users:
                        selected_users.append(user["name"])
        print("Selected users:", len(selected_users))

        num_comments_from_selected_users = 0
        num_pos_comments_from_selected_users = 0
        num_neg_comments_from_selected_users = 0
        num_NA_comments_from_selected_users = 0
        for game in data_games["items"]:
            for link in game["links"]:
                if link["type"] == category_type and link["id"] == category_id:
                    for comment in game["comments"]:
                        if comment["username"] in selected_users:
                            num_comments_from_selected_users += 1
                            if not comment["rating"] == "N/A":
                                if float(comment["rating"]) < 6:
                                    num_neg_comments_from_selected_users += 1
                                else:
                                    num_pos_comments_from_selected_users += 1
                            else:
                                num_NA_comments_from_selected_users += 1

        tot_comments_from_selected_users = 0
        for user in selected_users:
            tot_comments_from_selected_users += data_users_index[user]

        category_scores[category_id] = (num_pos_comments_from_selected_users,
                                          num_neg_comments_from_selected_users,
                                          num_comments_from_selected_users)

        '''print("# commenti utenti selezionati su giochi della categoria considerata:", num_comments_from_selected_users)
        print("# totale di commenti degli utenti selezionati:", tot_comments_from_selected_users)
        print("Tendenza a commentare giochi preferiti:", num_comments_from_selected_users/tot_comments_from_selected_users*100)
    
        print("# commenti POSITIVI:", num_pos_comments_from_selected_users)
        print("Rapporto positivi/totale-NA",
              num_pos_comments_from_selected_users /
              (num_comments_from_selected_users - num_NA_comments_from_selected_users) * 100)
    
        print("# commenti NEGATIVI:", num_neg_comments_from_selected_users)
        print("Rapporto negativi/totale-NA",
              num_neg_comments_from_selected_users /
              (num_comments_from_selected_users - num_NA_comments_from_selected_users) * 100)'''

    tot_pos_score = 0
    tot_neg_score = 0
    for category_id, val_comments in category_scores.items():
        pos, neg, tot = val_comments
        na = tot - (pos + neg)
        tot_pos_score += pos/(tot-na) * 100
        tot_neg_score += neg/(tot-na) * 100

    print("TENDENZA di valutazione degli utenti dei giochi preferiti")
    print("POS:", tot_pos_score/len(category_scores.keys()))
    print("NEG:", tot_neg_score/len(category_scores.keys()))

    with open("bgg_result/user_categories_comments.json", 'w') as out:
        json.dump(category_scores, out)





