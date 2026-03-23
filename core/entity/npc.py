from core.entity.basic_ent import BasicEnt, Ballon, Menu_interact
from core.entity.interact import distancia
from kivy.clock import Clock
from kivy.core.window import Window

size = Window.height / 12.5


class NPC(BasicEnt):
    def __init__(self,nome, **kwargs):
        super().__init__(**kwargs)
        self.nome=nome
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
        self.menu_is_active=True
        self.interact_button=Ballon()
        self.interact_menu=None
        self.interactions_text=["sai daqui","..."]
        self.interactions_funcs=[self.move_gabiru,self.free_menu]
    

    def add_interact_menu(self,*args):
        self.menu_is_active=True
        if not "..." in self.interactions_text:
            self.interactions_text.append("...")
        if not self.free_menu in self.interactions_funcs:
            self.interactions_funcs.append(self.free_menu)
        self.interact_menu=Menu_interact(nome_npc=self.nome,escolhas=self.interactions_text,funcs=self.interactions_funcs)
        self.world.parent.parent.add_widget(self.interact_menu)
    
    def free_menu(self,*args):
        self.menu_is_active=False
    
    def move_gabiru(self,*args):
        self.move_to_new_grid(17,5)
    
    def move_to_new_grid(self, x=None, y=None):
        need_to_move = False

        grid_x = int(self.x / size)
        grid_y = int(self.y / size)

        dx = 0 if x is None else x - grid_x
        dy = 0 if y is None else y - grid_y

        if x is not None and grid_x == x:
            self.x = x * size
            self.speed_x = 0
        if y is not None and grid_y == y:
            self.y = y * size
            self.speed_y = 0

        if dx != 0:
            self.speed_x = 1 if dx > 0 else -1
            self.speed_y = 0
            need_to_move = True
        elif dy != 0:
            self.speed_y = 1 if dy > 0 else -1
            self.speed_x = 0
            need_to_move = True

        self.global_pos = self.pos

        if need_to_move:
            Clock.schedule_once(lambda dt: self.move_to_new_grid(x, y), 0.1)
        else:
            if self.interact_button in self.children:
                self.remove_widget(self.interact_button)


    def add_interact_button(self,*args):
        self.add_widget(self.interact_button)
        self.interact_button.pos=self.x,self.y+self.height*0.6
        self.interact_button.size=(100,100)

    def interact(self,*args):
        print("oiiii")
        pass

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
                if not self.interact_button in self.children and "tradutor" in self.player.drivers and "tradutor" in self.player.drivers_cache:
                    self.add_interact_button()
                if not self.menu_is_active:
                    if self.interact_menu in self.world.parent.parent.children:
                        self.world.parent.parent.remove_widget(self.interact_menu)

            else:
                self.atacando=False
                if self.interact_button in self.children:
                    self.remove_widget(self.interact_button)
                if self.interact_menu in self.world.parent.parent.children:
                    self.world.parent.parent.remove_widget(self.interact_menu)
                self.estado="idle"
        else: 
            self.add_player()
    
    def get_hitbox(self, *args):
        x = self.x + (self.width * 0.25)
        y = self.y - 0.05 * self.height
        width = self.width * 0.5
        height = self.height * 0.8
        self.get_center_hitbox(x, y, width, height)
        return [x, y, width, height]