from kivy.clock import Clock
from kivy.core.window import Window

from core.logic.world import WorldLogico
from core.view.world_view import WorldView, ObjectView, GridView
from core.logic.entityfactory import EntityFactory

class ViewFactory:
    @staticmethod
    def create_view_for(logic_entity):
        if hasattr(logic_entity, "_view_widget") and getattr(logic_entity, "_view_widget"):
            return logic_entity._view_widget

        if hasattr(logic_entity, "_view_cls") and logic_entity._view_cls:
            try:
                return logic_entity._view_cls(logic_entity)
            except Exception:
                pass

        class_name = logic_entity.__class__.__name__
        base_name = class_name.replace("Logica", "").lower()
        try:
            module_name = f"core.view.{base_name}_view"
            module = __import__(module_name, fromlist=["*"])
            view_cls_name = class_name.replace("Logica", "View")
            view_cls = getattr(module, view_cls_name, None)
            if view_cls:
                view = view_cls(logic_entity)
                logic_entity._view_widget = view
                view._logic_entity = logic_entity
                return view
        except Exception:
            pass

        try:
            module = __import__("core.view.entity_view", fromlist=["EntityView"])
            EntityView = getattr(module, "EntityView")
            view = EntityView(logic_entity)
            logic_entity._view_widget = view
            view._logic_entity = logic_entity
            return view
        except Exception:
            return None


class WorldAdapter:

    def __init__(self, tile_size=75):
        self.logic = WorldLogico(tile_size=tile_size)
        self.view = WorldView(self.logic)


        self.ents = self.view.ents
        self.obj_list = self.view.obj_list
        self.tiles_list = self.view.tiles_list

        self.player = None
        self.trocando_mapa = False

        self.factory = EntityFactory()

        self._process_ev = Clock.schedule_interval(self._process_pending, 1/60)


    def add_entity(self, entity_logic):
        self.logic.add_entity(entity_logic)
        self.view.add_entity(entity_logic)
    
    def create(self, xm, ym, type=None):
        self.logic.create(xm, ym, type)
        self._sync_offsets()
        self.view.render_full_map()

    def carregar_mapa(self, sala):
        self.logic.carregar_mapa(sala)
        self._sync_offsets()
        self.view.render_full_map()

    def re_map(self, type, nivel=1):
        self.logic.re_map(type, nivel=nivel)
        self._sync_offsets()
        self.view.render_full_map()

    def add_objects(self, tipo, grid):
        if not tipo.endswith(".png"):
            tipo_arg = tipo + ".png"
        else:
            tipo_arg = tipo
        self.logic.add_objects(tipo_arg, grid)
        events = self.logic.drain_events()
        self.view._apply_events(events)

    def add_widget(self, widget):
        try:
            self.view.add_widget(widget)
            self.ents.append(widget)
        except Exception:
            pass


        logic_ent = None
        for attr in ("_logic_entity", "_ent_logic", "logic", "logic_entity"):
            if hasattr(widget, attr):
                logic_ent = getattr(widget, attr)
                break
        if logic_ent is not None:
            try:
                self.logic.entidades.append(self.logic.EntityRef(ent=logic_ent))
            except Exception:
                self.logic.entidades.append(type("Ref", (), {"ent": logic_ent})())

    def remove_widget(self, widget):
        try:
            if widget in self.ents:
                self.ents.remove(widget)
            self.view.remove_widget(widget)
        except Exception:
            pass

    def gerar_boss(self):
        if not self.factory:
            return
        boss_logic = self.factory.create("rata_mae")
        if boss_logic:
            self.logic.entidades.append(type("Ref", (), {"ent": boss_logic})())
            view = ViewFactory.create_view_for(boss_logic)
            if view:
                view.pos = (self.logic.offset_x + self.logic.linhas * 0.5 * self.logic.tile_size,
                            self.logic.offset_y + self.logic.colunas * 0.5 * self.logic.tile_height)
                self.view.add_widget(view)
                self.ents.append(view)



    def _sync_offsets(self):
        self.view.world_logic = self.logic
        self.view.world_logic.offset_x = (Window.width / 2) - ((self.logic.colunas * self.logic.tile_size) / 2)
        self.view.world_logic.offset_y = (Window.height / 2) - ((self.logic.linhas * self.logic.tile_height) / 2)
        self.view.offset_x = self.view.world_logic.offset_x
        self.view.offset_y = self.view.world_logic.offset_y

    def set_player(self, player_view, player_logic):
        self.player = player_view
        if player_view not in self.view.ents:
            self.view.add_widget(player_view)
            self.view.ents.append(player_view)
            self.ents = self.view.ents

        try:
            self.logic.set_player(player_logic)
            player_logic._view_widget = player_view
            player_view._logic_entity = player_logic
        except Exception:
            try:
                self.logic.entidades.insert(0, type("Ref", (), {"ent": player_logic})())
            except Exception:
                pass

    def _process_pending(self, dt):
        events = self.logic.drain_events()
        if events:
            self.view._apply_events(events)

    def update(self, dt):
        events = self.logic.update(dt)
        if events:
            self.view._apply_events(events)

