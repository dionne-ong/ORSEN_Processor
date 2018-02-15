from .Object import Object

class Character(Object):

    gender = ""
    desire = ""
    feeling = ""

    def __init__(self, idChar, name, typeChar, inSetting, times, attr, gender, desire, feeling):
        super().__init__(idChar, name, typeChar, inSetting, times, attr)
        self.gender = gender
        self.desire = desire
        self.feeling = feeling

    def __str__(self):
        return "CHARACTER #%d: \nName: %s \nGender: %s \ndesire: %s \nType: %s \ninSetting: %s \nmentioned: %d \nfeeling: %s\n" \
               % (self.idObjects, self.name, self.gender, self.desire, self.type, self.inSetting, self.timesMentioned, self.feeling)\
               + "attributes: " + str(self.attributes)