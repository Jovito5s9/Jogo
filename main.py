from kivy.app import App 
from game import GameScreen 

class Jogo(App):
    def build(self):
        return GameScreen()

Jogo().run()