import pprint
import spacy
import json


def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

# assert not isEnglish('slabiky, ale liší se podle významu')
# assert isEnglish('English')
# assert not isEnglish('ގެ ފުރަތަމަ ދެ އަކުރު ކަ')
# assert not isEnglish('how about this one : 通 asfަ')
# assert isEnglish('?fd4))45s&')

# with open('boardgames-temp/result/bgg-data.json', 'r', encoding="utf-8") as f:
#    data = json.load(f)
if __name__ == '__main__':
    with open('boardgames-temp/result/bgg-data.json', 'r', encoding="utf-8") as f:
        data = json.load(f)

    count_game = 0
    for data_game in data["items"]["item"]:
        count_game += 1
        data_game["id"] = data_game.pop('@id')

        data_game["type"] = data_game.pop('@type')

        for name_item in data_game["name"]:
            name_item["type"] = name_item.pop('@type')
            name_item["value"] = name_item.pop('@value')
            name_item["sortindex"] = name_item.pop('@sortindex')

        data_game["yearpublished"] = data_game["yearpublished"]["@value"]

        data_game["maxplayers"] = data_game["maxplayers"]["@value"]
        data_game["minplayers"] = data_game["minplayers"]["@value"]

        data_game["maxplaytime"] = data_game["maxplaytime"]["@value"]
        data_game["minplaytime"] = data_game["minplaytime"]["@value"]

        data_game["minage"] = data_game["minage"]["@value"]

        for poll_item in data_game["poll"]:
            poll_item["name"] = poll_item.pop('@name')
            poll_item["title"] = poll_item.pop('@title')
            poll_item["totalvotes"] = poll_item.pop('@totalvotes')
            if poll_item["name"] == 'suggested_numplayers':
                for result_item in poll_item["results"]:
                    result_item["numplayers"] = result_item.pop('@numplayers')
                    for result_vote in result_item["result"]:
                        result_vote["numvotes"] = result_vote.pop('@numvotes')
                        result_vote["value"] = result_vote.pop('@value')
            elif poll_item["name"] == 'suggested_playerage':
                poll_item['results'] = poll_item['results']['result']
                for result_vote in poll_item['results']:
                    result_vote["numvotes"] = result_vote.pop('@numvotes')
                    result_vote["value"] = result_vote.pop('@value')
            elif poll_item["name"] == 'language_dependence':
                poll_item['results'] = poll_item['results']['result']
                for result_vote in poll_item['results']:
                    result_vote["level"] = result_vote.pop('@level')
                    result_vote["numvotes"] = result_vote.pop('@numvotes')
                    result_vote["value"] = result_vote.pop('@value')

        data_game["totalcomments"] = data_game["comments"]["@totalitems"]
        data_game["comments"] = data_game["comments"]["comment"]
        for comment_item in data_game["comments"]:
            comment_item["username"] = comment_item.pop('@username')
            comment_item["rating"] = comment_item.pop('@rating')
            comment_item["value"] = comment_item.pop('@value')

        data_game["links"] = data_game.pop('link')
        for link_item in data_game["links"]:
            link_item["id"] = link_item.pop('@id')
            link_item["type"] = link_item.pop('@type')
            link_item["value"] = link_item.pop('@value')

        data_game["marketplacelistings"] = data_game["marketplacelistings"]["listing"]
        for listing in data_game["marketplacelistings"]:
            listing["condition"] = listing["condition"]["@value"]
            listing["listdate"] = listing["listdate"]["@value"]
            listing["link"] = listing["link"]["@href"]
            listing["notes"] = listing["notes"]["@value"]
            listing["price"]["currency"] = listing["price"].pop('@currency')
            listing["price"]["value"] = listing["price"].pop('@value')

        data_game["statistics_ratings"] = data_game["statistics"]["ratings"]
        data_game.pop('statistics', None)

        data_game["statistics_ratings"]["average"] = \
            data_game["statistics_ratings"]["average"]["@value"]

        data_game["statistics_ratings"]["averageweight"] = \
            data_game["statistics_ratings"]["averageweight"]["@value"]

        data_game["statistics_ratings"]["bayesaverage"] = \
            data_game["statistics_ratings"]["bayesaverage"]["@value"]

        data_game["statistics_rating"]["median"] = \
            data_game["statistics_rating"]["median"]["@value"]

        data_game["statistics_rating"]["numcomments"] = \
            data_game["statistics_rating"]["numcomments"]["@value"]

        data_game["statistics_rating"]["numweights"] = \
            data_game["statistics_rating"]["numweights"]["@value"]

        data_game["statistics_rating"]["owned"] = \
            data_game["statistics_rating"]["owned"]["@value"]

        data_game["statistics_rating"]["stddev"] = \
            data_game["statistics_rating"]["stddev"]["@value"]

        data_game["statistics_rating"]["trading"] = \
            data_game["statistics_rating"]["trading"]["@value"]

        data_game["statistics_rating"]["usersrated"] = \
            data_game["statistics_rating"]["usersrated"]["@value"]

        data_game["statistics_rating"]["wanting"] = \
            data_game["statistics_rating"]["wanting"]["@value"]

        data_game["statistics_rating"]["wishing"] = \
            data_game["statistics_rating"]["wishing"]["@value"]

        data_game["statistics_rating"]["ranks"] = data_game["statistics_rating"]["ranks"]["rank"]
        for rank_item in data_game["statistics_rating"]["ranks"]:
            rank_item["bayesaverage"] = rank_item.pop('@bayesaverage')
            rank_item["friendlyname"] = rank_item.pop('@friendlyname')
            rank_item["id"] = rank_item.pop('@id')
            rank_item["name"] = rank_item.pop('@name')
            rank_item["type"] = rank_item.pop('@type')
            rank_item["value"] = rank_item.pop('@value')

        # pprint.pprint(data["items"]["item"]["statistics_rating"])
        # pprint.pprint(data["items"]["item"].keys())

        print("REMAINING ", len(data["items"]["item"]) - count_game, "GAMES")


