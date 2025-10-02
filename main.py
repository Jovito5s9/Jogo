from kivy.app import App 
from game import GameScreenManager 

class Jogo(App):
    def build(self):
        return GameScreenManager

Jogo().run()