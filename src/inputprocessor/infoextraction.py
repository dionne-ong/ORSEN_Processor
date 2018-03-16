from src.db.concepts import DBO_Concept
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

#For Categorizing
commands = []
story = []

#For Semantic Role Labeling
sem_role = []

#For Setting Detail Extraction
setting_name = []
setting_type= []
setting_frame = [setting_name, setting_type]

#For Event Detail Extraction
seq_no = []
event_type = []
doer = []
doer_act = []
receiver = []
receiver_act = []
location = []
event_frame = [seq_no, event_type, doer, doer_act, receiver, receiver_act, location]
#ie_categorizing
def categorizing(sentence):
    #checks if entry has "orsen"
      if 'orsen' not in sentence:
        story.append(sentence)
      else:
        commands.append(sentence)

#ie_setting_detail_extraction
def settingExtract(sentences):
    for x in range(0, len(sentences)):
        rows  = []
        isLocation = False

        #preposition checking
        if 'in' in sentences[x]:
            a,c = sentences[x].split('in')
        elif 'on' in sentences[x]:
            a,c = sentences[x].split('on')
        elif 'at' in sentences[x]:
            a,c = sentences[x].split('at')
        elif 'by' in sentences[x]:
            a,c = sentences[x].split('by')
        elif 'to' in sentences[x]:
            a,c = sentences[x].split('to')

        #punctuation checking
        if '.' in c:
            c = c.replace('.', '')
        if ',' in c:
            c = c.replace(',', '')
        if '?' in c:
            c = c.replace('?', '')
        if '!' in c:
            c = c.replace('!', '')


        count = len(label)
        named_entity(c)
        if label[count] is not None:
            setting_type.append(label[count])
        else:
            db = mysqldbhelper.DatabaseConnection("localhost",
                                                  user="root",
                                                  passwd="root",
                                                  db="orsen_kb")
            row = db.get_one("SELECT second FROM concepts WHERE relation = %s AND first = %s AND second = %s", ('isA', c, 'location'))

            if row is not None:
                setting_type.append('location')
            db.close()

        setting_name.append(c)

#ie_event_detail_extract
def eventExtract(sentences):
    #TO DO: use dependency parsing to identify position of the event
    for x in range(0, len(sentences)):
        seq_no.append[x]
