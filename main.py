from kivy.app import App 
from game import Game 

class TwoPiece(App):
    def build(self):
        return Game()
#testando
TwoPiece().run()