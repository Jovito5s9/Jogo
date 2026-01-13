from .entity_view import EntityView
from utils.resourcesPath import resource_path

class PlayerView(EntityView):
    def __init__(self, logic, **kwargs):
        super().__init__(logic, **kwargs)

        self.source_idle = resource_path("assets/sprites/player/idle.png")
        self.source_run = resource_path("assets/sprites/player/running.png")
        self.source_dead = resource_path("assets/sprites/player/morto.png")

        self.source = self.source_idle

    def sync(self):
        super().sync()

        if not self.logic.vivo:
            self.source = self.source_dead
        elif self.logic.estado == "running":
            self.source = self.source_run
        else:
            self.source = self.source_idle
