from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.clock import Clock
import json
import random
from utils.resourcesPath import resource_path
from core.tiles import Object as Obj, Grid as Grd
from core.entity.ent_factory import create_ent
from screens.shared import size


class Grid(Grd):
    def __init__(self, source, **kwargs):
        super().__init__(global_size=size, source=source, **kwargs)


class Object(Obj):
    def __init__(self, source, **kwargs):
        super().__init__(global_size=size, source=source, **kwargs)


class Map:
    def __init__(self, world):
        self.letreiro = None
        self.world = world

        self.respawn_map = "inicial"
        self.current_map = ""
        self.background = ""
        self.spawn_pos = None

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

        self.procedural_ent_spawn = False
        self.ent_spawnable = []
        self.max_procedural_ents = 0
        self.spawned_ent = 0
        self.procedural_spawnable_area = 0.2

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

    def add_npc(self,ent_name,pos):
        npc = create_ent(ent_name)
        npc.global_pos=pos
        self.world.map_layout.add_widget(npc)
        self.world.ents.append(npc)
    
    def spawn_ent(self,*args):
        if len(self.world.ents)<self.max_procedural_ents:
            self.spawned_ent=len(self.world.ents)
        if not self.ent_spawnable or not self.procedural_ent_spawn:
            return
        if self.spawned_ent >= self.max_procedural_ents:
            return
        if not self.world.width>Window.width*(1+2*self.procedural_spawnable_area) and \
        not self.world.height>Window.height*(1+2*self.procedural_spawnable_area):
            return
        ent_name = random.choice(self.ent_spawnable)
        ent = create_ent(ent_name)
        if not ent:
            return
        visible_x = self.world.scroll_view.scroll_x * self.world.width
        visible_y = self.world.scroll_view.scroll_y * self.world.height
        visible_size_x = visible_x + Window.width
        visible_size_y = visible_y + Window.height

        margin_x = self.procedural_spawnable_area * Window.width
        margin_y = self.procedural_spawnable_area * Window.height

        spawn_area = [
            int(max(0, int(visible_x - margin_x))),
            int(max(0, int(visible_y - margin_y))),
            int(min(self.world.width, int(visible_size_x + margin_x))),
            int(min(self.world.height, int(visible_size_y + margin_y)))
        ]
        if spawn_area[0] >= spawn_area[2] or spawn_area[1] >= spawn_area[3]:
            return
        

        point=[
            random.randint(spawn_area[0],spawn_area[2]),
            random.randint(spawn_area[1],spawn_area[3])
        ]

        if (point[0]<visible_x or point[0]>visible_size_x) and (point[1]<visible_y or point[1]>visible_size_y):
            self.spawned_ent+=1
            ent.pos=point
            self.world.map_layout.add_widget(ent)
            self.world.ents.append(ent)

    def letreiro_msg(self, msg, duration=2):
        if self.letreiro:
            return
        self.letreiro = Label(
            text=msg,
            font_size=60,
            bold=True,
            color=(0.15, 0.4, 0.15, 1),
        )
        self.world.map_layout.add_widget(self.letreiro)
        Clock.schedule_once(self.remover_letreiro, duration)
    
    def remover_letreiro(self, *args):
        if self.letreiro:
            self.world.map_layout.remove_widget(self.letreiro)
            self.letreiro = None

    def show_dungeon_level(self, level):
        self.letreiro_msg(f"Nível {level}", duration=3)
        self.letreiro.pos_hint = {"center_x": 0.5, "center_y": 0.8}

    def limpar_mapa(self):
        for obj in self.obj_list[:]:
            self.world.map_layout.remove_widget(obj)
        for tile in self.tiles_list[:]:
            self.world.map_layout.remove_widget(tile)
        for ent in self.world.ents[:]:
            self.world.map_layout.remove_widget(ent)

        self.tiles_list.clear()
        self.obj_list.clear()
        self.world.ents=[self.world.player]


    def create(self, xm, ym, type=None):
        type = type or "esgoto"
        self.type = type
        if type == "esgoto":
            self.current_map = self.masmorra.get(self.nivel, None)

        combate_nivel = 1
        if self.mapa_modificador == "combate":
            combate_nivel = 2.5
        elif self.mapa_modificador == "coleta":
            combate_nivel = 1

        if type == "esgoto":
            if self.nivel <= 0:
                self.nivel = 1

            if self.nivel not in self.masmorra:
                self.masmorra[self.nivel] = {}

            if self.nivel > 0:
                self.subida_dungeon = self.descida_dungeon

            y = random.randint(0, xm - 1)
            x = random.randint(0, ym - 1)
            self.descida_dungeon = (x, y)

            if self.descida_dungeon == self.subida_dungeon:
                y = random.randint(0, xm - 1)
                x = random.randint(0, ym - 1)
                self.descida_dungeon = (x, y)

            if self.nivel == 10:
                combate_nivel = 7

        if type is None:
            self.nivel = 0

        grid_padrao = self.padrao["grid"][type]
        objeto_padrao = self.padrao["obj"][type]
        spawner_padrao = self.padrao["spawner"][type]

        self.linhas = xm
        self.colunas = ym

        self.world.size = (size * xm, size * ym * 0.8)

        self.world.pos = (0, 0)
        self.offset_x = 0
        self.offset_y = 0

        self.world.limites = (
            self.world.x,
            self.world.y,
            self.world.x + self.world.width,
            self.world.y + self.world.height
        )

        self.limpar_mapa()
        for y in range(self.linhas):
            for x in range(self.colunas):
                grid = Grid(
                    posicao=(x, y),
                    patern_center=(self.offset_x, self.offset_y),
                    max=(self.linhas, self.colunas),
                    source=grid_padrao
                )
                self.tiles_list.append(grid)
                self.world.map_layout.add_widget(grid)

        if self.world.player:
            self.world.player.pos = (self.offset_x, self.offset_y)

        self.ents = [self.world.player] if self.world.player else []
        self.world.ents = self.ents

        for y in range(self.linhas):
            for x in range(self.colunas):

                if self.descida_dungeon == (x, y):
                    obj = Object(
                        posicao=(x, y),
                        patern_center=(self.offset_x, self.offset_y),
                        max=(self.linhas, self.colunas),
                        source="descer_esgoto.png"
                    )
                    self.obj_list.append(obj)
                    self.world.map_layout.add_widget(obj)
                    continue

                if self.subida_dungeon == (x, y):
                    obj = Object(
                        posicao=(x, y),
                        patern_center=(self.offset_x, self.offset_y),
                        max=(self.linhas, self.colunas),
                        source="subir_esgoto.png"
                    )
                    self.obj_list.append(obj)
                    self.world.map_layout.add_widget(obj)
                    continue

                r = random.randint(0, 10)
                if r == 0:
                    if not ((x in (0, 1)) and (y in (0, 1))):
                        m = random.randint(0, 100)

                        if m < (10 + self.nivel) * combate_nivel:
                            obj = Object(
                                posicao=(x, y),
                                patern_center=(self.offset_x, self.offset_y),
                                max=(self.linhas, self.colunas),
                                source=spawner_padrao
                            )
                        else:
                            obj = Object(
                                posicao=(x, y),
                                patern_center=(self.offset_x, self.offset_y),
                                max=(self.linhas, self.colunas),
                                source=objeto_padrao
                            )

                        self.obj_list.append(obj)
                        self.world.map_layout.add_widget(obj)

        self.masmorra[self.nivel] = {
            "tiles": [(t.linha, t.coluna, t.type) for t in self.tiles_list],
            "objs": [(o.linha, o.coluna, o.type, o.resistencia, True) for o in self.obj_list]
        }

        try:
            if self.world.player:
                self.world.map_layout.remove_widget(self.world.player)
        except Exception:
            pass

        if self.world.player:
            self.world.map_layout.add_widget(self.world.player)

        if self.nivel == 10 and hasattr(self.world, "gerar_boss"):
            self.world.gerar_boss()
        
        if self.type == "esgoto":
            self.show_dungeon_level(self.nivel)
        self.world.trocando_mapa = False


    def re_map(self, type=None, nivel=1):
        self.limpar_mapa()
        if type == self.type:
            self.nivel += nivel
        if self.type == "esgoto" and self.nivel>10:
            self.type=None
            self.nivel=0
            self.load_mapa("inicial", entrada=2)
        if self.nivel in self.masmorra:
            self.carregar_mapa(self.masmorra[self.nivel])
        else:
            if type == "esgoto":
                self.type=type
                self.world.create(colunas=25, linhas=25, tipo=type)


    def load_mapa(self, mapa, respawn=False, entrada=0):
        if not "content/maps/" in mapa:
            mapa = "content/maps/" + mapa
        if not ".json" in mapa:
            mapa = mapa + ".json"
        with open(resource_path(mapa), "r") as file:
            data = json.load(file)
        
        self.procedural_ent_spawn=False
        self.max_procedural_ents=0
        self.ent_spawnable=[]
        if "spawn" in data:
            self.max_procedural_ents = data["spawn"].get("max", 0)
            self.ent_spawnable = data["spawn"].get("enemies", [])
            if self.ent_spawnable and self.max_procedural_ents:
                self.procedural_ent_spawn=True
            
        ponto_entrada=[]
        if "entrada" in data and entrada:
            ponto_entrada = data.get("entrada", {}).get(str(entrada), [])
            self.world.player.pos=[ponto_entrada[0]*size,ponto_entrada[1]*size*0.8]
            

        self.linhas = data["linhas"]
        self.colunas = data["colunas"]
        background_ok=False
        if "background" in data:
            if data["background"]:
                self.background = data["background"]
                background_ok=True

        if respawn:
            self.offset_x = data.get("respawn", {}).get("x", 0)
            self.offset_y = data.get("respawn", {}).get("y", 0)
            self.spawn_pos = (self.offset_x*size-size*0.5, self.offset_y*size*0.8)
        if background_ok:
            self.world.size = (size * self.colunas, (size * self.linhas * 0.8))
            self.world.background = Image(
                    source=resource_path("assets/tiles/background/" + self.background), 
                    size_hint = (None, None),
                    size=(self.world.width+size,75), 
                    pos=(0, self.world.height - 75),
                    allow_stretch=True,
                    keep_ratio=False
            )
            self.world.map_layout.add_widget(self.world.background)
        else:
            self.world.size = (size * self.colunas, size * self.linhas * 0.8)
        self.world.pos = (0, 0)
        self.offset_x = 0
        self.offset_y = 0
        self.world.limites = (self.world.x, self.world.y,
            self.world.x + self.world.width,
            self.world.y + self.world.height)

        self.carregar_mapa(data,entrada=ponto_entrada)
        self.current_map = mapa
        if "respawn" in data:
            self.respawn_map = mapa
            if ".json" in self.respawn_map:
                self.respawn_map = self.respawn_map.replace(".json", "")
            if "core/maps/" in self.respawn_map:
                self.respawn_map = self.respawn_map.replace("core/maps/", "")
        self.world.trocando_mapa = False

    
    def carregar_mapa(self, sala, entrada=[]):
        if not sala:
            return
        self.limpar_mapa()

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
            self.world.map_layout.add_widget(tile)

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
            self.world.map_layout.add_widget(obj)

        for coluna, linha, tipo, resistencia, ativado, extra_func, extra_arg1, extra_arg2 in sala.get("colliders", []):
            obj = Object(
                posicao=(coluna, linha),
                patern_center=(offset_x, offset_y),
                max=(self.linhas, self.colunas),
                source=tipo,
                ativado=ativado,
                extra_func=extra_func,
                extra_arg1=extra_arg1,
                extra_arg2=extra_arg2
            )
            obj.resistencia = resistencia
            self.obj_list.append(obj)
            self.world.map_layout.add_widget(obj)

        try:
            if getattr(self.world, "player", None):
                self.world.map_layout.remove_widget(self.world.player)
        except Exception:
            pass

        if getattr(self.world, "player", None):
            self.world.map_layout.add_widget(self.world.player)

            if entrada and len(entrada) >= 2:
                px = entrada[0] * size
                py = entrada[1] * size * 0.8

                Clock.schedule_once(
                    lambda dt: setattr(self.world.player, "pos", (px, py)), 0
    )
            else:
                self.world.player.pos = (offset_x, offset_y)

        if self.type == "esgoto":
            self.show_dungeon_level(self.nivel)
        self.world.trocando_mapa = False

