
class World:

    id = -1
    characters = {}
    objects = {}
    relationships = {}
    settings = {}

    def __init__(self, id):
        self.id = id

    def add_character(self, char):
        print(self.objects)
        print(self.characters)
        if self.objects[char.name] is None and self.characters[char.name] is None:
            self.characters[char.name] = char
            return True
        elif self.objects[char.name] is not None and self.characters[char.name] is None:
            self.objects.pop(char.name)
            self.characters[char.name] = char
        else:
            return False

    def add_object(self, obj):
        if self.objects[obj.name] is None:
            self.objects[obj.name] = obj
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