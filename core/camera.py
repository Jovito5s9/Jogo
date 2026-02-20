from kivy.core.window import Window

class Camera:
    def __init__(self, parent, position=(0, 0), map_size=(0, 0), player=None):
        self.parent = parent
        self.center = position
        self.map_size = map_size
        self.player = player

    def update(self):
        if self.center==(0,0):
            print("Camera: Center is (0,0), skipping update.")
        if not self.player:
            self.player = getattr(self.parent, "player", None)
        if not self.player:
            return None

        player_pos = self.player.center
        center_x = center_y = 0

        if self.map_size[0] > Window.width:
            center_x = min(max(player_pos[0] - Window.width / 2, 0), self.map_size[0] - Window.width)

        if self.map_size[1] > Window.height:
            center_y = min(max(player_pos[1] - Window.height / 2, 0), self.map_size[1] - Window.height)

        if self.center != (-center_x, -center_y):
            self.center = (-center_x, -center_y)
            return self.center

        return None