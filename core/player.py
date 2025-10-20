from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.properties import OptionProperty,BooleanProperty, NumericProperty

import random

class Barra(Widget):
    modificador=NumericProperty(100)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cor=([1,0,0,1])
        self.w=1
        self.h=1
        with self.canvas:
            self.color=Color(*self.cor)
            self.rect=Rectangle(
                pos=self.pos,
                size=(self.w*(self.modificador/100)+1,self.h),
            )
            self.bind(pos=self.atualizar)
            self.bind(modificador=self.atualizar)
            
    def atualizar(self,*args):
        self.rect.pos=(self.x-(self.w/2),self.y)
        self.rect.size=(self.w*(self.modificador/100)+1,self.h)


class BasicEnt(FloatLayout):
    vida=NumericProperty(1)
    i_frames=BooleanProperty(False)
    estado=OptionProperty ("idle",
    options=("idle","running","atacando","morto"))
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (32, 32)
        self.pos = (100, 100)
        self.recompensa = 0
        self.i_frames_time=0.8
        self.vida_maxima=100
        self.vida = self.vida_maxima
        self.vivo=True
        self.ataque_name=""
        self.repulsao=10
        self.dano = 5
        self.atacando=False
        self.alcance_fisico=70
        self.velocidade = 3
        self.speed_x=0
        self.speed_y=0
        self.facing_right = True
        self.idle_frames=1
        self.running_frames=1
        self.atacando_frames=1
        self.alvo=False
        self.player=None
        self.hitbox=()
        self.center_hitbox_x=0
        self.center_hitbox_y=0
        self.sources={}
        self.list_drops={}
        self.inventario={}

        
        
    def atualizar(self,*args):
        # Carrega o sprite sheet
        self.sprite_sheet = Image(source=self.sources.get("idle")).texture
        self.frame_width = 32
        self.frame_height = 32
        self.total_frames = self.idle_frames
        self.current_frame = 0

        # Cria o widget de imagem animada
        self.image = Image(
            size=(self.frame_width*5, self.frame_height*5),
            size_hint=(None, None),
            pos=(0, 0)  # fixa dentro do BasicEnt
        )
        self.image.allow_stretch=True
        self.image.keep_ratio=False
        self.add_widget(self.image)

        self.hitbox=self.get_hitbox()

        # Inicia com o primeiro frame
        self.update_texture()

        # Agendar a animação
        Clock.schedule_interval(self.animation, 0.15)
        self.image.bind(pos=self.on_image_pos)
        self.barra_vida=Barra(size=(self.image.width,10),pos=(self.image.center_x,self.image.center_y))
        self.barra_vida.w=self.image.width/3
        self.barra_vida.h=10
        self.add_widget(self.barra_vida)

    def move_x(self,*args):
        if self.vivo:
            self.image.x+=self.speed_x*self.velocidade 
    
    def move_y(self,*args):
        if self.vivo:
            self.image.y+=self.speed_y*self.velocidade 

    def atualizar_pos(self,*args):
        if not self.vivo:
            return
        if self.speed_x > 0:
            self.facing_right = True
        elif self.speed_x < 0:
            self.facing_right = False
        if self.atacando:
            self.estado="atacando"
        elif self.speed_x!=0 or self.speed_y:
            self.estado="running"
        else:
            self.estado="idle"
        self.barra_vida.pos=(self.image.center_x,self.image.center_y)
        self.hitbox = self.get_hitbox()

    def on_estado(self,*args):
        if not self.vivo:
            self.sprite_sheet = Image(source=self.sources.get("morto")).texture
            self.total_frames = 1
            return
        if self.estado=="atacando":
            self.sprite_sheet = Image(source=self.sources.get(f"{self.ataque_name}")).texture
            self.frame_width = 32
            self.frame_height = 32
            self.total_frames = self.atacando_frames
            self.current_frame = 0
        elif self.estado=="idle":
            self.sprite_sheet = Image(source=self.sources.get("idle")).texture
            self.frame_width = 32
            self.frame_height = 32
            self.total_frames = self.idle_frames
            self.current_frame = 0
        elif self.estado=="running":
            self.sprite_sheet = Image(source=self.sources.get("running")).texture
            self.frame_width = 32
            self.frame_height = 32
            self.total_frames = self.running_frames
            self.current_frame = 0

    def update_texture(self):
        x = self.frame_width * self.current_frame
        y = 0

        if self.facing_right:
            tex = self.sprite_sheet.get_region(x, y, self.frame_width, self.frame_height)
        else:
            tex = self.sprite_sheet.get_region(x + self.frame_width, y, -self.frame_width, self.frame_height)

        self.image.texture = tex

    def animation(self, dt):
        self.current_frame = (self.current_frame + 1) % self.total_frames
        self.update_texture()

    def on_image_pos(self,*args):
        try:
            self.pos=self.image.pos
        except:
            pass
    
    def on_pos(self,*args):
        try:
            if self.pos!=self.image.pos:
                self.image.pos=self.pos
        except:
            pass
    
    def get_center_hitbox(self,x,y,w,h):
        self.center_hitbox_x,self.center_hitbox_y=(x+w/2,y+h/2)
    
    def get_hitbox(self,*args):
        x=self.image.x + (self.image.width *0.25)
        y = self.image.y + (self.image.height *0.1)
        width = self.image.width * 0.5
        height = self.image.height * 0.35
        self.get_center_hitbox(x,y,width,height)
        return [x, y, width, height]
    
    def perder_i_frames(self,*args):
        self.i_frames=False

    def on_i_frames(self,*args):
        if self.i_frames:
            Clock.schedule_once(self.perder_i_frames,self.i_frames_time)
        
    def drop(self, *args):
        if not self.list_drops:
            print("sem drops")
            return
        for drop, quantidade in self.list_drops.items():
            self.parent.player.inventario[drop] = self.parent.player.inventario.get(drop, 0) + quantidade
        print("Inventário após drops:", self.parent.player.inventario)

    
    def morrer(self,*args):
        self.vivo=False
        self.estado="morto"
        self.speed_x=0
        self.speed_y=0
        if not self.parent.player==self:
            self.drop()

    def on_vida(self,*args):
        self.i_frames=True
        vida_mod=100*self.vida/self.vida_maxima
        if vida_mod<0:
            vida_mod=0
        try:
            self.barra_vida.modificador=vida_mod
        except:
            print("sem barra_vida")
        if self.vida<=0:
            self.morrer()
    



def mover(ent,dx,dy):
    ent.speed_x=dx
    ent.speed_y=dy

def perseguir(rastreador):
    dx=0
    dy=0
    if rastreador.player.image.center_x>rastreador.image.center_x:
        dx=1
    elif rastreador.player.image.center_x<rastreador.image.center_x:
        dx=-1
    if rastreador.player.image.center_y>rastreador.image.center_y:
        dy=1
    elif rastreador.player.image.center_y<rastreador.image.center_y:
        dy=-1
    mover(rastreador,dx,dy)

def rastrear(rastreador):
    try:
        if (distancia(rastreador)<=rastreador.raio_visao):
            rastreador.alvo=True
    except:
        pass

def atacar(atacante,alvo=None):
    if alvo is None:
        alvo=atacante.player
    if not alvo.i_frames:
        atacante.estado="atacando"
        knockback=1
        if not alvo.vivo:
            knockback=2
        if atacante.facing_right:
            alvo.image.x+=atacante.repulsao*knockback
        else:
            alvo.image.x-=atacante.repulsao*knockback
        alvo.image.y+=atacante.speed_y*atacante.repulsao*knockback
        atacante.speed_x=0
        atacante.speed_y=0
        alvo.vida-=atacante.dano
        print(atacante.estado)
    return

def distancia(ent1,ent2=None):
    if ent2 is None:
        try:
            d1,d2=ent1.player.center_hitbox_x-ent1.center_hitbox_x, ent1.player.center_hitbox_y-ent1.center_hitbox_y
            return ((d1*d1 + d2*d2)**0.5)
        except:
            pass
    else:
        d1,d2=ent2.center_hitbox_x-ent1.center_hitbox_x, ent2.center_hitbox_y-ent1.center_hitbox_y
        return ((d1*d1 + d2*d2)**0.5)

#funcao destinada a colocar as possibilidades de acoes de entidades basicas
def ia_base():
    acoes={
        "perseguir":perseguir,
        "rastrear":rastrear,
        "atacar":atacar
        }
    return acoes


class Rato(BasicEnt):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sources["idle"]="assets/sprites/rato/idle.png"
        self.sources["running"]="assets/sprites/rato/running.png"
        self.sources["morto"]="assets/sprites/rato/morto.png"
        self.sources["garras"]="assets/sprites/rato/garras.png"
        self.idle_frames=2
        self.running_frames=2
        self.atacando_frames=2
        
        self.atualizar()
        self.acoes=ia_base()
        Clock.schedule_interval(self.ia,1/10)
        Clock.schedule_once(self.add_player,2)
        self.atributos()
    
    def atributos(self,*args):
        self.raio_visao=300
        self.image.size=(90,90)
        self.vida_maxima=30
        self.vida=30
        self.dano=5
        self.velocidade=1.5
        self.list_drops["carne"]=random.randint(0,2)
    
    def add_player(self,*args):
        self.player=self.parent.player

    def ia(self,*args):
        if not self.vivo:
            return
        if self.alvo:
            if distancia(self)<=self.alcance_fisico and not self.atacando:
                self.ataque_name="garras"
                self.acoes["atacar"](self)
                self.atacando=True
                Clock.schedule_once(self.atualizar_atacando,0.4)
            else:
                self.acoes["perseguir"](self)
        else:
            self.acoes["rastrear"](self)
        pass
    
    def atualizar_atacando(self,*args):
        self.atacando=False
        if self.speed_x or self.speed_y:
            self.estado = "running"
        else:
            self.estado = "idle"

class Player(BasicEnt):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sources["idle"]="assets/sprites/player/idle.png"
        self.sources["running"]="assets/sprites/player/running.png"
        self.sources["morto"]="assets/sprites/player/morto.png"
        self.sources["soco"]="assets/sprites/player/soco.png"
        self.idle_frames=2
        self.running_frames=4
        self.atacando_frames=3

        self.atualizar()
        self.repulsao=20
        self.alcance_fisico=90
        self.acoes={"atacar":self.atacar}
        self.acao=""
        Clock.schedule_interval(self.verificar_acao,1/20)

    def atacar(self,*args):
        if self.atacando:
            self.acao=""
            return
        self.atacando=True
        self.ataque_name="soco"
        print("ataque gerado")
        for ent in self.parent.ents:
            if not ent==self:
                if distancia(self,ent)<=self.alcance_fisico:
                    if self.facing_right and ent.image.x>=self.image.x:
                        atacar(self,ent)
                        print("player atacou")
                    elif not self.facing_right and ent.image.x<=self.image.x:
                        atacar(self,ent)
                        print("player atacou")
        Clock.schedule_once(self.remover_ataque,0.4)
    
    def remover_ataque(self,*args):
        self.atacando=False
        if self.speed_x or self.speed_y:
            self.estado = "running"
        else:
            self.estado = "idle"
    
    def verificar_acao(self, *args):
        if not self.acao or not self.vivo:
            return

        action = self.acoes.get(self.acao)
        if action and callable(action):
            try:
                action() 
            except Exception as e:
                print("Erro ao executar ação", self.acao, ":", e)
        else:
            self.acao = ""