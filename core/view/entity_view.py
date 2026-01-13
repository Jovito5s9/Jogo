from kivy.uix.image import Image

class EntidadeView(Image):
    def __init__(self, logic, **kwargs):
        super().__init__(**kwargs)
        self.logic = logic

    def sync(self):
        self.pos = (self.logic.x, self.logic.y)
