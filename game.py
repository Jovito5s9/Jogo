from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock 
from kivy.core.window import Window
from core.player import Player
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
        
        self.player=Player()
        self.world.player=self.player
        
        self.world.create(12,12)
        

    def pre_enter(self,*args):
        self.interface=Interface()
        self.add_widget(self.interface)
        if not self.interface.configs["teclado"]:
            Clock.schedule_interval(self.joystick_movs, 1/20)
        else:
            self.keyboard_active()
            Clock.schedule_interval(self.keyboard_movs, 1/20)

    def pre_leave(self,*args):
        if not self.interface.configs["teclado"]:
            Clock.unschedule_interval(self.joystick_movs, 1/20)
        else:
            self.keyboard_desactive()
            Clock.unschedule_interval(self.keyboard_movs, 1/20)
        self.remove_widget(self.interface)

        

    def joystick_movs(self,*args):
        self.player.speed_x=self.interface.joystick.x_value
        self.player.speed_y=self.interface.joystick.y_value
    
    def keyboard_active(self,*args):
        self.key_pressed=set()
        Window.bind(on_key_down=self.on_key_down)
        Window.bind(on_key_up=self.on_key_up)

    def keyboard_desactive(self,*args):
        self.key_pressed=set()
        Window.unbind(on_key_down=self.on_key_down)
        Window.unbind(on_key_up=self.on_key_up)
    
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
        self.button_configs = Button(
            text='Configurações',
            size_hint=(0.25, 0.08),
            pos_hint={'center_x': 0.5, 'center_y': 0.2}
        )
        self.button_configs.bind(on_release=self.configurar)
        self.button_sair = Button(
            text='Sair',
            size_hint=(0.25, 0.08),
            pos_hint={'center_x': 0.5, 'center_y': 0.1}
        )
        self.button_sair.bind(on_release=self.sair)

        self.layout.add_widget(self.logo)
        self.layout.add_widget(self.button_play)
        self.layout.add_widget(self.button_configs)
        self.layout.add_widget(self.button_sair)

    def jogar(self,*args):
        GameScreenManager.current='game'
    
    def configurar(self,*args):
        GameScreenManager.current='configurações'
    
    def sair(self,*args):
        jogo=App.get_running_app()
        jogo.stop()


class ConfiguracoesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with open("configuracoes.json","r",encoding="utf-8") as config:
                self.configs=json.load(config)
        self.teclado=self.configs["teclado"]
        if self.teclado:
            self.input='Modo teclado'
        else:
            self.input='Modo toque'

        self.layout=FloatLayout()
        layout_inputs=FloatLayout(
            size_hint=(0.5,0.08),
            pos_hint={'center_x':0.5,'center_y':0.4}
            )
        self.label_inputs=Label(
            text='Layout de controle:',
            font_size=30,
            size_hint=(0.5,1),
            pos_hint={'center_x':0.2,'center_y':0.5}
            )
        self.button_inputs=Button(
            text=f'{self.input}',
            font_size=25,
            size_hint=(0.5,1),
            pos_hint={'center_x':0.78,'center_y':0.5}
            )
        self.button_inputs.bind(on_release=self.trocar_input)
        layout_inputs.add_widget(self.button_inputs)
        layout_inputs.add_widget(self.label_inputs)
        self.layout.add_widget(layout_inputs)

        self.add_widget(self.layout)

        Window.bind(on_keyboard=self.ir_para_menu)
    
    def trocar_input(self,*args):
        with open("configuracoes.json","r",encoding="utf-8") as config:
            self.configs=json.load(config)
        self.configs["teclado"]=not self.configs["teclado"]
        with open("configuracoes.json","w",encoding="utf-8") as old_config:
            json.dump(self.configs,old_config)
        if self.configs["teclado"]:
            self.input='Modo teclado'
        else:
            self.input='Modo toque'
        self.button_inputs.text=f'{self.input}'
    
    def ir_para_menu(self,window,key,*args):
        if key==27:
            GameScreenManager.current='menu'
            return True

class GameScreen(Screen): 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.ir_para_menu)
    
    def on_pre_enter(self, *args):
        try:
            self.game.pre_enter()
        except:
            self.game=Game()
            self.add_widget(self.game)
            self.game.pre_enter()
    
    def ir_para_menu(self,window,key,*args):
        if key==27:
            GameScreenManager.current='menu'
            return True
        

GameScreenManager=ScreenManager()

GameScreenManager.add_widget(MenuScreen(name='menu'))
GameScreenManager.add_widget(GameScreen(name='game'))
GameScreenManager.add_widget(ConfiguracoesScreen(name='configurações'))