FRAME_EVENT = 0
FRAME_DESCRIPTIVE = 1
FRAME_CREATION = 2


class EventFrame:

    event_type = -1
    # descriptive, action, etc.

    def __init__(self, seq_no=-1, type="", event_type=-1):
        self.sequence_no        = seq_no
        self.type               = type
        self.event_type         = event_type

        self.subject = []
        if event_type == FRAME_EVENT:
            self.action = ""
            self.direct_object = []
            self.preposition = ""
            self.obj_of_preposition = None
        elif event_type == FRAME_DESCRIPTIVE or event_type == FRAME_CREATION:
            self.attributes = []

    def __str__(self):
        return self.__str__()

    def to_sentence_string(self):
        string = "<event sentence>"
        return string
