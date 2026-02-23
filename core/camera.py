from kivy.core.window import Window

class Camera:
    def __init__(self, parent, position=(0, 0), map_size=(0, 0), player=None):
        self.parent = parent
        self.center = position
        self.map_size = map_size or (0, 0)
        self.player = player

    def update(self):
        if not self.player:
            self.player = getattr(self.parent, "player", None)
        if not self.player:
            return None

        map_w, map_h = self.map_size
        if map_w <= 0 or map_h <= 0:
            return None

        px = self.player.center_x
        py = self.player.center_y

        # Sempre centraliza
        cam_x = px - Window.width / 2
        cam_y = py - Window.height / 2

        # Limites
        max_x = map_w - Window.width
        max_y = map_h - Window.height

        # Clamp final
        cam_x = max(0, min(cam_x, max_x))
        cam_y = max(0, min(cam_y, max_y))

        new_center = (-cam_x, -cam_y)

        if new_center != self.center:
            self.center = new_center
            return self.center

        return None