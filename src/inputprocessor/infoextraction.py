from src.db.concepts import DBO_Concept
from src.objects.eventchain.EventFrame import EventFrame
from src.objects.nlp.Sentence import Sentence
from src.objects.storyworld.Attribute import Attribute
from src.objects.storyworld.Character import Character
from src.objects.storyworld.Object import Object
from src.objects.storyworld.Setting import Setting
from neuralcoref import Coref
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
        print("---POS----");
        print(token.text, token.head.text, token.lemma_, token.pos_, token.tag_, token.dep_)
        new_sentence.text_token.append(token.text)
        new_sentence.head_text.append(token.head.text)
        new_sentence.lemma.append(token.lemma_)
        new_sentence.pos.append(token.pos_)
        new_sentence.tag.append(token.tag_)
        new_sentence.dep.append(token.dep_)

        new_sentence.finished_nodes.append(0)
        for child in token.children:
            # print("child", child)
            new_sentence.children[len(new_sentence.children)-1].append(child)

    for ent in sentence.ents:
<<<<<<< HEAD
         print("---NER---")
         print(ent.text, ent.start_char, ent.end_char, ent.label_)
=======
         #print("---NER---")
         #print(ent.text, ent.start_char, ent.end_char, ent.label_)
>>>>>>> 33834a025b55fac192056f9d173f35ea3ff5f26f
         new_sentence.text_ent.append(ent.text)
         new_sentence.label.append(ent.label_)

    for chunk in sentence.noun_chunks:
<<<<<<< HEAD
        print("---NC---")
        print(chunk.text, chunk.root.text, chunk.root.dep_, chunk.root.head.text)
=======
        #print("---NC---")
        #print(chunk.text, chunk.root.text, chunk.root.dep_, chunk.root.head.text)
>>>>>>> 33834a025b55fac192056f9d173f35ea3ff5f26f

        new_sentence.text_chunk.append(chunk.text)
        new_sentence.dep_root.append(chunk.root.dep_)
        new_sentence.dep_root_head.append(chunk.root.head.text)

    return new_sentence


def find_text_index(sent, child):
    num = 0
    child = str(child).split()
    for k in range(0, len(sent.text_token)):
        if (str(child[-1]) == str(sent.text_token[k])) and (sent.finished_nodes[k] == 0):
            num = k
            break
    return num


def find_ent_index(sent, ent):
    for k in range(0, len(sent.text_ent)):
        if ent in str(sent.text_ent[k]):
            return str(sent.label[k])
    return None


def details_extraction(sent, world, current_node, subj="", loc="", neg=""):
    num = -1
    subject = subj
    location = loc
    current_index = -1
    dative = ""
    direct_object = ""
    for i in range(0, len(sent.dep)):
        if (sent.dep[i] == current_node) and (sent.finished_nodes[i] == 0):
            current_index = i
            print("HEREEE1", current_node, current_index)
            sent.finished_nodes[i] = 1
            break

    for i in sent.children[current_index]:
        print("HEREEEE2", i)

    if neg =="":
        is_negated = False
    else:
        is_negated = neg

    if current_index != -1:
        i = current_index
        for j in range(0, len(sent.children[i])):
            num = find_text_index(sent, str(sent.children[i][j]))
            print("-----------------", current_node, str(sent.children[i][j]), num)
            if num != -1 and sent.finished_nodes[num] == 0 and\
                    sent.dep[num] in ["nsubj", "acomp", "attr", "nsubjpass", "dobj", "xcomp", "appos", "relcl"]:

                # nominal subject
                if sent.dep[num] == "nsubj":
                    print("IN")
                    subject = compound_extraction(sent, str(sent.children[i][j]))
                    print("OUT")
                    add_objects(sent, str(subject), sent.dep[num], sent.lemma[i], world)
                    add_capability(sent, str(sent.lemma[i]), str(subject), world, current_index)

                # nominal subject (passive) or direct object
                elif sent.dep[num] == "nsubjpass" or sent.dep[num] == "dobj":
                    if not subject:
                        subject = compound_extraction(sent, str(sent.children[i][j]))

                    if dative and sent.dep[num] == "dobj":
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
                    location = add_settings(sent, num, subject, is_negated, world, location)
                    if location == "":
                        add_objects(sent, compound_extraction(sent, str(sent.children[i][j])), sent.dep[num],
                                    sent.lemma[i], world, subject)

                    is_negated = False

                # appositional modifier
                elif sent.dep[num] == "appos":
                    location = add_settings(sent, num, subject, is_negated, world, location)
                    if location == "":
                        add_objects(sent, compound_extraction(sent, str(sent.children[i][j])), sent.dep[num],
                                    sent.lemma[i], world, compound_extraction(sent, str(sent.head_text[num])))

                    is_negated = False

                # open clausal compliment
                elif sent.dep[num] == "xcomp":
                    add_capability(sent, str(sent.lemma[num]), str(subject), world, num)
                    is_negated = False

                # relative clause modifier
                elif sent.dep[num] == "relcl":
                    add_capability(sent, str(sent.lemma[num]), str(sent.head_text[num]), world, num)

                if sent.children[num] is not None:
                    for c in sent.children[num]:
                        dep_index = find_text_index(sent, str(c))
                        if sent.finished_nodes[dep_index] == 0:
                            details_extraction(sent, world, sent.dep[num], subject, location, is_negated)

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

            # noun phrase as adverbial modifier
            elif num != -1 and  sent.dep[num] == "npadvmod":
                print("LOCATION", location)
                location = add_settings(sent, num, subject, is_negated, world, location)
                sent.finished_nodes[num] = 1

            # object of preposition
            elif num != -1 and  sent.dep[num] == "pobj":
                location = add_settings(sent, num, subject, is_negated, world, location)
                if location == "":
                    print("WAHHH", current_node)
                    add_objects(sent, compound_extraction(sent, str(sent.children[i][j])), sent.dep[num], sent.lemma[i]
                                , world)
                details_extraction(sent, world, sent.dep[num], subject, location, is_negated)
                sent.finished_nodes[num] = 1

            # dative - the noun to which something is given
            elif num != -1 and sent.dep[num] == "dative":
                if str(sent.text_token[num]) == "to":
                    details_extraction(sent, world, sent.dep[num], subject, location, is_negated)
                    dative = sent.children[num]
                else:
                    add_objects(sent, compound_extraction(sent, str(sent.children[i][j])), sent.dep[num], sent.lemma[i],
                                world)
                    dative = sent.text_token[num]

                sent.finished_nodes[num] = 1

            # adverbial clause modifier
            # clausal complement
            # conjunction
            # preposition
            # agent
            # adverbial modifier
            elif num != -1 \
                    and sent.dep[num] in ["advcl", "ccomp", "conj", "prep", "agent", "advmod", "pcomp"]:
                print("HEREEEE", sent.dep[num])
                details_extraction(sent, world, sent.dep[num], subject, location, is_negated)

            else:
                print("WARNING: Dependecy ", sent.dep[num],  " not included in the list")
    else:
        print("ERROR: Cannot find current index or node ", current_node,  " has been recorded")


def compound_extraction(sent, subj):
    num = 0
    temp = str(subj).split()

    for k in range(0, len(sent.text_token)):
        if str(temp[-1]) == str(sent.text_token[k]):
            num = k
            break

    for c in sent.children[num]:
        for k in range(0, len(sent.text_token)):
            if str(sent.text_token[k]) == str(c):
                num = k
                break

        if sent.dep[num] == "compound":
            sent.finished_nodes[num] == 1
            return sent.text_token[num] + " " + subj

    return subj


def char_conj_extractions(sent, subj):
    list_of_conj = [subj]
    subj = str(subj).split()
    subj = subj[-1]
    for k in range(0, len(sent.head_text)):
        if str(sent.head_text[k]) == str(subj) and sent.dep[k] == "conj":
            subj = str(sent.text_token[k])
            list_of_conj.append(compound_extraction(sent, subj))
            sent.finished_nodes[k] == 1
    return list_of_conj


def add_capability(sent, attr, subject, world, num):
    list_of_char = char_conj_extractions(sent, subject)

    if sent.dep[num-1] == "neg":
        negation = True
    else:
        negation = False

    if attr not in ["is", "was", "are", "be", "am", "are", "were", "been", "being"]:
        new_attribute = Attribute(DBO_Concept.CAPABLE_OF, attr, negation)

        for c in list_of_char:
            if str(c) in world.characters:
                    world.characters[c].attributes.append(new_attribute)
            else:
                    world.objects[c].attributes.append(new_attribute)


def add_objects(sent, child, dep, lemma, world, subject=""):
    list_of_char = char_conj_extractions(sent, child)
    for c in list_of_char:
        if (c not in world.characters) and (c not in world.objects):
            if (DBO_Concept.get_concept_specified("character", DBO_Concept.CAPABLE_OF, lemma) is not None) \
                    and dep == "nsubj":
                new_character = Character()
                new_character.name = c
                new_character.id = c
                new_character.attributes = []
                world.add_character(new_character)
                world.characters[new_character.id].timesMentioned = 1
                print("ADDED", new_character.name)

            else:
                new_object = Object()
                new_object.name = c
                new_object.id = c
                new_object.attributes = []
                world.add_object(new_object)
                world.objects[new_object.id].timesMentioned = 1
                print("ADDED", new_object.name)

        elif c in world.objects:
            if DBO_Concept.get_concept_specified("character", DBO_Concept.CAPABLE_OF, lemma) is not None \
                    and dep == "nsubj":
                new_character = Character.convert_from_object(c)
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
                sent.finished_nodes[index] == 1

            elif sent.dep[index] in ["poss"]:
                if sent.text_token[index] in world.characters or sent.text_token[index] in world.objects:
                    add_attributes(sent, c, sent.text_token[index], world, "", DBO_Concept.HAS)
                    sent.finished_nodes[index] == 1
                else:
                    add_objects(sent, compound_extraction(sent, str(sent.text_token[index])), sent.dep[index], lemma,
                                world)
                    add_attributes(sent, c, compound_extraction(sent, str(sent.text_token[index])), world, "",
                                   DBO_Concept.HAS)
    print("CHILD---------------------------", child, subject)
    if dep in ["attr", "appos"]:
        add_attributes(sent, child, subject, world, "", DBO_Concept.IS_A)
    if dep in ["dobj", "relcl"]:
        if subject:
            add_attributes(sent, child, subject, world, "", DBO_Concept.HAS)

def add_attributes(sent, child, subject, world, negation="", relation=""):
    list_of_attributes = [child]
    list_of_char = char_conj_extractions(sent, subject)
    head = child

    if relation == "":
        relation = DBO_Concept.HAS_PROPERTY

    for i in range(0, len(sent.words)):
        if (sent.dep[i] == 'conj') and (sent.head_text[i] == str(head)):
            list_of_attributes.append(sent.text_token[i])
            head = sent.text_token[i]
    print("LLLLLLLLLLLLLL", list_of_attributes)
    for c in list_of_char:
        if c in world.characters:
            for attr in list_of_attributes:
                new_attribute = Attribute(relation, attr, negation)
                char = world.characters[c]
                print("ADD", attr, "TO", c)
                char.attributes.append(new_attribute)

        elif c in world.objects:
            for attr in list_of_attributes:
                new_attribute = Attribute(relation, attr, negation)
                print("ADD", attr, "TO", c)
                obj = world.objects[c]
                obj.attributes.append(new_attribute)


def add_settings(sent, num, subject, negation, world, location):
    current_location = location
    print("subject", subject)
    list_of_char = char_conj_extractions(sent, subject)
    print("CHARACTERS ------ SETTINGS", list_of_char, subject, location)
    if not negation:
        if str(sent.text_token[num]) not in world.settings:
            label = find_ent_index(sent, str(sent.text_token[num]))
            new_setting = Setting()
            new_setting.type = label
            if label in ["LOC", "GPE"]:

                if current_location is "":
                    current_location = sent.text_token[num]
                    new_setting.id = current_location
                    new_setting.name = current_location

                else:
                    prev_setting = world.settings(current_location)
                    print("PREV", prev_setting)
                    if prev_setting.type in ["DATE", "TIME"]:
                        current_location = sent.text_token[num]
                        new_setting.id = current_location
                        new_setting.name = current_location
                        new_setting.time = prev_setting.time
                        world.settings.pop(prev_setting.id)
                    else:
                        current_location = sent.text_token[num]
                        new_setting.id = current_location
                        new_setting.name = current_location
                print("CURR", current_location)
                world.add_setting(new_setting)

            elif label in ["DATE", "TIME"]:

                if current_location is "":
                    current_location = sent.text_token[num]
                    new_setting.id = current_location
                    new_setting.name = current_location
                    new_setting.type = label
                    new_setting.time = []
                    new_setting.time.append(str(sent.text_token[num]))
                    world.add_setting(new_setting)
                else:
                    setting = world.settings[current_location]
                    setting.time.append(str(sent.text_token[num]))

            elif DBO_Concept.get_concept_specified(str(sent.text_token[num]), DBO_Concept.IS_A, "location"):
                current_location = sent.text_token[num]
                new_setting.id = current_location
                new_setting.name = current_location
                new_setting.type = "LOC"
                world.add_setting(new_setting)

            for c in list_of_char:
                if str(c) in world.characters and current_location:
                    char = world.characters[str(c)]
                    char.inSetting = current_location
                    print("ch", char.inSetting)
                elif str(c) in world.objects and current_location:
                    print("OKAY ADDED")
                    obj = world.objects[str(c)]
                    print(obj.name, current_location)
                    obj.inSetting = current_location

    return current_location

# ---------- rachel

CAT_STORY = 1
CAT_COMMAND = 2
CAT_ANSWER = 3
#ie_categorizing
def getCategory(sentence):
    #checks if entry has "orsen"
    if 'orsen' in sentence or 'orson' in sentence:
        return CAT_COMMAND
    elif 'yes' in sentence or 'no' in sentence:
        return CAT_ANSWER
    else:
        return CAT_STORY

# #ie_setting_detail_extraction
# def setting_attribute_extraction(sentence, world):
#     setting_name = []
#     setting_time = []
#     setting_type = []
#     setting_char = []
#
#     isAdded = False
#
#     num_char = 0
#     num_loc = 0
#
#     isPROPN = False
#     isLocation = False
#     isDate = False
#     isChar = False
#
#     #Check in NER
#     for x in range(0, len(sentence.text_ent)):
#         text = sentence.text_ent[x]
#         label = sentence.label[x]
#
#         #find character
#         list_char = world.characters
#         if label == 'PERSON' or label == "ORG":
#             for k in list_char:
#                 print(sentence.text_chunk[x])
#                 print(list_char[k])
#                 if list_char[k].name == sentence.text_chunk[x]:
#                     char = list_char[k].name
#                     setting_char.append(char)
#                     isChar = True
#                     num_char += 1
#
#         #Check if GPE, Location, Date or Time
#         if label == 'GPE' or label == 'LOCATION':
#             setting_name.append(text)
#             isAdded = True
#             setting_type.append("LOCATION")
#             isLocation = True
#             isPROPN = True
#
#         if label == 'DATE':
#             if isLocation is False:
#                 setting_name.append(text)
#                 isAdded = True
#                 setting_type.append("DATE")
#                 isDate = True
#             elif isLocation is True:
#                 setting_time.append(text)
#                 isAdded = True
#                 setting_type.append("DATE")
#                 isDate = True
#
#         if label == 'TIME':
#             if isDate is False:
#                 if isLocation is True:
#                     setting_time.append(text)
#                     isAdded = True
#                     setting_type.append("TIME")
#                 elif isLocation is False:
#                     setting_name.append(text)
#                     isAdded = True
#                     setting_type.append("TIME")
#             elif isDate is True:
#                 if isLocation is True:
#                     hold = setting_time[len(setting_time)-1]
#                     setting_time[len(setting_time)-1] = hold + "," + text
#                     setting_type.append("TIME")
#                     isAdded = True
#                 elif isLocation is False:
#                     setting_time.append(text)
#                     setting_type.append("TIME")
#                     isAdded = True
#
#         #Check in DB if Location
#         for y in range(0, len(sentence.dep)):
#             text = sentence.text_token[y]
#             dep = sentence.dep[y]
#             if dep == 'pobj':
#                 db = pymysql.connect("localhost",
#                                      user="root",
#                                      passwd="root",
#                                      db="orsen_kb")
#                 cursor = db.cursor()
#                 cursor.execute("SELECT second" +
#                                " FROM concepts" +
#                                " WHERE relation = %s" +
#                                " AND first = %s " +
#                                " AND second = %s", ('isA', text, 'location'))
#                 locate = cursor.fetchone()
#                 if locate is not None:
#                     setting_name.append(text)
#                     isAdded = True
#
#
#
#     print("------ SETTING FRAME ------")
#     print(setting_name, setting_type, setting_time)
#     set = len(setting_name)-1
#
#     #connecting to characters
#     if isChar is True:
#         for k in list_char:
#             if list_char[k].name == char:
#                 list_char[k].inSetting = setting_name[set]
#
#     add_setting(setting_name, setting_type, setting_time, world)
#
#     return isAdded
# #Add Setting to World
# def add_setting(name, type, time, world):
#     for x in range(0, len(name)-1):
#         new_setting = Setting()
#         if name[x] is not None:
#             new_setting.name = name[x]
#             new_setting.id = name[x]
#         if type[x] is not None:
#             new_setting.type = type[x]
#         if time[x] is not None:
#             new_setting.time = time[x]
#
#         world.add_setting(new_setting)
#
#     print("----- ADDED SETTING TO THE WORLD -----")


def coref_resolution(s, sent_curr, sent_bef, world, isFirst):
    prn =  []
    noun = []
    curr = sent_curr
    bef = sent_bef

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

    print("num_conj", num_conj)
    for x in range(0, num_prn):
        if num_conj >= 1:
            sent = coref.continuous_coref(utterances=sent_curr)
            num_conj -=1
        elif isFirst is False:
            sent = coref.one_shot_coref(utterances=sent_curr, context=sent_bef)


        mentions = coref.get_mentions()
        print("mentions", mentions)

        rep = coref.get_most_representative()
        print("rep", rep)
        scores = coref.get_scores()
        print("scores", scores)
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
           sent_curr = sent_curr.replace(str(key), str(value))

           if (str(value) not in world.characters) and (str(value) not in world.objects):
            if(str(key).lower() == "he") or (str(key).lower() == "his") or (str(key).lower() == "him"):
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

    return sent_curr

    #extract scores
        #single_mention = scores.get('single_scores')
        #pair_mention = scores.get('pair_scores')
        #single_sc_lib = []
        #pair_sc_lib = []
        #for i in range(0, len(single_mention)):
          #  if single_mention.get(i) != 'None':
         #       single_sc_lib.append(str(single_mention[i]))

        #print(single_sc_lib)

        #low_single_index = single_sc_lib.index(min(single_sc_lib))
        #low_single_index += count

        #print("found it low_single_index: ", low_single_index)

        #for i in range(0, len(pair_mention.get(low_single_index))):
         #   hold = pair_mention.get(low_single_index)
          #  pair_sc_lib.append(str(hold[i]))

        #print(pair_sc_lib)

        #for i in range(0, len(pair_sc_lib)):
         #   pair_sc_lib[i] = float(pair_sc_lib[i])

        #high_pair_index = pair_sc_lib.index(max(pair_sc_lib))
        #print("found it high_pair_index: ", high_pair_index)
        #isMore = True

       # prn.append(mentions[low_single_index])
      #  noun.append(mentions[high_pair_index])

    #print("numPron", num_pron)
    #print(len(prn))

    #rep = coref.get_most_representative()
    #print("rep", rep)



def isAction(sentence):
    isAction = False
    be_forms = ["is", "are", "am", "were", "was"]
    for k in range(0, len(be_forms)):
        for i in range(0, len(sentence.text_token)):
            if be_forms[k] == sentence.text_token[i]:
                isAction = True

    return isAction

#ie_event_extract
def event_extraction(sentence, world, current_node):
    event_char = []
    event_char_action = []
    event_obj = []
    event_obj_action = []
    event_type = []
    event_loc = []
    #get list of characters and objects from world
    list_char = world.characters
    list_obj = world.objects
    print(len(sentence.text_token))
    nsubj_count = 0
    dobj_count = 0
    acomp_count = 0
    xcomp_count = 0
    isThere = False

    for i in range(0, len(sentence.dep_root)):
        if sentence.dep_root[i] == 'nsubj':
            nsubj_count += 1
        elif sentence.dep_root[i] == 'dobj':
            dobj_count += 1

    for i in range(0, len(sentence.dep)):
        if sentence.dep[i] == 'acomp':
            acomp_count += 1
        elif sentence.dep[i] == 'xcomp':
            xcomp_count += 1
            isThere = True


    print("xcomp", xcomp_count)
    curr_type = False
    char_action = ""
    for x in range(0, len(sentence.text_token)):
        isFound_char = False
        isFound_obj = False

        if nsubj_count > 0:
            #get the subject in the sentence
            if sentence.dep_root[x] == 'nsubj':
                nsubj_count -= 1
                char = sentence.text_chunk[x]
                event_char.append(char)
                #match the character with the list of characters from the world
              #  for y in range(0, len(list_char)):
             #       if char == list_char.name[y] and isFound_char is False:
              #          event_char.append(char)
               #         isFound_char = True
                #add event location
                #for x in range(0, len(list_char)):
                 #   if char == list_char[x].name:
                  #      event_loc.append(list_char[x].inSetting)
                #add character action
            event_char_action.append(sentence.dep_root_head[x])

        if isThere is True:
            if xcomp_count > 0:
                if sentence.dep[x] == 'xcomp':
                    event_char_action[len(event_char_action)-1] = sentence.lemma[x]
                    isThere = False


        if dobj_count > 0 and isAction(sentence) is False:
            if sentence.dep_root[x] == 'dobj':
                dobj_count -= 1
                print("dobj", sentence.dep_root_head[x])
                obj = sentence.text_chunk[x]
                print("obj", sentence.text_chunk[x])
                event_obj.append(obj)
                    #match the object with the list of objects from the world
                   #     for y in range(0, len(list_obj)):
                    #        if char == list_obj.name[y] and isFound_obj is False:
                     #           event_obj.append(obj)
                      #          isFound_obj = True

                        # add object action action
                        #event_obj_action.append(sentence.dep_root_head[x])

                event_type.append("Action")

        if acomp_count > 0 and isAction(sentence) == True:
            if sentence.dep[x] == 'acomp':
                obj = sentence.lemma[x]
                print(obj)
                event_obj.append(obj)
                event_type.append("Descriptive")



    print("---- EVENT FRAME ----")
    print(event_type, event_char, event_char_action, event_obj, event_obj_action)

#Add event to the world
def add_event(char, char_action, obj, obj_action, world):
    for x in range(0, len(char)-1):
        new_eventframe = EventFrame()

        if char[x] is not None:
            new_eventframe.char = char[x]
        if char_action[x] is not None:
            new_eventframe.character_actions = char_action[x]
        if obj[x] is not None:
            new_eventframe.obj = obj[x]
        if obj_action[x] is not None:
            new_eventframe.object_actions = obj_action[x]

        list_char = world.characters
        for k in list_char:
            if list_char[k].name == char:
                new_eventframe.setting = list_char[k].inSetting

        world.add_eventframe(new_eventframe)

    print("---- EVENT ADDED TO THE WORLD ----")

