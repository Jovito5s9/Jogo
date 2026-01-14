from kivy.uix.image import Image

class EntityView(Image):
    def __init__(self, logic, **kwargs):
        super().__init__(**kwargs)
        self.logic = logic

        self.size_hint = (None, None)
        self.allow_stretch = True
        self.keep_ratio = False

        self.frame_width = 32
        self.frame_height = 32
        self.current_frame = 0
        self.facing_right = True

        self.sprite_sheet = self.load_sprite()

        self.size = (self.frame_width, self.frame_height)

        self.update_texture()

    def load_sprite(self):
        if not self.logic.source:
            return None
        img = Image(source=self.logic.source)
        return img.texture

    def update_texture(self):
        if not self.sprite_sheet:
            return

        x = self.current_frame * self.frame_width
        y = 0

        if self.facing_right:
            tex = self.sprite_sheet.get_region(
                x, y,
                self.frame_width,
                self.frame_height
            )
        else:
            tex = self.sprite_sheet.get_region(
                x + self.frame_width, y,
                -self.frame_width,
                self.frame_height
            )

        self.texture = tex

    def sync(self):
        self.pos = (self.logic.x, self.logic.y)

        if self.logic.speed_x > 0:
            self.facing_right = True
        elif self.logic.speed_x < 0:
            self.facing_right = False

        if not self.logic.vivo:
            self.opacity = 0.6
        else:
            self.opacity = 1
