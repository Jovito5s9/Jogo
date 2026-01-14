from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.clock import Clock
from kivy.core.window import Window

from core.logic.world import WorldLogico, ObjData
from utils.resourcesPath import resource_path
from core.view.rato_view import RatoView as Rato
from core.view.rata_mae_view import RataMaeView as Rata_mae

size = 75

class EntityViewFactory:

    @staticmethod
    def create(entity_logic):
        if entity_logic is None:
            raise ValueError("Entity logic é None")

        from core.logic.player import PlayerLogica
        from core.logic.rato import RatoLogica
        from core.logic.rata_mae import RataMaeLogica

        from core.view.player_view import PlayerView
        from core.view.rato_view import RatoView
        from core.view.rata_mae_view import RataMaeView

        if isinstance(entity_logic, PlayerLogica):
            view = PlayerView(entity_logic)
        elif isinstance(entity_logic, RatoLogica):
            view = RatoView(entity_logic)
        elif isinstance(entity_logic, RataMaeLogica):
            view = RataMaeView(entity_logic)
        else:
            raise ValueError(
                f"View não definida para lógica {entity_logic.__class__.__name__}"
            )

        entity_logic._view_widget = view
        view._logic_entity = entity_logic
        return view


class ObjectView(FloatLayout):
    linha = NumericProperty(0)
    coluna = NumericProperty(0)
    posicao = ReferenceListProperty(linha, coluna)

    patern_x = NumericProperty(0)
    patern_y = NumericProperty(0)
    patern_center = ReferenceListProperty(patern_x, patern_y)

    linhas = NumericProperty(0)
    colunas = NumericProperty(0)
    max = ReferenceListProperty(linhas, colunas)
    
    resistencia = NumericProperty(0)

    def __init__(self, objdata: ObjData, ativado=False, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        global size
        self.objdata = objdata
        self.s = objdata.tipo
        self.type = objdata.tipo
        self.source = resource_path("assets/tiles/objects/" + f"{self.s}")
        self.size = (size, size * 0.8)
        self.colisivel = objdata.colisivel
        self.quebravel = objdata.quebravel
        self.quebrando = False
        self.ativado = objdata.ativado
        self.dano_colisao = objdata.dano_colisao
        self.drops = objdata.drops or {}
        self.resistencia = objdata.resistencia

        self.image = Image(
            source=self.source,
            allow_stretch=True,
            keep_ratio=False,
            size=self.size,
            pos=self.pos
        )
        self.add_widget(self.image)

        self.bind(pos=self.update_image_pos)
        self.bind(patern_center=self.on_center_changed)

        self.position()

    def update_image_pos(self, *args):
        self.image.pos = self.pos

    def position(self, *args):
        self.pos = (
            self.patern_x + (self.coluna * self.width),
            self.patern_y + (self.linha * self.height)
        )

    def get_hitbox(self, *args):
        if self.s == 'pedra.png':
            return [self.x + (self.width * 0.15), self.y + (self.height * 0.5), self.width * 0.7, self.height * 0.6]
        elif self.s in ('entrada_esgoto.png', 'descer_esgoto.png', 'veneno.png', 'subir_esgoto.png'):
            return [self.x + (self.width * 0.2), self.y + (self.height * 0.7), self.width * 0.6, self.height * 0.4]
        else:
            return [self.x, self.y, self.width, self.height]

    def spawn_visual(self, world_view):
        rato = Rato()
        rato.pos = self.pos
        world_view.add_widget(rato)
        world_view.ents.append(rato)
        self.ativado = True

    def quebrar_visual(self, world_view):
        try:
            self.remove_widget(self.image)
        except Exception:
            pass
        try:
            world_view.player.recive_itens(self.drops)
        except Exception:
            pass
        if self in world_view.obj_list:
            world_view.obj_list.remove(self)
        try:
            world_view.remove_widget(self)
        except Exception:
            pass

    def on_resistencia(self, *args):
        if self.resistencia and hasattr(self, 'resistencia'):
            if 100 * self.resistencia / getattr(self, "resistencia_max", max(1,self.resistencia)) < 40:
                if not self.quebrando:
                    self.image.source = self.image.source.replace(".png", "_quebrando.png")
                    self.quebrando = True

    def on_center_changed(self, *args):
        self.position()

class GridView(FloatLayout):
    linha = NumericProperty(0)
    coluna = NumericProperty(0)
    posicao = ReferenceListProperty(linha, coluna)

    patern_x = NumericProperty(0)
    patern_y = NumericProperty(0)
    patern_center = ReferenceListProperty(patern_x, patern_y)

    linhas = NumericProperty(0)
    colunas = NumericProperty(0)
    max = ReferenceListProperty(linhas, colunas)

    def __init__(self, source, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.ents = []
        self.type = source
        global size
        self.source = resource_path("assets/tiles/ground/" + f"{source}")
        self.size = (size, size * 0.8)

        self.image = Image(
            source=self.source,
            allow_stretch=True,
            keep_ratio=False,
            size=self.size,
            pos=self.pos
        )
        self.add_widget(self.image)

        self.bind(pos=self.update_image_pos)
        self.bind(patern_center=self.on_center_changed)

        self.position()

    def update_image_pos(self, *args):
        self.image.pos = self.pos

    def position(self, *args):
        self.pos = (
            self.patern_x + (self.coluna * self.width),
            self.patern_y + (self.linha * self.height)
        )

    def on_center_changed(self, *args):
        self.position()

class WorldView(FloatLayout):
    def __init__(self, world_logic: WorldLogico, **kwargs):
        super().__init__(**kwargs)
        self.world_logic = world_logic
        self.world_logic.offset_x = (Window.width / 2) - ((self.world_logic.colunas * self.world_logic.tile_size) / 2)
        self.world_logic.offset_y = (Window.height / 2) - ((self.world_logic.linhas * self.world_logic.tile_height) / 2)

        self.size_hint = (None, None)
        self.size = (Window.width, Window.height)
        self.offset_x = self.world_logic.offset_x
        self.offset_y = self.world_logic.offset_y

        self.tiles_list = []
        self.obj_list = []
        self.ents = []
        self.entities_view = []
        self.player = None

        self.ev_update = Clock.schedule_interval(self._tick, 1/60)
    
    def add_entity(self, entity_logic):
        view = EntityViewFactory.create(entity_logic)
        self.entities_view.append(view)
        self.add_widget(view)

    def render_full_map(self):
        for t in list(self.tiles_list):
            try:
                self.remove_widget(t)
            except Exception:
                pass
        for o in list(self.obj_list):
            try:
                self.remove_widget(o)
            except Exception:
                pass

        self.tiles_list.clear()
        self.obj_list.clear()

        for tdata in self.world_logic.tiles:
            g = GridView(source=tdata.tipo, posicao=(tdata.col, tdata.row), patern_center=(self.offset_x, self.offset_y), max=(self.world_logic.linhas, self.world_logic.colunas))
            g.coluna = tdata.col
            g.linha = tdata.row
            g.patern_x = self.offset_x
            g.patern_y = self.offset_y
            self.tiles_list.append(g)
            self.add_widget(g)

        for odata in self.world_logic.objetos:
            ov = ObjectView(odata, ativado=odata.ativado, posicao=(odata.col, odata.row), patern_center=(self.offset_x, self.offset_y), max=(self.world_logic.linhas, self.world_logic.colunas))
            ov.coluna = odata.col
            ov.linha = odata.row
            ov.patern_x = self.offset_x
            ov.patern_y = self.offset_y
            ov.resistencia = odata.resistencia
            self.obj_list.append(ov)
            self.add_widget(ov)

        if self.world_logic.player_ref:
            if self.player:
                try:
                    self.remove_widget(self.player)
                except Exception:
                    pass
            self.player = self.world_logic.player_ref.ent._view_widget if hasattr(self.world_logic.player_ref.ent, "_view_widget") else None

            if not self.player:
                try:
                    pview = __import__("core.player", fromlist=["Player"]).Player()
                    pview.pos = (self.offset_x, self.offset_y)
                    self.player = pview
                    self.add_widget(self.player)
                except Exception:
                    self.player = None

    def _apply_events(self, events):
        for ev in events:
            typ = ev.get("type")
            if typ == "spawn_entity":
                etype = ev.get("entity_type")
                pos = ev.get("pos", (0,0))
                if etype == "rato":
                    r = Rato()
                    r.pos = pos
                    self.add_widget(r)
                    self.ents.append(r)
            elif typ == "add_object":
                objdata = ev["obj"]
                ov = ObjectView(objdata, posicao=(objdata.col, objdata.row), patern_center=(self.offset_x, self.offset_y), max=(self.world_logic.linhas, self.world_logic.colunas))
                ov.coluna = objdata.col
                ov.linha = objdata.row
                ov.patern_x = self.offset_x
                ov.patern_y = self.offset_y
                ov.resistencia = objdata.resistencia
                self.obj_list.append(ov)
                self.add_widget(ov)
            elif typ == "remap":
                nivel = ev.get("nivel",1)
                map_type = ev.get("map_type","esgoto")
                self.world_logic.re_map(map_type, nivel=nivel)
                self.render_full_map()
            elif typ == "obj_quebrado":
                objdata = ev["obj"]
                match = next((ov for ov in self.obj_list if hasattr(ov,'objdata') and ov.objdata is objdata), None)
                if match:
                    match.quebrar_visual(self)
            elif typ == "dano":
                target = ev.get("target")
                if hasattr(target,"_view_widget") and target._view_widget:
                    try:
                        w = target._view_widget
                        w.opacity = 0.5
                        Clock.schedule_once(lambda dt: setattr(w,"opacity",1), 0.15)
                    except Exception:
                        pass
            elif typ == "gerar_boss":
                try:
                    boss = Rata_mae()
                    boss.pos = (self.offset_x + self.world_logic.linhas * size * 0.5, self.offset_y + self.world_logic.colunas * size * 0.5 * 0.8)
                    self.add_widget(boss)
                    self.ents.append(boss)
                except Exception:
                    pass

    def _tick(self, dt):
        events = self.world_logic.update(dt)
        self._apply_events(events)
        for ref in self.world_logic.entidades:
            ent_logic = ref.ent
            if hasattr(ent_logic, "_view_widget") and ent_logic._view_widget:
                widget = ent_logic._view_widget
                try:
                    widget.pos = (ent_logic.x, ent_logic.y)
                except Exception:
                    pass

    def attach_player_view(self, player_view, player_logic):
        self.player = player_view
        if not self.world_logic.player_ref:
            self.world_logic.set_player(player_logic)
        self.world_logic.player_ref.ent._view_widget = player_view
        player_logic._view_widget = player_view
        if player_view not in self.ents:
            self.ents.append(player_view)
