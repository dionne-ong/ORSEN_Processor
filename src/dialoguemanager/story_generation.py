import inflect
from src.objects.eventchain.EventFrame import FRAME_DESCRIPTIVE, FRAME_EVENT, FRAME_CREATION
inflect_engine = inflect.engine()


def generate_story(world):
    final_story = ""
    for event in world.event_chain:
        final_story += to_sentence_string(event) + " "
    return final_story


def to_sentence_string(event):
    string = ""
    subject_names = []
    for item in event.subject:
        subject_names.append(item.id)
    subject_string = inflect_engine.join(tuple(subject_names))

    verb_string = ""
    if len(event.subject) > 1 or (inflect_engine.singular_noun(event.subject[0].id) is True):
        verb_string += " were "
    else:
        verb_string += " was "

    if event.event_type == FRAME_EVENT:
        string = subject_string + " " + str(event.action) + " "

        do_names = []
        for item in event.direct_item:
            do_names.append(item.id)
        string += inflect_engine.join(tuple(do_names))

        if event.preposition != "" :
            string += " "+ str(event.preposition) + " " + str(event.obj_of_preposition.id)

    else:
        attr_string = inflect_engine.join(tuple(event.attributes))

        if event.event_type == FRAME_DESCRIPTIVE:
            string = subject_string + verb_string + attr_string
        elif event.event_type == FRAME_CREATION:
            article = ""
            if inflect_engine.singular_noun(event.subject[0].id) is False:
                article = inflect_engine.a(event.subject[0].id)
            string = "There" + verb_string + article.split()[0] +" "+ attr_string + " " + subject_string

    string += "."
    return string
