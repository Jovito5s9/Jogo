from kivy.uix.image import Image

class EntityView(Image):
    def __init__(self, logic, **kwargs):
        super().__init__(**kwargs)
        self.logic = logic

        self.size_hint = (None, None)
        self.allow_stretch = True
        self.keep_ratio = False

    def sync(self):
        self.pos = (self.logic.x, self.logic.y)

        if not self.logic.vivo:
            self.opacity = 0.6

