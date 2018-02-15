from ..storyworld.Object    import Object
from ..storyworld.Setting   import Setting

class EventFrame:

    sequence_no         = -1
    type                = ""
    doer                = Object()
    doer_actions        = []
    receiver            = Object()
    receiver_actions    = []
    location            = Setting()

    def __init__(self, seq_no, type, doer, doer_actions, receiver, receiver_actions, location):
        self.sequence_no        = seq_no
        self.type               = type
        self.doer               = doer
        self.doer_actions       = doer_actions
        self.receiver           = receiver
        self.receiver_actions   = receiver_actions
        self.location           = location