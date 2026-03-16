from core.entity.basic_ent import BasicEnt
from core.entity.interact import distancia
from kivy.clock import Clock

class NPC(BasicEnt):
    def __init__(self,nome, **kwargs):
        super().__init__(**kwargs)
        self.global_pos=self.pos
        self.i_frames=True
        self.sources={
            "idle":"assets/sprites/gabiru/idle.png",
            "atacando":"assets/sprites/gabiru/olhando.png"
        }
        self.idle_frames=2
        self.atacando_frames=2
        self.frame_height=self.frame_width=32
        self.area_detect = 150
        self.hitbox=self.get_hitbox()
        self.atualizar()
        self.size=(100,100)
        Clock.schedule_interval(self.ia, 1/10)
        self.add_player()
        self.pos=2000,2000
    
    def on_pos(self,*args):
        if not hasattr(self,"global_pos"):
            return
        if self.pos!=self.global_pos:
            self.pos=self.global_pos
    
    def on_i_frames(self, *args):
        pass

    
    def ia(self,*args):
        if self.pos!=self.global_pos:
            self.pos=self.global_pos
        if hasattr(self,"barra_vida") and self.barra_vida.parent==self:
            self.remove_widget(self.barra_vida)
        if self.player:
            if distancia(self,self.player) <= self.area_detect:
                self.atacando=True
            else:
                self.atacando=False
                self.estado="idle"
        else: 
            self.add_player()
            print(self.pos,self.global_pos)
    
    def get_hitbox(self, *args):
        x = self.x + (self.width * 0.25)
        y = self.y - 0.05 * self.height
        width = self.width * 0.5
        height = self.height * 0.7
        self.get_center_hitbox(x, y, width, height)
        return [x, y, width, height]