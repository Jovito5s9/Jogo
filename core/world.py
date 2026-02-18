from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty
from kivy.core.window import Window
from kivy.clock import Clock 

import random
import json

from utils.resourcesPath import resource_path
from core.tiles import Object as Obj, Grid as Grd
from core.player import Rata_mae


size = Window.height/12.5


class Grid(Grd):
    def __init__(self, source, **kwargs):
        super().__init__(global_size=size, source=source, **kwargs)


class Object(Obj):
    def __init__(self, source, **kwargs):
        super().__init__(global_size=size, source=source, **kwargs)


class World(FloatLayout):
    colunas = NumericProperty(0)
    linhas = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.ev_colisao = None
        self.ev_sprite = None
        self.trocando_mapa = False
        self.player = None
        self.size = (Window.width, Window.height)
        self.limites = []
        self.ents = []
        self.obj_list = []
        self.tiles_list = []
        self.descida_dungeon = []
        self.subida_dungeon = []
        self.masmorra = {}
        self.boss = None

        # mais facil de editar o mapa 
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

        self.nivel = 0
        self.lista_modificadores = ["coleta", "combate"]
        self.mapa_modificador = "coleta"
        self.atualizar()

    def create(self, xm, ym, type=None):
        type = 'esgoto'
        self.type = type
        combate_nivel = 1
        if self.mapa_modificador == "combate":
            combate_nivel = 2.5
        elif self.mapa_modificador == "coleta":
            combate_nivel = 1
        if type == "esgoto":
            if self.nivel <= 0:
                self.nivel = 1
            if not self.nivel in self.masmorra:
                self.masmorra[self.nivel] = {}
            if self.nivel > 0:
                self.subida_dungeon = self.descida_dungeon 
            y = random.randint(0, xm - 1)
            x = random.randint(0, ym - 1)
            self.descida_dungeon = (x, y)
            if self.descida_dungeon == self.subida_dungeon :
                y = random.randint(0, xm - 1)
                x = random.randint(0, ym - 1)
                self.descida_dungeon = (x, y)
            if self.nivel == 10:
                combate_nivel = 7
        if type == None:
            self.nivel = 0
        
        grid_padrao = self.padrao["grid"][type]
        objeto_padrao = self.padrao["obj"][type]
        spawner_padrao = self.padrao["spawner"][type]
        self.linhas = xm
        self.colunas = ym

        self.size = (size * xm, size * ym * 0.8)

        # Posição inicial (superior esquerdo) para começar a desenhar centralizado
        self.offset_x = (Window.width / 2) - (self.width / 2)
        self.offset_y = (Window.height / 2) - (self.height / 2)
        self.pos = (self.offset_x, self.offset_y)
        self.limites = (self.x, self.y, self.x + self.width, self.y + self.height)

        for y in range(self.linhas):
            for x in range(self.colunas):
                grid = Grid(
                    posicao=(x, y),
                    patern_center=(self.offset_x, self.offset_y),
                    max=(self.linhas, self.colunas),
                    source=grid_padrao
                )
                self.add_widget(grid)
                self.tiles_list.append(grid)
        # coloca player na posição inicial do mapa (usa pos do world)
        if self.player:
            self.player.pos = (self.offset_x, self.offset_y)
        self.ents = [self.player] if self.player else []
        
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
                    self.add_widget(obj)
                    continue
                if self.subida_dungeon == (x, y):
                    obj = Object(
                        posicao=(x, y),
                        patern_center=(self.offset_x, self.offset_y),
                        max=(self.linhas, self.colunas),
                        source="subir_esgoto.png"
                    )
                    self.obj_list.append(obj)
                    self.add_widget(obj)
                    continue
                r = random.randint(0, 10)
                if r == 0:
                    if not ((x == 0 or x == 1) and (y == 0 or y == 1)):
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
                        self.add_widget(obj)
        self.masmorra[self.nivel] = {
            "tiles": [(t.coluna, t.linha, t.type) for t in self.tiles_list],
            "objs": [(o.coluna, o.linha, o.type, o.resistencia, True) for o in self.obj_list]
        }
        try:
            if self.player:
                self.remove_widget(self.player)
        except Exception as e:
            print(e)
        if self.player:
            self.add_widget(self.player)
        if self.nivel == 10:
            self.gerar_boss()


    def carregar_mapa(self, sala):
        if not sala:
            return

        for obj in self.obj_list[:]:
            try:
                self.remove_widget(obj)
            except Exception:
                pass
        for tile in self.tiles_list[:]:
            try:
                self.remove_widget(tile)
            except Exception:
                pass
        for ent in self.ents[:]:
            if ent is not self.player:
                try:
                    self.remove_widget(ent)
                except Exception:
                    pass

        self.tiles_list.clear()
        self.obj_list.clear()
        self.ents = [self.player] if self.player else []

        for coluna, linha, tipo in sala["tiles"]:
            tile = Grid(
                posicao=(coluna, linha),
                patern_center=(self.offset_x, self.offset_y),
                max=(self.linhas, self.colunas),
                source=tipo
            )
            self.tiles_list.append(tile)
            self.add_widget(tile)

        for coluna, linha, tipo, resistencia, ativado in sala["objs"]:
            obj = Object(
                posicao=(coluna, linha),
                patern_center=(self.offset_x, self.offset_y),
                max=(self.linhas, self.colunas),
                source=tipo,
                ativado=ativado
            )
            obj.resistencia = resistencia
            self.obj_list.append(obj)
            self.add_widget(obj)

        try:
            if self.player:
                self.remove_widget(self.player)
        except Exception as e:
            print(e)
        if self.player:
            self.add_widget(self.player)

        if self.player:
            self.player.pos = (self.offset_x, self.offset_y)
            if hasattr(self.player, "atualizar_pos"):
                try:
                    self.player.atualizar_pos()
                except Exception:
                    pass

    def re_map(self, type, nivel=1):
        if self.trocando_mapa:
            return
        self.trocando_mapa = True
        if type == self.type:
            self.nivel += nivel
        for obj in self.obj_list[:]:
            self.obj_list.remove(obj)
            try:
                self.remove_widget(obj)
            except Exception:
                pass
        for tile in self.tiles_list[:]:
            self.tiles_list.remove(tile)
            try:
                self.remove_widget(tile)
            except Exception:
                pass
        for ent in self.ents[:]:
            if ent is not self.player:
                self.ents.remove(ent)
                try:
                    self.remove_widget(ent)
                except Exception:
                    pass
        self.mapa_modificador = random.choice(self.lista_modificadores)
        if self.nivel < 0 or self.nivel > 10:
            self.type = None
            self.nivel = 0
        if self.nivel in self.masmorra:
            self.carregar_mapa(self.masmorra[self.nivel])
            self.trocando_mapa = False
            return
        else:
            self.create(self.linhas, self.colunas, type)
            self.trocando_mapa = False

    def load_mapa(self, mapa):
        mapa = "core/maps/" + mapa + ".json"

        with open(resource_path(mapa), "r") as file:
            data = json.load(file)

        self.linhas = data["linhas"]
        self.colunas = data["colunas"]

        self.size = (size * self.colunas, size * self.linhas * 0.8)
        self.offset_x = (Window.width / 2) - (self.width / 2)
        self.offset_y = (Window.height / 2) - (self.height / 2)
        self.pos = (self.offset_x, self.offset_y)
        self.limites = (self.x, self.y, self.x + self.width, self.y + self.height)

        self.carregar_mapa(data)

        try:
            if self.player:
                self.remove_widget(self.player)
        except Exception as e:
            print(e)
        if self.player:
            self.add_widget(self.player)
            self.player.pos = (self.offset_x, self.offset_y)
            if hasattr(self.player, "atualizar_pos"):
                try:
                    self.player.atualizar_pos()
                except Exception:
                    pass

    
    def collision_verify(self, *args):        
        for ent in list(self.ents):
            self.verificar_colisao_horizontal(ent) 
            self.verificar_colisao_vertical(ent)
            self.map_collision(ent)
            self.grid_verify(ent)
        
    def grid_verify(self, ent):
        tile_width = size
        tile_height = size * 0.8 
        # usa center da hitbox para determinar grid
        grid_x = int((ent.center_hitbox_x - self.x) / tile_width)
        grid_y = int((ent.center_hitbox_y - self.y) / tile_height)
        grid_x = max(0, min(self.colunas - 1, grid_x))
        grid_y = max(0, min(self.linhas - 1, grid_y))
        ent.grid = (grid_x, grid_y)
        if ent == self.player:
            pass


    def map_collision(self, ent):
        ent.hitbox = ent.get_hitbox()
        right_limit = self.x + self.width - (ent.width * 0.75)
        left_limit = self.x - (ent.width * 0.25)
        if ent.x > right_limit:
            ent.x = right_limit
        elif ent.x < left_limit:
            ent.x = left_limit
        # limites verticais
        bottom_limit = self.y
        top_limit = self.y + self.height - (ent.height / 2)
        if ent.y < bottom_limit:
            ent.y = bottom_limit
        elif ent.y > top_limit:
            ent.y = top_limit
        try:
            ent.pos = (ent.x, ent.y)
        except Exception:
            pass
            
    def verificar_colisao_horizontal(self, ent):
        original_x = ent.x
        ent.move_x()
        ent.hitbox = ent.get_hitbox()
    
        for obj in self.obj_list:
            if not hasattr(obj, "hitbox"):
                continue
            if self.collision(ent.hitbox, obj.hitbox):
                obj.colisao()
                if obj.colisivel:
                    # Reverte X e zera velocidade no eixo X
                    ent.x = original_x
                    ent.speed_x = 0
                    ent.hitbox = ent.get_hitbox()
                    if self.collision(ent.hitbox, obj.hitbox):
                        # segundo teste: posiciona ao lado do objeto
                        ent.x = obj.x + obj.width
                        ent.speed_x = 0
                        ent.hitbox = ent.get_hitbox()
        for entit in self.ents:
            if ent == entit:
                continue
            if self.collision(ent.hitbox, entit.hitbox):
                # Reverte X e aplica dano por contato quando aplicável
                if not ent.i_frames:
                    ent.vida -= entit.dano_contato
                if not entit.i_frames:
                    entit.vida -= ent.dano_contato
                ent.x = original_x
                ent.speed_x = 0
                ent.hitbox = ent.get_hitbox()


    def verificar_colisao_vertical(self, ent):
        original_y = ent.y
        ent.move_y()
        ent.hitbox = ent.get_hitbox()
    
        for obj in self.obj_list:
            if not hasattr(obj, "hitbox"):
                continue
            if self.collision(ent.hitbox, obj.hitbox):
                obj.colisao()
                if obj.colisivel:
                    ent.y = original_y
                    ent.speed_y = 0
                    ent.hitbox = ent.get_hitbox()
                    if self.collision(ent.hitbox, obj.hitbox):
                        ent.y = obj.y
                        ent.speed_y = 0
                        ent.hitbox = ent.get_hitbox()

        for entit in self.ents:
            if ent == entit:
                continue
            if self.collision(ent.hitbox, entit.hitbox):
                ent.y = original_y
                ent.speed_y = 0
                ent.hitbox = ent.get_hitbox()

    def atualizar_sprites(self, *args):
        for ent in self.ents:
            ent.atualizar_pos()
        
    
    def atualizar(self, *args):
        if self.ev_colisao:
            self.ev_colisao.cancel()
        if self.ev_sprite:
            self.ev_sprite.cancel()
        self.ev_colisao = Clock.schedule_interval(self.collision_verify, 1/60)
        self.ev_sprite = Clock.schedule_interval(self.atualizar_sprites, 1/30)
    
    def collision(self, hitbox1, hitbox2):
        x1, y1, w1, h1 = hitbox1
        x2, y2, w2, h2 = hitbox2
        return (
            x1 < x2 + w2 and
            x1 + w1 > x2 and
            y1 < y2 + h2 and
            y1 + h1 > y2
        )

    def respawn_player(self,*args):
        if self.type=='esgoto' and not self.trocando_mapa:
            self.trocando_mapa=True
            for obj in self.obj_list[:]:
                self.obj_list.remove(obj)
                try:
                    self.remove_widget(obj)
                except Exception:
                    pass
            for tile in self.tiles_list[:]:
                self.tiles_list.remove(tile)
                try:
                    self.remove_widget(tile)
                except Exception:
                    pass
            for ent in self.ents[:]:
                if ent is not self.player:
                    self.ents.remove(ent)
                    try:
                        self.remove_widget(ent)
                    except Exception:
                        pass
            self.carregar_mapa(self.masmorra[1])
            self.trocando_mapa=False

    def gerar_boss(self, *args):
        boss = Rata_mae()
        self.add_widget(boss)
        self.ents.append(boss)
        boss.pos = (self.offset_x + self.linhas * size * 0.5, self.offset_y + self.colunas * size * 0.5 * 0.8)
        self.boss = boss
        Clock.schedule_once(self.remover_spawners, 0.5)

    def remover_spawners(self, *args):
        for obj in self.obj_list[:]:
            if obj.type != self.padrao["spawner"][self.type]:
                continue
            try:
                self.remove_widget(obj)
                self.obj_list.remove(obj)
            except Exception:
                pass
