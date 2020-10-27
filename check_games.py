import json
import string


def counter_valid_games(data):
    counter_not_valid = 0
    counter_valid = 0
    for item in data["items"]["item"]:
        if "comments" not in item.keys():
            counter_not_valid += 1
        else:
            counter_valid += 1

    return counter_not_valid, counter_valid


def counter_comments(data):
    item_comments = [len(item["comments"]["comment"]) for item in data["items"]["item"] if "comments" in item.keys()]
    return item_comments, sum(item_comments), max(item_comments)


def is_english(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True


def has_only_latin_letters(name):
    char_set = string.ascii_letters + string.punctuation + string.digits
    return all((True if x in char_set else False for x in name))


def detect_comment_not_english(data, detection_function):
    count_comment_not_english = 0
    for item in data["items"]["item"]:
        if "comments" in item.keys():
            if type(item["comments"]["comment"]) is list:
                for comment in item["comments"]["comment"]:
                    if not detection_function(comment["@value"]):
                        count_comment_not_english += 1
            else:
                if not detection_function(item["comments"]["comment"]["@value"]):
                    count_comment_not_english += 1

    print("COMMENT NOT IN ENGLISH:", count_comment_not_english)


if __name__ == '__main__':
    with open('boardgames-temp/result/bgg-data.json', 'r', encoding="utf-8") as f:
        data = json.load(f)
    # games_not_valid, games_valid = counter_valid_games(data)
    # print("GAMES NOT VALID (ZERO COMMENTS):", games_not_valid)
    # print("GAMES VALID (MORE COMMENTS):", games_valid)
    # items_comments, tot_comments, max_comments = counter_comments(data)
    # print(len(items_comments), tot_comments, max_comments)

    # plotting bars of number of comments
    # plt.hist(items_comments, bins=range(min(items_comments), max(items_comments) + 100, 100), cumulative=True)
    # plt.show()

    # detect_comment_not_english(data, is_english)
    # detect_comment_not_english(data, has_only_latin_letters)

    c = 0
    for comment in data["items"]["item"][100]["comments"]["comment"]:
        print(comment["@value"])
        c += 1
        if c == 5:
            break



