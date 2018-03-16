class Object:

    id = -1
    name = ""
    type = ""
    inSetting = 0
    timesMentioned = 0
    attributes = None

    def __init__(self, id, name, type, inSetting, times, attr):
        self.id   = id
        self.name       = name
        self.type       = type
        self.inSetting  = inSetting
        self.timesMentioned = times
        self.attributes = attr

    def __str__(self):
        return "OBJECT #%d: \nName: %s \nType: %s \ninSetting: %s \nmentioned: %d\n" \
               % (self.id, self.name, self.type, self.inSetting, self.timesMentioned)\
               + "attributes: " + str(self.attributes)
