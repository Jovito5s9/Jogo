from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock 
from core.player import BasicEnt
from core.world import World
from utils.joystick import Joystick 

class Interface(FloatLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.size_hint = None, None
        self.joystick = Joystick(size_hint=(None, None), size=(400, 400), pos_hint={'center_x': 2, 'center_y': 2})
        self.add_widget(self.joystick)

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