import re


'''def detect_noun(token):
    nouns = []
    children = list(token.children)
    negation = False
    for child in children:
        if child.pos == NOUN or child.pos == PROPN:
            nouns.append(child.text)
            print("CHILD", child.text, child.pos_, child.dep_)
            for child_of_child in list(child.children):
                print("CHILD OF CHILD", child_of_child.text, child_of_child.pos_, child_of_child.dep_)
                if child_of_child.pos == PROPN and child_of_child.dep == conj:
                    nouns.append(child_of_child .text)
    return nouns


# rileva gli aggettivi e aggettivi con congiunzione
def detect_adj_conj(token):
    adj_conj = []
    children = list(token.children)
    for child in children:
        # add to result couple NOUN + ADJ
        if child.pos == ADJ:
            adj_conj.append(child.text.lower())
            for child_of_child in list(child.children):
                # add to result couple NOUN + ADJ conjution (es. black and [white] [game])
                if child_of_child.pos == ADJ and child_of_child.dep == conj:
                    adj_conj.append(child_of_child.text.lower())
    return adj_conj


def detect_noun_adj(doc):
    result = []
    for token in doc:
        print(token.text, token.pos_, token.dep_, token.tag_, token.head)
        children = list(token.children)
        print("CHILDREN:", children)
        if token.pos == NOUN:
            # result += [(token.text.lower(), adj, False) for adj in detect_adj_conj(token)]

            for child in token.children:
                # add to result couple NOUN + ADJ
                if child.pos == ADJ:
                    result.append((token.text.lower(), child.text.lower(), False))
                    for child_of_child in child.children:
                        # add to result couple NOUN + ADJ conjution (es. black and [white] [game])
                        if child_of_child.pos == ADJ and child_of_child.dep == conj:
                            result.append((token.text, child_of_child.text.lower(), False))

        if token.pos == AUX or token.pos == VERB:
            # list_adj_conj = detect_adj_conj(token) --> determina gli aggettivo nel predicato o predicato nominale
            # list_noun = detect_noun(token) -> determina i sostantivi o soggetto da associare l'aggettivo
            # result += [(n, adj) for n in detect_noun(token) for adj in detect_adj_conj(token)]

            nouns = []
            adjs_neg = []
            verb_negation = False
            for child in token.children:

                if child.pos == NOUN or child.pos == PROPN:
                    nouns.append(child.text)
                    for child_of_child in child.children:
                        if child_of_child.pos == PROPN and child_of_child.dep == conj:
                            nouns.append(child_of_child.text)

                # add to result couple NOUN + ADJ
                if child.pos == ADJ:
                    child_negation = False
                    for child_of_child in child.children:
                        # controllo se l'aggettivo individuato presenta una congiunzione con un altro aggettivo
                        if child_of_child.pos == ADJ and child_of_child.dep == conj:
                            child_of_child_negation = False
                            # controllo l'aggettivo in congiunzione presenta una negazione
                            for child_of_child_of_child in child_of_child.children:
                                if child_of_child_of_child.pos == PART and child_of_child_of_child.dep == neg:
                                    child_of_child_negation = True
                            adjs_neg.append((child_of_child.text.lower(), child_of_child_negation))

                        if child_of_child.pos == PART and child_of_child.dep == neg:
                            child_negation = True
                    adjs_neg.append((child.text.lower(), child_negation))

                if child.pos == PART and child.dep == neg:
                    print(adjs_neg)
                    verb_negation = True

            if verb_negation:
                print([(noun, adj, n) for noun in nouns for adj, n in adjs_neg])
                print([(noun, adj, not n) for noun in nouns for adj, n in adjs_neg])
                result += [(noun, adj, not n) for noun in nouns for adj, n in adjs_neg]
            else:
                result += [(noun, adj, n) for noun in nouns for adj, n in adjs_neg]
        print("")
    # to visualize the dependency
    # spacy.displacy.serve(doc, style='dep')
    return result'''


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
                        '''if noun_child.dep_ == "compound":
                            noun_text = noun_child.text + " " + noun_text'''

                    # check shifting in verb/aux
                    if noun.dep_ in ["attr", "dobj"] and noun.head.pos_ in ["AUX", "VERB"]:
                        noun_verb = noun.head
                        for verb_child in noun_verb.children:
                            if verb_child.dep_ == "neg":
                                shifted = True

                            # add couple (subject, adj_to_object_complement) replacing subject with obj complement
                            '''if verb_child.dep_ == "nsubj":
                                verb_subj = verb_child.text
                                addAspectOpinion(verb_subj, (token.text, shifted, modifier))
                                for subj_child in verb_subj.children:
                                    if subj_child.dep_ == "conj" and subj_child.pos_ in ["NOUN", "PROPN"]:
                                        addAspectOpinion(subj_child.text, (token.text, shifted, modifier))'''

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
            if token.dep_ in ["acomp", "pobj", "attr"]:
                modifier = ""
                shifted = False

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
