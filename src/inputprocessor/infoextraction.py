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
        # print("---POS----");
        # print(token.text, token.head.text, token.lemma_, token.pos_, token.tag_, token.dep_)

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
        # print("---NER---")
        # print(ent.text, ent.start_char, ent.end_char, ent.label_)
        new_sentence.text_ent.append(ent.text)
        new_sentence.label.append(ent.label_)

    for chunk in sentence.noun_chunks:
        # print("---NC---")
        # print(chunk.text, chunk.root.text, chunk.root.dep_, chunk.root.head.text)

        new_sentence.text_chunk.append(chunk.text)
        new_sentence.dep_root.append(chunk.root.dep_)
        new_sentence.dep_root_head.append(chunk.root.head.text)

    return new_sentence


#def is_verb(sent, children):
#    for c in children:
#        temp = find_text_index(sent, c)
#        if sent.pos[temp] == "VERB" and str(sent.text_token[temp]) == str(c):
#            print("CH", c)
#            return sent.dep[temp]
#    return None


def find_text_index(sent, child):
    num = 0
    for k in range(0, len(sent.text_token)):
        if (str(child) == str(sent.text_token[k])) and (sent.finished_nodes[k] == 0):
            print("num", k)
            num = k
            break
    return num


def find_ent_index(sent, ent):
    for k in range(0, len(sent.text_ent)):
        if ent == str(sent.text_ent[k]):
            return str(sent.label[k])
    return None


def details_extraction(sent, world, current_node, subj="", loc=""):
    num = -1
    subject = subj
    location = loc
    current_index = -1
    for i in range(0, len(sent.dep)):
        if (sent.dep[i] == current_node) and (sent.finished_nodes[i] == 0):
            current_index = i
            sent.finished_nodes[i] = 1

    is_negated = False
    if current_index != -1:
        i = current_index
        for j in range(0, len(sent.children[i])):
            num = find_text_index(sent, str(sent.children[i][j]))

            if num != -1 and sent.dep[num] in ["nsubj", "acomp", "attr", "nsubjpass", "dobj", "xcomp"]:
                sent.finished_nodes[num] = 1

                # nominal subject
                if sent.dep[num] == "nsubj":
                    subject = sent.children[i][j]
                    add_objects(sent, str(subject), sent.dep[num], sent.lemma[i], world)
                    add_capability(sent, str(sent.lemma[i]), str(subject), world, is_negated)


                # nominal subject (passive) or direct object
                elif sent.dep[num] == "nsubjpass" or sent.dep[num] == "dobj":
                    add_objects(sent, str(sent.children[i][j]), sent.dep[num], sent.lemma[i], world)

                # adjectival complement
                elif sent.dep[num] == "acomp":
                    add_attributes(sent, num, str(subject), world, is_negated)

                # attribute
                elif sent.dep[num] == "attr":
                    location = add_settings(sent, num, subject, is_negated, world, location)
                    if location == "":
                        add_attributes(sent, num, str(subject), world, is_negated)

                # open clausal compliment
                elif sent.dep[num] == "xcomp":
                    add_capability(sent, str(sent.lemma[num]), str(subject), world, is_negated)

                is_negated = False

                if sent.children[num] is not None:
                    for c in sent.children[num]:
                        dep_index = find_text_index(sent, str(c))
                        details_extraction(sent, world, sent.dep[dep_index], subject, location)

            # negation
            elif num != -1 and sent.dep[num] == "neg":
                sent.finished_nodes[num] = 1
                is_negated = True

            # noun phrase as adverbial modifier
            elif num != -1 and  sent.dep[num] == "npadvmod":
                sent.finished_nodes[num] = 1
                location = add_settings(sent, num, subject, is_negated, world, location)

            # object of preposition
            elif num != -1 and  sent.dep[num] == "pobj":
                sent.finished_nodes[num] = 1
                location = add_settings(sent, num, subject, is_negated, world, location)

                if location == "":
                    add_objects(sent, str(sent.children[i][j]), sent.dep[num], sent.lemma[i], world)

            # adverbial clause modifier
            # clausal complement
            # conjunction
            # preposition
            # agent
            # dative - the noun to which something is given
            # adverbial modifier
            elif num != -1 \
                    and sent.dep[num] in ["advcl", "ccomp", "conj", "prep", "agent", "dative", "advmod"]:
                print("SENT", sent.dep[num], "TOKEN", sent.text_token[num])
                details_extraction(sent, world, sent.dep[num], subject, location)

            else:
                print("ERROR: Sentence num not found.")
    else:
        print("ERROR: CANNOT FIND CORRECT INDEX")
        print("ERROR", current_node)


def char_conj_extractions(sent, subj):
    list_of_conj = [subj]
    for k in range(0, len(sent.dep_root_head)):
        if str(sent.dep_root_head[k]) == str(subj):
            list_of_conj.append(str(sent.text_chunk[k]))
            subj = str(sent.text_chunk[k])
    return list_of_conj


def add_capability(sent, attr, subject, world, negation):
    list_of_char = char_conj_extractions(sent, subject)
    if attr not in ["is", "was", "are", "be", "am", "are", "were", "been", "being"]:
        new_attribute = Attribute(DBO_Concept.CAPABLE_OF, attr, negation)

        for c in list_of_char:
            if str(c) in world.characters:
                    world.characters[c].attributes.append(new_attribute)
            else:
                    world.objects[c].attributes.append(new_attribute)


def add_objects(sent, child, dep, lemma, world):
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
                setting = world.settings[c]
                new_character = Character()
                new_character.name = setting.name
                new_character.id = setting.id
                new_character.attributes = []
                new_character.inSetting = setting.time
                world.add_object(new_character)
        elif c in world.characters:
            world.characters[c].timesMentioned += 1


def add_attributes(sent, num, subject, world, negation):
    list_of_attributes = [sent.text_token[num]]
    list_of_char = char_conj_extractions(sent, subject)
    head = sent.text_token[num]

    for i in range(num, len(sent.words)):
        if (sent.dep[i] == 'conj') and (sent.head_text[i] == head):
            list_of_attributes.append(sent.text_token[i])
            head = sent.text_token[i]

    for c in list_of_char:
        if c in world.characters:
            for attr in list_of_attributes:
                new_attribute = Attribute(DBO_Concept.HAS_PROPERTY, attr, negation)
                char = world.characters[c]
                print("ADD", attr, "TO", c)
                char.attributes.append(new_attribute)

        elif c in world.objects:
            for attr in list_of_attributes:
                new_attribute = Attribute(DBO_Concept.HAS_PROPERTY, attr, negation)
                print("ADD", attr, "TO", c)
                obj = world.objects[c]
                obj.attributes.append(new_attribute)


def add_settings(sent, num, subject, negation, world, location):
    current_location = location
    list_of_char = char_conj_extractions(sent, subject)

    # is there a negation for settings
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

                world.add_setting(new_setting)

            elif label in ["DATE", "TIME"]:

                if current_location is "":
                    current_location = sent.text_token[num]
                    new_setting.id = current_location
                    new_setting.name = current_location
                    new_setting.type = label
                    new_setting.time.append(str(sent.text_token[num]))
                    world.add_setting(new_setting)
                else:
                    setting = world.settings[current_location]
                    setting.time.append(str(sent.text_token[num]))

            elif DBO_Concept.get_concept_specified(str(sent.text_token[num]), DBO_Concept.IS_A, "location"):
                print("---------------------------------------")
                current_location = sent.text_token[num]
                new_setting.id = current_location
                new_setting.name = current_location
                new_setting.type = "LOC"
                world.add_setting(new_setting)

            for c in list_of_char:
                if str(c) in world.characters:
                    char = world.characters[str(c)]
                    char.inSetting = current_location
                elif str(c) in world.objects:
                    obj = world.objects[str(c)]
                    obj.inSetting = current_location

    return current_location


def corenference_resolution(sentences, world):
    j = 1;
    for i in range(0, len(sentences)-1):
        coref = Coref()
        clusters = coref.one_shot_coref(utterances=sentences[j], context=sentences[i])
        print("clusters", clusters)
        print("a", str(sentences[i]), "b", str(sentences[j]) )
        mentions = coref.get_mentions()
        print("mentions", mentions)

        rep = coref.get_most_representative(use_no_coref_list=True)
        print("rep", rep)

        for key, value in rep.items():
            sentences[j] = sentences[j].replace(str(key), str(value))
            if (str(value) not in world.characters) and (str(value) not in world.objects):
                if(str(key).lower() == "he") or (str(key).lower() == "his") or (str(key).lower() == "him"):
                    new_character = Character()
                    new_character.name = str(value)
                    new_character.id = str(value)
                    new_character.gender = "M"
                    world.add_character(new_character)
                    world.characters[new_character.id].timesMentioned += 1
                elif (str(key).lower() == "she") or (str(key).lower() == "her") or (str(key).lower() == "hers"):
                    new_character = Character()
                    new_character.name = str(value)
                    new_character.id = str(value)
                    new_character.gender = "F"
                    world.add_character(new_character)
                    world.characters[new_character.id].timesMentioned += 1

        j += 1


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

#ie_event_extract
def event_extraction(sentence, world):
    event_char = []
    event_char_action = []
    event_obj = []
    event_obj_action = []

    #check a character appearance in the character world
    list_char = world.characters
    isFound = False
    sbj_c = 0
    vrb_c = 0
    pbj_c = 0

    for k in range(0, len(sentence.dep)):
        if sentence.dep[k] == 'nsubj':
            sbj_c += 1
        elif sentence.dep[k] == 'verb':
            vrb_c += 1
        elif sentence.dep[k] == 'pobj':
            pbj_c += 1
    

    for x in range(0, len(sentence.dep)):
        if sentence.dep[x] == 'nsubj':
            char = sentence.dep[x]
            for y in range(0, len(list_char)):
                if char == list_char.name[y]:
                    isFound = True
                    event_char.append(char)
                    continue

        if sentence.dep_root[x] == 'verb':
            act = sentence.dep_root_head[x]
            event_char_action.append(act)
            continue

        if sentence.dep_root[x] == 'pobj':
            obj = sentence.text_chunk[x]
            event_obj.append(obj)

    #TO DO: get object / character action

    #TO DO: get setting of the sentence

    print("---- EVENT FRAME ----")
    print(event_char, event_char_action, event_obj, event_obj_action)

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

