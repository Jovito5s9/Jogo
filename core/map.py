from kivy.core.window import Window
import json
from utils.resourcesPath import resource_path
from core.tiles import Object as Obj, Grid as Grd

size = Window.height / 12.5


class Grid(Grd):
    def __init__(self, source, **kwargs):
        super().__init__(global_size=size, source=source, **kwargs)


class Object(Obj):
    def __init__(self, source, **kwargs):
        super().__init__(global_size=size, source=source, **kwargs)


class Map:
    def __init__(self, world):
        self.world = world

        self.linhas = 0
        self.colunas = 0
        self.tiles_list = []
        self.obj_list = []
        self.ents = []

        self.descida_dungeon = []
        self.subida_dungeon = []
        self.masmorra = {}
        self.type = None
        self.nivel = 0

        self.lista_modificadores = ["coleta", "combate"]
        self.mapa_modificador = "coleta"

        self.padrao = {
            "spawner": {
                'esgoto': "entrada_esgoto.png",
                None: "entrada_esgoto.png"
            },
            "obj": {
                'esgoto': "veneno.png",
                None: "pedra.png"
            },
            "grid": {
                'esgoto': "ladrilhos_esgoto.png",
                None: "terra.png"
            }
        }

    def limpar_mapa(self):
        for obj in self.obj_list[:]:
            self.world.remove_widget(obj)
        for tile in self.tiles_list[:]:
            self.world.remove_widget(tile)

        self.tiles_list.clear()
        self.obj_list.clear()

    def create(self, xm, ym, type=None):
        self.type = type or 'esgoto'

        self.linhas = xm
        self.colunas = ym

        self.world.size = (size * xm, size * ym * 0.8)

        offset_x = (Window.width / 2) - (self.world.width / 2)
        offset_y = (Window.height / 2) - (self.world.height / 2)

        self.world.pos = (offset_x, offset_y)

        grid_padrao = self.padrao["grid"][self.type]

        for y in range(self.linhas):
            for x in range(self.colunas):
                grid = Grid(
                    posicao=(x, y),
                    patern_center=(offset_x, offset_y),
                    max=(self.linhas, self.colunas),
                    source=grid_padrao
                )
                self.tiles_list.append(grid)
                self.world.add_widget(grid)

    def re_map(self, type, nivel=1):
        self.limpar_mapa()

        if type == self.type:
            self.nivel += nivel

        if self.nivel in self.masmorra:
            self.carregar_mapa(self.masmorra[self.nivel])
        else:
            self.create(self.linhas, self.colunas, type)

    def load_mapa(self, mapa):
        mapa = "core/maps/" + mapa + ".json"

        with open(resource_path(mapa), "r") as file:
            data = json.load(file)

        self.linhas = data["linhas"]
        self.colunas = data["colunas"]

        self.world.size = (size * self.colunas, size * self.linhas * 0.8)
        offset_x = (Window.width / 2) - (self.world.width / 2)
        offset_y = (Window.height / 2) - (self.world.height / 2)
        self.world.pos = (offset_x, offset_y)
        self.world.limites = (self.world.x, self.world.y,
                            self.world.x + self.world.width,
                            self.world.y + self.world.height)

        self.offset_x = offset_x
        self.offset_y = offset_y

        self.carregar_mapa(data)

    
    def carregar_mapa(self, sala):
        if not sala:
            return

        for obj in list(self.obj_list):
            try:
                self.world.remove_widget(obj)
            except Exception:
                pass
        for tile in list(self.tiles_list):
            try:
                self.world.remove_widget(tile)
            except Exception:
                pass
        for ent in list(self.ents):
            if ent is not getattr(self.world, "player", None):
                try:
                    self.world.remove_widget(ent)
                except Exception:
                    pass

        self.tiles_list.clear()
        self.obj_list.clear()
        self.ents = [self.world.player] if getattr(self.world, "player", None) else []

        offset_x = getattr(self, "offset_x", self.world.x)
        offset_y = getattr(self, "offset_y", self.world.y)
        self.offset_x = offset_x
        self.offset_y = offset_y

        for coluna, linha, tipo in sala.get("tiles", []):
            tile = Grid(
                posicao=(coluna, linha),
                patern_center=(offset_x, offset_y),
                max=(self.linhas, self.colunas),
                source=tipo
            )
            self.tiles_list.append(tile)
            self.world.add_widget(tile)

        for coluna, linha, tipo, resistencia, ativado in sala.get("objs", []):
            obj = Object(
                posicao=(coluna, linha),
                patern_center=(offset_x, offset_y),
                max=(self.linhas, self.colunas),
                source=tipo,
                ativado=ativado
            )
            obj.resistencia = resistencia
            self.obj_list.append(obj)
            self.world.add_widget(obj)

        try:
            if getattr(self.world, "player", None):
                self.world.remove_widget(self.world.player)
        except Exception:
            pass

        if getattr(self.world, "player", None):
            self.world.add_widget(self.world.player)
            self.world.player.pos = (offset_x, offset_y)
            if hasattr(self.world.player, "atualizar_pos"):
                try:
                    self.world.player.atualizar_pos()
                except Exception:
                    pass

