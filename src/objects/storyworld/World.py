
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
        if char.id not in self.objects and char.id not in self.characters:
            self.characters[char.id] = char
            return True
        elif char.id in self.objects and char.id not in self.characters:
            self.objects.pop(char.id)
            self.characters[char.id] = char
            return True
        else:
            return False

    def add_object(self, obj):
        if obj.id not in self.objects:
            self.objects[obj.id] = obj
            return True
        else:
            return False

    def add_relationship(self, relationship):
        if relationship.id not in self.relationships:
            self.relationships[relationship.id] = relationship
            return True
        else:
            return False

    def add_setting(self, setting):
        if setting.id not in self.settings:
            self.settings[setting.id] = setting
            return True
        else:
            return False
