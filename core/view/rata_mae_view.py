from core.view.entity_view import EntityView
from utils.resourcesPath import resource_path

class RataMaeView(EntityView):
    def __init__(self, logic, **kwargs):
        super().__init__(logic, **kwargs)

        self.sources = {
            "idle": resource_path("assets/sprites/rata_mae/idle.png"),
            "atacando": resource_path("assets/sprites/rata_mae/rolling.png"),
            "morto": resource_path("assets/sprites/rata_mae/dead.png"),
        }

        self.source = self.sources["idle"]
        self.size = (96 * 3.5, 64 * 3.5)

    def sync(self):
        super().sync()
        self.source = self.sources.get(self.logic.estado, self.sources["idle"])
