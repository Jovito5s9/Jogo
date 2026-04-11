from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.core.window import Window
import json
import os

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
        self.linguagem = self.configs["linguagem"]
        fps = self.configs["fps"]
        self.fps_texts = {
            30: "low",
            60: "medium",
            120: "high"
        }
        self.ui_texts = json.load(open(resource_path(f"content/ui/{self.linguagem}.json"), "r", encoding="utf-8"))
        if self.teclado:
            self.input=self.ui_texts["keyboard_mode"]
        else:
            self.input=self.ui_texts["touch_mode"]
        if self.configs["font"]==35:
            self.font=self.ui_texts["low_font_size"]
        else:
            self.font=self.ui_texts["high_font_size"]

        self.layout=FloatLayout()
        layout_inputs=FloatLayout(
            size_hint=(0.5,0.08),
            pos_hint={'center_x':0.5,'center_y':0.4}
            )
        layout_font=FloatLayout(
            size_hint=(0.5,0.08),
            pos_hint={'center_x':0.5,'center_y':0.3}
            )
        layout_linguagem=FloatLayout(
            size_hint=(0.5,0.08),
            pos_hint={'center_x':0.5,'center_y':0.2}
            )
        layout_fps=FloatLayout(
            size_hint=(0.5,0.08),
            pos_hint={'center_x':0.5,'center_y':0.1}
            )


        self.label_inputs=Label(
            text=self.ui_texts["control_layout"],
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
            text=self.ui_texts["font_size"],
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


        self.label_linguagem=Label(
            text=self.ui_texts["language"],
            font_size=STD_font_size,
            size_hint=(0.5,1),
            pos_hint={'center_x':0.2,'center_y':0.5}
            )
        self.button_linguagem=CustomizedButton(
            text=f'{self.ui_texts["language"]}: {self.configs["linguagem"]}',
            font_size=STD_font_size*0.8,
            size_hint=(0.5,1),
            pos_hint={'center_x':0.78,'center_y':0.5}
            )
        

        self.label_fps=Label(
            text=self.ui_texts["frame_rate"],
            font_size=STD_font_size,
            size_hint=(0.5,1),
            pos_hint={'center_x':0.2,'center_y':0.5}
            )
        self.button_fps=CustomizedButton(
            text=f'{self.ui_texts.get(self.fps_texts.get(fps, fps), fps)}',
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

        self.button_linguagem.bind(on_release=self.trocar_linguagem)
        layout_linguagem.add_widget(self.button_linguagem)
        layout_linguagem.add_widget(self.label_linguagem)
        self.layout.add_widget(layout_linguagem)

        self.button_fps.bind(on_release=self.trocar_fps)
        layout_fps.add_widget(self.button_fps)
        layout_fps.add_widget(self.label_fps)
        self.layout.add_widget(layout_fps)

        self.add_widget(self.layout)

        Window.bind(on_keyboard=self.ir_para_menu)
    

    def trocar_input(self,*args):
        with open(self.configs_path,"r",encoding="utf-8") as config:
            self.configs=json.load(config)
        self.configs["teclado"]=not self.configs["teclado"]
        with open(self.configs_path,"w",encoding="utf-8") as old_config:
            json.dump(self.configs,old_config)
        if self.configs["teclado"]:
            self.input=self.ui_texts["keyboard_mode"]
        else:
            self.input=self.ui_texts["touch_mode"]
        self.button_inputs.text=f'{self.input}'
    

    def tamanho_da_fonte(self,*args):

        global STD_font_size

        with open(self.configs_path,"r",encoding="utf-8") as config:
            self.configs=json.load(config)

        if self.configs["font"]==35:
            self.configs["font"]=40
            self.font=self.ui_texts["high_font_size"]
        else:
            self.configs["font"]=35
            self.font=self.ui_texts["low_font_size"]

        STD_font_size=self.configs["font"]

        with open(self.configs_path,"w",encoding="utf-8") as old_config:
            json.dump(self.configs,old_config)
        self.button_font.text=f'{self.font}'

    def trocar_linguagem(self,*args):
        with open(self.configs_path,"r",encoding="utf-8") as config:
            if self.configs != json.load(config):
                self.configs=json.load(config)
        linguagens = os.listdir(resource_path("content/itens"))
        linguagens = [linguagem.split(".")[0] for linguagem in linguagens if linguagem.endswith(".json")]
        current_index = linguagens.index(self.configs.get("linguagem", "pt"))
        next_index = (current_index + 1) % len(linguagens)
        self.configs["linguagem"] = linguagens[next_index]
        self.linguagem = self.configs["linguagem"]
        self.ui_texts = json.load(open(resource_path(f"content/ui/{self.linguagem}.json"), "r", encoding="utf-8"))
        with open(self.configs_path,"w",encoding="utf-8") as old_config:
            json.dump(self.configs,old_config)
        self.button_linguagem.text=f'{self.ui_texts["language"]}: {self.configs["linguagem"]}'
        self.remove_widget(self.layout)
        self.layout=FloatLayout()
        self.__init__(GameScreenManager=self.GameScreenManager)

    def trocar_fps(self,*args):
        fps_list = [30, 60, 120]
        with open(self.configs_path,"r",encoding="utf-8") as config:
            if self.configs != json.load(config):
                self.configs=json.load(config)
        current_index = fps_list.index(self.configs.get("fps", 60))
        next_index = (current_index + 1) % len(fps_list)
        self.configs["fps"] = fps_list[next_index]
        self.fps = self.configs["fps"]
        self.ui_texts = json.load(open(resource_path(f"content/ui/{self.linguagem}.json"), "r", encoding="utf-8"))
        with open(self.configs_path,"w",encoding="utf-8") as old_config:
            json.dump(self.configs,old_config)
        self.button_fps.text=f'{self.ui_texts.get(self.fps_texts.get(self.configs["fps"], self.configs["fps"]))}'
    

    def ir_para_menu(self,window,key,*args):
        if key==27:
            screen = self.GameScreenManager.get_screen('menu').__init__(GameScreenManager=self.GameScreenManager)
            self.GameScreenManager.current='menu'
            return True
