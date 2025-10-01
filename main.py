from kivy.app import App 
from game import Game 

class Jogo(App):
    def build(self):
        return Game()

Jogo().run()