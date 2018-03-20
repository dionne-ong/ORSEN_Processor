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
list_of_sentences = []

#Character
characters = []

#Part-Of-Speech, NER, Dependency Parsing
for sent in sentences:
    print(sent)
    sent = nlp(sent)
    list_of_sentences.append(infoextraction.pos_ner_nc_processing(sent))

#CharacterExtraction
infoextraction.character_attribute_extraction(list_of_sentences, world)


# print("AAAAA")
# for key, values in characters_attributes.items():
#     new_character = Character()
#     new_character.name = key
#     print("CHAR", key)
#     if values is not None:
#         for value in values:
#             print("CHAR ATTR" , value)
#             new_character.attributes.append(value)
#     world.add_character(new_character)
#
# for key, values in object_attributes.items():
#     new_obj = Object()
#     new_obj.name = key
#     print("OBJ", key)
#     if values is not None:
#         for value in values:
#             print("OBJ ATTR", value)
#             new_obj.attributes.append(value)
#     world.add_object(new_obj)

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


