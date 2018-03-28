from numpy import random
from src.objects.ServerInstance import ServerInstance
from src.inputprocessor.infoextraction import getCategory,CAT_STORY,CAT_COMMAND,CAT_ANSWER
from src.dialoguemanager import DBO_Move
from src.db.concepts import DBO_Concept
from pattern.text.en import conjugate

from src.objects.storyworld.Character import Character
from src.objects.storyworld.Object import Object
from src.objects.storyworld.World import World
from operator import  itemgetter
import time

MOVE_FEEDBACK = 1
MOVE_GENERAL_PUMP = 2
MOVE_SPECIFIC_PUMP = 3
MOVE_HINT = 4
MOVE_REQUESTION = 5

CONVERT_INFINITIVE = "inf"
CONVERT_1PRSG = "1sg"
CONVERT_2PRSG = "2sg"
CONVERT_3PRSG = "3sg"
CONVERT_PRPL = "pl"
CONVERT_PRPART = "part"

CONVERT_PAST = "p"
CONVERT_1PASG = "1sgp"
CONVERT_2PASG = "2sgp"
CONVERT_3PASG = "3sgp"
CONVERT_PAPL = "ppl"
CONVERT_PAPART = "ppart"

server = ServerInstance()

def retrieve_output(coreferenced_text, world_id):
    world = server.worlds[world_id]
    output = ""

    if coreferenced_text == "":  # if no input found
        world.empty_response += 1
        output = "I'm sorry, I did not understand what you just said. Can you say it again?"

        if world.empty_response == 2 :
            print("2nd no response")
            choice = random.randint(MOVE_GENERAL_PUMP, MOVE_HINT+1)
            output = generate_response(choice)

        elif world.empty_response == 3 :
            print("3rd no response")
            output = "I don't understand, maybe we can try again later?"

    elif getCategory(coreferenced_text) == CAT_STORY:
        print("check_story")
        choice = random.randint(MOVE_FEEDBACK, MOVE_HINT+1)
        output = generate_response(choice)

    elif getCategory(coreferenced_text) == CAT_ANSWER:
        print("check_answer")
        # TEMP
        choice = random.randint(MOVE_FEEDBACK, MOVE_HINT+1)
        output = generate_response(choice)

    elif getCategory(coreferenced_text) == CAT_COMMAND:
        print("check_command")
        # TEMP
        choice = random.randint(MOVE_FEEDBACK, MOVE_HINT+1)
        output = generate_response(choice, world)

    else:
        output = "I don't know what to say."

    return output


def generate_response(move_code, world):
    response = ""
    choices = []

    subject = None

    if move_code == MOVE_FEEDBACK:
        choices = DBO_Move.get_templates_of_type(DBO_Move.TYPE_FEEDBACK)

    elif move_code == MOVE_GENERAL_PUMP:
        choices = DBO_Move.get_templates_of_type(DBO_Move.TYPE_GENERAL_PUMP)

    elif move_code == MOVE_SPECIFIC_PUMP:
        choices = DBO_Move.get_templates_of_type(DBO_Move.TYPE_SPECIFIC_PUMP)

    elif move_code == MOVE_HINT:
        choices = DBO_Move.get_templates_of_type(DBO_Move.TYPE_HINT)

    elif move_code == MOVE_REQUESTION:
        choices = ["requestioning..."]

    choices = []
    choices.append(DBO_Move.get_specific_template(21))
    print(str(choices[0]))
    index = random.randint(0, len(choices))
    move = choices[index]

    for blank_type in move.blanks:

        if ":" in blank_type:
            split_relation = str(blank_type).split(":")
            relation_index = -1

            for i in range(0, len(split_relation)):
                if split_relation[i] in DBO_Concept.RELATIONS:
                    relation_index = i

            usable_concepts = []
            to_replace = ""

            if relation_index == 0:
                usable_concepts = DBO_Concept.get_concept_like(split_relation[relation_index], second=split_relation[1])
                to_replace=split_relation[1]
            elif relation_index == 1:
                usable_concepts = DBO_Concept.get_concept_like(split_relation[relation_index], first=split_relation[0])
                to_replace=split_relation[0]
            else:
                print("ERROR: Index not found.")

            print(relation_index)
            if len(usable_concepts) > 0 :
                concept_string = ""
                concept_index = random.randint(0,len(usable_concepts))

                if relation_index == 0:
                    concept_string = usable_concepts[concept_index].first
                elif relation_index == 1:
                    concept_string = usable_concepts[concept_index].second

                move.template[move.template.index(to_replace)] = concept_string

        elif blank_type in DBO_Concept.RELATIONS:

            # CHOOSE THE CONCEPT
            decided_concept = ""
            decided_node = -1

            charas = world.get_top_characters()
            objects = world.get_top_objects()
            list_choices = charas + objects
            loop_total = 0

            while True and subject is None:

                loop_total += 1
                choice_index = random.randint(0, len(choices))
                decided_item = list_choices[choice_index]

                if isinstance(decided_item, Object):
                    decided_concept = decided_item.name
                    subject = decided_item
                    decided_node = 0

                elif isinstance(decided_item, Character):
                    # get... something... relationship??
                    # TODO: use relationship or something to get a concept
                    print("check relationship")

                if decided_node != -1 or loop_total > 10:
                    break

            # find
            if decided_node == 0:
                usable_concepts = DBO_Concept.get_concept_like(blank_type, first=decided_concept)
            elif decided_node == 1:
                usable_concepts = DBO_Concept.get_concept_like(blank_type, second=decided_concept)
            else:
                usable_concepts = DBO_Concept.get_concept_like(blank_type)

            if len(usable_concepts) > 0:
                concept_index = random.randint(0,len(usable_concepts))
                concept = usable_concepts[concept_index]
                move.template[move.template.index("start")] = concept.first
                move.template[move.template.index("end")] = concept.second

        elif blank_type == "Object":

            if subject is None:
                charas = world.get_top_characters()
                objects = world.get_top_objects()
                list_choices = charas + objects

                choice_index = random.randint(0, len(choices))
                subject = list_choices[choice_index]

            move.template[move.template.index("object")] = subject.id

        elif blank_type == "Character":
            if subject is None or not isinstance(subject, Character):
                charas = world.get_top_characters(5)

                choice_index = random.randint(0, len(charas))
                subject = charas[choice_index]
            else:
                chara = subject

            move.template[move.template.index("character")] = subject.id


        elif blank_type == "Event":
            print("replace event")

    response = move.to_string()

    return response

start_time = time.time()


world = World()

world.characters["KAT"] = Character("KAT", "KAT", times=3)
world.characters["DAVE"] = Character("DAVE", "DAVE", times=5)
world.characters["JADE"] = Character("JADE", "JADE", times=0)
world.characters["ROSE"] = Character("ROSE", "ROSE", times=0)

world.objects["O1"] = Object("O1", "O1", times=3)
world.objects["O2"] = Object("O2", "O2", times=5)
world.objects["O3"] = Object("O3", "O3", times=0)

o = world.objects.values()
c = world.characters.values()

print(list(o))
print(c)
print(list(o)+list(c))

print(world.get_main_character())
print("--- %s seconds ---" % (time.time() - start_time))
