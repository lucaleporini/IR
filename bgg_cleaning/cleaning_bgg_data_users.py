import pprint
import json
import requests
import xmltodict

if __name__ == '__main__':
    input_folder = '../bgg_download/data/boardgames-data'
    with open(input_folder+'/bgg-data-users.json', 'r', encoding="utf-8") as f:
        data = json.load(f)

    count_user = 0

    data_result = {"users": data}
    for data_user in data_result["users"]:

        count_user += 1
        data_user["id"] = data_user.pop('@id')
        data_user["name"] = data_user.pop('@name')
        data_user["termsofuse"] = data_user.pop('@termsofuse')
        data_user["avatarlink"] = data_user["avatarlink"]["@value"]
        data_user["battlenetaccount"] = data_user["battlenetaccount"]["@value"]

        if "buddy" in data_user["buddies"].keys():
            data_user["totalbuddies"] = data_user["buddies"]["@total"]
            data_user["buddies"] = data_user["buddies"]["buddy"]
            if type(data_user["buddies"]) is dict:
                data_user["buddies"]["id"] = data_user["buddies"].pop("@id")
                data_user["buddies"]["name"] = data_user["buddies"].pop("@name")
                data_user["buddies"] = [data_user["buddies"]]
            else:
                for buddy in data_user["buddies"]:
                    buddy["id"] = buddy.pop("@id")
                    buddy["name"] = buddy.pop("@name")
        else:
            data_user["totalbuddies"] = '0'

        data_user["country"] = data_user["country"]["@value"]
        data_user["firstname"] = data_user["firstname"]["@value"]

        if "guild" in data_user["guilds"].keys():
            data_user["totalguilds"] = data_user["guilds"]["@total"]
            data_user["guilds"] = data_user["guilds"]["guild"]
            if type(data_user["guilds"]) is dict:
                data_user["guilds"]["id"] = data_user["guilds"].pop("@id")
                data_user["guilds"]["name"] = data_user["guilds"].pop("@name")
                data_user["guilds"] = [data_user["guilds"]]
            else:
                for guild in data_user["guilds"]:
                    guild["id"] = guild.pop("@id")
                    guild["name"] = guild.pop("@name")
        else:
            data_user["totalguilds"] = '0'

        if "hot" in data_user.keys():
            data_user["hot"] = data_user["hot"]["item"]
            if type(data_user["hot"]) is dict:
                data_user["hot"]["id"] = data_user["hot"].pop("@id")
                data_user["hot"]["name"] = data_user["hot"].pop("@name")
                data_user["hot"]["rank"] = data_user["hot"].pop("@rank")
                data_user["hot"]["type"] = data_user["hot"].pop("@type")
                data_user["hot"] = [data_user["hot"]]
            else:
                for item in data_user["hot"]:
                    item["id"] = item.pop("@id")
                    item["name"] = item.pop("@name")
                    item["rank"] = item.pop("@rank")
                    item["type"] = item.pop("@type")

        data_user["lastlogin"] = data_user["lastlogin"]["@value"]
        data_user["lastname"] = data_user["lastname"]["@value"]
        data_user["marketrating"] = data_user["marketrating"]["@value"]
        data_user["psnaccount"] = data_user["psnaccount"]["@value"]
        try:
            data_user["stateorprovince"] = data_user["stateorprovince"]["@value"]
        except:
            pprint.pprint(data_user["stateorprovince"])
            input()

        data_user["steamaccount"] = data_user["steamaccount"]["@value"]

        if "top" in data_user.keys():
            data_user["top"] = data_user["top"]["item"]
            if type(data_user["top"]) is dict:
                data_user["top"]["id"] = data_user["top"].pop("@id")
                data_user["top"]["name"] = data_user["top"].pop("@name")
                data_user["top"]["rank"] = data_user["top"].pop("@rank")
                data_user["top"]["type"] = data_user["top"].pop("@type")
                data_user["top"] = [data_user["top"]]
            else:
                for item in data_user["top"]:
                    item["id"] = item.pop("@id")
                    item["name"] = item.pop("@name")
                    item["rank"] = item.pop("@rank")
                    item["type"] = item.pop("@type")

        data_user["traderating"] = data_user["traderating"]["@value"]
        data_user["webaddress"] = data_user["webaddress"]["@value"]
        data_user["wiiaccount"] = data_user["wiiaccount"]["@value"]
        data_user["xboxaccount"] = data_user["xboxaccount"]["@value"]
        data_user["yearregistered"] = data_user["yearregistered"]["@value"]

        print("REMAINING ", len(data_result["users"]) - count_user, "USERS")

    with open(input_folder+'/bgg-data-users-cleaned.json', 'w', encoding="utf-8") as out:
        json.dump(data_result, out)



