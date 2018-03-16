class Sentence:
    words = ""
    text_token = []
    lemma = []
    pos = []
    tag = []
    dep = []
    children = []


    text_ent = []
    label = []

    text_chunk = []
    dep_root = []
    dep_root_head = []

    characters_attributes = {}
    objects_attributes = {}

    def __init__(self):
        self.words = ""
        self.text_token = []
        self.lemma = []
        self.pos = []
        self.tag = []
        self.dep = []
        self.children = []

        self.text_ent = []
        self.label = []

        self.text_chunk = []
        self.dep_root = []
        self.dep_root_head = []

        self.characters_attributes = {}
        self.objects_attributes = {}