from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Ellipse, Line, Color
from kivy.properties import NumericProperty


class Joystick(Widget):
    
    # Coordenadas relativas do joystick
    x_value = NumericProperty(0)
    y_value = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        with self.canvas:
            # Desenha o círculo base (área de movimentação do joystick)
            Color(0.8, 0.8, 0.8, 0.5)
            self.base_circle = Ellipse(pos=(self.center_x - 100 , self.center_y -100), size=(200, 200))
            
            # Desenha o botão do joystick
            Color(0, 0.6, 0.8)
            self.stick_circle = Ellipse(pos=(self.center_x - 25, self.center_y - 25), size=(50, 50))

        # Atualiza o layout quando a janela é redimensionada
        self.bind(size=self.update_graphics, pos=self.update_graphics)

    def update_graphics(self, *args):
        # Centraliza o círculo base e o stick na tela
        self.base_circle.pos = (self.center_x - 100, self.center_y - 100)
        self.stick_circle.pos = (self.center_x - 25, self.center_y - 25)

    def on_touch_down(self, touch):
        # Verifica se o toque está dentro da área base
        if self.collide_point(*touch.pos):
            self.move_stick(touch.x, touch.y)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        # Move o joystick se o toque estiver dentro da área base
        if self.collide_point(*touch.pos):
            self.move_stick(touch.x, touch.y)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        # Retorna o stick para o centro ao soltar o toque
        self.stick_circle.pos = (self.center_x - 25, self.center_y - 25)
        self.x_value = 0
        self.y_value = 0
        return super().on_touch_up(touch)

    def move_stick(self, x, y):
        # Calcula o deslocamento do toque em relação ao centro do círculo base
        dx = x - self.center_x
        dy = y - self.center_y
        distance = (dx**2 + dy**2)**0.5
        
        # Limita o stick ao raio do círculo base
        max_distance = 100
        if distance > max_distance:
            factor = max_distance / distance
            dx *= factor
            dy *= factor

        # Atualiza a posição do stick
        self.stick_circle.pos = (self.center_x + dx - 25, self.center_y + dy - 25)
        self.x_value = dx / max_distance
        self.y_value = dy / max_distance
        
        

class JoystickApp(App):
    def build(self):
        root = Widget()
        joystick = Joystick(size_hint=(None, None), size=(400, 400), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        
        root.add_widget(joystick)

        # Exibe as coordenadas do joystick no console
        joystick.bind(x_value=lambda instance, value: print(f"x: {value}"))
        joystick.bind(y_value=lambda instance, value: print(f"y: {value}"))
        return root

if __name__ == '__main__':
    JoystickApp().run()
