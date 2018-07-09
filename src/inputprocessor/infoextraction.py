from src.db.concepts import DBO_Concept
from src.objects.eventchain.EventFrame import EventFrame, FRAME_DESCRIPTIVE, FRAME_EVENT, FRAME_CREATION
from src.objects.nlp.Sentence import Sentence
from src.objects.storyworld.Attribute import Attribute
from src.objects.storyworld.Character import Character
from src.objects.storyworld.Object import Object
from src.objects.storyworld.Setting import Setting
from neuralcoref import Coref
import _operator
# ----- luisa


def reading(filename):
    with open(filename, 'r') as f:
        userinput = f.read()
    return userinput


def pos_ner_nc_processing(sentence):
    new_sentence = Sentence()
    new_sentence.words = sentence
    for token in sentence:
        new_sentence.children.append([])
        new_sentence.text_token.append(token.text)
        new_sentence.head_text.append(token.head.text)
        new_sentence.lemma.append(token.lemma_)
        new_sentence.pos.append(token.pos_)
        new_sentence.tag.append(token.tag_)
        new_sentence.dep.append(token.dep_)

        new_sentence.finished_nodes.append(0)
        for child in token.children:
            new_sentence.children[len(new_sentence.children)-1].append(child)

       # print("------POS------")
        print("text_token: " + token.text, "dep: " + token.dep_, "head_text: " + token.head.text)
    for ent in sentence.ents:
         new_sentence.text_ent.append(ent.text)
         new_sentence.label.append(ent.label_)

    for chunk in sentence.noun_chunks:
        new_sentence.text_chunk.append(chunk.text)
        new_sentence.dep_root.append(chunk.root.dep_)
        new_sentence.dep_root_head.append(chunk.root.head.text)
     #   print("------NC------")
        print("text_chunk: " + chunk.text, "dep_root: " + chunk.root.dep_, "dep_root_head: " + chunk.root.head.text)
    return new_sentence


def find_text_index(sent, child):
    num = 0
    child = str(child).lower()
    temp = child.split()
    for k in range(0, len(sent.text_token)):
        text_token = str(sent.text_token[k]).lower()
        if (temp[-1] == text_token) and (sent.finished_nodes[k] == 0):
            num = k
            break
    return num


def find_ent_index(sent, ent):
    ent = ent.lower()
    for k in range(0, len(sent.text_ent)):
        if ent in str(sent.text_ent[k]).lower():
            return k
            break
    return None


def details_extraction(sent, world, current_node, subj="", neg="", text=""):
    num = -1
    subject = subj
    current_index = -1
    dative = ""
    direct_object = ""
    for i in range(0, len(sent.dep)):
        if not text:
            if (sent.dep[i] == current_node) and (sent.finished_nodes[i] == 0):
                current_index = i
                sent.finished_nodes[i] = 1
                break
        else:
            if (sent.dep[i] == current_node) and (sent.finished_nodes[i] == 0) and (sent.text_token[i] == text):
                current_index = i
                sent.finished_nodes[i] = 1
                break

    if (current_node == "ROOT") and (sent.pos[i] in ["NOUN", "PROPN"]):
        add_objects(sent, sent.text_token[i], sent.dep[i], sent.lemma[i], world)

    if neg =="":
        is_negated = False
    else:
        is_negated = neg

    if current_index != -1:
        i = current_index
        for j in range(0, len(sent.children[i])):
            num = find_text_index(sent, str(sent.children[i][j]))
            if num != -1 and sent.finished_nodes[num] == 0 and\
                    sent.dep[num] in ["nsubj", "acomp", "attr", "nsubjpass", "dobj", "xcomp", "appos", "relcl",
                                      "npadvmod", "advmod", "pcomp"]:
                # nominal subject
                if sent.dep[num] == "nsubj":
                    print("ENTERED")
                    subject = compound_extraction(sent, str(sent.children[i][j]))
                    add_objects(sent, str(subject), sent.dep[num], sent.lemma[i], world)
                    add_capability(sent, str(sent.lemma[i]), str(subject), world, current_index)

                # nominal subject (passive) or direct object
                elif sent.dep[num] == "nsubjpass" or sent.dep[num] == "dobj":
                    if not subject:
                        subject = compound_extraction(sent, str(sent.children[i][j]))

                    if dative and sent.dep[num] == "dobj":
                        subject = compound_extraction(sent, str(sent.children[i][j]))
                        add_objects(sent, compound_extraction(sent, str(sent.children[i][j])), sent.dep[num],
                                    sent.lemma[i], world, dative)
                    else:
                        add_objects(sent, compound_extraction(sent, str(sent.children[i][j])), sent.dep[num],
                                    sent.lemma[i], world)

                    if sent.dep[num] == "dobj":
                        direct_object = sent.text_token[num]

                # adjectival complement
                elif sent.dep[num] == "acomp":
                    add_attributes(sent, str(sent.children[i][j]), str(subject), world, is_negated)
                    is_negated = False

                # attribute and appositional modifier
                elif sent.dep[num] == "attr":
                    if not add_settings(sent, num, subject, is_negated, world):
                        add_objects(sent, compound_extraction(sent, str(sent.children[i][j])), sent.dep[num],
                                    sent.lemma[i], world, subject)
                        if not subject:
                            subject = sent.text_token[num]

                    is_negated = False

                # appositional modifier
                elif sent.dep[num] == "appos":
                    if not add_settings(sent, num, subject, is_negated, world):
                        add_objects(sent, compound_extraction(sent, str(sent.children[i][j])), sent.dep[num],
                                    sent.lemma[i], world, compound_extraction(sent, str(sent.head_text[num])))

                    is_negated = False

                # open clausal compliment
                elif sent.dep[num] in ["xcomp", "pcomp"]:
                    add_capability(sent, str(sent.lemma[num]), str(subject), world, num)
                    is_negated = False

                # relative clause modifier
                elif sent.dep[num] == "relcl":
                    add_capability(sent, str(sent.lemma[num]), str(sent.head_text[num]), world, num)

                # noun phrase as adverbial modifier
                elif num != -1 and sent.dep[num] in ["npadvmod", "advmod"]:
                    add_settings(sent, num, subject, is_negated, world)
                    sent.finished_nodes[num] = 1

                if sent.children[num] is not None:
                    for c in sent.children[num]:
                        dep_index = find_text_index(sent, str(c))
                        if sent.finished_nodes[dep_index] == 0:
                            details_extraction(sent, world, sent.dep[num], subject, is_negated)

                sent.finished_nodes[num] = 1

            # object predicate
            elif num != -1 and sent.dep[num] == "oprd":
                if direct_object:
                    add_attributes(sent, sent.text_token[num], direct_object, world)
                else:
                    add_attributes(sent, sent.text_token[num], subject, world)

            # negation
            elif num != -1 and sent.dep[num] == "neg":
                sent.finished_nodes[num] = 1
                is_negated = True

            # object of preposition
            elif num != -1 and sent.dep[num] == "pobj":
                if not add_settings(sent, num, subject, is_negated, world):
                    add_objects(sent, compound_extraction(sent, str(sent.children[i][j])), sent.dep[num], sent.lemma[i]
                                , world)
                details_extraction(sent, world, sent.dep[num], subject, is_negated)
                sent.finished_nodes[num] = 1

            # dative - the noun to which something is given
            elif num != -1 and sent.dep[num] == "dative":
                if str(sent.text_token[num]) == "to":
                    details_extraction(sent, world, sent.dep[num], subject, is_negated)
                    if sent.children[num]:
                        dative = compound_extraction(sent, sent.children[num][0])
                else:
                    add_objects(sent, compound_extraction(sent, str(sent.children[i][j])), sent.dep[num], sent.lemma[i],
                                world)
                    dative = compound_extraction(sent, str(sent.children[i][j]))

                sent.finished_nodes[num] = 1

            elif num != -1 and sent.dep[num] == "agent":
                for nc in range(0, len(sent.text_chunk)):
                    if sent.dep_root_head[nc] == sent.text_token[num]:
                        add_objects(sent, compound_extraction(sent, str(sent.text_chunk[nc])), sent.dep[num],
                                    sent.lemma[i], world)
                        add_capability(sent, str(sent.lemma[i]), str(sent.text_chunk[nc]), world, current_index)
                        sent.finished_nodes[num] == 1
                        break

            # adverbial clause modifier
            # clausal complement
            # conjunction
            # preposition
            # agent
            # adverbial modifier
            elif num != -1 \
                    and sent.dep[num] in ["advcl","ccomp", "conj", "prep", "acl", "aux"]:
                details_extraction(sent, world, sent.dep[num], subject, is_negated)

            #compound
            elif num !=-1 and sent.dep[num] == "compound":
                if sent.pos[num] == "VERB":
                    details_extraction(sent, world, sent.dep[num], subject, is_negated, str(sent.children[i][j]))
                elif sent.pos[num] in ["NOUN", "PROPN"]:
                    subject = compound_extraction(sent, str(sent.children[i][j]))
                    add_objects(sent, str(subject), sent.dep[num], sent.lemma[i], world)
                    add_capability(sent, str(sent.lemma[i]), str(subject), world, current_index)
                    sent.finished_nodes[num] = 1

            else:
                print("WARNING: Dependecy ", sent.dep[num],  " not included in the list")
    else:
        print("ERROR: Cannot find current index or node ", current_node,  " has been recorded")


def compound_extraction(sent, subj):
    num = 0
    subj = str(subj).lower()
    temp = subj.split()

    if not temp:
        return ""

    for k in range(0, len(sent.text_token)):
        text_token = str(sent.text_token[k]).lower()
        if str(temp[-1]) == text_token:
            num = k
            break

    for c in sent.children[num]:
        c = str(c).lower()

        for k in range(0, len(sent.text_token)):
            text_token = str(sent.text_token[k]).lower()
            if text_token == c:
                num = k
                break

        if sent.dep[num] == "compound":
            sent.finished_nodes[num] = 1
            return str(sent.text_token[num]).lower() + " " + subj

    return subj


def char_conj_extractions(sent, subj):
    subj = str(subj).lower()
    list_of_conj = [subj]
    temp = str(subj).split()
    if not temp:
        return []

    subj = temp[-1]
    for k in range(0, len(sent.head_text)):
        head_text = str(sent.head_text[k]).lower()
        if head_text == subj and sent.dep[k] == "conj":
            subj = sent.text_token[k].lower()
            list_of_conj.append(compound_extraction(sent, subj))
            sent.finished_nodes[k] = 1
    return list_of_conj


def add_capability(sent, attr, subject, world, num):
    list_of_char = char_conj_extractions(sent, subject)
    list_of_capabilities = [attr.lower()]
    head = attr.lower()

    for i in range(0, len(sent.words)):
        if sent.dep[i] in ['conj'] and (sent.head_text[i] == str(head)):
            list_of_capabilities.append(sent.text_token[i].lower())
            head = sent.text_token[i].lower()

    if sent.dep[num-1] == "neg":
        negation = True
    else:
        negation = False
    for cap in list_of_capabilities:
        if cap not in ["is", "was", "are", "be", "am", "are", "were", "been", "being"]:

            if sent.dep[num] == "relcl":
                new_attribute = Attribute(DBO_Concept.RECEIVED_ACTION, cap, negation)
            else:
                new_attribute = Attribute(DBO_Concept.CAPABLE_OF, cap, negation)
            for c in list_of_char:
                c = str(c).lower()
                if c in world.characters:
                    new_attribute = check_duplicate_attribute(world.characters[c].attributes, new_attribute)
                    if new_attribute is not None:
                        world.characters[c].attributes.append(new_attribute)
                elif c in world.objects:
                    new_attribute = check_duplicate_attribute(world.objects[c].attributes, new_attribute)
                    if new_attribute is not None:
                        world.objects[c].attributes.append(new_attribute)


def add_objects(sent, child, dep, lemma, world, subject=""):
    list_of_char = char_conj_extractions(sent, child)
    for c in list_of_char:
        c = c.lower()
        if (c not in world.characters) and (c not in world.objects):
            if (DBO_Concept.get_concept_specified("character", DBO_Concept.CAPABLE_OF, lemma) or
                    DBO_Concept.get_concept_specified("person", DBO_Concept.CAPABLE_OF, lemma) is not None)\
                    and dep in ["nsubj", "agent", "compound"]:
                new_character = Character()
                new_character.name = c
                new_character.id = c
                new_character.attributes = []
                new_character.type = []
                new_character.inSetting = {'LOC': None, 'DATE': None, 'TIME': None}
                if sent.location:
                    new_character.inSetting = sent.location
                world.add_character(new_character)
                world.characters[new_character.id].timesMentioned = 1
                print("ADDED", new_character.name)

            else:
                new_object = Object()
                new_object.name = c
                new_object.id = c
                new_object.attributes = []
                new_object.type = []
                new_object.inSetting = {'LOC': None, 'DATE': None, 'TIME': None}
                if sent.location:
                    new_object.inSetting = sent.location
                world.add_object(new_object)
                world.objects[new_object.id].timesMentioned = 1
                print("ADDED", new_object.name)

        elif c in world.objects:
            if DBO_Concept.get_concept_specified("character", DBO_Concept.CAPABLE_OF, lemma) is not None \
                    and dep == "nsubj":
                new_character = Character.convert_from_object(world.objects[c])
                world.add_character(new_character)
                world.characters[new_character.id].timesMentioned += 1
            else:
                world.objects[c].timesMentioned += 1

        elif c in world.settings:
            if DBO_Concept.get_concept_specified("character", DBO_Concept.CAPABLE_OF, lemma) is not None \
                    and dep == "nsubj":
                new_character = Character.convert_from_setting(c)
                world.add_character(new_character)
                world.characters[new_character.id].timesMentioned += 1

        elif c in world.characters:
            world.characters[c].timesMentioned += 1

        # add amod and poss attribute
        char_index = find_text_index(sent, c)
        for ch in sent.children[char_index]:
            index = find_text_index(sent, ch)

            if sent.dep[index] in ["amod", "nummod"]:
                add_attributes(sent, sent.text_token[index], str(c), world)
                sent.finished_nodes[index] = 1

            elif sent.dep[index] in ["poss"]:
                if sent.text_token[index] in world.characters:
                    add_attributes(sent, c, sent.text_token[index], world, "", DBO_Concept.HAS)
                    char = world.characters[sent.text_token[index]]
                    char.timesMentioned += 1
                    sent.finished_nodes[index] = 1
                elif sent.text_token[index] in world.objects:
                    add_attributes(sent, c, sent.text_token[index], world, "", DBO_Concept.HAS)
                    obj = world.objects[sent.text_token[index]]
                    obj.timesMentioned += 1
                    sent.finished_nodes[index] = 1
                else:
                    add_objects(sent, compound_extraction(sent, str(sent.text_token[index])), sent.dep[index], lemma,
                                world)
                    add_attributes(sent, c, compound_extraction(sent, str(sent.text_token[index])), world, "",
                                   DBO_Concept.HAS)
    if dep in ["attr", "appos"]:
        add_attributes(sent, child, subject, world, "", DBO_Concept.IS_A)
    if dep in ["dobj", "relcl"]:
        if subject:
            add_attributes(sent, child, subject, world, "", DBO_Concept.HAS)


def check_duplicate_attribute(obj_attributes, attribute):
    for i in obj_attributes:
        if i.name == attribute.name:
            if i.isNegated is not attribute.isNegated:
                i.isNegated = attribute.isNegated
            return None
    return attribute


def add_attributes(sent, child, subject, world, negation="", relation=""):
    list_of_attributes = [child.lower()]
    list_of_char = char_conj_extractions(sent, subject)
    head = child.lower()

    if relation == "":
        relation = DBO_Concept.HAS_PROPERTY

    for i in range(0, len(sent.words)):
        if (sent.dep[i] == 'conj') and (sent.head_text[i] == str(head)):
            list_of_attributes.append(sent.text_token[i].lower())
            head = sent.text_token[i].lower()
            sent.finished_nodes[i] = 1

    print("LIST OF ATTR", list_of_attributes)

    for c in list_of_char:
        c = str(c).lower()
        if c in world.characters:
            for attr in list_of_attributes:
                attr = attr.lower()
                new_attribute = Attribute(relation, attr, negation)
                char = world.characters[c]
                print("ADD", attr, "TO", c)

                new_attribute = check_duplicate_attribute(char.attributes, new_attribute)
                if new_attribute is not None:
                    char.attributes.append(new_attribute)

                    if relation == DBO_Concept.IS_A:
                        print("RELATION", relation)
                        char.type.append(attr)

        elif c in world.objects:
            for attr in list_of_attributes:
                attr = attr.lower()
                new_attribute = Attribute(relation, attr, negation)
                print("ADD", attr, "TO", c)
                obj = world.objects[c]

                new_attribute = check_duplicate_attribute(obj.attributes, new_attribute)
                if new_attribute is not None:
                    obj.attributes.append(new_attribute)

                    if relation == DBO_Concept.IS_A:
                        print("RELATION", relation)
                        obj.type.append(attr)


def add_settings(sent, num, subject, negation, world):

    if sent.location:
        current_location = sent.location
    else:
        current_location = {'LOC': None, 'DATE': None, 'TIME': None}

    list_of_char = []
    is_setting = False
    if subject:
        list_of_char = char_conj_extractions(sent, subject)

    if not negation:
        ent_index = find_ent_index(sent, str(sent.text_token[num]))
        if ent_index is not None:
            label = sent.label[ent_index]
            ent_text = sent.text_ent[ent_index]
        else:
            label = ""
            ent_text = sent.text_token[num]
        ent_text = str(ent_text).lower()

        if ent_text not in world.settings:

            is_location = \
                label in ["LOC", "GPE"] or \
                DBO_Concept.get_concept_specified(str(sent.text_token[num]), DBO_Concept.IS_A, "place") or \
                DBO_Concept.get_concept_specified(str(sent.text_token[num]), DBO_Concept.IS_A, "location") or\
                DBO_Concept.get_concept_specified(str(sent.text_token[num]), DBO_Concept.IS_A, "site")

            is_date_time = \
                label in ["DATE", "TIME"] or \
                DBO_Concept.get_concept_specified(str(sent.text_token[num]), DBO_Concept.IS_A, "time period")

            if is_location or is_date_time:

                if is_location:
                    type_name = "LOC"
                else:
                    type_name = "TIME"

                is_setting = True
                new_setting = Setting()
                new_setting.id = ent_text
                new_setting.name = ent_text
                new_setting.type = type_name
                current_location[type_name] = ent_text
                world.add_setting(new_setting)

            sent.location = current_location

        else:
            is_setting = True

            if world.settings[str(sent.text_token[num])].type == "LOC":
                current_location["LOC"] = ent_text
            elif world.settings[str(sent.text_token[num])].type == "TIME":
                current_location["TIME"] = ent_text

        for c in list_of_char:
            if str(c) in world.characters and current_location:
                char = world.characters[str(c)]
                for key, value in current_location.items():
                    if value:
                        char.inSetting[key] = value
            elif str(c) in world.objects and current_location:
                obj = world.objects[str(c)]
                for key, value in current_location.items():
                    if value:
                        obj.inSetting[key] = value
    return is_setting


# ---------- rachel

CAT_STORY = 1
CAT_COMMAND = 2
CAT_ANSWER = 3
#ie_categorizing
def getCategory(sentence):
    #checks if entry has "orsen"
    if 'orsen' in sentence or 'orson' in sentence or 'Orson' in sentence or 'Orsen' in sentence or 'arson' in sentence:
        return CAT_COMMAND
    elif 'yes' in sentence or 'no' in sentence:
        return CAT_ANSWER
    else:
        return CAT_STORY


def coref_resolution(s, sent_curr, sent_bef, world, isFirst):
    prn =  []
    noun = []
    curr = sent_curr
    bef = sent_bef
    none = {0: None}
    coref = Coref()

    num_prn = 0
    num_conj = 0
    num_pron = 0

    for x in range(0, len(s.pos)):
        if s.tag[x] == 'PRP' or s.tag[x] == 'PRP$':
            num_prn += 1
        if s.pos[x] == 'CCONJ':
            num_conj += 1
        if s.lemma[x] =='-PRON-':
            num_pron += 1

    for x in range(0, num_prn):
        if num_conj >= 1:
            sent = coref.continuous_coref(utterances=sent_curr)
            num_conj -=1
        elif isFirst is False:
            sent = coref.one_shot_coref(utterances=sent_curr, context=sent_bef)

        mentions = coref.get_mentions()
        # print("mentions", mentions)

        rep = coref.get_most_representative()
        scores = coref.get_scores()
        propn_count = 0
        noun_count = 0

        for i in range(0, len(s.text_token)):
            #print(s.tag)
            if s.pos[i] == 'PROPN':
                propn_count += 1
            if s.tag[i] == 'NN':
                noun_count += 1

        #print("noun", noun_count)
        if propn_count < 1:
            if noun_count < 1 and isFirst is True:
                return sent_curr

        if len(rep) > 0 and len(scores)>0:
            count = 0

            add_apos = []
            for key, value in rep.items():
                if str(key).lower() == "his" or str(key).lower() == "hers" or str(key).lower() == "their" or str(key).lower() == "our" or str(key).lower() == "its":
                    add_apos.append(count)
                count +=1
            c = 0
            for key, value in rep.items():
               for i in range(0, len(add_apos)):
                   if add_apos[i] == c:
                       sent_curr = sent_curr.replace(str(key), str(value) + "'s")

            c += 1
            hold_key = " " + str(key) + " "
            hold_val = " " + str(value) + " "
            sent_curr = sent_curr.replace(hold_key, hold_val)

            if (str(value) not in world.characters) and (str(value) not in world.objects):
                if (str(key).lower() == "he") or (str(key).lower() == "his") or (str(key).lower() == "him"):
                    new_character = Character()
                    new_character.name = str(value)
                    new_character.id = str(value)
                    world.add_character(new_character)
                    world.characters[new_character.id].timesMentioned += 1
                elif (str(key).lower() == "she") or (str(key).lower() == "her") or (str(key).lower() == "hers"):
                    new_character = Character()
                    new_character.name = str(value)
                    new_character.id = str(value)
                    new_character.gender = "F"
                    world.add_character(new_character)
                    world.characters[new_character.id].timesMentioned += 1

        #elif len(scores.get('single_scores')) > 1:
            # extract scores
        #    single_mention = scores.get('single_scores')

        #    pair_mention = scores.get('pair_scores')

        #    single_sc_lib = []
        #    pair_sc_lib = []
        #    count = 0
        #    for i in range(0, len(single_mention)):
        #        if single_mention.get(i) == none.get(0):
        #          count += 1
        #        else:
        #          single_sc_lib.append(float(single_mention.get(i)))

            #count -=1
            # print("COUNT", count)
            #print("SINGLE_SC_LIB", single_sc_lib)
            #
            #print("INDEX min", single_sc_lib.index(min(single_sc_lib)))
            #ow_single_index = single_sc_lib.index(min(single_sc_lib))
            #low_single_index += count

            #print("found it low_single_index: ", low_single_index)
            #holder = {}

            #print(pair_mention.get(low_single_index))
            #holder = pair_mention.get(low_single_index)

            #print("holder", len(holder))
            ##for i in range(0, len(holder)):
            #    pair_sc_lib.append(holder.get(i))

            #print("PAIR!!!!!!!!!!!", pair_sc_lib)
            #high_pair_index = pair_sc_lib.index(max(pair_sc_lib))
            #print("found it high_pair_index: ", high_pair_index)

            #prn.append(mentions[low_single_index])
            #noun.append(mentions[high_pair_index])
            #print(noun, prn)
            #print("numPron", num_pron)


            #for i in range(0, len(prn)):
            #    for k in range(0, len(s.text_token)):
            #        #print("ASAIFHA", str(noun[i]), s.text_token[k])
            #        if s.text_token[k] in str(noun[i]):
            #            if s.pos[k] != 'NOUN' or s.pos[k] != 'PROPN':
            #                return sent_curr
            #    print("SENTENCE", sent_curr)
            #    sent_curr = sent_curr.replace(str(prn[i]), str(noun[i]))

        else:
            print("OWN CODE")
            print(s.text_token)
            isThis = ""
            changeThis = ""
            for i in range(0, len(s.text_token)):
                if s.dep[i] == 'nsubj' and (s.pos[i] == 'PROPN' or s.pos[i] == 'NOUN'):
                    #print(s.dep[i], "check prop or noun", s.pos[i])
                    isThis = s.text_token[i]
                    for j in range(0, len(s.text_token)):
                        if s.dep[j] == 'nsubj' and s.pos[j] == 'PRON' or s.tag[j] =='PRP$' or s.tag[j] == 'PRP':
                            #print(s.dep[j], "check pron", s.pos[j])
                            changeThis = s.text_token[j]

                elif s.pos[i] == 'NOUN' or s.pos[i] == 'PROPN':
                    isThis = s.text_token[i]
                    for j in range(0, len(s.text_token)):
                        if s.dep[j] == 'nsubj' and s.pos[j] == 'PRON' or s.tag[j] =='PRP$' or s.tag[j] == 'PRP':
                            #print(s.dep[j], "check pron", s.pos[j])
                            changeThis = s.text_token[j]

                if len(isThis) > 0 and len(changeThis) > 0:
                    if changeThis.lower() == 'her' or changeThis.lower() == 'his' or changeThis.lower() == 'our':
                        isThis = isThis + "'s"

                    split = sent_curr.split(" ")
                    for i in range(0, len(split)):
                        if split[i] == changeThis:
                            split[i] = isThis
                    sent_curr = " ".join(split)

    return sent_curr

def isAction(sentence):
    isAction = False
    be_forms = ["is", "are", "am", "were", "was", "feels", "looks"]
    for k in range(0, len(be_forms)):
        for i in range(0, len(sentence.text_token)):
            if be_forms[k] == sentence.text_token[i]:
                isAction = True

    return isAction

#ie_event_extract
def event_extraction(sentence, world, current_node):
    print("----- Entering EVENT EXTRACTION -----")
    event_subj = []
    event_subj_act = []
    event_dobj = []
    event_prep = []
    event_detail = []
    event_type = []
    event_attr = []
    event_pobj = []
    event_create = []
    #Getting the count of each annotation
    nsubj_c = 0
    comp_c = 0
    poss_c = 0
    acomp_c = 0
    agent_c = 0
    root_c = 0
    neg_act_c = 0
    pobj_c = 0
    dobj_c = 0
    neg_obj_c = 0
    attr_c = 0
    ccomp_c = 0
    advcl_c = 0
    relcl_c = 0
    dative_c = 0
    oprd_c = 0
    xcomp_c = 0
    advmod_c = 0
    npadvmod_c = 0
    prep_c = 0
    expl_c = 0

    for i in range(0, len(sentence.dep)):
        if sentence.dep[i] == 'nsubj' or sentence.dep[i] == 'nsubjpass':
            nsubj_c += 1
        elif sentence.dep[i] == 'compound':
            comp_c += 1
        elif sentence.dep[i] == 'poss':
            poss_c += 1
        elif sentence.dep[i] == 'acomp':
            acomp_c += 1
        elif sentence.dep[i] == 'agent':
            agent_c += 1

        if sentence.dep[i] == 'ROOT':
            root_c += 1
            if sentence.dep[i-1] == 'neg':
                neg_act_c += 1

        if sentence.dep[i] == 'pobj':
            pobj_c += 1
        elif sentence.dep[i] == 'dobj':
            dobj_c += 1
        elif sentence.dep[i] == 'attr':
            attr_c += 1
        elif sentence.dep[i] == 'ccomp':
            ccomp_c += 1
        elif sentence.dep[i] == 'advcl':
            advcl_c += 1
        elif sentence.dep[i] == 'relcl':
            relcl_c += 1
        elif sentence.dep[i] == 'dative':
            dative_c += 1
        elif sentence.dep[i] == 'oprd':
            oprd_c += 1
        elif sentence.dep[i] == 'xcomp':
            xcomp_c += 1
        elif sentence.dep[i] == 'advmod':
            advmod_c += 1
        elif sentence.dep[i] == 'npadvmod':
            npadvmod_c += 1
        elif sentence.dep[i] == 'prep':
            prep_c += 1
        elif sentence.dep[i] == 'pobj':
            pobj_c += 1
    #print("nsubj count: ", nsubj_c)
    #print("root count: ", root_c)
    #print("advmod count: ", advmod_c)
    #print("dobj count: ", dobj_c)
    isFound_char = False
    isFound_char_act = False
    isFound_obj = False
    isFound_obj_act = False
    isFound_mobj_act = False
    isFound = False

    if agent_c > 0:
        isPassive = True

    desc = ['being', 'be', 'been', 'is', 'are', 'was', 'were', 'am']
    plural = ['we', 'they', 'them', 'our', 'them', 'us', 'you']
    for i in range(0, len(sentence.dep)):
        #----START OF CHARACTER EXTRACTION----#

        if nsubj_c == 0:

            if sentence.dep[i] == 'expl':
                expl_c += 1
                print("EXPL", expl_c)
                event_create.append(sentence.text_token[i].lower())
                for y in range(0, len(sentence.dep)):
                    if sentence.dep[y] == 'attr':
                        event_subj.append(sentence.text_token[y])
                        hold_c = sentence.text_token[y]
                        attr_c -= 1

        elif sentence.dep[i] == 'nsubj' or sentence.dep[i] == 'nsubjpass' and nsubj_c > 0 and isFound_char is False:
            #print("CHECKING NSUB COUNT", nsubj_c)
            #print("this is the subject", sentence.text_token[i])
            if i > 0:
                #Compound Subj
                if sentence.dep[i-1] == 'compound' and comp_c > 0 and sentence.dep[i] == 'nsubj':
                    #print("Compound and not poss")
                    if sentence.text_token[i-1] != sentence.text_token[i]:
                        c_char = sentence.text_token[i-1] + " " + sentence.head_text[i-1]
                    else:
                        c_char = sentence.head_text[i-1]

                    event_subj.append(c_char)
                    if (i+1) < len(sentence.dep):
                        if sentence.dep[i+1] == 'cc' or sentence.dep[i+1] == 'punct':
                            for k in range(0, len(sentence.dep)):
                                if (i+k) < len(sentence.dep):
                                    if sentence.dep[i+k] == 'conj':
                                        event_subj[len(event_subj)-1] += ',' + sentence.text_token[i+k]
                                        if sentence.dep[i+k+1] != 'cc' or sentence.dep[i+k+1] != 'punct':
                                            k = len(sentence.dep)
                    print("Added Char: ", c_char)
                    comp_c -= 1
                    nsubj_c -= 1
                    if nsubj_c == 0:
                        isFound_char = True

                #Poss Subj
                elif poss_c > 0 and sentence.dep[i-2] == 'poss':
                    if sentence.dep[i-1] == 'case':
                        #print("poss and not compound")
                        p_char = sentence.text_token[i-2] + sentence.text_token[i-1] + " " + sentence.text_token[i]

                        event_subj.append(p_char)
                        print("Added Char: ", p_char)
                        poss_c -= 1
                        nsubj_c -= 1

                        if nsubj_c == 0:
                            isFound_char = True

                elif comp_c > 0 and poss_c > 0 and isFound_char is False:
                    print("compound and poss")
                    cp_char = sentence.text_token[i-3] + " " + sentence.text_token[i-2] + sentence.text_token[i-1] + " " + sentence.text_token[i]

                    event_subj.append(cp_char)
                    print("Added Char: ", cp_char)
                    poss_c -= 1
                    comp_c -= 1
                    nsubj_c -= 1
                    if nsubj_c == 0:
                        isFound_char = True

            if (i+1) < len(sentence.dep) and isFound_char is False:
                if sentence.dep[i+1] == 'cc' or sentence.dep[i+1] == 'punct':
                    #Multiple Subj
                    test_char = sentence.text_token[i]
                    isAdded = False

                    for k in range(0, len(sentence.dep)):
                        if (i+k) < len(sentence.dep):
                            if sentence.dep[i+k] == 'conj':
                                print("event_subj: ", len(event_subj), event_subj)
                                if isAdded is False:
                                    print("test", test_char)
                                    event_subj.append(test_char)
                                    isAdded = True
                                print("event_subj: ", len(event_subj), event_subj)
                                if sentence.head_text[i+k] == event_subj[len(event_subj)-1]:
                                    event_subj[len(event_subj)-1] += "," + sentence.text_token[i+k]
                                    print("event_subj: ", len(event_subj), event_subj)
                                    isFound_mchar = True

                                    nsubj_c -= 1
                                    if nsubj_c == 0:
                                        isFound_char = True
            if nsubj_c >0 and isFound_char is False:
                event_subj.append(sentence.text_token[i])
                print("Added Char: ", sentence.text_token[i])
                nsubj_c -= 1
                if nsubj_c == 0:
                    isFound_char = True

        #----END OF CHARACTER EXTRACTION -----#
        #----START OF CHARACTER ACTION EXTRACTION ----#
        if (i+1) < len(sentence.dep):
            if sentence.dep[i] == 'aux':
                isFound = False
                if sentence.dep[i+1] == 'ccomp' and ccomp_c > 0:
                    isFound = True
                    ccomp_c -= 1
                    event_subj_act.append(sentence.text_token[i] + " " + sentence.text_token[i+1])
                    print("Added Char Action: ", sentence.text_token[i] + " " + sentence.text_token[i+1])
                    head_hold = sentence.text_token[i+1]
                    if (i+2) < len(sentence.dep):
                        if sentence.dep[i + 2] == 'cc' or sentence.dep[i + 2] == 'punct':
                            for x in range(0, len(sentence.dep)):
                                if sentence.dep[x] == 'conj' and sentence.head_text[x] == head_hold:
                                    event_subj_act[len(event_subj_act) - 1] += "," + sentence.text_token[x]
                                    print("Added Char Action: ", sentence.text_token[x])
                if (i+2) < len(sentence.dep):
                    if sentence.dep[i+1] == 'neg':
                        isFound = True
                        event_subj_act.append(sentence.text_token[i] + " " + sentence.text_token[i+1] + " " + sentence.text_token[i+2])
                        print("Added Char Action: ", sentence.text_token[i] + " " + sentence.text_token[i+1] + " " + sentence.text_token[i+2])
                        head_hold = sentence.text_token[i+2]
                        if (i+3) < len(sentence.dep):
                            if sentence.dep[i+3] == 'cc' or sentence.dep[i+3] == 'punct':
                                for x in range(0, len(sentence.dep)):
                                    if sentence.dep[x] == 'conj' and sentence.head_text[x] == head_hold:
                                        event_subj_act[len(event_subj_act)-1] += "," + sentence.text_token[x]
                                        print("Added Char Action: ", sentence.text_token[x])

                if (i+2) < len(sentence.dep):
                    if sentence.dep[i+2] == 'cc' or sentence.dep[i+2] == 'punct':
                        isFound = True
                        event_subj_act.append(sentence.text_token[i] + " " + sentence.text_token[i+1])
                        print("Added Char Action: ",sentence.text_token[i] + " " + sentence.text_token[i+1])
                        head_hold = sentence.text_token[i+1]
                        for x in range(0, len(sentence.dep)):
                            if sentence.dep[x] == 'conj' and sentence.head_text[x] == head_hold:
                                event_subj_act[len(event_subj_act) - 1] += "," + sentence.text_token[x]
                                print("Added Char Action: ", sentence.text_token[i])
                    if sentence.pos[i+1] == 'VERB':
                        event_subj_act.append(sentence.text_token[i] + " " + sentence.text_token[i+1])
                        print("Added Char Action: ", sentence.text_token[i] + " " + sentence.text_token[i+1])
                        isFound = True
                        head_hold = sentence.text_token[i+1]
                        for x in range(0, len(sentence.dep)):
                            if sentence.dep[x] == 'conj' and sentence.head_text[x] == head_hold:
                                event_subj_act[len(event_subj_act) - 1] += "," + sentence.text_token[x]
                                print("Added Char Action: ", sentence.text_token[x])

            elif sentence.pos[i] == 'VERB' and sentence.dep[i] != 'advcl':
                isFound = False
                if sentence.dep[i] == 'punct':
                    event_subj_act.append(sentence.text_token[i])
                    print("Added Char Action: ", sentence.text_token[i])
                elif sentence.dep[i-1] == 'punct':
                    event_subj_act[len(event_subj_act)-1] += ' ' + sentence.text_token[i]
                    print("Added Char Action: ", sentence.text_token[i])
                elif sentence.dep[i] == 'ccomp':
                    event_subj_act.append(sentence.text_token[i])
                    print("Added Char Action: ", sentence.text_token[i])
                elif sentence.dep[i-1] != 'punct':
                    event_subj_act.append(sentence.text_token[i])
                    print("Added Char Action: ", sentence.text_token[i])
                head_hold = sentence.text_token[i]
                isFound = True
                if sentence.dep[i+1] == 'cc' or sentence.dep[i+1] == 'punct':
                    event_subj_act.append(sentence.sentence.text_token[i])
                    head_hold = sentence.text_token[i]
                    for x in range(0, len(sentence.dep)):
                        if sentence.dep[x] == 'conj' and sentence.head_text[x] == head_hold:
                            event_subj_act[len(event_subj_act) - 1] += "," + sentence.text_token[x]
                            print("Added Char Action: ", sentence.text_token[x])

            if isFound is True:
                if event_subj_act[len(event_subj_act)-1] in desc:
                    if expl_c > 0:
                        event_type.append(2)
                        print("Added a CREATION")
                    else:
                        event_type.append(1)
                        print("Added a DESCRIPTIVE")
                else:
                    event_type.append(0)
                    print("Added an EVENT")

                event_detail.append('-')
                event_pobj.append('-')
                event_prep.append('-')
                event_attr.append('-')
                event_dobj.append('-')
                isFound = False
            #if neg_act_c == 0 and (i+1) < len(sentence.dep):
            #    test_char_act = sentence.text_token[i]
            #    isAdded = False

            #    if sentence.dep[i+1] == 'cc' or sentence.dep[i+1] == 'punct' or (sentence.dep[i+1] == 'punct' and sentence.dep[i+2] == 'cc'):
            #        for k in range(0, len(sentence.dep)):
            #            if (i + k) < len(sentence.dep):
            #                if sentence.dep[i + k] == 'conj':
            #                    if isAdded is False:
            #                        event_subj_act.append(test_char_act)
            #                        if test_char_act in desc:
            #                            if expl_c == 1:
            #                                event_type.append(2)
            #                                event_dobj.append('-')
            #                                event_prep.append('-')
            #                                event_pobj.append('-')
            #                                event_attr.append('-')
            #                                event_detail.append('-')
            #                               expl_c -= 1
            #                            else:
            #                                event_type.append(1)
            #                                event_dobj.append('-')
            #                                event_prep.append('-')
            #                                event_pobj.append('-')
            ##                                event_attr.append('-')
             #                               event_detail.append('-')
            #                        else:
            #                            event_type.append(0)
            #                            event_dobj.append('-')
            #                            event_pobj.append('-')
            #                            event_prep.append('-')
            #                            event_attr.append('-')
            #                            event_detail.append('-')
            #                        print("Added Char Action: " + test_char_act)

            #                        isAdded = True

            #                    if sentence.head_text[i+k] == test_char_act:
            #                        test_char_act = sentence.text_token[i+k]
            #                        event_subj_act[len(event_subj_act)-1] += "," + sentence.text_token[i+k]

            #                        print("Added Char Action: " + sentence.text_token[i+k])

            #Neg Action
            #if neg_act_c > 0:
            #    if (i+2) < len(sentence.dep):
            #        if sentence.dep[i+1] == 'neg' and sentence.dep[i] == 'aux' and (sentence.dep[i+3] != 'cc' and sentence.dep[i+3] != 'punct'):
            #            if sentence.pos[i+2] == 'VERB':
            #                event_subj_act.append(sentence.text_token[i] + " not " + sentence.text_token[i+2])
            #                if sentence.text_token[i] in desc:
            #                    if expl_c == 1:
            #                        event_type.append(2)
            #                        event_dobj.append('-')
            #                        event_prep.append('-')
            #                        event_pobj.append('-')
            #                        event_attr.append('-')
            #                        event_detail.append('-')
            #                        expl_c -= 1
            #                    else:
            #                        event_type.append(1)
            #                        event_dobj.append('-')
            #                        event_attr.append('-')
            #                        event_prep.append('-')
            #                        event_pobj.append('-')
            #                        event_detail.append('-')
            #                else:
            #                    event_type.append(0)
            #                    event_attr.append('-')
            #                    event_dobj.append('-')
            #                    event_pobj.append('-')
            #                    event_prep.append('-')
            #                    event_detail.append('-')

            #                print("Added Char Action: " + sentence.text_token[i+2], " not " + sentence.text_token[i])

                #Multiple Action
            #    test_char_act = sentence.text_token[i]
            #    isAdded = False
            #    if (i+3) < len(sentence.dep):
            #        if sentence.dep[i+1] == 'neg' and sentence.dep[i] == 'aux':
            #            if sentence.dep[i+3] == 'cc' or sentence.dep[i+3] == 'punct':
            #                for k in range(0, len(sentence.dep)):
            #                    if (i+k) < len(sentence.dep):
            #                        if sentence.dep[i+k] == 'conj':
            #                            if isAdded is False:
            #                                event_subj_act.append(test_char_act)
            #                                if test_char_act in desc:
            #                                    if expl_c == 1:
            #                                        event_type.append(2)
            #                                        event_dobj.append('-')
            #                                        event_prep.append('-')
            #                                        event_pobj.append('-')
            #                                        event_attr.append('-')
            #                                        event_detail.append('-')
            #                                        expl_c -= 1
            #                                    else:
            #                                        event_type.append(1)
            #                                        event_dobj.append('-')
            #                                        event_prep.append('-')
            #                                        event_pobj.append('-')
            #                                        event_attr.append('-')
            #                                        event_detail.append('-')
            #                                else:
            #                                    event_type.append(0)
            #                                    event_dobj.append('-')
            #                                    event_pobj.append('-')
            #                                    event_attr.append('-')
            #                                    event_prep.append('-')
            #                                    event_detail.append('-')
            #                                print("@Added Char Action: ", test_char_act)
            #                                isAdded = True

            #                            if sentence.head_text[i+k] == test_char_act:
            #                                test_char_act = sentence.text_token[i+k]
            #                                event_subj_act[len(event_subj_act)-1] += "," + "not " + sentence.text_token[i + k]
            #                                print("@Added Char Action: ", event_subj_act[len(event_subj_act)-1])
            #                                neg_act_c -= 1


            #Preposition
            #if (i+3) < len(sentence.dep):
            #    if sentence.dep[i] == 'aux' and sentence.dep[i+2] == 'prep' and sentence.dep[i+3] == 'pcomp':
            #        event_subj_act.append(sentence.text_token[i] + " " + sentence.text_token[i+1])
            #        if sentence.text_token[i+1] in desc:
            #            if expl_c == 1:
            #                event_type.append(2)
            #                event_dobj.append('-')
            #                event_prep.append('-')
            #                event_pobj.append('-')
            #                event_attr.append('-')
            #                event_detail.append('-')
            #                expl_c -= 1
            #            else:
            #                event_type.append(1)
            #                event_dobj.append('-')
            #                event_prep.append('-')
            #                event_pobj.append('-')
            #                event_attr.append('-')
            #                event_detail.append('-')
            #        else:
            #            event_type.append(0)
            #            event_dobj.append('-')
            #            event_pobj.append('-')
            #            event_prep.append('-')
            #            event_attr.append('-')
            #            event_detail.append('-')

            #        head_hold = sentence.text_token[i] + " " + sentence.text_token[i+1]
            #        for z in range(0, len(event_subj_act)):
            #            if event_subj_act[z] == head_hold and event_prep[z] == '-':
            #                event_prep[z] = sentence.text_token[i+2]
            #                prep_c -= 1
            #                event_pobj[z] = sentence.text_token[i+3]
            #                pobj_c -= 1

            #        print("Added Char Action: ", head_hold)


            #    if sentence.dep[i] == 'aux' or sentence.dep[i] == 'auxpass':
            #        event_subj_act.append(sentence.text_token[i] + " " +sentence.head_text[i])
            #    else:
            #        event_subj_act.append(sentence.text_token[i])

             #   isFound_agent = False
            #    if sentence.text_token[i] in desc:
            #        if expl_c == 1:
            #            event_type.append(2)
            #            event_dobj.append('-')
            #            event_prep.append('-')
            #            event_pobj.append('-')
            #            event_attr.append('-')
            #            event_detail.append('-')
            #            expl_c -= 1
            #        else:
            #            event_type.append(1)
            #            if agent_c > 0:
            #                for x in range(0, len(sentence.dep)):
            #                    if sentence.dep[x] == 'agent':
            #                        event_prep.append(sentence.text_token[x])
            #                        event_dobj.append(sentence.text_token[x-1])
            #                        isFound_agent = True

            #            if isFound_agent is False:
            #                event_dobj.append('-')
            #                event_prep.append('-')

            #            event_attr.append('-')
            #            event_pobj.append('-')
            #            event_detail.append('-')
            #    else:
            #        event_type.append(0)
            #        event_dobj.append('-')
            #        event_prep.append('-')
            #        event_pobj.append('-')
            #        event_attr.append('-')
            #        event_detail.append('-')

            #    print("Added Char Action: ", sentence.text_token[i])
            #    isFound_char_act = True
            #    root_c -= 1

        #----END OF CHARACTER ACTION EXTRACTION----#

        #----START OF OBJECT EXTRACTION----#
        elif sentence.dep[i] == 'acomp' and acomp_c > 0:
            #print("found an acomp")
            head_hold = sentence.head_text[i]
            if (i+1) < len(sentence.dep):
                if sentence.dep[i+1] == 'cc' or sentence.dep[i + 1] == 'punct':
                    # Multiple Object
                    test_obj = sentence.text_token[i]
                    isAdded = False
                    if sentence.dep[i + 1] == 'cc' or sentence.dep[i + 1] == 'punct':
                        for k in range(0, len(sentence.dep)):
                            if (i + k) < len(sentence.dep):
                                if sentence.dep[i + k] == 'conj':
                                    if isAdded is False:
                                        if head_hold in event_dobj:
                                            for x in range(0, len(event_dobj)):
                                                if event_dobj[x] == head_hold and event_attr[x] == '-':
                                                    event_attr[x] = test_obj
                                                    isAdded = True
                                        elif head_hold in event_subj_act:
                                            for x in range(0, len(event_subj_act)):
                                                if event_subj_act[x] == head_hold and event_attr[x] == '-':
                                                    event_attr[x] = test_obj
                                                    isAdded = True

                                    if sentence.head_text[i + k] == test_obj or sentence.head_text[i + k] == ',':
                                        test_obj = sentence.text_token[i+k]
                                        event_attr[x] += ',' + test_obj

                                        isFound_obj = True
                                        acomp_c -= 1

            if acomp_c > 0:
                if sentence.dep[i-1] == 'neg':
                    if head_hold in event_dobj:
                        for x in range(0, len(event_dobj)):
                            if event_dobj[x] == head_hold and event_attr[x] == '-':
                                event_attr[x] = sentence.text_token[i-1] + " " + sentence.text_token[i]
                                acomp_c -=1
                    elif head_hold in event_subj_act:
                        for x in range(0, len(event_subj_act)):
                            if event_subj_act[x] == head_hold and event_attr[x] == '-':
                                event_attr[x] = sentence.text_token[i-1] + " " + sentence.text_token[i]
                                acomp_c -= 1
                else:
                    if head_hold in event_dobj:
                        for x in range(0, len(event_dobj)):
                            if event_dobj[x] == head_hold and event_attr[x] == '-':
                                event_attr[x] = sentence.text_token[i]
                                acomp_c -=1
                    elif head_hold in event_subj_act:
                        print(event_subj_act)
                        for x in range(0, len(event_subj_act)):
                            if event_subj_act[x] == head_hold and event_attr[x] == '-':
                                event_attr[x] = sentence.text_token[i]
                                acomp_c -= 1
                isFound_obj = True

        elif sentence.dep[i] == 'dobj' and dobj_c > 0 and isFound_obj is False:
            head_hold = sentence.head_text[i]
            saved_index = 0
            if (i+1) < len(sentence.dep):
                if sentence.dep[i + 1] == 'cc' or sentence.dep[i + 1] == 'punct':
                    # Multiple Object
                    test_obj = sentence.text_token[i]
                    isAdded = False
                    if sentence.dep[i + 1] == 'cc' or sentence.dep[i + 1] == 'punct':
                        for k in range(0, len(sentence.dep)):
                            if (i + k) < len(sentence.dep):
                                if sentence.dep[i + k] == 'conj':
                                    if isAdded is False:
                                        head_hold = sentence.head_text[i]

                                        for z in range(0, len(event_subj_act)):
                                            if head_hold == event_subj_act[z] and event_dobj[z] == '-':
                                                saved_index = z

                                        if event_dobj[saved_index] == '-':
                                            event_dobj[saved_index] = test_obj
                                        else:
                                            saved_index += 1
                                            event_dobj[saved_index] = test_obj


                                        isAdded = True
                                        dobj_c -= 1

                                    if sentence.head_text[i + k] == test_obj or sentence.head_text[i + k] == ',':
                                        test_obj = sentence.text_token[i + k]
                                        event_dobj[saved_index] += "," + test_obj

                                        isFound_obj = True


            if dobj_c > 0 and isFound_obj is False:
                head_hold = sentence.head_text[i]

                for z in range(0, len(event_subj_act)):
                    if head_hold == event_subj_act[z] and event_dobj[z] == '-':
                        saved_index = z
                if event_dobj[saved_index] == '-':
                    event_dobj[saved_index] = sentence.text_token[i]
                else:
                    saved_index += 1
                    event_dobj[saved_index] = sentence.text_token[i]

                dobj_c -= 1
                isFound_obj = True

        if sentence.dep[i] == 'attr' and attr_c > 0:
            head_hold = sentence.head_text[i]
            if sentence.dep[i-2] == 'neg' and sentence.dep[i-1] == 'det':
                for x in range(0, len(event_subj_act)):
                    if event_subj_act[x] == head_hold and event_attr[x] == '-':
                        event_attr[x] = "not " + sentence.text_token[i-1] + " " + sentence.text_token[i]
                        attr_c -= 1
                        isFound_obj = True
            elif sentence.dep[i-1] == 'compound':
                for x in range(0, len(event_subj_act)):
                    if event_subj_act[x] == head_hold and event_attr[x] == '-':
                        event_attr[x] = sentence.text_token[i-1] + " " + sentence.text_token[i]
                        attr_c -= 1
            elif (i+1) < len(sentence.dep):
                if sentence.dep[i + 1] == 'cc' or sentence.dep[i + 1] == 'punct':
                    # Multiple Object
                    test_obj = sentence.text_token[i]
                    isAdded = False
                    if sentence.dep[i + 1] == 'cc' or sentence.dep[i + 1] == 'punct':
                        for k in range(0, len(sentence.dep)):
                            if (i + k) < len(sentence.dep):
                                if sentence.dep[i + k] == 'conj':
                                    if isAdded is False:
                                        for x in range(0, len(event_subj_act)):
                                            if event_subj_act[x] == head_hold and event_attr[x] == '-':
                                                event_attr[x] = test_obj
                                                attr_c -= 1
                                        isAdded = True

                                    if sentence.head_text[i + k] == test_obj or sentence.head_text[i + k] == ',':
                                        event_attr[x] += "," + sentence.text_token[i + k]

                                        isFound_obj = True
                                        attr_c -= 1


            else:
                for x in range(0, len(event_subj_act)):
                    if event_subj_act[x] == head_hold and event_attr[x] == '-':
                        event_attr[x] = sentence.text_token[i]
                        x = len(event_subj_act)
                        attr_c -= 1

                attr_c -= 1
                isFound_obj = True


        elif sentence.dep[i] == 'xcomp' and xcomp_c > 0:
            head_hold = sentence.head_text[i]
            saved_index = 0
            isFound_xcomp = False
            for x in range(0, len(event_subj_act)):
                if head_hold in event_subj_act[x]:
                    if sentence.dep[i-2] == 'aux' and sentence.dep[i-1] == 'neg':
                        event_subj_act[x] += " " + sentence.text_token[i-1] + " not " + sentence.text_token[i]
                    elif sentence.dep[i-1] == 'neg':
                        event_subj_act[x] += " not " + sentence.text_token[i]
                    elif sentence.dep[i-1] == 'aux':
                        event_subj_act[x] += " " + sentence.text_token[i-1] + " " + sentence.text_token[i]
                    else:
                        event_subj_act[x] += " " + sentence.text_token[i]

                    test_xcomp = sentence.text_token[i]
                    for k in range(0, len(sentence.dep)):
                        if (i+2+k) < len(sentence.dep):
                            if sentence.dep[i+k] == 'cc' or sentence.dep[i+k] == 'punct' and test_xcomp == sentence.head_text[i+k]:

                                event_subj_act[x] += "," + sentence.text_token[i+2+k]
                                test_xcomp = sentence.text_token[i+2+k]

        if sentence.dep[i] == 'prep' and sentence.text_token[i-1] != '-' and prep_c > 0:
            head_hold = sentence.head_text[i]
            #print("found prep")
            if sentence.head_text[i] in event_subj_act:
                for z in range(0, len(event_subj_act)):
                    if head_hold == event_subj_act[z] and event_prep[z] == '-':
                        event_prep[z] = sentence.text_token[i]
                        prep_c -= 1
            elif sentence.head_text[i] in event_attr:
                for z in range(0, len(event_attr)):
                    if head_hold == event_attr[z] and event_prep[z] == '-':
                        event_prep[z] = sentence.text_token[i]
                        prep_c -= 1
            else:
                for x in range(0, len(event_subj_act)):
                    holder = event_subj_act[x]
                    if holder.find(head_hold) == -1:
                        print("")
                    else:
                        event_prep[x] = sentence.text_token[i]
                        prep_c -= 1

        if sentence.dep[i] == 'pobj':
            #print("found pobj")
            head_hold = sentence.head_text[i]
            saved_index = 0
            for z in range(0, len(event_prep)):
                print(head_hold, event_prep[z])
                if head_hold == event_prep[z] and event_pobj[z] == '-':
                    event_pobj[z] = sentence.text_token[i]
                    pobj_c -= 1
        #----END OF OBJECT EXTRACTION----#

        #----START OF OBJECT ACTION EXTRACTION----#
        elif sentence.dep[i] == 'npadvmod' and npadvmod_c > 0 and isFound_obj_act is False:
            head_hold = sentence.head_text[i]
            if (i + 1) < len(sentence.dep):
                if sentence.dep[i + 1] == 'cc' or sentence.dep[i + 1] == 'punct':
                    # Multiple Object
                    test_obj = sentence.text_token[i]
                    isAdded = False
                    if sentence.dep[i + 1] == 'cc' or sentence.dep[i + 1] == 'punct':
                        for k in range(0, len(sentence.dep)):
                            if (i + k) < len(sentence.dep):
                                if sentence.dep[i + k] == 'conj':
                                    if isAdded is False:
                                        for x in range(0, len(event_subj_act)):
                                            if event_subj_act[x] == head_hold and event_detail[x] == '-':
                                                event_detail[x] = test_obj
                                                isAdded = True

                                        isAdded = True

                                    if sentence.head_text[i + k] == test_obj or sentence.head_text[i + k] == ',':
                                        test_obj = sentence.text_token[i + k]

                                        event_detail[x] += "," + test_obj
                                        isFound_obj_act = True
                                        npadvmod_c -=1

            else:
                for x in range(0, len(event_subj_act)):
                    if event_subj_act[x] == head_hold and event_detail[x] == '-':
                        if sentence.dep[i-1] == 'amod':
                            event_detail[x] = sentence.text_token[i-1] + " " + sentence.text_token[i]
                        else:
                            event_detail[x] = sentence.text_token[i]

                    npadvmod_c -= 1
                print("Added Obj Act: ", sentence.text_token[i])
                isFound_obj_act = True

        elif sentence.dep[i] == 'advmod' and advmod_c > 0 and isFound_obj_act is False:
            head_hold = sentence.head_text[i]
            if (i + 1) < len(sentence.dep):
                if sentence.dep[i + 1] == 'cc' or sentence.dep[i + 1] == 'punct':
                    # Multiple Object
                    test_obj = sentence.text_token[i]
                    isAdded = False
                    if sentence.dep[i + 1] == 'cc' or sentence.dep[i + 1] == 'punct':
                        for k in range(0, len(sentence.dep)):
                            if (i + k) < len(sentence.dep):
                                if sentence.dep[i + k] == 'conj':
                                    if isAdded is False:
                                        for x in range(0, len(event_subj_act)):
                                            if event_subj_act[x] == head_hold and event_detail[x] == '-':
                                                event_detail[x] = test_obj
                                                isAdded = True

                                    if sentence.head_text[i + k] == test_obj or sentence.head_text[i + k] == ',':
                                        test_obj = sentence.text_token[i + k]

                                        event_detail[x] += "," + test_obj
                                        isFound_mobj_act = True
                                        isFound_obj_act = True

                        if isFound_mobj_act is True:
                            for l in range(1, len(event_detail)):
                                event_detail[0] += "," + event_detail.pop()
            if advmod_c > 0:
                for x in range(0, len(event_subj_act)):
                    if event_subj_act[x] == head_hold and event_detail[x] == '-':
                        if sentence.dep[i - 1] == 'amod':
                            event_detail[x] = sentence.text_token[i - 1] + " " + sentence.text_token[i]
                        else:
                            event_detail[x] = sentence.text_token[i]
                        advmod_c-=1
        #----END OF OBJECT ACTION EXTRACTION----#
        #----START OF SPECIAL CASES----#

        if sentence.dep[i] == 'appos':
            event_subj.insert(0, sentence.head_text[i])
            event_subj_act.insert(0, "is")
            event_type.insert(0,1)
            event_dobj.insert(0, '-')
            event_prep.insert(0, '-')
            event_pobj.insert(0, '-')
            event_detail.insert(0, '-')
            event_attr.insert(0, sentence.text_token[i])
        elif sentence.dep[i] == 'poss':
            if (i-1) > 0:
                if sentence.pos[i-1] != 'ADJ':
                    event_subj.insert(0, sentence.text_token[i])
                    if sentence.text_token[i] in plural:
                        event_subj_act.insert(0, "have")
                    else:
                        event_subj_act.insert(0, "has")

                    event_dobj.insert(0, sentence.head_text[i])
                    event_type.insert(0, 0)
                    event_prep.insert(0, '-')
                    event_pobj.insert(0, '-')
                    event_detail.insert(0, '-')
                    event_attr.insert(0, '-')
            else:
                event_subj.insert(0, sentence.text_token[i])
                if sentence.text_token[i] in plural:
                    event_subj_act.insert(0, "have")
                else:
                    event_subj_act.insert(0, "has")

                event_dobj.insert(0, sentence.head_text[i])
                event_type.insert(0, 0)
                event_detail.insert(0, '-')
                event_prep.insert(0, '-')
                event_pobj.insert(0, '-')
                event_attr.insert(0, '-')

        elif sentence.dep[i] == 'relcl' and relcl_c > 0:
            event_subj_act.append(sentence.text_token[i])
            if sentence.text_token[i] in desc:
                event_type.append(1)
                event_prep.append('-')
                event_pobj.append('-')
                event_detail.append('-')
                event_attr.append('-')
            else:
                event_type.append(0)
                event_prep.append('-')
                event_pobj.append('-')
                event_attr.append('-')
                event_detail.append('-')

            event_dobj.append(sentence.head_text[i])

        elif sentence.dep[i] == 'dative' and dative_c > 0:
            hold = " "
            char_hold = " "
            isFound_obj_dative = False
            for x in range(0, len(sentence.dep_root)):
                print("x: ", x)
                if sentence.dep_root[x] == 'dative':
                    event_subj.append(sentence.text_chunk[x])
                    char_hold = sentence.text_chunk[x]
                    print("Added Char: ", sentence.text_chunk[x])
                    hold = sentence.dep_root_head[x]

                if sentence.dep_root_head[x] == char_hold and sentence.dep_root[x] == 'conj':
                    print("Added Char: ", sentence.text_chunk[x])
                    char_hold = sentence.text_chunk[x]
                    event_subj[len(event_subj) - 1] += "," + sentence.text_chunk[x]

                if sentence.dep_root_head[x] == hold and sentence.dep_root[x] != 'dative' and isFound_obj_dative is False:
                    event_subj_act.append("has")
                    event_dobj.append(sentence.text_chunk[x])
                    event_type.append(0)
                    event_detail.append('-')
                    event_prep.append('-')
                    event_pobj.append('-')
                    event_attr.append('-')
                    hold = sentence.text_chunk[x]
                    if (x+1) < len(sentence.dep_root):
                        if sentence.dep_root[x+1] == 'conj':
                            event_dobj[len(event_dobj)-1] += "," + sentence.text_chunk[x+1]
                            print("Added Obj: ", event_dobj[len(event_dobj)-1])

                    isFound_obj_dative = True
                dative_c -= 1
        elif sentence.dep[i] == 'amod':
            isadv = False

            if (i+1) < len(sentence.dep):
                if sentence.dep[i+1] == 'npadvmod' or sentence.dep[i+1] == 'advmod':
                    print("don't add anymore")
                    isadv = True

            if isadv is False:
                isFound_char_amod = False
                test = ""
                index = len(event_subj)-1
                event_type.insert(index, 1)
                event_dobj.insert(index, '-')
                event_prep.insert(index, '-')
                event_pobj.insert(index, '-')
                event_detail.insert(index, '-')
                if (i+2) < len(sentence.dep):
                    if sentence.dep[i+2] == 'cc':
                        if (i+3) < len(sentence.dep):
                            if sentence.dep[i+3] == 'neg':
                                if (i+4) < len(sentence.dep):
                                    if sentence.dep[i+4] == 'amod':
                                        print("not connected")
                            elif sentence.dep[i+3] == 'amod':
                                print("not connected")
                            elif sentence.dep[i+3] == 'conj':
                                #print("I added it here")
                                event_subj.insert(index, sentence.head_text[i] + "," + sentence.text_token[i+3])
                                test = sentence.head_text[i] + "," + sentence.text_token[i+3]
                                isFound_char_amod = True

                if isFound_char_amod is False:
                    event_subj.insert(index, sentence.head_text[i])
                    test = sentence.head_text[i]

                if test in plural:
                    event_subj_act.insert(index, 'are')
                elif ',' in test:
                    event_subj_act.insert(index, 'are')
                else:
                    event_attr.insert(index, sentence.text_token[i])

                if (i+1) < len(sentence.dep) and (i+2) < len(sentence.dep):
                    if sentence.dep[i+1] == 'cc' or sentence.dep[i+1] == 'punct' and sentence.dep[i+2] == 'conj':
                        test_attr = sentence.text_token[i+2]
                        for x in range(1, len(sentence.dep)):
                            if (x+i+1) < len(sentence.dep):
                                if sentence.dep[x+i+1] == 'cc' or sentence.dep[i+1+x] == 'punct' and sentence.head_text[i+2+x] == test_attr:
                                    test_attr = sentence.text_token[i+x+2]
                                    event_attr[index] += ',' + sentence.text_token[i+x+2]

        elif sentence.dep[i] == 'advcl':
            if sentence.dep[i-1] != 'nsubj':
                print("not added anymore")
            else:
                event_type.append(0)
                event_subj_act.append(sentence.text_token[i])
                event_dobj.append('-')
                event_pobj.append('-')
                event_prep.append('-')
                event_attr.append('-')
                event_detail.append('-')
        elif sentence.dep[i] == 'oprd':
            head_hold = sentence.head_text[i]
            for z in range(0, len(event_subj_act)):
                if head_hold == event_subj_act[z] and event_detail[z] == '-':
                    event_detail[z] = sentence.text_token[i]
                    z = len(event_subj_act)

        #----END OF SPECIAL CASES----#



    #for checking
    for i in range(0, len(event_subj_act)):
        print("----Event Frame:----")
        print("Event Type: ", event_type)
        print("Subject: ", event_subj)
        print("Action: ", event_subj_act)
        print("Direct Object: ", event_dobj)
        print("Preposition: ", event_prep)
        print("Object of Preposition: ", event_pobj)
        print("Attribute: ", event_attr)
        print("Detail: ", event_detail)
        print("-------------------")

    for x in range(0, len(event_type)):
        add_event(event_type, event_subj, event_subj_act, event_prep, event_pobj, event_detail, event_dobj, event_attr,
                  event_create, world)


#Add event to the world
def add_event(type, subj, subj_act, prep, pobj, detail, dobj, attr, create, world):
    list_char = world.characters
    subj_hold = list()
    text_hold = list()
    dobj_hold = list()
    attr_hold = list()
    crt_hold = list()
    print("list_char: ", list_char)
    list_obj = world.objects
    print("list_obj: ", list_obj)
    for x in range(0, len(type)):
        if subj:
            hold = subj.pop(0)
            if ',' in hold:
                subj_hold = hold.split(',')
            else:
                subj_hold.append(hold)
            print(subj_hold)
            for i in range(0, len(subj_hold)):
                if subj_hold[i].lower().find("'s") != -1:
                    text_hold = subj_hold[i].lower().split(" ")
                    if list_obj[text_hold[1].lower()] is not None:
                        if type[x] == 0:
                            new_eventframe = EventFrame(len(world.event_chain), FRAME_EVENT)
                            new_eventframe.subject.append(list_obj[text_hold[1].lower()])
                        elif type[x] == 1:
                            new_eventframe = EventFrame(len(world.event_chain), FRAME_DESCRIPTIVE)

                            new_eventframe.subject.append(list_obj[text_hold[1].lower()])
                        elif type[x] == 2:
                            new_eventframe = EventFrame(len(world.event_chain), FRAME_CREATION)

                            new_eventframe.subject.append(list_obj[text_hold[1].lower()])

                        isFound = True
                    elif list_char[subj_hold[i].lower()] is not None:
                        if type[x] == 0:
                            new_eventframe = EventFrame(len(world.event_chain), FRAME_EVENT)

                            new_eventframe.subject.append(text_hold[1].lower())
                        elif type[x] == 1:
                            new_eventframe = EventFrame(len(world.event_chain), FRAME_DESCRIPTIVE)
                            new_eventframe.subject.append(text_hold[1].lower())
                        elif type[x] == 2:
                            new_eventframe = EventFrame(len(world.event_chain), FRAME_CREATION)
                            new_eventframe.subject.append(text_hold[1].lower())
                        isFound = True
                    else:
                        isFound = False
                elif subj_hold[i].lower() in list_obj:
                    if type[x] == 0:
                        new_eventframe = EventFrame(len(world.event_chain),FRAME_EVENT)
                        new_eventframe.subject.append(subj_hold[i].lower())
                    elif type[x] == 1:
                        new_eventframe = EventFrame(len(world.event_chain), FRAME_DESCRIPTIVE)

                        new_eventframe.subject.append(subj_hold[i].lower())
                    elif type[x] == 2:
                        new_eventframe = EventFrame(len(world.event_chain), FRAME_CREATION)

                        new_eventframe.subject.append(subj_hold[i].lower())
                    isFound = True
                elif subj_hold[i].lower() in list_char:
                    if type[x] == 0:
                        new_eventframe = EventFrame(len(world.event_chain),FRAME_EVENT)
                        new_eventframe.subject.append(subj_hold[i].lower())
                    elif type[x] == 1:
                        new_eventframe = EventFrame(len(world.event_chain), FRAME_DESCRIPTIVE)
                        new_eventframe.subject.append(subj_hold[i].lower())
                    elif type[x] == 2:
                        new_eventframe = EventFrame(len(world.event_chain), FRAME_CREATION)
                        new_eventframe.subject.append(subj_hold[i].lower())
                    isFound = True
                else:
                    isFound = False

                if isFound is True:
                    if new_eventframe.event_type is FRAME_EVENT:
                        new_eventframe.action = subj_act[x]
                        if prep[x] != '-':
                            new_eventframe.preposition = prep[x]
                        if pobj[x] != '-':
                            new_eventframe.obj_of_preposition = pobj[x]
                        if dobj[x] != '-':
                            hold_o = dobj[x]
                            if ',' in hold_o:
                                dobj_hold = hold_o.split(',')
                            else:
                                dobj_hold.append(hold_o)

                            for y in range(0, len(dobj_hold)):
                                if list_obj[dobj_hold[y].lower()] is not None:
                                    new_eventframe.direct_object.append(dobj_hold[y].lower())
                        if detail[x] != '-':
                            new_eventframe.adverb = detail[x]
                    elif new_eventframe.event_type is FRAME_DESCRIPTIVE:
                        if attr:
                            hold_a = attr[x]
                            if ',' in hold_a:
                                attr_hold = hold_a.split(',')
                            else:
                                attr_hold.append(hold_a)

                            for y in range(0, len(attr_hold)):
                                if attr_hold[y] != '-':
                                    new_eventframe.attributes.append(attr_hold[y].lower())

                    elif new_eventframe.event_type is FRAME_CREATION:
                        if attr:
                            hold_a = attr[x]
                            if ',' in hold_a:
                                attr_hold = hold_a.split(',')
                            else:
                                attr_hold.append(hold_a)

                            for y in range(0, len(attr_hold)):
                                if attr_hold[y] != '-':
                                    new_eventframe.attributes.append(attr_hold[y].lower())


                    world.add_eventframe(new_eventframe)

    print(world.event_chain)