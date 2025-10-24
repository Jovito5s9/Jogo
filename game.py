from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.properties import OptionProperty
from kivy.clock import Clock 
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager,Screen
from kivy.uix.scrollview import ScrollView

from core.player import Player
from core.world import World
from utils.joystick import Joystick 
from saved.itens_db import ITENS

import json 

class Interface(FloatLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.size_hint = None, None
        self.configs=[]
        self.configuracoes()

        if not self.configs["teclado"]:
            self.add_ui()
            
    def add_ui(self,*args):
        self.add_joytick()
        self.add_button_ataque()

        Clock.schedule_once(self.bind_buttons,1)
    
    def add_joytick(self):
        self.joystick = Joystick(size_hint=(None, None), size=(400, 400), pos_hint={'center_x': 2, 'center_y': 2})
        self.add_widget(self.joystick)
    
    def add_button_ataque(self,*args):
        self.button_ataque=Button(size=(200,200),pos_hint={'center_x' : 15,'center_y' : 7},text='ataque')
        self.add_widget(self.button_ataque)
    
    def bind_buttons(self,*args):
        self.button_ataque.bind(on_release=self.parent.ataque)
    
    def configuracoes(self):
        try:
            with open("saved/configuracoes.json","r",encoding="utf-8") as config:
                self.configs=json.load(config)
        except:
            with open("saved/configuracoes.json","w",encoding="utf-8") as config:
                newconfig={"teclado": False}
                self.configs=newconfig
                json.dump(newconfig, config)


class Game(FloatLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.world=World()
        self.add_widget(self.world)
        
        self.player=Player()
        self.world.player=self.player
        
        self.world.create(12,12)
        self.inventario_menu=False
        self.menu_player=Menu_player()
        

    def pre_enter(self,*args):
        self.interface=Interface()
        self.add_widget(self.interface)
        if not self.interface.configs["teclado"]:
            Clock.schedule_interval(self.joystick_movs, 1/20)
        else:
            self.keyboard_active()
            Clock.schedule_interval(self.keyboard_actions, 1/20)
        Clock.schedule_interval(self.menus,1/10)

    def pre_leave(self,*args):
        if not self.interface.configs["teclado"]:
            Clock.unschedule_interval(self.joystick_movs, 1/20)
        else:
            self.keyboard_desactive()
            Clock.unschedule_interval(self.keyboard_actions, 1/20)
        self.remove_widget(self.interface)

    def menus(self,*args):
        if self.inventario_menu:
            try:
                self.add_widget(self.menu_player)
            except:
                pass
        else:
            try:
                self.remove_widget(self.menu_player)
            except:
                pass
    

    def joystick_movs(self,*args):
        self.player.speed_x=self.interface.joystick.x_value
        self.player.speed_y=self.interface.joystick.y_value
    
    def ataque(self,*args):
        self.player.acao="atacar"
    
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
        if key == 105:
            self.inventario_menu= not self.inventario_menu
    
    def on_key_up(self, window, key, *args):
        self.key_pressed.remove(key)
    
    def keyboard_actions(self,*args):
        if 32 in self.key_pressed:
            self.player.acao="atacar"
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
        

class Menu_player(Popup):
    tipo=OptionProperty ("inventario",
    options=("inventario"," "))
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title=''
        self.separator_height=0
        self.size_hint=(0.9,0.9)
        self.pos_hint={'center_x': 0.5, 'center_y': 0.5}
        self.layout=FloatLayout()
        self.add_widget(self.layout)
        self.inventario()
    
    def inventario(self, *args):
        self.scroll_view = ScrollView(
            size_hint=(1, 0.8),
            pos_hint={'center_x': 0.5, 'center_y': 0.4}
        )

        self.itens_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=15,
            padding=10
        )
        self.itens_layout.bind(minimum_height=self.itens_layout.setter('height'))

        try:
            with open("saved/player.json", "r", encoding="utf-8") as arquivo:
                player = json.load(arquivo)
                inventario = player.get("inventario", {})
            if inventario:
                for nome, quantidade in inventario.items(): 
                    info=ITENS.get(nome,{}) 
                    item = FloatLayout(
                        size_hint_y=None, 
                        height=120
                        )
                    item_image=Image( 
                        size_hint=(0.6,0.6), 
                        pos_hint={"center_x": 0.1, "center_y": 0.7}, 
                        source=info["source"] ) 
                    item_label = Label( 
                        text=f"- {nome} : {quantidade}\n {info["raridade"]}", 
                        font_size=20, 
                        size_hint=(None, None), 
                        pos_hint={"center_x": 0.1, "center_y": 0.2} 
                        ) 
                    item_descricao=Label(
                         text=f"- Descriçâo : {info["descrição"]}",
                           font_size=20,
                            size_hint=(None, None),
                            pos_hint={"center_x": 0.6, "center_y": 0.5} 
                            ) 
                    item.add_widget(item_descricao) 
                    item.add_widget(item_image) 
                    item.add_widget(item_label) 
                    self.itens_layout.add_widget(item)
            else:
                self.itens_layout.add_widget(Label(text="Sem itens", font_size=30))
        except Exception as e:
            self.itens_layout.add_widget(Label(text=str(e), font_size=30))

        self.scroll_view.add_widget(self.itens_layout)
        self.layout.add_widget(self.scroll_view)



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
        with open("saved/configuracoes.json","r",encoding="utf-8") as config:
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
        with open("saved/configuracoes.json","r",encoding="utf-8") as config:
            self.configs=json.load(config)
        self.configs["teclado"]=not self.configs["teclado"]
        with open("saved/configuracoes.json","w",encoding="utf-8") as old_config:
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