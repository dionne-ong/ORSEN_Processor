import spacy
from stanfordcorenlp import StanfordCoreNLP
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

counter = 0
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

    for token in sent:
        print("---POS----");
        print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_)
        text_token[counter].append(token.text)
        lemma[counter].append(token.lemma_)
        pos[counter].append(token.pos_)
        tag[counter].append(token.tag_)
        dep[counter].append(token.dep_)

    for ent in sent.ents:
        print("---NER----");
        print(ent.text, ent.start_char, ent.end_char, ent.label_)
        text_ent[counter].append(ent.text)
        label[counter].append(ent.label_)

    for chunk in sent.noun_chunks:
        print("----NC---");
        print(chunk.text, chunk.root.text, chunk.root.dep_,
              chunk.root.head.text)
        text_chunk[counter].append(chunk.text)
        dep_root[counter].append(chunk.root.dep_)
        dep_root_head[counter].append(chunk.root.head.text)

    counter += 1

nlp = StanfordCoreNLP(r'C:\stanford-corenlp-full-2018-01-31', memory='8g')
props = {'annotators': 'dcoref', 'pipelineLanguage': 'en', 'outputFormat': 'json'}
output = [nlp.annotate(sent, properties=props) for sent in sentences]
print("------------------")
print(output)


#ie_categorizing
count = len(sentences)
print("HAYYYYY")
commands = []
story_text = []
for x in range(0, count):
    check = sentences[x]

    if 'orsen' not in check:
        story_text.append(sentences[x])
    else:
        commands.append(sentences[x])

#ie_semantic_role_labelling
srl_entity_list = {"person", "place", "object"}
result_entity = "Unknown"

for entity in srl_entity_list:
        result_entity = entity;