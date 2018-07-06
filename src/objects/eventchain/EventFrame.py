
FRAME_EVENT = 0
FRAME_DESCRIPTIVE = 1
FRAME_CREATION = 2

class EventFrame:

    event_type = -1
    # descriptive, action, etc.

    def __init__(self, seq_no=-1, event_type=-1):
        self.sequence_no        = seq_no
        self.event_type         = event_type

        self.subject = []
        if event_type == FRAME_EVENT:
            self.action = ""
            self.direct_object = []
            self.preposition = ""
            self.obj_of_preposition = None
            self.adverb = []
        elif event_type == FRAME_DESCRIPTIVE:
            self.attributes = []
            self.preposition = ""
            self.obj_of_preposition = None
            self.adverb = []
        elif event_type == FRAME_CREATION:
            self.attributes = []

    def __str__(self):
        subject_string = "\tSubject = [ "
        for object in self.subject:
            subject_string += object.id + ","
        subject_string += " ]\n"

        string = "EVENT #" + self.sequence_no + " - "
        if self.event_type == FRAME_EVENT:
            string += "ACTION EVENT\n"
            string += subject_string
            string += "\tD.O. = [ "
            for object in self.direct_object:
                string += object.id + ","
            string += " ]\n"
            if self.preposition != "":
                string += "\tPREP = " + self.preposition + "\n"
            if self.obj_of_preposition is not None:
                string += "\tOBJ PREP = " + self.obj_of_preposition.id + "\n"

        elif self.event_type == FRAME_DESCRIPTIVE:
            string += "DESCRIPTIVE\n"
            string += subject_string
            string += "\tattributes = [ "
            for attr in self.attributes:
                string += attr + ","
            string += " ]\n"

        elif self.event_type == FRAME_CREATION:
            string += "CREATION\n"
            string += subject_string
            string += "\tattributes = [ "
            for attr in self.attributes:
                string += attr + ","
            string += " ]\n"

        else:
            string += "UNKNOWN"
        return self.__str__()
