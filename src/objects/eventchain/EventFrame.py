
FRAME_EVENT = 0
FRAME_DESCRIPTIVE = 1

class EventFrame:

    characters = {}
    character_actions = {}
    # character = a Character() object
    # character_actions is a dict of character names as key connected to an action verb
    #       ie. { "KAT" : "run" , "John" : "run" }

    objects = {}
    object_actions = {}
    # same except for objects

    setting = None

    event_type = -1
    # descriptive, action, etc.

    def to_sentence_string(self):
        string = "<event sentence>"
        return string
