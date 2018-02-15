class Setting:
    id = -1
    name = ""
    type = ""
    time = 0

    def __init__(self, id, name, type, time):
        self.id   = id
        self.name = name
        self.type = type
        self.time = time

    def __str__(self):
        return "SETTING #%d: \nName: %s \nType: %s \nTime: %s" % (self.id, self.name, self.type, self.time)