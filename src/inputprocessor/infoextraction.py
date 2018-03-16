from src.db.concepts import DBO_Concept
import mysqldbhelper
# ----- luisa

def reading(filename):
    with open(filename, 'r') as f:
        userinput = f.read()
    return userinput


def part_of_speech(sentence, text_token, lemma, pos, tag, dep, counter):

    for token in sentence:
        print("---POS----");
        print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_)
        text_token[counter].append(token.text)
        lemma[counter].append(token.lemma_)
        pos[counter].append(token.pos_)
        tag[counter].append(token.tag_)
        dep[counter].append(token.dep_)


def named_entity(sentence, text_ent, label, counter):

    for ent in sentence.ents:
        print("---NER----");
        print(ent.text, ent.start_char, ent.end_char, ent.label_)

        text_ent[counter].append(ent.text)
        label[counter].append(ent.label_)


def noun_chunks(sentence, text_chunk, dep_root, dep_root_head, counter):
    for chunk in sentence.noun_chunks:
        print("----NC---");
        print(chunk.text, chunk.root.text, chunk.root.dep_,
              chunk.root.head.text)
        text_chunk[counter].append(chunk.text)
        dep_root[counter].append(chunk.root.dep_)
        dep_root_head[counter].append(chunk.root.head.text)


def remove_duplicate(alist):
    return list(set(alist))


def add_character_attribute(count, nc_text, pos_dep, pos_text):
    characters_attributes = {}
    for i in range(0, len(nc_text[count])):
        if nc_text[count][i] not in characters_attributes:
            #characters_attributes.fromkeys(nc_text[count][i])
            characters_attributes.update({nc_text[count][i]: None})

    for i in range(0, len(pos_dep[count])):
        if pos_dep[count][i] == "acomp":
            for j in range(0, len(nc_text[count])):
                characters_attributes[nc_text[count][j]].append(pos_text[count][i])

    return characters_attributes


def add_object_attribute(count, nc_text, pos_dep, pos_text):
    objects_attributes = {}
    for i in range(0, len(nc_text[count])):
        if nc_text[count][i] not in objects_attributes:
            #objects_attributes.fromkeys(nc_text[count][i])
            objects_attributes.update({nc_text[count][i]: None})

    for i in range(0, len(pos_dep[count])):
        if pos_dep[count][i] == "acomp":
            for j in range(0, len(nc_text[count])):
                objects_attributes[nc_text[count][j]].append(pos_text[count][i])

    return objects_attributes


def character_attribute_extraction(nc_text, pos_lemma, pos_dep, pos_text):
    for i in range(0, len(pos_dep)):
        for j in range(0, len(pos_dep[i])):
            if pos_dep[i][j] == "ROOT":
                if DBO_Concept.get_concept_specified("character", DBO_Concept.CAPABLE_OF, pos_lemma[i][j]) is not None:
                        characters = add_character_attribute(i, nc_text, pos_dep, pos_text)
                else:
                        objects = add_object_attribute(i, nc_text, pos_dep, pos_text)

    return characters, objects

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
