from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty
from kivy.core.window import Window
from kivy.clock import Clock

from core.map import Map
from core.player import Rata_mae

size = Window.height / 12.5


class World(FloatLayout):
    colunas = NumericProperty(0)
    linhas = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.size_hint = (None, None)
        self.size = (Window.width, Window.height)

        self.player = None
        self.ents = []
        self.boss = None

        self.ev_colisao = None
        self.ev_sprite = None

        self.trocando_mapa = False

        self.map = Map(world=self)

        self.atualizar()


    def create(self, linhas, colunas, tipo="esgoto"):
        self.map.create(linhas, colunas, tipo)
        self.linhas = self.map.linhas
        self.colunas = self.map.colunas


    def re_map(self, tipo, nivel=1):
        if self.trocando_mapa:
            return

        self.trocando_mapa = True
        self.map.re_map(tipo, nivel)
        self.trocando_mapa = False


    def load_mapa(self, nome):
        self.map.load_mapa(nome)
        self.linhas = self.map.linhas
        self.colunas = self.map.colunas


    def collision_verify(self, *args):
        for ent in list(self.ents):
            self.verificar_colisao_horizontal(ent)
            self.verificar_colisao_vertical(ent)
            self.map_collision(ent)
            self.grid_verify(ent)


    def verificar_colisao_horizontal(self, ent):
        original_x = ent.x
        ent.move_x()
        ent.hitbox = ent.get_hitbox()

        for obj in self.map.obj_list:
            if not hasattr(obj, "hitbox"):
                continue

            if self.collision(ent.hitbox, obj.hitbox):
                obj.colisao()

                if obj.colisivel:
                    ent.x = original_x
                    ent.speed_x = 0
                    ent.hitbox = ent.get_hitbox()

        for entit in self.ents:
            if ent is entit:
                continue

            if self.collision(ent.hitbox, entit.hitbox):
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

        for obj in self.map.obj_list:
            if not hasattr(obj, "hitbox"):
                continue

            if self.collision(ent.hitbox, obj.hitbox):
                obj.colisao()

                if obj.colisivel:
                    ent.y = original_y
                    ent.speed_y = 0
                    ent.hitbox = ent.get_hitbox()

        for entit in self.ents:
            if ent is entit:
                continue

            if self.collision(ent.hitbox, entit.hitbox):
                ent.y = original_y
                ent.speed_y = 0
                ent.hitbox = ent.get_hitbox()


    def grid_verify(self, ent):
        tile_width = size
        tile_height = size * 0.8

        grid_x = int((ent.center_hitbox_x - self.x) / tile_width)
        grid_y = int((ent.center_hitbox_y - self.y) / tile_height)

        grid_x = max(0, min(self.map.colunas - 1, grid_x))
        grid_y = max(0, min(self.map.linhas - 1, grid_y))

        ent.grid = (grid_x, grid_y)


    def map_collision(self, ent):
        right_limit = self.x + self.width - (ent.width * 0.75)
        left_limit = self.x - (ent.width * 0.25)

        if ent.x > right_limit:
            ent.x = right_limit
        elif ent.x < left_limit:
            ent.x = left_limit

        bottom_limit = self.y
        top_limit = self.y + self.height - (ent.height / 2)

        if ent.y < bottom_limit:
            ent.y = bottom_limit
        elif ent.y > top_limit:
            ent.y = top_limit

        ent.pos = (ent.x, ent.y)

    def collision(self, hitbox1, hitbox2): 
        x1, y1, w1, h1 = hitbox1 
        x2, y2, w2, h2 = hitbox2 
        return ( x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2 )

    def atualizar(self, *args):
        if self.ev_colisao:
            self.ev_colisao.cancel()
        if self.ev_sprite:
            self.ev_sprite.cancel()

        self.ev_colisao = Clock.schedule_interval(self.collision_verify, 1/60)
        self.ev_sprite = Clock.schedule_interval(self.atualizar_sprites, 1/30)


    def atualizar_sprites(self, *args):
        for ent in self.ents:
            ent.atualizar_pos()


    def gerar_boss(self):
        boss = Rata_mae()
        self.add_widget(boss)
        self.ents.append(boss)

        boss.pos = (
            self.x + self.map.linhas * size * 0.5,
            self.y + self.map.colunas * size * 0.5 * 0.8
        )

        self.boss = boss
