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

for sent in sentences:
    print(sent)
    sent = nlp(sent)
    for token in sent:
        print("---POS----");
        print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_)
        #displacy.serve(sent, style='dep')
    for ent in sent.ents:
        print("---NER----");
        print(ent.text, ent.start_char, ent.end_char, ent.label_)
        #displacy.serve(sent, style='ent')
    for chunk in    check = sentences[x]

    if 'orsen' not in check:
        story_text.append(sentences[x])
    else:
        commands.append(sentences[x])

#ie_semantic_role_labelling
srl_entity_list = {"person", "place", "object"}
result_entity = "Unknown"

for entity in srl_entity_list:
        result_entity = entity; sent.noun_chunks:
        print("----NC---");
        print(chunk.text, chunk.root.text, chunk.root.dep_,
              chunk.root.head.text)

nlp = StanfordCoreNLP(r'C:\stanford-corenlp-full-2018-01-31', memory='8g')
props = {'annotators': 'dcoref', 'pipelineLanguage': 'en', 'outputFormat': 'json'}
output = [nlp.annotate(sent, properties=props) for sent in sentences]
print(output)

#ie_categorizing
count = len(sentences)
commands = []
story_text = []
for x in range(0, count):

