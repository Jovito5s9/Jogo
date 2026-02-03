from kivy.uix.button import Button
from kivy.graphics import RoundedRectangle, Color
from kivy.properties import ListProperty

class CustomizedButton(Button):
    cor = ListProperty([0.2, 0.4, 0.1, 0.9])
    cor2 = ListProperty([0.4, 0.5, 0.4, 0.9])
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)  
        with self.canvas.before:
            self.instrucao_cor = Color(*self.cor)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
        
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_cor(self, instance, value):
        self.instrucao_cor.rgba = value

    def on_press(self, *args):
        self.cor, self.cor2 = self.cor2, self.cor

    def on_release(self, *args):
        self.cor, self.cor2 = self.cor2, self.cor