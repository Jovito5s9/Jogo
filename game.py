from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock 
from core.player import BasicEnt
from core.world import World
from utils.joystick import Joystick 
import json

class Interface(FloatLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.size_hint = None, None
        self.configs=[]
        self.configuracoes()

        if not self.configs["teclado"]:
            self.add_joytick()
    
    def add_joytick(self):
        self.joystick = Joystick(size_hint=(None, None), size=(400, 400), pos_hint={'center_x': 2, 'center_y': 2})
        self.add_widget(self.joystick)
    
    def configuracoes(self):
        try:
            with open("configuracoes.json","r",encoding="utf-8") as config:
                self.configs=json.load(config)
        except:
            with open("configuracoes.json","w",encoding="utf-8") as config:
                newconfig={"teclado": False}
                json.dump(newconfig, config)


class Game(FloatLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.world=World()
        self.add_widget(self.world)
        
        self.player=BasicEnt()
        self.world.player=self.player
        
        self.world.create(12,12)
        
        self.interface=Interface()
        self.add_widget(self.interface)
        
        Clock.schedule_interval(self.joystick_movs, 1/20)
        
        #self.add_widget(BasicEnt())
    def joystick_movs(self,*args):
        self.player.speed_x=self.interface.joystick.x_value
        self.player.speed_y=self.interface.joystick.y_value