import json

if __name__ == '__main__':
    input_folder = '../bgg_download/data/boardgames-data'
    with open(input_folder+'/bgg-data.json', 'r', encoding="utf-8") as f:
        data = json.load(f)

    count_game = 0
    data["items"] = data["items"]["item"]
    for data_game in data["items"]:
        count_game += 1
        data_game["id"] = data_game.pop('@id')

        data_game["type"] = data_game.pop('@type')

        if type(data_game["name"]) is dict:
            data_game["name"]["type"] = data_game["name"].pop('@type')
            data_game["name"]["value"] = data_game["name"].pop('@value')
            data_game["name"]["sortindex"] = data_game["name"].pop('@sortindex')
            data_game["name"] = [data_game["name"]]
        else:
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

            # DIPENDENZA TRA TOTALVOTES E RESULTS
            if not int(poll_item["totalvotes"]) == 0:
                if poll_item["name"] == 'suggested_numplayers':
                    if type(poll_item["results"]) is dict:
                        poll_item["results"]["numplayers"] = poll_item["results"].pop('@numplayers')
                        for result_vote in poll_item["results"]["result"]:
                            result_vote["numvotes"] = result_vote.pop('@numvotes')
                            result_vote["value"] = result_vote.pop('@value')
                    else:
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

        if "comments" in data_game.keys():
            data_game["totalcomments"] = data_game["comments"]["@totalitems"]
            data_game["comments"] = data_game["comments"]["comment"]
            if (type(data_game["comments"])) is dict:
                data_game["comments"]["username"] = data_game["comments"].pop('@username')
                data_game["comments"]["rating"] = data_game["comments"].pop('@rating')
                data_game["comments"]["value"] = data_game["comments"].pop('@value')
                data_game["comments"] = [data_game["comments"]]
            else:
                for comment_item in data_game["comments"]:
                    comment_item["username"] = comment_item.pop('@username')
                    comment_item["rating"] = comment_item.pop('@rating')
                    comment_item["value"] = comment_item.pop('@value')
        else:
            data_game["totalcomments"] = '0'
            data_game["comments"] = []

        data_game["links"] = data_game.pop('link')
        if type(data_game["links"]) is dict:
            data_game["links"]["id"] = data_game["links"].pop('@id')
            data_game["links"]["type"] = data_game["links"].pop('@type')
            data_game["links"]["value"] = data_game["links"].pop('@value')
            data_game["links"] = [data_game["links"]]
        else:
            for link_item in data_game["links"]:
                link_item["id"] = link_item.pop('@id')
                link_item["type"] = link_item.pop('@type')
                link_item["value"] = link_item.pop('@value')

        # per il campo marketplacelisting possono esserci giochi con:
        # - dict: un solo elemento a dizionario
        # - campo "listing" come array di elementi
        # - campo "listing" con un solo elemento
        if "marketplacelistings" in data_game.keys():
            if "listing" not in data_game["marketplacelistings"].keys():
                data_game["marketplacelistings"]["condition"] = data_game["marketplacelistings"]["condition"]["@value"]
                data_game["marketplacelistings"]["listdate"] = data_game["marketplacelistings"]["listdate"]["@value"]
                data_game["marketplacelistings"]["link"] = data_game["marketplacelistings"]["link"]["@href"]
                data_game["marketplacelistings"]["notes"] = data_game["marketplacelistings"]["notes"]["@value"]
                data_game["marketplacelistings"]["price"]["currency"] = data_game["marketplacelistings"]["price"].pop('@currency')
                data_game["marketplacelistings"]["price"]["value"] = data_game["marketplacelistings"]["price"].pop('@value')
                data_game["marketplacelistings"] = [data_game["marketplacelistings"]]
            else:
                data_game["marketplacelistings"] = data_game["marketplacelistings"]["listing"]
                if type(data_game["marketplacelistings"]) is dict:
                    data_game["marketplacelistings"]["condition"] = data_game["marketplacelistings"]["condition"][
                        "@value"]
                    data_game["marketplacelistings"]["listdate"] = data_game["marketplacelistings"]["listdate"][
                        "@value"]
                    data_game["marketplacelistings"]["link"] = data_game["marketplacelistings"]["link"]["@href"]
                    data_game["marketplacelistings"]["notes"] = data_game["marketplacelistings"]["notes"]["@value"]
                    data_game["marketplacelistings"]["price"]["currency"] = data_game["marketplacelistings"][
                        "price"].pop('@currency')
                    data_game["marketplacelistings"]["price"]["value"] = data_game["marketplacelistings"]["price"].pop(
                        '@value')
                    data_game["marketplacelistings"] = [data_game["marketplacelistings"]]
                else:
                    for listing in data_game["marketplacelistings"]:
                        listing["condition"] = listing["condition"]["@value"]
                        listing["listdate"] = listing["listdate"]["@value"]
                        listing["link"] = listing["link"]["@href"]
                        listing["notes"] = listing["notes"]["@value"]
                        listing["price"]["currency"] = listing["price"].pop('@currency')
                        listing["price"]["value"] = listing["price"].pop('@value')
        else:
            data_game["marketplacelistings"] = []

        data_game["statistics_ratings"] = data_game["statistics"]["ratings"]
        data_game.pop('statistics', None)

        data_game["statistics_ratings"]["average"] = \
            data_game["statistics_ratings"]["average"]["@value"]

        data_game["statistics_ratings"]["averageweight"] = \
            data_game["statistics_ratings"]["averageweight"]["@value"]

        data_game["statistics_ratings"]["bayesaverage"] = \
            data_game["statistics_ratings"]["bayesaverage"]["@value"]

        data_game["statistics_ratings"]["median"] = \
            data_game["statistics_ratings"]["median"]["@value"]

        data_game["statistics_ratings"]["numcomments"] = \
            data_game["statistics_ratings"]["numcomments"]["@value"]

        data_game["statistics_ratings"]["numweights"] = \
            data_game["statistics_ratings"]["numweights"]["@value"]

        data_game["statistics_ratings"]["owned"] = \
            data_game["statistics_ratings"]["owned"]["@value"]

        data_game["statistics_ratings"]["stddev"] = \
            data_game["statistics_ratings"]["stddev"]["@value"]

        data_game["statistics_ratings"]["trading"] = \
            data_game["statistics_ratings"]["trading"]["@value"]

        data_game["statistics_ratings"]["usersrated"] = \
            data_game["statistics_ratings"]["usersrated"]["@value"]

        data_game["statistics_ratings"]["wanting"] = \
            data_game["statistics_ratings"]["wanting"]["@value"]

        data_game["statistics_ratings"]["wishing"] = \
            data_game["statistics_ratings"]["wishing"]["@value"]

        data_game["statistics_ratings"]["ranks"] = data_game["statistics_ratings"]["ranks"]["rank"]
        if type(data_game["statistics_ratings"]["ranks"]) is dict:
            data_game["statistics_ratings"]["ranks"]["bayesaverage"] = data_game["statistics_ratings"]["ranks"].pop('@bayesaverage')
            data_game["statistics_ratings"]["ranks"]["friendlyname"] = data_game["statistics_ratings"]["ranks"].pop('@friendlyname')
            data_game["statistics_ratings"]["ranks"]["id"] = data_game["statistics_ratings"]["ranks"].pop('@id')
            data_game["statistics_ratings"]["ranks"]["name"] = data_game["statistics_ratings"]["ranks"].pop('@name')
            data_game["statistics_ratings"]["ranks"]["type"] = data_game["statistics_ratings"]["ranks"].pop('@type')
            data_game["statistics_ratings"]["ranks"]["value"] = data_game["statistics_ratings"]["ranks"].pop('@value')
            data_game["statistics_ratings"]["ranks"] = [data_game["statistics_ratings"]["ranks"]]
        else:
            for rank_item in data_game["statistics_ratings"]["ranks"]:
                rank_item["bayesaverage"] = rank_item.pop('@bayesaverage')
                rank_item["friendlyname"] = rank_item.pop('@friendlyname')
                rank_item["id"] = rank_item.pop('@id')
                rank_item["name"] = rank_item.pop('@name')
                rank_item["type"] = rank_item.pop('@type')
                rank_item["value"] = rank_item.pop('@value')

        print("REMAINING ", len(data["items"]) - count_game, "GAMES")

    with open(input_folder+'/bgg-data-cleaned.json', 'w', encoding="utf-8") as out:
        json.dump(data, out)
