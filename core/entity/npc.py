from core.entity.basic_ent import BasicEnt
from core.entity.interact import distancia

class NPC(BasicEnt):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.remove_widget(self.barra_vida)
        self.global_pos=self.pos
        self.i_frames=True
        self.sources={
            "idle":"assets/sprites/gabiru/idle.png",
            "atacando":"assets/sprites/gabiru/olhando.png"
        }
        self.idle_frames=2
        self.atacando_frames=2
        self.area_detect = 150
    
    def on_pos(self,*args):
        if self.pos!=self.global_pos:
            self.pos=self.global_pos
    
    def on_i_frames(self, *args):
        pass
    
    def ia(self,*args):
        if self.player:
            if distancia(self,self.player) <= self.area_detect:
                self.atacando=True