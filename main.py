from kivy.app import App 
from game import GameScreenManager 

class RadioRoots(App):
    def build(self):
        return GameScreenManager

RadioRoots().run()