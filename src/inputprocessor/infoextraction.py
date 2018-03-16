from src.db.concepts import DBO_Concept
from src.objects.nlp.Sentence import Sentence
from spacy import symbols
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


def character_attribute_extraction(list_of_sentences):
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
                        add_objects(sent, i, j)
                        print("AAAA", sent.characters_attributes)


                    elif sent.dep[num] == "acomp":
                        print("acom", sent.dep[num])
                        print("CCCC", sent.objects_attributes)
                        add_attributes(sent, i, j, subject)
                        print("BBBB", sent.objects_attributes)


def add_objects(sent, count1, count2):
    if (sent.children[count1][count2] not in sent.characters_attributes) and (sent.children[count1][count2] not in sent.characters_attributes):
        if DBO_Concept.get_concept_specified("character", DBO_Concept.CAPABLE_OF, sent.lemma[count1]) is not None:
            sent.characters_attributes.update({str(sent.children[count1][count2]): []})
            print("CHAR", sent.children[count1][count2])
            subj = sent.children[count1][count2]
            for k in range(0, len(sent.dep_root_head)):
                if (str(sent.dep_root_head[k]) == str(subj)) and (sent.text_chunk[k] not in sent.characters_attributes):
                    sent.characters_attributes.update({sent.text_chunk[k]: []})
                    subj = sent.text_chunk[k]
        else:
            sent.objects_attributes.update({str(sent.children[count1][count2]): []})
            print("CHAR", sent.children[count1][count2])
            subj = sent.children[count1][count2]
            for k in range(0, len(sent.dep_root_head)):
                if (str(sent.dep_root_head[k]) == str(subj)) and (sent.text_chunk[k] not in sent.objects_attributes):
                    sent.objects_attributes.update({sent.text_chunk[k]: []})
                    subj = sent.text_chunk[k]


def add_attributes(sent, count1, count2, subject):
    if str(subject) in sent.characters_attributes:
        sent.characters_attributes[subject].append(sent.children[count1][count2])
        for k in range(0, len(sent.dep_root_head)):
            if str(sent.dep_root_head[k]) == str(subject):
                sent.characters_attributes[sent.dep_root_head[k]].append(sent.children[count1][count2])
                subject = sent.text_chunk[k]
    elif str(subject) in sent.objects_attributes.keys():
        sent.objects_attributes[str(subject)].append(sent.children[count1][count2])
        for k in range(0, len(sent.dep_root_head)):
            if str(sent.dep_root_head[k]) == str(subject):
                sent.objects_attributes[sent.text_chunk[k]].append(sent.children[count1][count2])
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
#                 if DBO_Concept.get_concept_specified("character", DBO_Concept.CAPABLE_OF, pos_lemma[i][j]) is not None:
#                         characters = add_character_attribute(i, nc_text, pos_dep, pos_text, nc_dep_root)
#                 else:
#                         print("ELSE", pos_dep[i][j])
#                         objects = add_object_attribute(i, nc_text, pos_dep, pos_text, nc_dep_root)
#
#     return characters, objects

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
