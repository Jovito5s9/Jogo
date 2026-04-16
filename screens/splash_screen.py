from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

from utils.resourcesPath import resource_path

class SplashScreen(Screen):
    def __init__(self, GameScreenManager=None, **kwargs):
        super().__init__(**kwargs)
        self.GameScreenManager=GameScreenManager
        with self.canvas:
            Color(0.1, 0.1, 0.15, 1)
            self.bg_rect = Rectangle(size=Window.size, pos=self.pos)
        self.layout=FloatLayout()
        self.SolarBurn_logo=Image(
            source=resource_path('assets/geral/logo_SolarBurn.png'),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(0.8, 0.8)
        )
        self.layout.add_widget(self.SolarBurn_logo)
        self.label=Label(
            text="SolarBurn Studios",
            font_size=60,
            pos_hint={'center_x': 0.5, 'center_y': 0.2},
            color=(1, 0.2, 0.2, 1)
        )
        self.layout.add_widget(self.label)
        self.add_widget(self.layout)
        Clock.schedule_once(self.go_to_menu, 1.8)

    def go_to_menu(self, dt):
        self.GameScreenManager.current = 'menu'