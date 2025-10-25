from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock 

import random

from core.player import Rato

size=90

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
    
    resistencia=NumericProperty(0)

    def __init__(self,source, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        
        global size
        self.s=source
        self.type=source
        self.source="assets/tiles/objects/"+f"{source}"
        self.size = (size, size*0.8)
        self.quebravel=False
        self.quebrando=False
        self.drops={}

        self.image = Image(
            source=self.source,
            allow_stretch=True,
            keep_ratio=False,
            size=self.size,
            pos=self.pos
        )
        if source=='pedra.png':
            self.hitbox=[self.x+(self.width*0.05),self.y+(self.height*0.2),self.width*0.6, self.height*0.6]
            self.quebravel=True
            self.resistencia_max=23
            self.resistencia=self.resistencia_max
            apatita=random.randint(0,6)-4
            mica=random.randint(0,5)-3
            if apatita>0:
                self.drops["apatita"]= apatita
            if mica>0:
                self.drops["mica"]= mica
        
        if self.type=="entrada_esgoto.png":
            Clock.schedule_once(self.spawn,3)
        
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
        
    def spawn(self,*args):
        world = self.parent
        if not world:
            return
        if self.type=="entrada_esgoto.png":
            
            rato=Rato()
            rato.image.pos = (self.image.x,self.image.y)
            print(rato.pos)
            world.add_widget(rato)
            world.ents.append(rato)
    
    def quebrar(self,*args):
        if self.quebravel:
            self.remove_widget(self.image)
            self.parent.player.recive_itens(self.drops)
            self.parent.obj_list.remove(self)
            self.parent.remove_widget(self)  
    
    def on_resistencia(self,*args):
        if 100*self.resistencia/self.resistencia_max < 40:
            if not self.quebrando:
                self.image.source = self.image.source.replace(".png", "_quebrando.png")
                self.quebrando=True
        if self.resistencia <= 0:
            Clock.schedule_once(self.quebrar, 0.6)


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
        self.ents=[]
        self.type=source
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
        self.limites=[]
        self.ents=[]
        self.obj_list=[]

    def create(self, xm, ym):
        global size
        
        self.linhas = xm
        self.colunas = ym

        self.size=(size*xm,size*ym*0.8)

        # Posição inicial (superior esquerdo) para começar a desenhar centralizado
        self.offset_x = (Window.width/2)-(self.width/2)
        self.offset_y = (Window.height/2)-(self.height/2)
        self.pos=(self.offset_x,self.offset_y)
        self.limites=(self.x,self.y,self.x+self.width,self.y+self.height)

        for y in range(self.linhas):
            for x in range(self.colunas):
                grid = Grid(
                    posicao=(x, y),
                    patern_center=(self.offset_x, self.offset_y),
                    max=(self.linhas, self.colunas),
                    source="terra.png"
                )
                self.add_widget(grid)
        self.player.image.pos=(self.offset_x,self.offset_y )
        self.ents.append(self.player)
        
        for y in range(self.linhas):
            for x in range(self.colunas):
                r=random.randint(0,10)
                if r==0:
                    if not((x==0 or x==1) and (y==0 or y==1)):
                        m = random.randint(0,100)
                        if m < 30  :
                            obj = Object(
                            posicao=(x, y),
                            patern_center=(self.offset_x, self.offset_y),
                            max=(self.linhas, self.colunas),
                            source="entrada_esgoto.png"
                        )
                        else:
                            obj = Object(
                                posicao=(x, y),
                                patern_center=(self.offset_x, self.offset_y),
                                max=(self.linhas, self.colunas),
                                source="pedra.png"
                            )
                        self.obj_list.append(obj)
                        self.add_widget(obj)
        
        self.add_widget(self.player)
        self.atualizar()
        print(f"player: {self.player.hitbox}, mapa: {self.limites}, tilessize: {self.colunas*size,self.linhas*0.8*size}")
    

    def add_objects(self,type,grid):
        grid_x,grid_y=grid
        obj=Object(
            posicao=(grid_y,grid_x),
            patern_center=(self.offset_x,self.offset_y),
            max=(self.linhas,self.colunas),
            source=type+".png"
        )
        self.add_widget(obj)
        self.obj_list.append(obj)
        for ent in self.ents:
            self.remove_widget(ent)
            self.add_widget(ent)
    
    
    def collision_verify(self, *args):        
        for ent in self.ents:
            self.verificar_colisao_horizontal(ent) 
            self.verificar_colisao_vertical(ent)
            self.map_collision(ent)
            self.grid_verify(ent)
        
    def grid_verify(self,ent):
        grid_x=(ent.center_hitbox_x-self.x)/(self.width/self.colunas)
        grid_y=(ent.center_hitbox_y-self.y)/(self.height/self.linhas)
        grid_x=int(grid_x)
        grid_y=int(grid_y)
        ent.grid=grid_x,grid_y


    def map_collision(self,ent):
        ent.hitbox = ent.get_hitbox()
        if ent.image.x>self.x+self.width-(ent.image.width*0.75):
            ent.image.x=self.width+self.x-(ent.image.width*0.75)
        elif ent.image.x<self.x-(ent.image.width*0.25):
            ent.image.x=self.x-(ent.image.width*0.25)
        if ent.image.y<self.y:
            ent.image.y=self.y
        elif ent.image.y>self.y+self.height-(ent.image.height/2):
            ent.image.y=self.y+self.height-(ent.image.height/2)
            
    def verificar_colisao_horizontal(self,ent):
        original_x = ent.image.x
        ent.move_x()
        ent.hitbox = ent.get_hitbox()
    
        for obj in self.obj_list:
            if not hasattr(obj, "hitbox"):
                continue
            if self.collision(ent.hitbox, obj.hitbox):
                # Reverte X e zera velocidade no eixo X
                ent.image.x = original_x
                ent.speed_x = 0
                ent.hitbox = ent.get_hitbox()
                if self.collision(ent.hitbox, obj.hitbox):
                    #segundo teste
                    ent.image.x = obj.image.x+obj.image.width
                    ent.speed_x = 0
                    ent.hitbox = ent.get_hitbox()
        for entit in self.ents:
            if ent==entit:
                continue
            if self.collision(ent.hitbox, entit.hitbox):
                # Reverte X e zera velocidade no eixo Y
                ent.image.x = original_x
                ent.speed_x = 0
                ent.hitbox = ent.get_hitbox()


    def verificar_colisao_vertical(self,ent):
        original_y = ent.image.y
        ent.move_y()
        ent.hitbox = ent.get_hitbox()
    
        for obj in self.obj_list:
            if not hasattr(obj, "hitbox"):
                continue
            if self.collision(ent.hitbox, obj.hitbox):
                # Reverte Y e zera velocidade no eixo Y
                ent.image.y = original_y
                ent.speed_y = 0
                ent.hitbox = ent.get_hitbox()
                if self.collision(ent.hitbox, obj.hitbox):
                    #segundo teste
                    ent.image.y = obj.image.y
                    ent.speed_y = 0
                    ent.hitbox = ent.get_hitbox()

        for entit in self.ents:
            if ent==entit:
                continue
            if self.collision(ent.hitbox, entit.hitbox):
                # Reverte Y e zera velocidade no eixo Y
                ent.image.y = original_y
                ent.speed_y = 0
                ent.hitbox = ent.get_hitbox()

    def atualizar_sprites(self,*args):
        for ent in self.ents:
            ent.atualizar_pos()
        
    
    def atualizar(self,*args):
        Clock.schedule_interval(self.collision_verify,1/60)
        Clock.schedule_interval(self.atualizar_sprites,1/30)
    
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
