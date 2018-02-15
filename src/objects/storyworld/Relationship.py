class Relationship:

    id = -1
    idObjectA = -1
    idObjectB = -1
    relation = ""
    score = 0

    def __init__(self, id, idObjA, idObjB, relName, score):
        self.id = id
        self.idObjectA = idObjA
        self.idObjectB = idObjB
        self.relation = relName
        self.score = score

    def __str__(self):
        return "Relationship #%d: \nObjectA: %d \nObjectB: %d \nrelation: %s \nscore: %d"\
               % (self.id, self.idObjectA, self.idObjectB, self.relation, self.score)
