from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.core.window import Window
import json

from utils.customizedButton import CustomizedButton
from utils.resourcesPath import resource_path
from screens.shared import STD_font_size, configuracoes

class ConfiguracoesScreen(Screen):
    def __init__(self, GameScreenManager=None, **kwargs):
        super().__init__(**kwargs)
        self.GameScreenManager=GameScreenManager
        self.configs=configuracoes()
        self.teclado=self.configs["teclado"]
        self.configs_path=resource_path("saved/configuracoes.json")
        if self.teclado:
            self.input='Modo teclado'
        else:
            self.input='Modo toque'
        if self.configs["font"]==35:
            self.font='fonte normal'
        else:
            self.font='fonte grande'

        self.layout=FloatLayout()
        layout_inputs=FloatLayout(
            size_hint=(0.5,0.08),
            pos_hint={'center_x':0.5,'center_y':0.4}
            )
        layout_font=FloatLayout(
            size_hint=(0.5,0.08),
            pos_hint={'center_x':0.5,'center_y':0.3}
            )
        self.label_inputs=Label(
            text='Layout de controle:',
            font_size=STD_font_size,
            size_hint=(0.5,1),
            pos_hint={'center_x':0.2,'center_y':0.5}
            )
        self.button_inputs=CustomizedButton(
            text=f'{self.input}',
            font_size=STD_font_size*0.8,
            size_hint=(0.5,1),
            pos_hint={'center_x':0.78,'center_y':0.5}
            )
        
        self.label_font=Label(
            text='Tamanho da fonte:',
            font_size=STD_font_size,
            size_hint=(0.5,1),
            pos_hint={'center_x':0.2,'center_y':0.5}
            )
        self.button_font=CustomizedButton(
            text=f'{self.font}',
            font_size=STD_font_size*0.8,
            size_hint=(0.5,1),
            pos_hint={'center_x':0.78,'center_y':0.5}
            )
        
        self.button_inputs.bind(on_release=self.trocar_input)
        layout_inputs.add_widget(self.button_inputs)
        layout_inputs.add_widget(self.label_inputs)
        self.layout.add_widget(layout_inputs)

        self.button_font.bind(on_release=self.tamanho_da_fonte)
        layout_font.add_widget(self.button_font)
        layout_font.add_widget(self.label_font)
        self.layout.add_widget(layout_font)

        self.add_widget(self.layout)

        Window.bind(on_keyboard=self.ir_para_menu)
    

    def trocar_input(self,*args):
        with open(self.configs_path,"r",encoding="utf-8") as config:
            self.configs=json.load(config)
        self.configs["teclado"]=not self.configs["teclado"]
        with open(self.configs_path,"w",encoding="utf-8") as old_config:
            json.dump(self.configs,old_config)
        if self.configs["teclado"]:
            self.input='Modo teclado'
        else:
            self.input='Modo toque'
        self.button_inputs.text=f'{self.input}'
    

    def tamanho_da_fonte(self,*args):

        global STD_font_size

        with open(self.configs_path,"r",encoding="utf-8") as config:
            self.configs=json.load(config)

        if self.configs["font"]==35:
            self.configs["font"]=40
            self.font='fonte grande'
        else:
            self.configs["font"]=35
            self.font='fonte normal'
        
        STD_font_size=self.configs["font"]

        with open(self.configs_path,"w",encoding="utf-8") as old_config:
            json.dump(self.configs,old_config)
        self.button_font.text=f'{self.font}'
    

    def ir_para_menu(self,window,key,*args):
        if key==27:
            self.GameScreenManager.current='menu'
            return True
