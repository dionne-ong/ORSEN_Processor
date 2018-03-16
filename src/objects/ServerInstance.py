from .storyworld.World import World
class ServerInstance:

    instance = None
    worlds = []

    def get_instance(self):
        if self.instance == None:
            self.instance = ServerInstance()

        return self.instance

    def new_world(self, id):
        self.worlds.append(World(id))

    def add_world(self, world):
        self.worlds.append(world)

