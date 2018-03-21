from src.db.concepts import DBO_Concept
import pymysql
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
        print(ent.text, ent.start_char, ent.end_char, ent.label_)
        new_sentence.text_ent.append(ent.text)
        new_sentence.label.append(ent.label_)

    for chunk in sentence.noun_chunks:
        # print("---NC---")
        # print(chunk.text, chunk.root.text, chunk.root.dep_, chunk.root.head.text)

        new_sentence.text_chunk.append(chunk.text)
        new_sentence.dep_root.append(chunk.root.dep_)
        new_sentence.dep_root_head.append(chunk.root.head.text)

    return new_sentence


def details_extraction(list_of_sentences, world):
    num = 0
    subject = ""
    current_node = "ROOT"
    is_negated = False
    for sent in list_of_sentences:
        for i in range(0, len(sent.dep)):
            if sent.dep[i] == current_node:
                sent.finished_nodes[i] = 1
                # print("iii", i, sent.text_token[i])
                for j in range(0, len(sent.children[i])):
                    num = find_index(sent, str(sent.children[i][j]))
                    # print("child", sent.children[i][j], "dep", sent.dep[num])
                    # nominal subject
                    if sent.dep[num] == "nsubj":
                        subject = sent.children[i][j]
                        # print("SUBJECT", subject)
                        add_objects(sent, str(subject), sent.dep[num], sent.lemma[i], world)
                        add_capability(sent, str(sent.lemma[i]), str(subject), world, is_negated)
                        is_negated = False

                    # adjectival complement
                    elif sent.dep[num] == "acomp":
                        add_attributes(sent, num, str(subject), world, is_negated)
                        is_negated = False

                    # negation
                    elif sent.dep[num] == "neg":
                        is_negated = True

                    # nominal subject (passive)
                    elif sent.dep[num] == "nsubjpass":
                        subject = sent.children[i][j]
                        add_objects(sent, str(sent.children[i][j]), sent.dep[num], sent.lemma[i], world)

                    # direct object
                    elif sent.dep[num] == "dobj":
                        add_objects(sent, str(sent.children[i][j]), sent.dep[num], sent.lemma[i], world)

                    # dative - the noun to which something is given
                    elif sent.dep[num] == "dative":
                        if sent.text_token[num].children is None:
                            add_objects(sent, str(sent.children[i][j]), sent.dep[num], sent.lemma[i], world)
                        else:
                            print("may be added to settings or objects")

                    # preposition
                    elif sent.dep[num] == "prep":
                        print("add it to settings or add it to objects")

                    # agent
                    elif sent.dep[num] == "agent":
                        print("add it to settings or add it to objects")

                    # conjunction
                    elif sent.dep[num] == "conj":
                        current_node = "conj"
                        i = num
                        break

                    # clausal complement
                    elif sent.dep[num] == "ccomp":
                        current_node = "ccomp"
                        i = num
                        break

                    # adverbial clause modifier
                    elif sent.dep[num] == "advcl":
                        current_node = "advcl"
                        i = num
                        break

                    # open clausal compliment - it doesn't have its own subject
                    elif sent.dep[num] == "xcomp":
                        current_node = "xcomp"
                        i = num
                        break


def add_capability(sent, attr, subj, world, negation):
    if attr not in ["is", "was", "are", "be", "am", "are", "were", "been", "being"]:
        new_attribute = Attribute(DBO_Concept.CAPABLE_OF, attr, negation)

        if subj in world.characters:
            world.characters[subj].attributes.append(new_attribute)
        else:
            world.objects[subj].attributes.append(new_attribute)

        for k in range(0, len(sent.dep_root_head)):
            if str(sent.dep_root_head[k]) == subj:
                if str(sent.text_chunk[k]) in world.characters:
                    world.characters[str(sent.text_chunk[k])].attributes.append(new_attribute)
                else:
                    world.objects[str(sent.text_chunk[k])].attributes.append(new_attribute)

                subj = str(sent.text_chunk[k])


def find_index(sent, child):
    num = 0
    for k in range(0, len(sent.text_token)):
        # print("aa", len(sent.text_token), "node", sent.finished_nodes[k], "com", sent.text_token[k],
        #     sent.children[i][j])
        if (child == str(sent.text_token[k])) and (sent.finished_nodes[k] == 0):
            num = k
            sent.finished_nodes[k] == 1
            break
    return num


def add_objects(sent, child, dep, lemma, world):
    if (child not in world.characters) and (child not in world.objects):
        if (DBO_Concept.get_concept_specified("character", DBO_Concept.CAPABLE_OF, lemma) is not None) \
                and dep == "nsubj":
            new_character = Character()
            new_character.name = child
            new_character.id = child
            new_character.attributes = []
            world.add_character(new_character)
            world.characters[new_character.id].timesMentioned = 1
            subj = child
            for k in range(0, len(sent.dep_root_head)):
                if (str(sent.dep_root_head[k]) == subj) and (sent.text_chunk[k] not in world.characters):
                    new_character = Character()
                    new_character.name = str(sent.text_chunk[k])
                    new_character.id = str(sent.text_chunk[k])
                    new_character.attributes = []
                    world.add_character(new_character)
                    world.characters[new_character.id].timesMentioned = 1
                    subj = sent.text_chunk[k]
        else:
            new_object = Object()
            new_object.name = child
            new_object.id = child
            new_object.attributes = []
            world.add_object(new_object)
            world.objects[new_object.id].timesMentioned = 1
            subj = child
            for k in range(0, len(sent.dep_root_head)):
                if (str(sent.dep_root_head[k]) == subj) and (sent.text_chunk[k] not in world.objects):
                    new_object = Object()
                    new_object.name = str(sent.text_chunk[k])
                    new_object.id = str(sent.text_chunk[k])
                    world.add_object(new_object)
                    new_object.attributes = []
                    world.objects[new_object.id].timesMentioned = 1
                    subj = str(sent.text_chunk[k])
    elif child in world.objects:
        if DBO_Concept.get_concept_specified("character", DBO_Concept.CAPABLE_OF, lemma) is not None:
            new_character = Character.convert_from_object(child)
            world.add_character(new_character)
            world.characters[new_character.id].timesMentioned += 1
        else:
            world.objects[child].timesMentioned += 1
    elif child in world.characters:
        world.characters[child].timesMentioned += 1


def add_attributes(sent, num, subject, world, negation):
    list_of_attributes = [sent.text_token[num]]
    head = sent.text_token[num]
    for i in range(num, len(sent.words)):
        if (sent.dep[i] == 'conj') and (sent.head_text[i] == head):
            list_of_attributes.append(sent.text_token[i])
            head = sent.text_token[i]
    if subject in world.characters:
        for attr in list_of_attributes:
            new_attribute = Attribute(DBO_Concept.HAS_PROPERTY, attr, negation)
            char = world.characters[subject]
            print(char)
            char.attributes.append(new_attribute)
        for k in range(0, len(sent.dep_root_head)):
            if str(sent.dep_root_head[k]) == subject:
                for attr in list_of_attributes:
                    new_attribute = Attribute(DBO_Concept.HAS_PROPERTY, attr, negation)
                    char = world.characters[sent.text_chunk[k]]
                    char.attributes.append(new_attribute)
                subject = str(sent.text_chunk[k])

    elif subject in world.objects:
        for attr in list_of_attributes:
            new_attribute = Attribute(DBO_Concept.HAS_PROPERTY, attr, negation)
            print("ADD", attr, "TO", subject)
            obj = world.objects[subject]
            obj.attributes.append(new_attribute)
        for k in range(0, len(sent.dep_root_head)):
            if str(sent.dep_root_head[k]) == subject:
                for attr in list_of_attributes:
                    new_attribute = Attribute(DBO_Concept.HAS_PROPERTY, attr, negation)
                    print("ADD", attr, "TO", sent.text_chunk[k])
                    obj = world.objects[sent.text_chunk[k]]
                    obj.attributes.append(new_attribute)
                subject = str(sent.text_chunk[k])


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




#ie_categorizing
def isStoryText(sentence):
    #checks if entry has "orsen"
    if 'orsen' not in sentence:
        return True
    else:
        return False

#ie_setting_detail_extraction
def setting_attribute_extraction(sentence, world):
    setting_name = []
    setting_time = []
    setting_type = []
    isAdded = False

    isPROPN = False
    isLocation = False
    isDate = False

    #Check in NER
    for x in range(0, len(sentence.text_ent)):
        text = sentence.text_ent[x]
        label = sentence.label[x]
        print("LABEL", sentence.label[x])

        #Checking for Duplicate Entries

        print("label: ", label)
        #Check if GPE, Location, Date or Time
        if label == 'GPE' or label == 'LOCATION':
            setting_name.append(text)
            print("it is a location!!")
            isAdded = True
            setting_type.append("LOCATION")
            isLocation = True
            isPROPN = True

        if label == 'DATE':
            if isLocation is False:
                setting_name.append(text)
                isAdded = True
                setting_type.append("DATE")
                isDate = True
            elif isLocation is True:
                setting_time.append(text)
                isAdded = True
                setting_type.append("DATE")
                isDate = True

        if label == 'TIME':
            if isDate is False:
                if isLocation is True:
                    setting_time.append(text)
                    isAdded = True
                    setting_type.append("TIME")
                elif isLocation is False:
                    setting_name.append(text)
                    isAdded = True
                    setting_type.append("TIME")
            elif isDate is True:
                if isLocation is True:
                    hold = setting_time[len(setting_time)-1]
                    setting_time[len(setting_time)-1] = hold + "," + text
                    setting_type.append("TIME")
                    isAdded = True
                elif isLocation is False:
                    setting_time.append(text)
                    setting_type.append("TIME")
                    isAdded = True

        #Check in DB if Location
        for y in range(0, len(sentence.dep)):
            text = sentence.text_token[y]
            dep = sentence.dep[y]
            if dep == 'pobj':
                db = pymysql.connect("localhost",
                                     user="root",
                                     passwd="root",
                                     db="orsen_kb")
                cursor = db.cursor()
                cursor.execute("SELECT second" +
                               " FROM concepts" +
                               " WHERE relation = %s" +
                               " AND first = %s " +
                               " AND second = %s", ('isA', text, 'location'))
                locate = cursor.fetchone()
                if locate is not None:
                    setting_name.append(text)
                    isAdded = True

    print("------SETTING FRAME------")
    print(setting_name, setting_type, setting_time)
    
    add_setting(setting_name, setting_type, setting_time, world)

    return isAdded
#Add Setting to World
def add_setting(name, type, time, world):
    for x in range(0, len(name)-1):
        new_setting = Setting()
        if name[x] is not None:
            new_setting.name = name[x]
            new_setting.id = name[x]
        if type[x] is not None:
            new_setting.type = type[x]
        if time[x] is not None:
            new_setting.time = time[x]

        world.add_setting(new_setting)

    print("-----ADDED SETTING TO THE WORLD----")

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