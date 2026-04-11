from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.stencilview import StencilView

from core.entity.player import Player
from core.world import World
from utils.joystick import Joystick
from utils.resourcesPath import resource_path
from screens.shared import configuracoes, size
from screens.menu_player import Menu_player
from screens.menu_pause import MenuPause
from kivy.utils import platform



class Viewport(StencilView):
    pass


class InteractiveImage(ButtonBehavior, Image):
    pass


class Interface(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.configs = configuracoes()
        std_size = 0.15
        self.fixed_w = self.height * std_size
        self.fixed_h = (self.fixed_w / self.height) if self.height else std_size
        self.fixed_w = std_size
        self.fixed_size = (self.fixed_w, self.fixed_h)

        self.joystick = None
        self.button_ataque = None
        self.button_quebrar = None
        self.button_menu = None
        self.joystick_bind = None
        self.button_ataque_bind = None
        self.button_quebrar_bind = None
        self.button_menu_player_bind = None

        self.mobile_layout = FloatLayout()

        self.atualizar()

    def atualizar(self, *args):
        new_cfg = configuracoes()
        if new_cfg != self.configs:
            self.configs = new_cfg

        self.remove_ui()
        if not self.configs["teclado"]:
            self.add_ui()

    def add_ui(self, *args):
        if not self.joystick:
            self.add_joytick()
        if not self.button_ataque:
            self.add_button_ataque()
        if not self.button_quebrar:
            self.add_button_quebrar()
        self.add_button_menu_player()

        if self.mobile_layout not in self.children:
            self.add_widget(self.mobile_layout)

        Clock.schedule_once(self.bind_buttons, 1)

    def add_joytick(self):
        self.joystick = Joystick(
            size_hint=(None, None),
            size=(800, 800),
            pos_hint={'center_x': 0.125, 'center_y': 0.35}
        )
        self.mobile_layout.add_widget(self.joystick)

    def add_button_ataque(self, *args):
        self.button_ataque = InteractiveImage(
            size_hint=self.fixed_size,
            pos_hint={'center_x': 0.875, 'center_y': 0.45},
            source=resource_path("assets/ui/soco.png"),
            allow_stretch=True,
            keep_ratio=False
        )
        self.mobile_layout.add_widget(self.button_ataque)

    def add_button_quebrar(self, *args):
        self.button_quebrar = InteractiveImage(
            size_hint=self.fixed_size,
            pos_hint={'center_x': 0.825, 'center_y': 0.3},
            source=resource_path("assets/ui/golpe_pesado.png"),
            allow_stretch=True,
            keep_ratio=False
        )
        self.mobile_layout.add_widget(self.button_quebrar)

    def add_button_menu_player(self, *args):
        self.button_menu = InteractiveImage(
            size_hint=self.fixed_size,
            pos_hint={'center_x': 0.5, 'center_y': 0.925},
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

    def remove_ui(self, *args):
        self.unbind_buttons()
        if self.mobile_layout.parent:
            self.remove_widget(self.mobile_layout)


class Game(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.world = World()
        self.add_widget(self.world)

        self.player = Player()
        self.world.player = self.player

        self.joystick_clock = None
        self.keyboard_clock = None
        self._joystick_start_event = None

        self.keymap = {
            "move_up": 119,
            "move_down": 115,
            "move_left": 97,
            "move_right": 100,

            "attack": 32,
            "heavy": 98,

            "inventory": 105,
            "equip": 101,
            "core": 99,

            "pause": 27
        }

        self.world.load_mapa("inicial", respawn=True)

        self.inventario_menu = False
        self.menu_player = Menu_player()
        self.menu_pause = MenuPause()
        self.menu_player.player = self.player

        self.pausado = False
        self._pause_pressed = False

        self.interface = Interface()
        self.add_widget(self.interface)

    def on_parent(self, *args):
        self.menu_pause.game = self

    def pre_enter(self, *args):
        fps = configuracoes()["fps"]
        if fps != self.world.fps:
            self.world.fps = fps
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
                    self.joystick_clock = Clock.schedule_interval(self.joystick_movs, 1 / 20)
            else:
                if self._joystick_start_event:
                    self._joystick_start_event.cancel()
                self._joystick_start_event = Clock.schedule_interval(self._try_start_joystick, 1 / 30)
        else:
            self.keyboard_active()
            self.keyboard_clock = Clock.schedule_interval(self.keyboard_actions, 1 / 20)
            
        self.world.atualizar()

    def _try_start_joystick(self, dt):
        if getattr(self.interface, "joystick", None) and self.interface.joystick.parent:
            if self._joystick_start_event:
                self._joystick_start_event.cancel()
                self._joystick_start_event = None
            if not self.joystick_clock:
                self.joystick_clock = Clock.schedule_interval(self.joystick_movs, 1 / 20)

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

        self.world.pausar()

    def joystick_movs(self, dt):
        j = getattr(self.interface, "joystick", None)
        if not j:
            self.player.speed_x = 0
            self.player.speed_y = 0
            return

        self.player.speed_x = j.x_value
        self.player.speed_y = j.y_value

    def pause(self, *args):
        if self.pausado:
            self.world.despausar()
            self.menu_pause.dismiss()
            self.pausado = False
            return
        self.world.pausar()
        self.menu_pause.open()
        self.pausado = True

    def ataque(self, *args):
        self.player.acao = "soco_normal"

    def quebrar(self, *args):
        self.player.acao = "soco_forte"

    def menu_window(self, *args, tipo="inventario"):
        if self.menu_player._window:
            if self.menu_player.tipo == tipo:
                self.menu_player.dismiss()
                return
            self.menu_player.tipo = tipo
            self.menu_player.open()
        else:
            self.menu_player.tipo = tipo
            self.menu_player.open()

    def keyboard_active(self, *args):
        self.key_pressed = set()
        Window.bind(on_key_down=self.on_key_down)
        Window.bind(on_key_up=self.on_key_up)

    def keyboard_desactive(self, *args):
        self.key_pressed = set()
        Window.unbind(on_key_down=self.on_key_down)
        Window.unbind(on_key_up=self.on_key_up)

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        self.key_pressed.add(key)

        if key == self.keymap["pause"] and not self._pause_pressed:
            self.pause()
            self._pause_pressed = True
            return True
        elif key == self.keymap["inventory"]:
            self.menu_window(tipo="inventario")
        elif key == self.keymap["equip"]:
            self.menu_window(tipo="equipaveis")
        elif key == self.keymap["core"]:
            self.menu_window(tipo="core")

    def on_key_up(self, window, key, *args):
        if key in self.key_pressed:
            self.key_pressed.remove(key)

        if key == self.keymap["pause"]:
            self._pause_pressed = False

    def keyboard_actions(self, *args):
        if self.keymap["attack"] in self.key_pressed:
            self.ataque()
        if self.keymap["heavy"] in self.key_pressed:
            self.quebrar()

        if self.keymap["move_up"] in self.key_pressed:
            self.player.speed_y = 0.9
        elif self.keymap["move_down"] in self.key_pressed:
            self.player.speed_y = -0.9
        else:
            self.player.speed_y = 0

        if self.keymap["move_right"] in self.key_pressed:
            self.player.speed_x = 0.9
        elif self.keymap["move_left"] in self.key_pressed:
            self.player.speed_x = -0.9
        else:
            self.player.speed_x = 0


class GameScreen(Screen):
    def __init__(self, GameScreenManager=None, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()
        self.add_widget(self.layout)
        self.GameScreenManager = GameScreenManager

        self.game = None
        self.viewport = None
        self._viewport_size_ev = None

    def _ensure_game(self):
        if self.game is not None:
            return

        self.game = Game()
        self.game.size_hint = (None, None)
        self.game.size = (size * 20, size * 15)
        self.game.pos = (0, 0)
        if platform == "android":
            self.viewport = Viewport(size_hint=(None, None))
            self.layout.add_widget(self.viewport)
            self.viewport.add_widget(self.game)
        else:
            self.layout.add_widget(self.game)

        def ajustar_viewport(*args):
            if not self.viewport:
                return
            android_extra_grids = ((Window.width / size) - 20) / 2
            recuo = android_extra_grids * size
            self.viewport.size = (size * 20, size * 15)
            self.viewport.pos = (recuo, 0)

        self._viewport_size_ev = Clock.schedule_once(ajustar_viewport, 0)

        self.game.pre_enter()

    def on_pre_leave(self, *args):
        if self.game:
            self.game.keyboard_desactive()
            self.game.key_pressed.clear()
            self.game._pause_pressed = False

    def on_pre_enter(self, *args):
        self._ensure_game()

        def reajustar(*args):
            if not self.viewport:
                return
            android_extra_grids = ((Window.width / size) - 20) / 2
            recuo = android_extra_grids * size
            self.viewport.size = (size * 20, size * 15)
            self.viewport.pos = (recuo, 0)

        Clock.schedule_once(reajustar, 0)

        if self.game:
            self.game.pre_enter()