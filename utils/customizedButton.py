from kivy.uix.button import Button
from kivy.graphics import RoundedRectangle, Color
from kivy.properties import ListProperty, NumericProperty


class CustomizedButton(Button):
    cor = ListProperty([0.2, 0.4, 0.1, 0.95])
    cor2 = ListProperty([0.15, 0.3, 0.1, 0.95])
    cor_borda = ListProperty([0.05, 0.15, 0.05, 1])

    border_width = NumericProperty(4)
    radius = NumericProperty(20)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.background_color = (0, 0, 0, 0)

        with self.canvas.before:
            self.color_border = Color(*self.cor_borda)
            self.border_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.radius]
            )

            self.color_bg = Color(*self.cor)
            self.bg_rect = RoundedRectangle(
                pos=(self.x + self.border_width, self.y + self.border_width),
                size=(
                    self.width - self.border_width * 2,
                    self.height - self.border_width * 2
                ),
                radius=[self.radius - 4]
            )

        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.border_rect.pos = self.pos
        self.border_rect.size = self.size

        self.bg_rect.pos = (
            self.x + self.border_width,
            self.y + self.border_width
        )
        self.bg_rect.size = (
            self.width - self.border_width * 2,
            self.height - self.border_width * 2
        )

    def on_cor(self, instance, value):
        self.color_bg.rgba = value

    def on_press(self, *args):
        self.cor, self.cor2 = self.cor2, self.cor

        self.bg_rect.pos = (
            self.bg_rect.pos[0],
            self.bg_rect.pos[1] - 2
        )

    def on_release(self, *args):
        self.cor, self.cor2 = self.cor2, self.cor
