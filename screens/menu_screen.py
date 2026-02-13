from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.app import App

from utils.customizedButton import CustomizedButton
from utils.resourcesPath import resource_path
from screens.shared import STD_font_size

class MenuScreen(Screen):
    def __init__(self, GameScreenManager=None, **kwargs):
        super().__init__(**kwargs)
        global STD_font_size
        self.GameScreenManager=GameScreenManager
        background=Image(
            source=resource_path("assets/geral/dungeon_background.png"),
            size=self.size,
            allow_stretch=True,
            keep_ratio=False
        )
        self.add_widget(background)
        self.layout = FloatLayout()
        self.add_widget(self.layout)
        self.logo = Image(
            source=resource_path('assets/geral/logo_RadioRoots.png'),
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(0.6, 0.6),   
            pos_hint={'center_x': 0.5, 'center_y': 0.65}
        )
          
        self.button_play = CustomizedButton(
            text='Jogar',
            font_size=STD_font_size*1.2,
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            size_hint=(0.25, 0.08),
            pos_hint={'center_x': 0.5, 'center_y': 0.3}
        )
        self.button_play.bind(on_release=self.jogar)
        self.button_configs = CustomizedButton(
            text='Configurações',
            font_size=STD_font_size*1.2,
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            size_hint=(0.25, 0.08),
            pos_hint={'center_x': 0.5, 'center_y': 0.2}
        )
        self.button_configs.bind(on_release=self.configurar)
        self.button_sair = CustomizedButton(
            text='Sair',
            font_size=STD_font_size*1.2,
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            size_hint=(0.25, 0.08),
            pos_hint={'center_x': 0.5, 'center_y': 0.1}
        )
        self.button_sair.bind(on_release=self.sair)

        self.layout.add_widget(self.logo)
        self.layout.add_widget(self.button_play)
        self.layout.add_widget(self.button_configs)
        self.layout.add_widget(self.button_sair)

    def jogar(self,*args):
        self.GameScreenManager.current='game'
    
    def configurar(self,*args):
        self.GameScreenManager.current='configurações'
    
    def sair(self,*args):
        jogo=App.get_running_app()
        jogo.stop()
