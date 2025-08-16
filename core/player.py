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
        self.velocidade = 7
        self.speed_x=0
        self.speed_y=0
        self.facing_right = True
        
        self.hitbox=( )

        # Carrega o sprite sheet
        self.sprite_sheet = Image(source="assets/sprites/player/idle.png").texture
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
            self.sprite_sheet = Image(source="assets/sprites/player/idle.png").texture
            self.frame_width = 32
            self.frame_height = 32
            self.total_frames = 2
            self.current_frame = 0
        elif self.estado=="running":
            self.sprite_sheet = Image(source="assets/sprites/player/running.png").texture
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
    
    def get_hitbox(self,*args):
        x=self.image.x + (self.image.width *0.25)
        y = self.image.y + (self.image.height *0.1)
        width = self.image.width * 0.5
        height = self.image.height * 0.35
        return [x, y, width, height]

