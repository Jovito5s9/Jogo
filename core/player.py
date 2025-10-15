from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.properties import OptionProperty 

class BasicEnt(FloatLayout):
    estado=OptionProperty ("idle",
    options=("idle","running"))
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.size = (32, 32)
        self.pos = (100, 100)
        self.recompensa = 0
        self.vida = 100
        self.dano = 5
        self.velocidade = 3
        self.speed_x=0
        self.speed_y=0
        self.facing_right = True

        self.alvo=False
        self.player=None
        
        self.hitbox=( )

        self.sources={}

        
        
    def atualizar(self,*args):
        # Carrega o sprite sheet
        self.sprite_sheet = Image(source=self.sources.get("idle")).texture
        self.frame_width = 32
        self.frame_height = 32
        self.total_frames = 2
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
        Clock.schedule_interval(self.animation, 0.3)
        self.image.bind(pos=self.on_image_pos)

    def atualizar_pos(self,*args):
        if self.speed_x > 0:
            self.facing_right = True
        elif self.speed_x < 0:
            self.facing_right = False

        self.image.x+=self.speed_x*self.velocidade 
        self.image.y+=self.speed_y*self.velocidade 
        if self.speed_x!=0 or self.speed_y:
            self.estado="running"
        else:
            self.estado="idle"
        self.hitbox = self.get_hitbox()

    def on_estado(self,*args):
        if self.estado=="idle":
            self.sprite_sheet = Image(source=self.sources.get("idle")).texture
            self.frame_width = 32
            self.frame_height = 32
            self.total_frames = 2
            self.current_frame = 0
        elif self.estado=="running":
            self.sprite_sheet = Image(source=self.sources.get("running")).texture
            self.frame_width = 32
            self.frame_height = 32
            self.total_frames = 4
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
    
    def get_hitbox(self,*args):
        x=self.image.x + (self.image.width *0.25)
        y = self.image.y + (self.image.height *0.1)
        width = self.image.width * 0.5
        height = self.image.height * 0.35
        return [x, y, width, height]



def mover(ent,dx,dy):
    ent.speed_x=dx
    ent.speed_y=dy

def perseguir(rastreador):
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
    if alvo is not None:
        if distancia(atacante,alvo):
            alvo.vida-=atacante.dano
    else:
        if distancia(atacante):
            atacante.player.vida-=atacante.dano

def distancia(ent1,ent2=None):
    if ent2 is None:
        try:
            d1,d2=abs(ent1.player.image.center_x-ent1.image.center_x), abs(ent1.player.image.center_y-ent1.image.center_y)
            return ((d1*d1 + d2*d2)**0.5)
        except:
            pass
    else:
        d1,d2=abs(ent2.image.center_x-ent1.image.center_x), abs(ent2.image.center_y-ent1.image.center_y)
        return ((d1*d1 + d2*d2)**0.5)

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
        self.atualizar()
        self.image.size=(90,90)
        Clock.schedule_once(self.add_player,2)
        self.acoes=ia_base()
        self.raio_visao=80
        Clock.schedule_interval(self.ia,1/20)
    
    def add_player(self,*args):
        self.player=self.parent.player

    def ia(self,*args):
        if self.alvo:
            self.acoes["perseguir"](self)
        else:
            self.acoes["rastrear"](self)
        pass


class Player(BasicEnt):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sources["idle"]="assets/sprites/player/idle.png"
        self.sources["running"]="assets/sprites/player/running.png"
        self.atualizar()
        self.acoes={}