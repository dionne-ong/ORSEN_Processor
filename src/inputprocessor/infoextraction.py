import spacy
from stanfordcorenlp import StanfordCoreNLP
from src.db.concepts import DBO_Concept
# ----- luisa


def reading(filename):
    with open(filename, 'r') as f:
        userinput = f.read()
    return userinput


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

#For Categorizing
commands = []
story = []

#For Semantic Role Labeling
sem_role = []

#For Setting Detail Extraction
setting = []
setting_detail = []
counter = 0

#Character
characters = []


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



#def character_extraction(nc_text, nc_root, nc_root_head):
#    for i in range(0, len(ner_label)):
#        for j in range(0, len(ner_label[i])):
#            if ner_label[i][j] == "PERSON":
#                characters.append(ner_text[i][j])









character_extraction(text_ent, label)

nlp = StanfordCoreNLP(r'C:\stanford-corenlp-full-2018-01-31', memory='8g')
props = {'annotators': 'dcoref', 'pipelineLanguage': 'en', 'outputFormat': 'json'}
output = [nlp.annotate(sent, properties=props) for sent in sentences]
print("------------------")
print(output)



# ---------- rachel

#ie_categorizing
def categorizing(sentence):
    #checks if entry has "orsen"
      if 'orsen' not in sentence:
        story.append(sentence)
      else:
        commands.append(sentence)

# ie_semantic_role_label
def semanticRoleLabel(sentence):
    print("SRL PLACE")
    # TO DO: check with database if it has relationship



#setting_detail_extraction
def settingExtract(sentences):
    for x in range(0, len(sentences)):
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


        count = len(label)+1
        named_entity(c)
        if label[count] is not None:
            setting_detail.append(label[count])
        # TO DO: check with SRL for nouns

        #return object
        setting.append(c)

#ie_event_detail_extract
def eventExtract(sentences):
    event = []
    #TO DO: use dependency parsing to identify position of the event
    return event