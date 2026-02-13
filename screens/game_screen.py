from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior

from core.player import Player
from core.world import World
from utils.joystick import Joystick
from utils.resourcesPath import resource_path
from screens.shared import configuracoes
from screens.menu_player import Menu_player

class InteractiveImage(ButtonBehavior, Image):
    pass

class Interface(FloatLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.configs = configuracoes()
        std_size=0.15
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
            pos_hint={'center_x': 0.125, 'center_y': 0.35}
            )
        self.mobile_layout.add_widget(self.joystick)#allowstretchg
    
    def add_button_ataque(self,*args):
        self.button_ataque=InteractiveImage(
            size_hint=self.fixed_size,
            pos_hint={'center_x' : 0.875,'center_y' : 0.45},
            source=resource_path("assets/ui/soco.png"),
            allow_stretch=True,
            keep_ratio=False
            )
        self.mobile_layout.add_widget(self.button_ataque)
    
    def add_button_quebrar(self,*args):
        self.button_quebrar=InteractiveImage(
            size_hint=self.fixed_size,
            pos_hint={'center_x' : 0.825,'center_y' : 0.3},
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
        
class GameScreen(Screen): 
    def __init__(self, GameScreenManager=None, **kwargs):
        super().__init__(**kwargs)
        self.GameScreenManager=GameScreenManager
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
            self.GameScreenManager.current='menu'
            return True