from numpy import random
from src.objects.ServerInstance import ServerInstance
from src.inputprocessor.infoextraction import getCategory,CAT_STORY,CAT_COMMAND,CAT_ANSWER
from pattern.text.en import conjugate
from src.db.dialoguemanager import DBO_Move
from src.objects.storyworld.World import World

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
        output = generate_response(choice)

    else:
        output = "I don't know what to say."

    return output


def generate_response(move_code):
    response = ""
    choices = []

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

    index = random.randint(0, len(choices))
    move = choices[index]

    for i in move.blank_index:
        # fill in blanks
        print("BLANKS TO BE FILLED")

    response = move.to_string()

    return response