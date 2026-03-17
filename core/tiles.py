from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.clock import Clock
from kivy.uix.widget import Widget

import random

from utils.resourcesPath import resource_path
from core.entity.ent_factory import create_ent

class Tile(FloatLayout):
    linha = NumericProperty(0)
    coluna = NumericProperty(0)
    posicao = ReferenceListProperty(linha, coluna)

    patern_x = NumericProperty(0)
    patern_y = NumericProperty(0)
    patern_center = ReferenceListProperty(patern_x, patern_y)

    linhas = NumericProperty(0)
    colunas = NumericProperty(0)
    max = ReferenceListProperty(linhas, colunas)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)

    def update_image_pos(self, *args):
        if hasattr(self, "image"):
            self.image.pos = self.pos

    def position(self, *args):
        self.pos = (
            self.patern_x + (self.coluna * self.width),
            self.patern_y + (self.linha * self.height),
        )


class Object(Tile):
    resistencia = NumericProperty(0)
    def __init__(self, global_size, source, ativado=False, extra_func="", extra_arg1=None, extra_arg2=None, **kwargs):
        super().__init__(**kwargs)
        self.extra_func = extra_func
        self.extra_arg1 = extra_arg1
        self.extra_arg2 = extra_arg2
        self.passivo=True
        if self.passivo:
            Clock.schedule_once(self.ativar_func,1)
        
        self.width = global_size
        self.height = global_size * 0.8
        self.s = source
        self.type = source
        
        self.source = resource_path("assets/tiles/objects/" + f"{source}")
        if self.parent:
            self.world = self.parent.parent.parent
        else:
            self.world = None
            Clock.schedule_once(self.procurar_parent, 0.5)

        self.image = Image(
        source=self.source,
        allow_stretch=True,
        keep_ratio=False,
        size=self.size,
        pos=self.pos,
        )
        self.add_widget(self.image)
        self.bind(pos=self.update_image_pos)

        self.colisivel = True
        self.quebravel = False
        self.quebrando = False
        self.ativado = ativado
        self.resistencia=0
        self.dano_colisao = 0
        self.drops = {}


        if source == "vazio.png":
            self.colisivel=False

        if source == "pedra.png":
            self.hitbox = [
                self.x + (self.width * 0.05),
                self.y + (self.height * 0.2),
                self.width * 0.6,
                self.height * 0.6,
            ]
            self.quebravel = True
            self.resistencia_max = 23
            self.resistencia = self.resistencia_max
            apatita = random.randint(0, 6) - 4
            mica = random.randint(0, 5) - 3
            if apatita > 0:
                self.drops["apatita"] = apatita
            if mica > 0:
                self.drops["mica"] = mica

        elif source == "veneno.png":
            self.colisivel = False
            self.dano_colisao = 0.075

        elif source == "entrada_esgoto.png":
            Clock.schedule_once(self.spawn, 0.5)

        elif source=="usb.png":
            self.colisivel=False

        self.position()


    def procurar_parent(self, *args):
        if self.parent:
            self.world = self.parent.parent.parent
        else:
            Clock.schedule_once(self.procurar_parent, 0.5)

    def position(self, *args):
        self.pos = (
            self.patern_x + (self.coluna * self.width),
            self.patern_y + (self.linha * self.height),
        )
        self.get_hitbox()

    def get_hitbox(self, *args):
        if self.s == "vazio.png":
            self.hitbox = [
                self.x,
                self.y,
                self.width,
                self.height,
            ]
        elif self.s == "pedra.png":
            self.hitbox = [
                self.x + (self.width * 0.1),
                self.y + (self.height * 0.45),
                self.width * 0.8,
                self.height * 0.65,
            ]
        elif self.s == "teto_quebrado.png":
            self.hitbox = [
                self.x + (self.width * 0.15),
                self.y + (self.height * 0.5),
                self.width * 0.65,
                self.height * 0.55,
            ]
        elif self.s == "pc.png":
            self.hitbox = [
                self.x + (self.width * 0.075),
                self.y + (self.height * 0.5),
                self.width * 0.65,
                self.height * 0.55,
            ]
        elif self.s == "usb.png":
            self.hitbox = [
                self.x + (self.width * 0.4),
                self.y + (self.height * 0.4),
                self.width * 0.2,
                self.height * 0.15,
            ]
        elif self.s in (
            "entrada_esgoto.png",
            "descer_esgoto.png",
            "veneno.png",
            "subir_esgoto.png",
        ):
            self.hitbox = [
                self.x + (self.width * 0.2),
                self.y + (self.height * 0.7),
                self.width * 0.6,
                self.height * 0.4,
            ]

    def spawn(self, *args):
        if self.ativado and random.randint(1, 10) <= 5:
            return
        
        if not self.world:
            return
        if self.type == "entrada_esgoto.png":
            rato = create_ent("rato")
            rato.pos = self.pos
            self.world.map_layout.add_widget(rato)
            self.world.ents.append(rato)
            self.ativado = True

    def quebrar(self, *args):
        if self.quebravel:
            try:
                self.remove_widget(self.image)
            except Exception:
                pass
            self.world.player.recive_itens(self.drops)
            if self in self.world.map.obj_list:
                self.world.map.obj_list.remove(self)
            try:
                self.world.map_layout.remove_widget(self)
            except Exception:
                pass

    def on_resistencia(self, *args):
        if 100 * self.resistencia / self.resistencia_max < 40:
            if not self.quebrando:
                self.image.source = self.image.source.replace(
                    ".png", "_quebrando.png"
                )
                self.quebrando = True
        if self.resistencia <= 0:
            Clock.schedule_once(self.quebrar, 0.2)

    def colisao(self, *args):
        if not self.world:
            return
        if self.type in ("descer_esgoto.png", "subir_esgoto.png"):
            for ent in self.world.ents:
                if not ent.vivo:
                    continue
                if not ent == self.world.player:
                    return
            if not self.world.trocando_mapa:
                if self.type == "descer_esgoto.png":
                    self.world.map.re_map(type="esgoto")
                elif self.type == "subir_esgoto.png":
                    self.world.map.re_map(type="esgoto", nivel=-1)
        if self.type == "veneno.png":
            for ent in self.world.ents:
                if ent.grid == (self.coluna, self.linha):
                    ent.vida -= self.dano_colisao
        if self.extra_func and self.extra_arg1:
            self.ativar_func()
    
    
    def ativar_func(self, *args):
        try:
            if not self.passivo:
                if self.extra_func == "load_mapa":
                    self.world.map.load_mapa(self.extra_arg1,entrada=self.extra_arg2)
                elif self.extra_func == "create":
                    self.world.map.create(self.extra_arg1)
                elif self.extra_func=="unlock_skill":
                    if not self.extra_arg1 in self.world.player.geral_skills:
                        self.world.player.unlock_skill(self.extra_arg1)
        except:
            Clock.schedule_once(self.ativar_func,0.1)
        try:
            if self.extra_func == "spawn_npc" and self.passivo:
                if not self.extra_arg2:
                    self.extra_arg2=self.pos
                self.world.map.add_npc(ent_name=self.extra_arg1,pos=self.extra_arg2)
            if self.passivo:
                self.passivo=False
        except:
            self.passivo=True
            Clock.schedule_once(self.ativar_func,0.1)


class Grid(Tile):
    def __init__(self, global_size, source, **kwargs):
        super().__init__(**kwargs)
        self.width = global_size
        self.height = global_size * 0.8
        self.ents = []
        self.type = source
        self.source = resource_path("assets/tiles/ground/" + f"{source}")

        self.image = Image(
            source=self.source,
            allow_stretch=True,
            keep_ratio=False,
            size=self.size,
            pos=self.pos,
        )
        self.add_widget(self.image)

        self.bind(pos=self.update_image_pos)

        self.position()
