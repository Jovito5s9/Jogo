from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import OptionProperty
from kivy.clock import Clock

from utils.resourcesPath import resource_path
from utils.customizedButton import CustomizedButton
from core.BitCoreSkills import NAME_TO_SKILL_ID
from saved.itens_db import ITENS
from screens.shared import STD_font_size
from functools import partial
import json
import os

class InteractiveImage(ButtonBehavior, Image):
    pass

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
            size_hint=(1, 0.25),
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
            source=resource_path(info.get("source", "")),
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
            with open(resource_path("saved/player.json"), "r", encoding="utf-8") as arquivo:
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
                    font_size=STD_font_size*0.6,
                    size_hint=(0.8, None),
                    height=40
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
                        font_size=STD_font_size*0.6,
                        size_hint=(0.8, None),
                        height=40
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

            src = resource_path("assets/ui/slot_vazio.png")

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
                source=resource_path(img_source),
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
            with open(resource_path("saved/player.json"), "r", encoding="utf-8") as arquivo:
                player = json.load(arquivo)
                inventario = player.get("inventario", {})

            self.adicionar_itens(inventario)

        except Exception:
            self.grid.clear_widgets()
            self.grid.add_widget(Label(text="Sem itens", font_size=STD_font_size*0.8, size_hint_y=None, height=40))
            if self.scroll_view.parent is None:
                self.layout.add_widget(self.scroll_view)
