from core.view.entity_view import EntityView
from utils.resourcesPath import resource_path

class RatoView(EntityView):
    def __init__(self, logic, **kwargs):
        super().__init__(logic, **kwargs)

        self.sources = {
            "idle": resource_path("assets/sprites/rato/idle.png"),
            "running": resource_path("assets/sprites/rato/running.png"),
            "morto": resource_path("assets/sprites/rato/morto.png"),
            "atacando": resource_path("assets/sprites/rato/garras.png"),
        }

        self.source = self.sources["idle"]
        self.size = (32 * 2.8, 32 * 2.8)

    def sync(self):
        super().sync()

        estado = self.logic.estado
        self.source = self.sources.get(estado, self.sources["idle"])
