from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout

from utils.customizedButton import CustomizedButton
from utils.resourcesPath import resource_path
from screens.shared import configuracoes

import json

class MenuPause(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game=None
        self.size_hint = (0.4,0.5)
        self.title=''
        self.background=''
        self.background_color=(0, 0, 0, 0)
        self.separator_height = 0


        self.linguagem=configuracoes().get("linguagem","pt")
        self.ui_texts = json.load(open(resource_path(f"content/ui/{self.linguagem}.json"), "r", encoding="utf-8"))

        self.layout=BoxLayout(
            orientation='vertical',
            padding=(100,30,100,30),
            spacing=50
        )

        self.button_continue = CustomizedButton(
            text=self.ui_texts["continue"],
            font_size=45,
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
        )
        self.button_continue.bind(on_release=self.continuar)
        self.button_config = CustomizedButton(
            text=self.ui_texts["settings"],
            font_size=40,
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
        )
        self.button_config.bind(on_release=self.configs)
        self.button_quit = CustomizedButton(
            text=self.ui_texts["main_menu"],
            font_size=40,
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
        )
        self.button_quit.bind(on_release=self.menu)

        self.layout.add_widget(self.button_continue)
        self.layout.add_widget(self.button_config)
        self.layout.add_widget(self.button_quit)

        self.add_widget(self.layout)
    
    def continuar(self,*args):
        self.game.pause()
        self.dismiss()
    
    def configs(self,*args):
        if self.game.parent.parent.parent.current:
            self.game.pausado=False
            self.game.parent.parent.parent.current='configurações'
            self.dismiss()

    def menu(self,*args):
        if self.game.parent.parent.parent.current:
            self.game.pausado=False
            self.game.parent.parent.parent.current='menu'
            self.dismiss()
