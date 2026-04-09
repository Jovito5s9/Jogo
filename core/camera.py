from kivy.core.window import Window
from kivy.utils import platform as kivy_platform

from screens.shared import size


class Camera:
    def __init__(self, parent, position=(0, 0), map_size=(0, 0), player=None):
        self.parent = parent
        self.center = position
        self.map_size = map_size or (0, 0)
        self.player = player
        self.recuo_viewport = 0

    def _get_viewport_size(self):
        if kivy_platform == "android":
            android_extra_grids = ((Window.width / size) - 20) / 2
            self.recuo_viewport = android_extra_grids * size
            game = getattr(self.parent, "parent", None)
            viewport = getattr(game, "parent", None) if game else None

            if viewport and getattr(viewport, "width", 0) > 0 and getattr(viewport, "height", 0) > 0:
                return viewport.width, viewport.height

        return Window.width, Window.height

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

        view_w, view_h = self._get_viewport_size()

        px = self.player.center_x
        cam_x = px - (view_w - self.recuo_viewport) / 2
        max_x = map_w - view_w - self.recuo_viewport 
        cam_x = max(-1*self.recuo_viewport, min(cam_x, max_x))

        if map_h > view_h:
            py = self.player.center_y
            cam_y = py - view_h / 2
            max_y = map_h - view_h
            cam_y = max(0, min(cam_y, max_y))
        else:
            cam_y = 0

        new_center = (-cam_x, -cam_y)

        if new_center != self.center:
            self.center = new_center
            return self.center

        return None