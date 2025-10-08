from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.clock import Clock 
from kivy.core.window import Window
from core.player import BasicEnt
from core.world import World
from utils.joystick import Joystick 
from kivy.uix.screenmanager import ScreenManager,Screen
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
        
        if not self.interface.configs["teclado"]:
            Clock.schedule_interval(self.joystick_movs, 1/20)
        else:
            self.keyboard_active()
            Clock.schedule_interval(self.keyboard_movs, 1/20)
        

    def joystick_movs(self,*args):
        self.player.speed_x=self.interface.joystick.x_value
        self.player.speed_y=self.interface.joystick.y_value
    
    def keyboard_active(self,*args):
        self.key_pressed=set()
        Window.bind(on_key_down=self.on_key_down)
        Window.bind(on_key_up=self.on_key_up)
    
    def on_key_down(self, window, key, *args):
        self.key_pressed.add(key)
    
    def on_key_up(self, window, key, *args):
        self.key_pressed.remove(key)
    
    def keyboard_movs(self,*args):
        if 119 in self.key_pressed:
            self.player.speed_y=0.9
        elif 115 in self.key_pressed:
            self.player.speed_y=-0.9
        else:
            self.player.speed_y=0

        if 100 in self.key_pressed:
            self.player.speed_x=0.9
        elif 97 in self.key_pressed:
            self.player.speed_x=-0.9
        else:
            self.player.speed_x=0


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()
        self.add_widget(self.layout)
        self.logo = Image(
            source='assets/geral/logo_RadioRoots.png',
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(0.4, 0.4),   
            pos_hint={'center_x': 0.5, 'center_y': 0.65}
        )
          
        self.button_play = Button(
            text='Jogar',
            size_hint=(0.25, 0.08),
            pos_hint={'center_x': 0.5, 'center_y': 0.3}
        )
        self.button_play.bind(on_release=self.jogar)
        self.layout.add_widget(self.logo)
        self.layout.add_widget(self.button_play)

    def jogar(self,*args):
        GameScreenManager.current='game'


class GameScreen(Screen): 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Game())

GameScreenManager=ScreenManager()
GameScreenManager.add_widget(MenuScreen(name='menu'))
GameScreenManager.add_widget(GameScreen(name='game'))