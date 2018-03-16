from .storyworld.World import World


class ServerInstance:

    instance = None
    worlds = {}

    def new_world(self, new_id):
        if self.worlds.get(new_id) is None:
            self.worlds[new_id] = World(new_id)
            return True
        else:
            return False

    def add_world(self, world):
        if self.worlds.get(world.id) is None:
            self.worlds[world.id] = world
            return True
        else:
            return False

