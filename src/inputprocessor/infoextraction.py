from src.db.concepts import DBO_Concept
from src.objects.nlp.Sentence import Sentence
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
        for child in token.children:
            print("child", child)
            new_sentence.children[len(new_sentence.children)-1].append(child)

    for ent in sentence.ents:
        print("---NER---")
        print(ent.text, ent.start_char, ent.end_char, ent.label_)
        new_sentence.text_ent.append(ent.text)
        new_sentence.label.append(ent.text)

    for chunk in sentence.noun_chunks:
        print("---NC---")
        print(chunk.text, chunk.root.text, chunk.root.dep_,
              chunk.root.head.text)

        new_sentence.text_chunk.append(chunk.text)
        new_sentence.dep_root.append(chunk.root.dep_)
        new_sentence.dep_root_head.append(chunk.root.head.text)

    return new_sentence


def character_attribute_extraction(list_of_sentences, world):
    num = 0
    subject = ""
    for sent in list_of_sentences:
        for i in range(0, len(sent.dep)):
            if sent.dep[i] == "ROOT":
                for j in range(0, len(sent.children[i])):
                    for k in range(0, len(sent.text_token)):
                        if str(sent.children[i][j]) == str(sent.text_token[k]):
                            num = k
                            break
                    if sent.dep[num] == "nsubj":
                        subject = sent.children[i][j]
                        add_objects(sent, sent.children[i][j], sent.lemma[i], world)

                    elif sent.dep[num] == "acomp":
                        add_attributes(sent, sent.children[i][j], subject, world)


def add_objects(sent, child, lemma, world):
    if (child not in sent.characters_attributes) and (child not in sent.objects_attributes):
        if DBO_Concept.get_concept_specified("character", DBO_Concept.CAPABLE_OF, lemma) is not None:
            world.add_character(str(child))
            world.characters[str(child)].timesMentioned += 1
            print("CHAR", child)
            subj = child
            # update # of times
            for k in range(0, len(sent.dep_root_head)):
                if (str(sent.dep_root_head[k]) == str(subj)) and (sent.text_chunk[k] not in sent.characters_attributes):
                    world.add_character(str(sent.text_chunk[k]))
                    world.characters[str(sent.text_chunk[k])].timesMentioned += 1
                    # update # of times
                    subj = sent.text_chunk[k]
        else:
            world.add_object(str(child))
            world.objects[str(child)].timesMentioned += 1
            print("CHAR", child)
            subj = child
            # update # of times
            for k in range(0, len(sent.dep_root_head)):
                if (str(sent.dep_root_head[k]) == str(subj)) and (sent.text_chunk[k] not in sent.objects_attributes):
                    world.add_character(str(sent.text_chunk[k]))
                    world.objects[str(sent.text_chunk[k])].timesMentioned += 1
                    subj = sent.text_chunk[k]
                    # update # of times
    elif child in sent.objects_attributes:
        if DBO_Concept.get_concept_specified("character", DBO_Concept.CAPABLE_OF, lemma) is not None:
            world.add_character(str(child))
            # transfer all attributes from object to character, delete the one in object
        else:
            world.objects[str(child)].timesMentioned += 1
    elif child in sent.characters_attributes:
        world.characters[str(child)].timesMentioned += 1


def add_attributes(sent, child, subject):
    if str(subject) in sent.characters_attributes:
        sent.characters_attributes[subject].append(child)
        for k in range(0, len(sent.dep_root_head)):
            if str(sent.dep_root_head[k]) == str(subject):
                sent.characters_attributes[sent.dep_root_head[k]].append(child)
                subject = sent.text_chunk[k]
    elif str(subject) in sent.objects_attributes.keys():
        sent.objects_attributes[str(subject)].append(child)
        for k in range(0, len(sent.dep_root_head)):
            if str(sent.dep_root_head[k]) == str(subject):
                sent.objects_attributes[sent.text_chunk[k]].append(child)
                subject = sent.text_chunk[k]


# def add_character_attribute(count, nc_text, pos_dep, pos_text, nc_dep_root):
#     characters_attributes = {}
#     for i in range(0, len(nc_text[count])):
#         if nc_text[count][i] not in characters_attributes:
#             #characters_attributes.fromkeys(nc_text[count][i])
#             if(nc_dep_root[count][i] is "conj") or (nc_dep_root[count][i] is "nsubj"):
#                 characters_attributes.update({nc_text[count][i]: []})
#
#     for i in range(0, len(pos_dep[count])):
#         if pos_dep[count][i] == "acomp":
#             for j in range(0, len(nc_text[count])):
#                 characters_attributes[nc_text[count][j]].append(pos_text[count][i])
#
#     return characters_attributes
#
#
# def add_object_attribute(count, nc_text, pos_dep, pos_text, nc_dep_root):
#     objects_attributes = {}
#     for i in range(0, len(nc_text[count])):
#         if nc_text[count][i] not in objects_attributes:
#             #objects_attributes.fromkeys(nc_text[count][i])
#             objects_attributes.update({nc_text[count][i]: []})
#
#     for i in range(0, len(pos_dep[count])):
#         if pos_dep[count][i] == "acomp":
#             for j in range(0, len(nc_text[count])):
#                 objects_attributes[nc_text[count][j]].append(pos_text[count][i])
#
#     return objects_attributes
#
#
# def character_attribute_extraction(nc_text, pos_lemma, pos_dep, pos_text, nc_dep_root):
#     characters = {}
#     objects = {}
#     for i in range(0, len(pos_dep)):
#         for j in range(0, len(pos_dep[i])):
#             if pos_dep[i][j] == "ROOT":
#                if DBO_Concept.get_concept_specified("character", DBO_Concept.CAPABLE_OF, pos_lemma[i][j]) is not None:
#                         characters = add_character_attribute(i, nc_text, pos_dep, pos_text, nc_dep_root)
#                 else:
#                         print("ELSE", pos_dep[i][j])
#                         objects = add_object_attribute(i, nc_text, pos_dep, pos_text, nc_dep_root)
#
#     return characters, objects

# ---------- rachel


#ie_categorizing
def isStoryText(sentence):
    #checks if entry has "orsen"
    if 'orsen' not in sentence:
        return True
    else:
        return False

#ie_setting_detail_extraction
def settingExtract(sentence):
        #preposition checking
        if 'in' in sentence:
            a,c = sentence.split('in')
        elif 'on' in sentence:
            a,c = sentence.split('on')
        elif 'at' in sentence:
            a,c = sentence.split('at')
        elif 'by' in sentence:
            a,c = sentence.split('by')
        elif 'to' in sentence:
            a,c = sentence.split('to')

        #punctuation checking
        if '.' in c:
            c = c.replace('.', '')
        if ',' in c:
            c = c.replace(',', '')
        if '?' in c:
            c = c.replace('?', '')
        if '!' in c:
            c = c.replace('!', '')

        count = len(sentence.label)
        named_entity(c)
        if sentence.label[count] is not None:
            sentence.setting_type.append(sentence.label[count])
        else:
           db = mysqldbhelper.DatabaseConnection("localhost",
                                                user="root",
                                                passwd="root",
                                                db="orsen_kb")
           row = db.get_one("SELECT second FROM concepts WHERE relation = %s AND first = %s AND second = %s", ('isA', c, 'location'))
           if row is not None:
               sentence.setting_type.append('location')
               sentence.setting_name.append(c)
           db.close()

        print(sentence.setting_frame)

    #TO DO: make setting an object to add sa World.py

#ie_event_extract
def eventExtract(sentence, sentences):
       sent_pos = len(sentences)-1
       root_count = len(sentences[sent_pos].dep_root)
       be_forms = ['be', 'am', 'is', 'are', 'was', 'were', 'been', 'being']
       type = "Action"

       for x in range(0, root_count):
            # Assign sequence number
            if len(sentences.seq_no) == 0:
                sentences.seq_no.append(0)
            else:
                sentences.seq_no.append(len(sentences.seq_no))

            sentence.doer.append(sentences[sent_pos].dep_root[x])
            sentence.doer_act.append(sentences[sent_pos].dep_root[x].dep_root_head)
            sentence.rec.append(sentences[sent_pos].dep[x])

            #Add Event Type
            for i in range(0, len(be_forms)):
                if be_forms[i] in sentence:
                    type = "Descriptive"


            sentence.event_type.append(type)
            type = "Action" #reset

            #Check for Location
            if sentence.setting_label is 'location':
                locate = sentence.setting_name

            if locate is not None:
                sentence.location.append(locate)

            print(sentence.event_frame)
