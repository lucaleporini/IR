import re
import spacy
import csv
from nltk.corpus import wordnet
import vaderSentiment.vaderSentiment as vader
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Loading Spacy Model
nlp = spacy.load("en_core_web_lg")
sentiment_analyzer = SentimentIntensityAnalyzer()

# Loading SentiWordNet
file = open("SentiWordNetDict.txt", newline="\n")
filereader = csv.reader(file, delimiter=",")
next(filereader)

swn_dict = {}
for row in filereader:
    if row:
        swn_dict[(row[0], row[1])] = (float(row[2]), float(row[3]))


def pre_processing(sentence):
    s = re.sub(r"[^a-zA-Z0-9.',:;?!]+", ' ', sentence)
    s = re.sub(r"([;. ]+)([Bb])ut", " but", s)
    s = re.sub(r"([;., ]+)([Aa])nd", " and", s)
    return s


def extract_aspect_opinion(sentence):
    dict_result = {}

    def addAspectOpinion(aspect, opinion):
        if aspect not in dict_result.keys():
            dict_result[aspect] = [opinion]
        else:
            if opinion[0] not in [op for op, is_shifted, mod in dict_result[aspect]]:
                dict_result[aspect].append(opinion)

    for token in sentence:
        # print(token.text, token.pos_, token.dep_, token.tag_, token.head)
        # print(list(token.children), "\n")

        if token.tag_ in ["JJ", "JJS"]:
            modifier = ""
            shifted = False
            for jj_child in token.children:
                if jj_child.dep_ == "advmod":
                    modifier = jj_child.text
                if jj_child.dep_ == "neg":
                    shifted = True

            # NOUN-ADJ case with dep_= amod
            if token.dep_ in ["amod", "compound"]:
                noun = token.head
                if noun.pos_ in ["NOUN", "PROPN"]:

                    # Check if head is a compound noun
                    noun_text = noun.text
                    for noun_child in noun.children:
                        if noun_child.dep_ == "neg":
                            shifted = True

                    # check shifting in verb/aux
                    if noun.dep_ in ["attr", "dobj"] and noun.head.pos_ in ["AUX", "VERB"]:
                        noun_verb = noun.head
                        for verb_child in noun_verb.children:
                            if verb_child.dep_ == "neg":
                                shifted = True

                    addAspectOpinion(noun_text, (token.text, shifted, modifier))

                    # Propagate to subject conjuction
                    for noun_child in noun.children:
                        if noun_child.dep_ == "conj" and noun_child.pos_ in ["NOUN", "PROPN"]:
                            addAspectOpinion(noun_child.text, (token.text, shifted, modifier))

                    # ADJ conjuction with check shifting
                    for adj_child in token.children:
                        if adj_child.dep_ == "conj" and adj_child.tag_ in ["JJ", "JJS"]:
                            shifted = False
                            modifier = ""
                            for adj_child_of_child in adj_child.children:
                                if adj_child_of_child.dep_ == "neg":
                                    shifted = True
                                if adj_child_of_child.dep_ == "advmod":
                                    modifier = adj_child_of_child.text
                            addAspectOpinion(noun_text, (adj_child.text, shifted, modifier))

            # nuon -> verb --> adj with dep_ = acomp
            if token.dep_ in ["acomp", "pobj", "attr", "oprd"]:
                modifier = ""
                shifted = False

                for adj_child in token.children:
                    if adj_child.dep_ == "advmod":
                        modifier = adj_child.text

                verb = token.head
                while (verb.pos_ != "VERB" and verb.pos_ != "AUX") and verb.dep_ == "conj":
                    verb = verb.head

                for verb_child in verb.children:
                    if verb_child.dep_ == "neg":
                        shifted = True

                for verb_child in verb.children:
                    if verb_child.dep_ == "nsubj":
                        subject = verb_child

                        # Check if subject is a compound noun
                        noun_text = subject.text
                        for noun_child in subject.children:
                            if noun_child.dep_ == "compound":
                                noun_text = noun_child.text + " " + noun_text

                        addAspectOpinion(noun_text, (token.text, shifted, modifier))

                        # Propagate to subject conjuction
                        for subj_child in subject.children:
                            if subj_child.dep_ == "conj" and subj_child.pos_ == "NOUN":
                                addAspectOpinion(subj_child.text, (token.text, shifted, modifier))

                        # Propagate to adjective conjuction
                        for adj_child in token.children:
                            if adj_child.dep_ == "conj" and adj_child.tag_ in ["JJ", "JJS"]:
                                modifier = ""
                                shifted = False
                                for subchild in adj_child.children:
                                    if subchild.dep_ == "neg":
                                        shifted = True
                                    if subchild.dep_ == "advmod":
                                        modifier = subchild.text

                                addAspectOpinion(noun_text, (adj_child.text, shifted, modifier))

    return dict_result


def swn_polarity(word):
    synset = wordnet.synsets(word)
    if len(synset) == 0:
        return 0
    swn_scores = []
    for syn in synset:
        if syn.pos() in ["a", "s"]:
            # print(syn.pos(), str(syn.offset()).zfill(8), swn_dict[("a", str(syn.offset()).zfill(8))])
            sysnet_polarity = swn_dict[("a", str(syn.offset()).zfill(8))]
            if sysnet_polarity[0] > sysnet_polarity[1]:
                swn_scores.append(sysnet_polarity[0])
            elif sysnet_polarity[0] < sysnet_polarity[1]:
                swn_scores.append(-sysnet_polarity[1])
    if len(swn_scores) == 0:
        return 0
    return sum(swn_scores) / len(swn_scores)


def get_polarity(opinion):
    adj, shifted, mod = opinion
    phrase = ("not " if shifted else "") + mod + " " + adj
    vader_score = sentiment_analyzer.polarity_scores(phrase)
    # return vader_score["compound"]

    if vader_score["compound"] != 0:
        return vader_score["compound"]

    swn_score = swn_polarity(opinion[0])
    if mod and not -0.2 < swn_score < 0.2:
        if vader.BOOSTER_DICT.get(opinion[1]) is not None:
            swn_score += vader.BOOSTER_DICT[opinion[1]] if swn_score > 0 else -vader.BOOSTER_DICT[opinion[1]]
        swn_score = 1 if swn_score > 1 else -1 if swn_score < -1 else swn_score
    swn_score = -swn_score if shifted else swn_score
    return swn_score
