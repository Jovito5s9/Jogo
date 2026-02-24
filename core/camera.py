from kivy.core.window import Window

class Camera:
    def __init__(self, parent, position=(0, 0), map_size=(0, 0), player=None):
        self.parent = parent
        self.center = position
        self.map_size = map_size or (0, 0)
        self.player = player

    def update(self):
        if self.map_size != self.parent.size:
            self.map_size = self.parent.size
        if not self.player:
            self.player = getattr(self.parent, "player", None)
        if not self.player:
            return None

        map_w, map_h = self.map_size
        if map_w <= 0 or map_h <= 0:
            return None

        px = self.player.center_x
        cam_x = px - Window.width / 2
        max_x = map_w - Window.width
        cam_x = max(0, min(cam_x, max_x))

        if map_h > Window.height:
            py = self.player.center_y
            # Sempre centraliza
            cam_y = py - Window.height / 2
            # Limites
            max_y = map_h - Window.height
            # Clamp final
            cam_y = max(0, min(cam_y, max_y))
        else:
            cam_y = 0


        new_center = (-cam_x, -cam_y)

        if new_center != self.center:
            self.center = new_center
            return self.center

        return None