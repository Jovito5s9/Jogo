from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.clock import Clock
from kivy.core.window import Window

import random

from utils.resourcesPath import resource_path
from core.player import Rato


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

    def on_center_changed(self, *args):
        self.position()


class Object(Tile):
    def __init__(self, global_size, source, ativado=False, **kwargs):
        super().__init__(**kwargs)
        self.width = global_size
        self.height = global_size * 0.8
        self.s = source
        self.type = source
        self.source = resource_path("assets/tiles/objects/" + f"{source}")
        self.colisivel = True
        self.quebravel = False
        self.quebrando = False
        self.ativado = ativado
        self.resistencia=0
        self.dano_colisao = 0
        self.drops = {}

        self.image = Image(
            source=self.source,
            allow_stretch=True,
            keep_ratio=False,
            size=self.size,
            pos=self.pos,
        )

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

        elif self.type == "entrada_esgoto.png":
            Clock.schedule_once(self.spawn, 0.5)

        self.add_widget(self.image)

        self.bind(pos=self.update_image_pos)
        self.bind(patern_center=self.on_center_changed)

        self.position()

    def position(self, *args):
        self.pos = (
            self.patern_x + (self.coluna * self.width),
            self.patern_y + (self.linha * self.height),
        )
        self.get_hitbox()

    def get_hitbox(self, *args):
        if self.s == "pedra.png":
            self.hitbox = [
                self.x + (self.width * 0.15),
                self.y + (self.height * 0.5),
                self.width * 0.7,
                self.height * 0.6,
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
        world = self.parent
        if not world:
            return
        if self.type == "entrada_esgoto.png":
            rato = Rato()
            rato.pos = self.pos
            world.add_widget(rato)
            world.ents.append(rato)
            self.ativado = True

    def quebrar(self, *args):
        if self.quebravel:
            try:
                self.remove_widget(self.image)
            except Exception:
                pass
            self.parent.player.recive_itens(self.drops)
            if self in self.parent.obj_list:
                self.parent.obj_list.remove(self)
            try:
                self.parent.remove_widget(self)
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
        if self.type in ("descer_esgoto.png", "subir_esgoto.png"):
            for ent in self.parent.ents:
                if not ent.vivo:
                    continue
                if not ent == self.parent.player:
                    return
            if not self.parent.trocando_mapa:
                if self.type == "descer_esgoto.png":
                    self.parent.map.re_map(type="esgoto")
                elif self.type == "subir_esgoto.png":
                    self.parent.map.re_map(type="esgoto", nivel=-1)
        if self.type == "veneno.png":
            for ent in self.parent.ents:
                if ent.grid == (self.coluna, self.linha):
                    ent.vida -= self.dano_colisao


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
        self.bind(patern_center=self.on_center_changed)

        self.position()
