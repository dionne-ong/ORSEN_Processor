import spacy
from stanfordcorenlp import StanfordCoreNLP
from src.objects.ServerInstance import ServerInstance
from src.objects.storyworld.World import World
from src.objects.storyworld.Character import Character
from src.objects.storyworld.Object import Object
from src.inputprocessor import infoextraction

server = ServerInstance()
worldid = "0"
world = World(worldid)
server.add_world(world)

#Loading of text and segmentation of sentences
nlp = spacy.load('en')
document = nlp(infoextraction.reading("document.txt"))
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

#Character
characters = []

#Counter for loops
counter = 0

#Part-Of-Speech, NER, Dependency Parsing
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

    infoextraction.part_of_speech(sent, text_token, lemma, pos, tag, dep, counter)
    infoextraction.named_entity(sent, text_ent, label, counter)
    infoextraction.noun_chunks(sent, text_chunk, dep_root, dep_root_head, counter)
    counter += 1

#CharacterExtraction
characters_attributes, object_attributes = infoextraction.character_attribute_extraction(text_chunk, lemma, dep,
                                                                                         text_token)

print("AAAAA")
for key, values in characters_attributes.items():
    new_character = Character()
    new_character.name = key
    print("CHAR", key)
    if values is not None:
        for value in values:
            print("CHAR ATTR" , value)
            new_character.attributes.append(value)
    world.add_character(new_character)

for key, values in object_attributes.items():
    new_obj = Object()
    new_obj.name = key
    print("OBJ", key)
    if values is not None:
        for value in values:
            print("OBJ ATTR", value)
            new_obj.attributes.append(value)
    world.add_object(new_obj)

#nlp = StanfordCoreNLP(r'C:\stanford-corenlp-full-2018-01-31', memory='8g')
#props = {'annotators': 'dcoref', 'pipelineLanguage': 'en', 'outputFormat': 'json'}
#output = [nlp.annotate(sent, properties=props) for sent in sentences]
#print("------------------")
#print(output)

#For Categorizing


#For Semantic Role Labeling
sem_role = []

#For Setting Detail Extraction
setting_name = []
setting_type= []
setting_frame = [setting_name, setting_type]

#For Event Extraction
seq_no = []
event_type = []
doer = []
doer_act = []
rec = []
rec_act = []
location = []
event_frame = [seq_no, event_type, doer, doer_act, rec, rec_act, location]


