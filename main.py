from kivy.config import Config

Config.set('graphics', 'fullscreen', 'auto')
Config.set('graphics', 'borderless', '1')
Config.set('graphics', 'resizable', '0')

from kivy.app import App 
from game import GameScreenManager 
from kivy.config import Config

Config.set('kivy', 'window_icon', 'assets/geral/logo_RadioRoots.png')


class RadioRoots(App):
    def build(self):
        return GameScreenManager

RadioRoots().run()