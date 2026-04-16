from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import ButtonBehavior
from kivy.utils import platform
from kivy.app import App

from utils.customizedButton import CustomizedButton
from utils.resourcesPath import resource_path
from screens.shared import STD_font_size, configuracoes

import json
import subprocess
import webbrowser

def open_link(url):
    try:
        if platform == "linux":
            subprocess.Popen(["xdg-open", url])
        else:
            webbrowser.open(url)
    except Exception as e:
        print("Erro ao abrir link:", e)

class InteractiveImage(ButtonBehavior, Image):
    pass

class MenuScreen(Screen):
    def __init__(self, GameScreenManager=None, **kwargs):
        super().__init__(**kwargs)
        global STD_font_size
        self.GameScreenManager=GameScreenManager

        self.linguagem=configuracoes().get("linguagem","pt")
        self.ui_texts = json.load(open(resource_path(f"content/ui/{self.linguagem}.json"), "r", encoding="utf-8"))

        background=Image(
            source=resource_path("assets/geral/outside_background.png"),
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
            text=self.ui_texts["play"],
            font_size=STD_font_size*1.2,
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            size_hint=(0.25, 0.08),
            pos_hint={'center_x': 0.5, 'center_y': 0.3}
        )
        self.button_play.bind(on_release=self.jogar)
        self.button_configs = CustomizedButton(
            text=self.ui_texts["settings"],
            font_size=STD_font_size*1.2,
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            size_hint=(0.25, 0.08),
            pos_hint={'center_x': 0.5, 'center_y': 0.2}
        )
        self.button_configs.bind(on_release=self.configurar)
        self.button_sair = CustomizedButton(
            text=self.ui_texts["exit"],
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


        self.redes_layout = BoxLayout(
            size_hint=(None, None),
            height=60,
            pos_hint={'center_x': 0.05, 'center_y': 0.035},
            spacing=15
        )
        self.layout.add_widget(self.redes_layout)
        self.follow_label = Label(
            text=self.ui_texts["follow_us"],
            font_size=STD_font_size * 0.9,
            color=(0.2, 0.2, 0.2, 1),
            pos_hint={'center_x': 0.055, 'center_y': 0.09},
            bold=True
        )
        self.layout.add_widget(self.follow_label)
        self.instagram_button = InteractiveImage(
            source=resource_path("assets/geral/redes_sociais/Instagram.png"),
            size_hint=(None, None),
            size=(60, 60)
        )
        self.instagram_button.bind(on_release=self.go_to_instagram)
        self.redes_layout.add_widget(self.instagram_button)
        self.facebook_button = InteractiveImage(
            source=resource_path("assets/geral/redes_sociais/Facebook.png"),
            size_hint=(None, None),
            size=(60, 60)
        )
        self.facebook_button.bind(on_release=self.go_to_facebook)
        self.redes_layout.add_widget(self.facebook_button)


    def jogar(self,*args):
        self.GameScreenManager.current='game'
    
    def configurar(self,*args):
        self.GameScreenManager.current='configurações'
    
    def sair(self,*args):
        jogo=App.get_running_app()
        jogo.stop()

    def go_to_instagram(self, *args):
        open_link("https://www.instagram.com/solarburn.studio/")

    def go_to_facebook(self, *args):
        open_link("https://www.facebook.com/people/SolarBurn-Studio/61575485297715/")