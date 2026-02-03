from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.properties import OptionProperty
from kivy.clock import Clock 
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager,Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.behaviors import ButtonBehavior

from core.player import Player
from core.world import World
from utils.joystick import Joystick 
from saved.itens_db import ITENS
from core.BitCoreSkills import NAME_TO_SKILL_ID
from utils.resourcesPath import resource_path
from utils.customizedButton import CustomizedButton
from functools import partial
import json
import os

STD_font_size=30

def configuracoes():
        global STD_font_size
        try:
            with open("saved/configuracoes.json","r",encoding="utf-8") as config:
                configs=json.load(config)
            if not "font" in configs:
                with open("saved/configuracoes.json","w",encoding="utf-8") as config:
                    configs["font"]=30
                    json.dump(configs,config)
        except:
            with open("saved/configuracoes.json","w",encoding="utf-8") as config:
                newconfig={
                    "teclado": False,
                    "font": 30
                    }
                configs=newconfig
                json.dump(newconfig, config)
        if STD_font_size!=configs["font"]:
            STD_font_size=configs["font"]
        return configs

class InteractiveImage(ButtonBehavior, Image):
    pass

class Interface(FloatLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.configs = configuracoes()
        std_size=0.1
        self.fixed_w=self.height*std_size
        self.fixed_h=(self.fixed_w/self.height)
        self.fixed_w=std_size
        self.fixed_size=(self.fixed_w,self.fixed_h)

        self.joystick=None
        self.button_ataque=None
        self.button_quebrar=None
        self.button_menu=None
        self.joystick_bind=None
        self.button_ataque_bind=None
        self.button_quebrar_bind=None
        self.button_menu_player_bind=None

        self.mobile_layout=FloatLayout()

        self.atualizar()
        
    def atualizar(self, *args):
        new_cfg = configuracoes()
        if new_cfg != self.configs:
            self.configs = new_cfg

        self.remove_ui()
        if not self.configs["teclado"]:
            self.add_ui()
            
    def add_ui(self,*args):
        if not self.joystick:
            self.add_joytick()
        if not self.button_ataque:
            self.add_button_ataque()
        if not self.button_quebrar:
            self.add_button_quebrar()
        self.add_button_menu_player()

        if not self.mobile_layout in self.children:
            self.add_widget(self.mobile_layout)

        Clock.schedule_once(self.bind_buttons,1)
    
    def add_joytick(self):
        self.joystick = Joystick(
            size_hint=(None, None), 
            size=(800, 800), 
            pos_hint={'center_x': 0.150, 'center_y': 0.275}
            )
        self.mobile_layout.add_widget(self.joystick)#allowstretchg
    
    def add_button_ataque(self,*args):
        self.button_ataque=InteractiveImage(
            size_hint=self.fixed_size,
            pos_hint={'center_x' : 0.875,'center_y' : 0.7},
            source=resource_path("assets/ui/soco.png"),
            allow_stretch=True,
            keep_ratio=False
            )
        self.mobile_layout.add_widget(self.button_ataque)
    
    def add_button_quebrar(self,*args):
        self.button_quebrar=InteractiveImage(
            size_hint=self.fixed_size,
            pos_hint={'center_x' : 0.825,'center_y' : 0.6},
            source=resource_path("assets/ui/golpe_pesado.png"),
            allow_stretch=True,
            keep_ratio=False
            )
        self.mobile_layout.add_widget(self.button_quebrar)
    
    def add_button_menu_player(self,*args):
        self.button_menu=InteractiveImage(
            size_hint=self.fixed_size,
            pos_hint={'center_x' : 0.5,'center_y' : 0.925},
            source=resource_path("assets/ui/menu.png"),
            allow_stretch=True,
            keep_ratio=False
            )
        self.add_widget(self.button_menu)
    
    def bind_buttons(self, *args):
        if self.button_ataque:
            self.button_ataque.bind(on_release=self.parent.ataque)
        if self.button_quebrar:
            self.button_quebrar.bind(on_release=self.parent.quebrar)
        if self.button_menu:
            self.button_menu.bind(on_release=self.parent.menu_window)
        self._bind_event = None
    
    def unbind_buttons(self, *args):
        if self.button_ataque:
            try:
                self.button_ataque.unbind(on_release=self.parent.ataque)
            except Exception:
                pass
        if self.button_quebrar:
            try:
                self.button_quebrar.unbind(on_release=self.parent.quebrar)
            except Exception:
                pass
        if self.button_menu:
            try:
                self.button_menu.unbind(on_release=self.parent.menu_window)
            except Exception:
                pass      
    
    def remove_ui(self,*args):
        self.unbind_buttons()
        if self.mobile_layout.parent:
            self.remove_widget(self.mobile_layout)

class Game(FloatLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.world=World()
        self.add_widget(self.world)
        
        self.player=Player()
        self.world.player=self.player
        self.joystick_clock=None
        self.keyboard_clock = None
        self._joystick_start_event = None
        
        self.world.create(20,15)
        self.inventario_menu=False
        self.menu_player=Menu_player()
        self.menu_player.player=self.player

        self.interface = Interface()
        self.add_widget(self.interface)
        

    def pre_enter(self, *args):
        if self.joystick_clock:
            self.joystick_clock.cancel()
            self.joystick_clock = None

        if self._joystick_start_event:
            self._joystick_start_event.cancel()
            self._joystick_start_event = None

        if self.keyboard_clock:
            self.keyboard_clock.cancel()
            self.keyboard_clock = None

        self.keyboard_desactive()
        if self.interface.configs["teclado"] != configuracoes()["teclado"]:
            self.interface.atualizar()
        if not self.interface.configs["teclado"]:
            if getattr(self.interface, "joystick", None) and self.interface.joystick.parent:
                if not self.joystick_clock:
                    self.joystick_clock = Clock.schedule_interval(self.joystick_movs, 1/20)
            else:
                if self._joystick_start_event:
                    self._joystick_start_event.cancel()
                self._joystick_start_event = Clock.schedule_interval(self._try_start_joystick, 1/30)
        else:
            self.keyboard_active()
            self.keyboard_clock = Clock.schedule_interval(self.keyboard_actions, 1/20)

    def _try_start_joystick(self, dt):
        if getattr(self.interface, "joystick", None) and self.interface.joystick.parent:
            if self._joystick_start_event:
                self._joystick_start_event.cancel()
                self._joystick_start_event = None
            if not self.joystick_clock:
                self.joystick_clock = Clock.schedule_interval(self.joystick_movs, 1/20)

    def pre_leave(self, *args):
        if not self.interface.configs["teclado"]:
            if getattr(self, "joystick_clock", None):
                self.joystick_clock.cancel()
                self.joystick_clock = None
        else:
            self.keyboard_desactive()
            if getattr(self, "keyboard_clock", None):
                self.keyboard_clock.cancel()
                self.keyboard_clock = None
    

    def joystick_movs(self, dt):
        j = getattr(self.interface, "joystick", None)
        if not j:
            self.player.speed_x = 0
            self.player.speed_y = 0
            return

        self.player.speed_x = j.x_value
        self.player.speed_y = j.y_value

    
    def ataque(self,*args):
        self.player.acao="soco_normal"
    
    def quebrar(self,*args):
        self.player.acao="soco_forte"
    
    def menu_window(self,*args, tipo="inventario"):
        if self.menu_player._window:
            if self.menu_player.tipo==tipo:
                self.menu_player.dismiss()
                return
            self.menu_player.tipo=tipo
            self.menu_player.on_open()

        else:
            self.menu_player.tipo=tipo
            self.menu_player.open()


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
            self.menu_window()
        if key == 101:
            self.menu_window(tipo="equipaveis")
    
    def on_key_up(self, window, key, *args):
        self.key_pressed.remove(key)
    
    def keyboard_actions(self,*args):
        if 32 in self.key_pressed: 
            self.ataque()
        if 98 in self.key_pressed:
            self.quebrar()
        if 119 in self.key_pressed:
            self.player.speed_y=0.9
        elif 115 in self.key_pressed:
            self.player.speed_y=-0.9
        elif self.player.speed_y!=0:
            self.player.speed_y=0

        if 100 in self.key_pressed:
            self.player.speed_x=0.9
        elif 97 in self.key_pressed:
            self.player.speed_x=-0.9
        elif self.player.speed_x!=0:
            self.player.speed_x=0
        

class Menu_player(Popup):
    tipo = OptionProperty("inventario", options=("inventario", "equipaveis"))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        global STD_font_size
        self.title = ''
        self.separator_height = 0
        self.size_hint = (0.8, 0.8)
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        self.layout = BoxLayout(orientation='vertical')
        self.add_widget(self.layout)

        self.selection_panel = None
        self.selected_item_panel = None
        self.equipped_panel = None
        self.equipped_grid = None
        self.scroll_view = None
        self.grid = None

        self.player = None

        self.menu = {
            "inventario": self.inventario,
            "equipaveis": self.equipaveis
        }

    def on_open(self):
        self.menu[self.tipo]()
        Clock.schedule_once(lambda dt: self.atualizar_equipados(), 0)

    def on_dismiss(self):
        try:
            self.parent.inventario_menu = False
        except Exception:
            pass
    
    def menu_equipaveis(self,*args):
        if self.tipo=="equipaveis":
            pass
        self.tipo="equipaveis"
        self.on_open()
    
    def menu_inventario(self,*args):
        if self.tipo=="inventario":
            pass
        self.tipo="inventario"
        self.on_open()
    
    def preparar_menu(self, *args):
        self.layout.clear_widgets()

        browse_layout =FloatLayout(size_hint=(1, 0.2))
        
        tipo_label = Label(text=self.tipo, font_size=STD_font_size, size_hint=(0.7, 1),pos_hint={'center_x' : 0.5,'center_y' : 0.5})
        inventario_browse = InteractiveImage(source=resource_path("assets/ui/slot_vazio.png"),pos_hint={'center_x' : 0.25,'center_y' : 0.5})
        inventario_browse.bind(on_release=self.menu_inventario)
        equipaveis_browse = InteractiveImage(source=resource_path("assets/ui/bitcore.png"),pos_hint={'center_x' : 0.75,'center_y' : 0.5})        
        equipaveis_browse.bind(on_release=self.menu_equipaveis)

        browse_layout.add_widget(tipo_label)
        browse_layout.add_widget(inventario_browse)
        browse_layout.add_widget(equipaveis_browse)
        
        self.layout.add_widget(browse_layout)

        self.selection_panel = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.2),
            padding=8,
            spacing=8
        )

        self.selected_item_panel = BoxLayout(
            orientation='horizontal',
            size_hint=(0.6, 1),
            padding=6,
            spacing=6
        )
        self.selected_item_panel.add_widget(
            Label(text="Nenhum item selecionado", font_size=STD_font_size*0.6)
        )

        self.equipped_panel = BoxLayout(
            orientation='vertical',
            size_hint=(0.4, 1),
            padding=6,
            spacing=4
        )

        equipped_title = Label(
            text="Equipados",
            font_size=STD_font_size*0.5,
            size_hint=(1, 0.2)
        )

        self.equipped_grid = GridLayout(cols=1, rows=1, size_hint=(1, 0.8), spacing=6)
        self.equipped_panel.add_widget(equipped_title)
        self.equipped_panel.add_widget(self.equipped_grid)

        self.selection_panel.add_widget(self.selected_item_panel)
        self.selection_panel.add_widget(self.equipped_panel)

        self.layout.add_widget(self.selection_panel)

        size_px = self.width/8

        self.scroll_view = ScrollView(size_hint=(1, 0.6), do_scroll_x=False, do_scroll_y=True)
        self.grid = GridLayout(cols=4, spacing=size_px, padding=size_px, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll_view.add_widget(self.grid)

    def on_item_selected(self, widget):
        nome = getattr(widget, "item_nome", "Desconhecido")
        info = getattr(widget, "item_info", {}) or {}
        quantidade = getattr(widget, "item_quantidade", "")

        self.selected_item_panel.clear_widgets()

        img = Image(
            source=info.get("source", ""),
            size_hint=(0.3, 1),
            allow_stretch=True,
            keep_ratio=True
        )
        text_layout = BoxLayout(
            orientation='vertical',
            padding=6,
            spacing=4
        )
        nome_label = Label(
            text=f"{nome}  x{quantidade}",
            font_size=STD_font_size*0.7,
            size_hint=(1, None),
            height=30
        )
        raridade_label = Label(
            text=f"Raridade: {info.get('raridade', 'N/A')}",
            font_size=STD_font_size*0.5,
            size_hint=(1, None),
            height=24
        )
        descricao_label = Label(
            text=f"Descrição: {info.get('descrição', 'Sem descrição')}",
            font_size=STD_font_size*0.45
        )

        text_layout.add_widget(nome_label)
        text_layout.add_widget(raridade_label)
        text_layout.add_widget(descricao_label)

        self.selected_item_panel.add_widget(img)
        self.selected_item_panel.add_widget(text_layout)

        if self.tipo == "equipaveis":
            with open("saved/player.json", "r", encoding="utf-8") as arquivo:
                data = json.load(arquivo)

            raw_map = data.get("equipaveis") or data.get("bitcores") or {}

            if raw_map and all(str(v).isdigit() for v in raw_map.values()):
                equipados = {str(v): k for k, v in raw_map.items()}
            else:
                equipados = {str(k): v for k, v in raw_map.items()}

            slot_equipado = next((s for s, item in equipados.items() if item == nome), None)
    #auxilia nas identificacoes
            if slot_equipado is not None:
                desequipar_button = CustomizedButton(
                    text='desequipar',
                    font_size=16,
                    size_hint=(1, None),
                    height=24
                )#desequipar
                desequipar_button.bind(on_release=partial(self.desequipar_bitcore, slot=slot_equipado, widget=widget))
                self.selected_item_panel.add_widget(desequipar_button)

            else:
                slot_livre = None
                slots_usados = set(equipados.keys())
                for i in range(1, getattr(self.player, "max_skills", 4) + 1):
                    s = str(i)
                    if s not in slots_usados:
                        slot_livre = s
                        break

                if slot_livre is not None:
                    equipar_button = CustomizedButton(#equipar
                        text=f'equipar (slot {slot_livre})',
                        font_size=STD_font_size*0.5,
                        size_hint=(1, None),
                        height=24
                    )
                    equipar_button.bind(on_release=partial(self.equipar_bitcore, nome=nome, widget=widget))
                    self.selected_item_panel.add_widget(equipar_button)

                else:
                    sem_slot = Label(
                        text="Sem slots livres. Desequipe um item antes de equipar.",
                        font_size=STD_font_size*0.45,
                        size_hint=(1, None),
                        height=40
                    )
                    self.selected_item_panel.add_widget(sem_slot)

    def equipar_bitcore(self, *args, nome, widget):
        skill=NAME_TO_SKILL_ID[nome]
        self.player.equipar_bitcore(skill)
        self.atualizar_equipados()
        self.on_item_selected(widget=widget)
    
    def desequipar_bitcore(self,*args,slot,widget):
        self.player.desequipar_slot(slot)
        self.atualizar_equipados()
        self.on_item_selected(widget=widget)

    def safe_image(self, path, fallback="assets/ui/slot_vazio.png"):
        path = resource_path(path)
        if path and os.path.exists(path):
            return path
        return resource_path(fallback)


    def atualizar_equipados(self):

        player = getattr(self, "player", None)
        if not player:
            return

        max_slots = getattr(player, "max_skills", 0)
        skills_slots = getattr(player, "skills_slots", {})

        if getattr(self, "equipped_grid", None) and self.equipped_grid.parent:
            self.equipped_panel.remove_widget(self.equipped_grid)

        if max_slots <= 0:
            self.equipped_grid = GridLayout(cols=1, rows=1, size_hint=(1, 0.8))
            self.equipped_grid.add_widget(
                Label(text="Nenhum slot", font_size=STD_font_size*0.45)
            )
            self.equipped_panel.add_widget(self.equipped_grid)
            return

        self.equipped_grid = GridLayout(
            cols=max_slots,
            rows=1,
            size_hint=(1, 0.8),
            spacing=6
        )

        for i in range(1,max_slots+1):
            slot_id = str(i)
            skill_id = skills_slots.get(slot_id)

            src = "assets/ui/slot_vazio.png"

            if skill_id:
                for _, item_data in ITENS.get("equipaveis", {}).items():
                    if item_data.get("skill") == skill_id:
                        src = self.safe_image(item_data.get("source"))
                        break


            img = Image(
                source=src,
                allow_stretch=True,
                keep_ratio=True,
                size_hint=(1, 1)
            )

            self.equipped_grid.add_widget(img)

        self.equipped_panel.add_widget(self.equipped_grid)



    def adicionar_itens(self, inventario):
        if self.grid:
            self.grid.clear_widgets()

        itens = ITENS.get(self.tipo, {})

        if not inventario:
            self.grid.add_widget(Label(text="Sem itens", font_size=STD_font_size*0.8, size_hint_y=None, height=40))
            if self.scroll_view.parent is None:
                self.layout.add_widget(self.scroll_view)
            return

        for nome, quantidade in inventario.items():

            info = itens.get(nome, {})

            img_source = self.safe_image(info.get("source"))

            btn = InteractiveImage(
                source=img_source,
                size_hint=(None, None),
                allow_stretch=True,
                keep_ratio=False
            )
            btn.item_nome = nome
            btn.item_info = info
            btn.item_quantidade = quantidade
            btn.bind(on_press=self.on_item_selected)

            self.grid.add_widget(btn)

        if self.scroll_view.parent is None:
            self.layout.add_widget(self.scroll_view)

    def equipaveis(self, *args):
        self.preparar_menu()

        if not self.player:
            return

        inventario = self.player.bitcores

        self.adicionar_itens(inventario)


    def inventario(self, *args):
        self.preparar_menu()

        try:
            with open("saved/player.json", "r", encoding="utf-8") as arquivo:
                player = json.load(arquivo)
                inventario = player.get("inventario", {})

            self.adicionar_itens(inventario)

        except Exception:
            self.grid.clear_widgets()
            self.grid.add_widget(Label(text="Sem itens", font_size=STD_font_size*0.8, size_hint_y=None, height=40))
            if self.scroll_view.parent is None:
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
          
        self.button_play = CustomizedButton(
            text='Jogar',
            size_hint=(0.25, 0.08),
            pos_hint={'center_x': 0.5, 'center_y': 0.3}
        )
        self.button_play.bind(on_release=self.jogar)
        self.button_configs = CustomizedButton(
            text='Configurações',
            size_hint=(0.25, 0.08),
            pos_hint={'center_x': 0.5, 'center_y': 0.2}
        )
        self.button_configs.bind(on_release=self.configurar)
        self.button_sair = CustomizedButton(
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
        self.configs=configuracoes()
        self.teclado=self.configs["teclado"]
        if self.teclado:
            self.input='Modo teclado'
        else:
            self.input='Modo toque'
        if self.configs["font"]==30:
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
    

    def tamanho_da_fonte(self,*args):

        global STD_font_size

        with open("saved/configuracoes.json","r",encoding="utf-8") as config:
            self.configs=json.load(config)

        if self.configs["font"]==30:
            self.configs["font"]=35
            self.font='fonte grande'
        else:
            self.configs["font"]=30
            self.font='fonte normal'
        
        STD_font_size=self.configs["font"]

        with open("saved/configuracoes.json","w",encoding="utf-8") as old_config:
            json.dump(self.configs,old_config)
        self.button_font.text=f'{self.font}'
    

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