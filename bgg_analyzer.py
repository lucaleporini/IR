import spacy
import mining_tools as mt
import json
import pprint
import matplotlib.pyplot as plt
from spacy_langdetect import LanguageDetector


params = {
    "lang": "en",
    "lang_score": 0.70,
    "min_len": 10
}

if __name__ == '__main__':
    print("loading dataset..")
    with open('bgg_download/data/boardgames-data/bgg-data-cleaned.json', 'r', encoding="utf-8") as f:
        data = json.load(f)
    print("dataset loaded")

    print("loading model...")
    nlp = spacy.load("en_core_web_lg")
    nlp.add_pipe(LanguageDetector(), name='language_detector', last=True)
    print("model loaded!")

    # GENERALE
    empty_count = 0
    comment_w_rating = 0
    total_rating = 0.0
    neg_count = 0
    neu_count = 0
    pos_count = 0
    en_comments = 0
    comment_len = 0

    # ANALISI
    comment_count = 0
    empty_asp_opn = 0
    pos_comments_count = 0
    neg_comments_count = 0

    game_asp_opn_dict = {"neg_comments": {}, "pos_comments": {}}
    game_lang_dict = {}
    index_game = 20
    # for i in range(0, 20):
    for com in data["items"][index_game]["comments"]:
        # comment = data["items"][0]["comments"][i]
        comment = nlp(mt.pre_processing(com["value"].lower()))
        comment_lang, comment_lang_score = comment._.language.values()
        if comment_lang not in game_lang_dict.keys():
            game_lang_dict[comment_lang] = 1
        else:
            game_lang_dict[comment_lang] += 1
        if not com["rating"] == "N/A" and comment_lang == params["lang"] and comment_lang_score > params["lang_score"] and len(comment) > params["min_len"]:
            asp_opn_dict = mt.extract_aspect_opinion(comment)
            if asp_opn_dict.keys():
                comment_count += 1
                pol_comment = "neg_comments" if float(com["rating"]) < 6 else "pos_comments"

                # ONLY FOR STATS
                if pol_comment == "neg_comments":
                    pos_comments_count += 1
                else:
                    neg_comments_count += 1

                for aspect, opinion in asp_opn_dict.items():
                    if aspect not in game_asp_opn_dict.keys():
                        game_asp_opn_dict[pol_comment][aspect] = opinion
                    else:
                        game_asp_opn_dict[pol_comment][aspect] += opinion
            else:
                empty_asp_opn += 1

        if comment_lang == params["lang"] and comment_lang_score > params["lang_score"]:
            en_comments += 1
        if len(comment) > params["min_len"]:
            comment_len += 1

        asp_opn_dict = mt.extract_aspect_opinion(comment)
        if not asp_opn_dict.keys():
            empty_count += 1
        if not com["rating"] == "N/A":
            rating = float(com["rating"])
            total_rating += rating
            comment_w_rating += 1
            if rating < 6:
                neg_count += 1
            else:
                pos_count += 1
    
    totalcomments = len(data["items"][index_game]["comments"])
    print("GENERAL INFO ABOUT GAME:", data["items"][index_game]["id"])
    print("Total comments:", totalcomments)
    print("Total ENGLISH comments:", en_comments, en_comments/totalcomments*100)
    print("Total NOT ENGLISH comments:", totalcomments-en_comments, (totalcomments-en_comments)/totalcomments*100)
    print("COMMENT with LENGHT > "+str(params["min_len"])+":", comment_len)
    print()

    print("EMPTY COMMENTS:", empty_count, empty_count/totalcomments*100)
    print("VALID COMMENTS:", totalcomments-empty_count, (totalcomments - empty_count)/totalcomments*100)
    print()

    print("TOTAL COMMENT WITH RATING:", comment_w_rating)
    print("RATING MEDIO:", total_rating/comment_w_rating)
    print("NEGATIVE RATING (< 6):", neg_count, neg_count/comment_w_rating*100)
    print("POSITIVE RATING (>= 6):", pos_count, pos_count/comment_w_rating*100)
    print()

    print("PLOTTING GAME LANG DICT")
    pprint.pprint(game_lang_dict)
    plt.plot(game_lang_dict.keys(), game_lang_dict.values())
    plt.show()
    print()

    print("TOTAL COMMENTS ANALYSED:", comment_count)
    print("TOTAL COMMENTS with EMPTY AO DICT:", empty_asp_opn)
    print("TOTAL POSITIVE COMMENTS (rating >= 6):", pos_comments_count)
    print("TOTAL NEGATIVE COMMENTS (rating < 6)", neg_comments_count)
    pprint.pprint(game_asp_opn_dict)



