class Concept():

    RELATION_ISA = "isA"
    RELATION_PARTOF = "PartOf"
    RELATION_LOCATION = "AtLocation"

    id = -1
    relation = ""
    first = ""
    second = ""

    def __init__(self, id, first, rel, second):
        self.id         = id
        self.relation   = rel
        self.first      = first
        self.second     = second


    def __str__(self):
        return self.first +" "+ self.relation +" "+ self.second