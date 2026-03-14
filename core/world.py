from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import NumericProperty
from kivy.core.window import Window
from kivy.clock import Clock

from core.map import Map
from core.camera import Camera
from core.entity.ent_factory import create_ent

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
        self.ev_camera = None
        self.ev_spawn_ents = None

        self.trocando_mapa = False

        self.scroll_view = ScrollView(size=self.size, do_scroll_x=False, do_scroll_y=False)
        self.map_layout = FloatLayout(size=self.size, size_hint=(None, None))
        self.scroll_view.add_widget(self.map_layout)
        self.scroll_view.scroll_x = 0
        self.scroll_view.scroll_y = 0
        self.add_widget(self.scroll_view)   
        self.map = Map(world=self)
        self.background = None
        self.camera = Camera(
            position=(0, 0), 
            map_size=(0,0), 
            player=self.player,
            parent=self
            )

        self.atualizar()


    def create(self, colunas = 0, linhas = 0, tipo="esgoto"):
        self.map.create(colunas, linhas, tipo)
        self.linhas = self.map.linhas
        self.colunas = self.map.colunas

        self.add_player()
        self.camera.map_size = (self.map.colunas * size, self.map.linhas * size * 0.8)
        self.camera.player = self.player


    def re_map(self, tipo, nivel=1):
        if self.trocando_mapa:
            return

        self.trocando_mapa = True
        self.map.re_map(tipo, nivel)
        self.trocando_mapa = False

        self.add_player()
        self.size = self.camera.map_size = (self.map.colunas * size, self.map.linhas * size * 0.8)
        self.camera.player = self.player


    def load_mapa(self, nome, respawn=False):
        self.map.load_mapa(nome, respawn=respawn)
        self.linhas = self.map.linhas
        self.colunas = self.map.colunas

        self.add_player()
        self.camera.map_size = (self.map.colunas * size, self.map.linhas * size * 0.8)
        self.camera.player = self.player


    def collision_verify(self, *args):
        for ent in list(self.ents):
            self.verificar_colisao_horizontal(ent)
            self.verificar_colisao_vertical(ent)
            self.map_collision(ent)
            self.grid_verify(ent)


    def add_player(self, *args):
        try:
            self.map_layout.remove_widget(self.player)
            self.map_layout.add_widget(self.player)
        except:
            self.map_layout.add_widget(self.player)

        if self.map.spawn_pos:
            self.player.center = self.map.spawn_pos

        if not self.player in self.ents:
            self.ents.append(self.player)
        if hasattr(self, "camera"):
            self.camera.player = self.player
        
    def respawn_player(self, *args):
        for obj in self.map.obj_list[:]:
            self.map.obj_list.remove(obj)
            try:
                self.map_layout.remove_widget(obj)
            except Exception:
                pass
        for tile in self.map.tiles_list[:]:
            self.map.tiles_list.remove(tile)
            try:
                self.map_layout.remove_widget(tile)
            except Exception:
                pass
        for ent in self.ents[:]:
            if ent is not self.player:
                try:
                    self.map_layout.remove_widget(ent)
                except Exception:
                    pass

        self.ents = [self.player]
        self.map.ents = [self.player]
        if self.map.respawn_map:
            self.trocando_mapa=True
            self.load_mapa(self.map.respawn_map, respawn=True)
            self.trocando_mapa=False
        else:
            self.trocando_mapa=True
            self.load_mapa("inicial", respawn=True)
            self.trocando_mapa=False

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
        top_limit = self.y + self.height - size * 1.2

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
        if self.ev_camera:
            self.ev_camera.cancel()
        if self.ev_spawn_ents:
            self.ev_spawn_ents.cancel()

        self.ev_camera = Clock.schedule_interval(self.atualizar_camera, 1/60)
        self.ev_colisao = Clock.schedule_interval(self.collision_verify, 1/60)
        self.ev_sprite = Clock.schedule_interval(self.atualizar_sprites, 1/30)
        self.ev_spawn_ents = Clock.schedule_interval(self.procedural_ent_spawn, 1)
        
    def new_limites(self, *args):
        self.limites = (
            self.x,
            self.y,
            self.width - self.x-size,
            self.height - self.y-size
        )

    def atualizar_camera(self, *args):
        nova_pos = self.camera.update()
        if nova_pos:
            if self.size[0] !=Window.width:
                self.scroll_view.scroll_x = nova_pos[0]/(self.size[0]-Window.width)
            if self.size[1] != Window.height:
                self.scroll_view.scroll_y = nova_pos[1]/(self.size[1]-Window.height)
            self.new_limites()

    def atualizar_sprites(self, *args):
        for ent in self.ents:
            ent.atualizar_pos()
    
    def procedural_ent_spawn(self,*args):
        if self.map.procedural_ent_spawn:
            self.map.spawn_ent()


    def gerar_boss(self):
        boss = create_ent("ratona")
        self.map_layout.add_widget(boss)
        self.ents.append(boss)

        boss.pos = (
            self.x + self.map.linhas * size * 0.5,
            self.y + self.map.colunas * size * 0.5 * 0.8
        )
        self.boss = boss
        Clock.schedule_once(self.limpar_sala_boss, 0.5)
    
    def limpar_sala_boss(self,*args):
    
        for obj in self.map.obj_list[:]:
            if obj.type == self.map.padrao["spawner"][self.map.type]:
                self.map_layout.remove_widget(obj)
                self.map.obj_list.remove(obj)
