from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock 

import random

from core.player import Rato

size=75

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

    def __init__(self,source,ativado=False, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        
        global size
        self.s=source
        self.type=source
        self.source="assets/tiles/objects/"+f"{source}"
        self.size = (size, size*0.8)
        self.colisivel=True
        self.quebravel=False
        self.quebrando=False
        self.ativado=ativado
        self.dano_colisao=0
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

        elif source=='veneno.png':
            self.colisivel=False
            self.dano_colisao=0.075

        elif self.type=="entrada_esgoto.png":
            if not self.ativado:
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
        elif self.s in ('entrada_esgoto.png', 'descer_esgoto.png', 'veneno.png',  'subir_esgoto.png'):
            self.hitbox=[self.x+(self.width*0.2),self.y+(self.height*0.7),self.width*0.6, self.height*0.4]
        
    def spawn(self,*args):
        if self.ativado:
            return
        world = self.parent
        if not world:
            return
        if self.type=="entrada_esgoto.png":
            
            rato=Rato()
            rato.image.pos = (self.image.x,self.image.y)
            print(rato.pos)
            world.add_widget(rato)
            world.ents.append(rato)
            self.ativado=True
    
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
            Clock.schedule_once(self.quebrar, 0.2)
    
    def colisao(self,*args):
        if self.type in ('descer_esgoto.png' , 'subir_esgoto.png'):
            for ent in self.parent.ents:
                if not ent.vivo:
                    continue
                if not ent==self.parent.player:
                    return
            if not self.parent.trocando_mapa:
                if self.type=='descer_esgoto.png':
                    self.parent.re_map(type="esgoto")
                elif self.type == 'subir_esgoto.png':
                    self.parent.re_map(type="esgoto",nivel=-1)
        if self.type=='veneno.png':
            for ent in self.parent.ents:
                if ent.grid==(self.coluna,self.linha):
                    ent.vida-=self.dano_colisao


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
        self.ev_colisao = None
        self.ev_sprite = None
        self.trocando_mapa = False
        self.player=None
        self.size = (Window.width, Window.height)
        self.limites=[]
        self.ents=[]
        self.obj_list=[]
        self.tiles_list=[]
        self.descida_dungeon=[]
        self.subida_dungeon=[]
        self.masmorra={}
        self.grid_padrao="terra.png"
        self.obj_padrao="pedra.png"
        self.grid_esgoto="ladrilhos_esgoto.png"
        self.obj_esgoto="veneno.png"
        self.nivel=0
        self.lista_modificadores=["coleta","combate"]
        self.mapa_modificador="coleta"
        self.atualizar()


    def create(self, xm, ym, type=None):
        global size
        type='esgoto'
        self.type=type
        combate_nivel=1
        if self.mapa_modificador=="combate":
            combate_nivel=2.5
        elif self.mapa_modificador=="coleta":
            combate_nivel=1
        if type=="esgoto":
            if not self.nivel in self.masmorra:
                self.masmorra[self.nivel]={}
            objeto_padrao=self.obj_esgoto
            grid_padrao=self.grid_esgoto
            if self.nivel>0:
                self.subida_dungeon = self.descida_dungeon 
            y = random.randint(0, xm - 1)
            x = random.randint(0, ym - 1)
            self.descida_dungeon = (x, y)
            if self.descida_dungeon == self.subida_dungeon :
                y = random.randint(0, xm - 1)
                x = random.randint(0, ym - 1)
                self.descida_dungeon = (x, y)
            print(x,y)
        if type==None:
            objeto_padrao=self.obj_padrao
            grid_padrao=self.grid_padrao
            self.nivel=0
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
                    source=grid_padrao
                )
                self.add_widget(grid)
                self.tiles_list.append(grid)
        self.player.image.pos=(self.offset_x,self.offset_y )
        self.ents=[self.player]
        
        for y in range(self.linhas):
            for x in range(self.colunas):
                if self.descida_dungeon==(x,y):
                    obj = Object(
                            posicao=(x, y),
                            patern_center=(self.offset_x, self.offset_y),
                            max=(self.linhas, self.colunas),
                            source="descer_esgoto.png"
                        )
                    self.obj_list.append(obj)
                    self.add_widget(obj)
                    continue
                if self.subida_dungeon==(x,y):
                    obj = Object(
                            posicao=(x, y),
                            patern_center=(self.offset_x, self.offset_y),
                            max=(self.linhas, self.colunas),
                            source="subir_esgoto.png"
                        )
                    self.obj_list.append(obj)
                    self.add_widget(obj)
                    continue
                r=random.randint(0,10)
                if r==0:
                    if not((x==0 or x==1) and (y==0 or y==1)):
                        m = random.randint(0,100)
                        if m < (10 +self.nivel)*combate_nivel :
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
                                source=objeto_padrao
                            )
                        self.obj_list.append(obj)
                        self.add_widget(obj)
        self.masmorra[self.nivel] = {
            "tiles": [(t.coluna, t.linha, t.type) for t in self.tiles_list],
            "objs": [(o.coluna, o.linha, o.type, o.resistencia, True) for o in self.obj_list]
        }
        try:
            self.remove_widget(self.player)
        except Exception as e:
            print(e)
        self.add_widget(self.player)
        print(f"player: {self.player.hitbox}, mapa: {self.limites}, tilessize: {self.colunas*size,self.linhas*0.8*size}")
    

    def carregar_mapa(self, sala):
        if not sala:
            return
        self.tiles_list.clear()
        self.obj_list.clear()
        for coluna, linha, tipo in sala["tiles"]:
            tile = Grid(
                posicao=(linha, coluna),
                patern_center=(self.offset_x, self.offset_y),
                max=(self.linhas, self.colunas),
                source=tipo
            )
            self.tiles_list.append(tile)
            self.add_widget(tile)

        for coluna, linha, tipo, resistencia, ativado in sala["objs"]:
            obj = Object(
                posicao=(linha, coluna),
                patern_center=(self.offset_x, self.offset_y),
                max=(self.linhas, self.colunas),
                source=tipo,
                ativado=ativado
            )
            obj.resistencia = resistencia
            self.obj_list.append(obj)
            self.add_widget(obj)
        try:
            self.remove_widget(self.player)
        except Exception as e:
            print(e)
        self.add_widget(self.player)
    

    def re_map(self,type,nivel=1):
        if self.trocando_mapa:
            return
        self.trocando_mapa=True
        if type==self.type:
            self.nivel+=nivel
        for obj in self.obj_list[:]:
            self.obj_list.remove(obj)
            self.remove_widget(obj)
        for tile in self.tiles_list[:]:
            self.tiles_list.remove(tile)
            self.remove_widget(tile)
        for ent in self.ents[:]:
            if ent is not self.player:
                self.ents.remove(ent)
                self.remove_widget(ent)
        self.mapa_modificador=random.choice(self.lista_modificadores)
        if self.nivel<0:
            self.type=None
            self.nivel=0
        if self.nivel in self.masmorra:
            self.carregar_mapa(self.masmorra[self.nivel])
            self.trocando_mapa=False
            return
        else:
            self.create(self.linhas,self.colunas,type)
            self.trocando_mapa=False
    

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
        
    def grid_verify(self, ent):
        tile_width = size
        tile_height = size * 0.8 
        grid_x = int((ent.center_hitbox_x - self.x) / tile_width)
        grid_y = int((ent.center_hitbox_y - self.y) / tile_height)
        grid_x = max(0, min(self.colunas - 1, grid_x))
        grid_y = max(0, min(self.linhas - 1, grid_y))
        ent.grid = (grid_x, grid_y)
        if ent==self.player:
            #print(self.player.grid)
            pass


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
                obj.colisao()
                if obj.colisivel:
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
                obj.colisao()
                if obj.colisivel:
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
        
    
    def atualizar(self, *args):
        if self.ev_colisao:
            self.ev_colisao.cancel()
        if self.ev_sprite:
            self.ev_sprite.cancel()
        self.ev_colisao = Clock.schedule_interval(self.collision_verify, 1/60)
        self.ev_sprite = Clock.schedule_interval(self.atualizar_sprites, 1/30)
    
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
