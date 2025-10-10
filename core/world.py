from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock 

import random

size=90
obj_list=[ ]

class Object(FloatLayout):
    linha = NumericProperty(0)
    coluna = NumericProperty(0)
    posicao = ReferenceListProperty(linha, coluna)

    patern_x = NumericProperty(0)
    patern_y = NumericProperty(0)
    patern_center = ReferenceListProperty(patern_x, patern_y)

    linhas = NumericProperty(0)
    colunas = NumericProperty(0)
    max = ReferenceListProperty(linhas, colunas)

    def __init__(self,source, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        
        global size
        self.s=source
        self.source="assets/tiles/objects/"+f"{source}"
        self.size = (size, size*0.8)

        self.image = Image(
            source=self.source,
            allow_stretch=True,
            keep_ratio=False,
            size=self.size,
            pos=self.pos
        )
        if source=='pedra.png':
            self.hitbox=[self.x+(self.width*0.05),self.y+(self.height*0.2),self.width*0.6, self.height*0.6]
            
        self.add_widget(self.image)

        self.bind(pos=self.update_image_pos)
        self.bind(patern_center=self.on_center_changed)

        self.position()

    def update_image_pos(self, *args):
        self.image.pos = self.pos

    def position(self, *args):
        self.pos = (
            self.patern_x + (self.coluna * self.width),
            self.patern_y + (self.linha * self.height)
        )
        self.get_hitbox()
        
    def get_hitbox (self,*args):
        if self.s=='pedra.png':
            self.hitbox=[self.x+(self.width*0.15),self.y+(self.height*0.5),self.width*0.7, self.height*0.6]
        
        
        

    def on_center_changed(self, *args):
        self.position()
        
        #outra class começa a baixo

class Grid(FloatLayout):
    linha = NumericProperty(0)
    coluna = NumericProperty(0)
    posicao = ReferenceListProperty(linha, coluna)

    patern_x = NumericProperty(0)
    patern_y = NumericProperty(0)
    patern_center = ReferenceListProperty(patern_x, patern_y)

    linhas = NumericProperty(0)
    colunas = NumericProperty(0)
    max = ReferenceListProperty(linhas, colunas)

    def __init__(self,source, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        
        global size
        global obj_list
        self.source="assets/tiles/ground/"+f"{source}"
        self.size = (size, size*0.8)

        self.image = Image(
            source=self.source,
            allow_stretch=True,
            keep_ratio=False,
            size=self.size,
            pos=self.pos
        )
        self.add_widget(self.image)

        self.bind(pos=self.update_image_pos)
        self.bind(patern_center=self.on_center_changed)

        self.position()

    def update_image_pos(self, *args):
        self.image.pos = self.pos

    def position(self, *args):
        self.pos = (
            self.patern_x + (self.coluna * self.width),
            self.patern_y + (self.linha * self.height)
        )

    def on_center_changed(self, *args):
        self.position()

#outra class começa a baixo

class World(FloatLayout):
    colunas = NumericProperty(0)
    linhas = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.player=None
        self.size = (Window.width, Window.height)

    def create(self, xm, ym):
        global size
        
        self.linhas = xm
        self.colunas = ym

        # Tamanho fixo do tile
        tile_w, tile_h = size/2, 0.8*size/2

        # Cálculo do ponto central
        map_width = self.colunas * tile_w
        map_height = self.linhas * tile_h
        self.size=(size*xm,size*ym*0.8)

        # Posição inicial (superior esquerdo) para começar a desenhar centralizado
        offset_x = (Window.width/2)-(self.width/2)
        offset_y = (Window.height/2)-(self.height/2)
        self.pos=(offset_x,offset_y)

        for y in range(self.linhas):
            for x in range(self.colunas):
                grid = Grid(
                    posicao=(x, y),
                    patern_center=(offset_x, offset_y),
                    max=(self.linhas, self.colunas),
                    source="terra.png"
                )
                self.add_widget(grid)
        self.player.image.pos=(offset_x-20,offset_y )
        
        for y in range(self.linhas):
            for x in range(self.colunas):
                r=random.randint(0,10)
                if r==0:
                    if not(x==0 and y==0):
                        obj = Object(
                            posicao=(x, y),
                            patern_center=(offset_x, offset_y),
                            max=(self.linhas, self.colunas),
                            source="pedra.png"
                        )
                        obj_list.append(obj)
                        self.add_widget(obj)
        
        self.add_widget(self.player)
        self.atualizar()
    
    
    def collision_verify(self, *args):
        self.verificar_colisao_horizontal()
        self.verificar_colisao_vertical()


    def verificar_colisao_horizontal(self):
        original_x = self.player.image.x
        self.player.image.x += self.player.speed_x * self.player.velocidade
        self.player.hitbox = self.player.get_hitbox()
    
        for obj in obj_list:
            if not hasattr(obj, "hitbox"):
                continue
            if self.collision(self.player.hitbox, obj.hitbox):
                # Reverte X e zera velocidade no eixo X
                self.player.image.x = original_x
                self.player.speed_x = 0
                self.player.hitbox = self.player.get_hitbox()
                return


    def verificar_colisao_vertical(self):
        original_y = self.player.image.y
        self.player.image.y += self.player.speed_y * self.player.velocidade
        self.player.hitbox = self.player.get_hitbox()
    
        for obj in obj_list:
            if not hasattr(obj, "hitbox"):
                continue
            if self.collision(self.player.hitbox, obj.hitbox):
                # Reverte Y e zera velocidade no eixo Y
                self.player.image.y = original_y
                self.player.speed_y = 0
                self.player.hitbox = self.player.get_hitbox()
                return


        
    
    def atualizar(self,*args):
        Clock.schedule_interval(self.collision_verify,1/60)
        #atualização de posição do plsyer
        Clock.schedule_interval(self.player.atualizar_pos ,1/30)
    
    def collision(self,hitbox1, hitbox2):
        x1, y1, w1, h1 = hitbox1
        x2, y2, w2, h2 = hitbox2
        return (
            x1 < x2 + w2 and
            x1 + w1 > x2 and
            y1 < y2 + h2 and
            y1 + h1 > y2
        )
 


class TestApp(App):
    def build(self):
        world = World()
        world.create(10, 10)  # Altere aqui o tamanho do mapa
        return world


if __name__ == '__main__':
    TestApp().run()
