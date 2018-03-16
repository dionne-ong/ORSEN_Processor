import spacy
import mysqldbhelper
from stanfordcorenlp import StanfordCoreNLP
from src.db.concepts import DBO_Concept
from src.objects.storyworld.Character import Character
# ----- luisa

def reading(filename):
    with open(filename, 'r') as f:
        userinput = f.read()
    return userinput


def part_of_speech(sentence):

    for token in sentence:
        print("---POS----");
        print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_)
        text_token[counter].append(token.text)
        lemma[counter].append(token.lemma_)
        pos[counter].append(token.pos_)
        tag[counter].append(token.tag_)
        dep[counter].append(token.dep_)


def named_entity(sentence):

    for ent in sentence.ents:
        print("---NER----");
        print(ent.text, ent.start_char, ent.end_char, ent.label_)

        text_ent[counter].append(ent.text)
        label[counter].append(ent.label_)


def noun_chunks(sentence):

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
    for i in range(0, len(nc_text[count])):
        new_character = Character()
        new_character.name = nc_text[count][i]

    for i in range(0, len(pos_dep[count])):
        if pos_dep[count][i] == "acomp":
            new_character.attributes.append(pos_text[count][i])


def character_attribute_extraction(nc_text, pos_lemma, pos_dep, pos_text):
    for i in range(0, len(pos_dep)):
        for j in range(0, len(pos_dep[i])):
            if pos_dep[i][j] == "ROOT":
                if DBO_Concept.get_concept_specified("character", DBO_Concept.CAPABLE_OF, pos_lemma[i][j]) is not None:
                        add_character_attribute(i, nc_text, pos_dep, pos_text)




nlp = spacy.load('en')
document = nlp(reading("document.txt"))

sentences = [sent.string.strip() for sent in document.sents]

#For POS
text_token = []
lemma = []
pos = []
tag = []
dep = []

#For NER
text_ent = []
label = []

#For Noun Chunks
text_chunk = []
dep_root = []
dep_root_head = []

counter = 0

#Character
characters = []

for sent in sentences:

    print(sent)
    sent = nlp(sent)

    text_token.append([])
    lemma.append([])
    pos.append([])
    tag.append([])
    dep.append([])

    text_ent.append([])
    label.append([])

    text_chunk.append([])
    dep_root.append([])
    dep_root_head.append([])

    part_of_speech(sent)
    named_entity(sent)
    noun_chunks(sent)
    counter += 1

character_attribute_extraction(text_chunk, lemma, dep, text_token)

nlp = StanfordCoreNLP(r'C:\stanford-corenlp-full-2018-01-31', memory='8g')
props = {'annotators': 'dcoref', 'pipelineLanguage': 'en', 'outputFormat': 'json'}
output = [nlp.annotate(sent, properties=props) for sent in sentences]
print("------------------")
print(output)

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
