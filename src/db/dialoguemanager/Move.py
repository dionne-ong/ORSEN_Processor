class Move:

    def __init__(self, move_id=-1, response_type="", template=[], blanks=[], blank_index=[]):
        self.type = type
        self.template = template
        self.blanks = blanks
        self.response_type = response_type
        self.blank_index = blank_index

    def fill_blank(self, fill):
        for i in range(0, len(fill)):
            self.template[self.blank_index[i]] = fill[i]

    def to_string(self):
        string = ""

        for s in self.template:
            string += str(s)

        return string

    def __str__(self):
        return "MOVE:" + self.response_type +"\n"+ str(self.template) + "\n" + str(self.blanks) + "\n" + str(self.blank_index)