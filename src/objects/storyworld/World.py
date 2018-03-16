
class World:

    id = -1
    characters = {}
    objects = {}
    relationships = {}
    settings = {}
    event_chain = []

    def __init__(self, id=-1):
        self.id = id

    def add_character(self, char):
        if self.objects[char.id] is None and self.characters[char.id] is None:
            self.characters[char.id] = char
            return True
        elif self.objects[char.id] is not None and self.characters[char.id] is None:
            self.objects.pop(char.id)
            self.characters[char.id] = char
        else:
            return False

    def add_object(self, obj):
        if self.objects[obj.id] is None:
            self.objects[obj.id] = obj
            return True
        else:
            return False

    def add_relationship(self, relationship):
        if self.relationships[relationship.id] is None:
            self.relationships[relationship.id] = relationship
            return True
        else:
            return False

    def add_setting(self, setting):
        if self.settings[setting.id] is None:
            self.settings[setting.id] = setting
            return True
        else:
            return False
