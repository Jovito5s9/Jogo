import random
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional

Tile = Tuple[int, int, str]
ObjTuple = Tuple[int, int, str, int, bool]

@dataclass
class ObjData:
    col: int
    row: int
    tipo: str
    resistencia: int = 0
    ativado: bool = False

    colisivel: bool = True
    quebravel: bool = False
    dano_colisao: float = 0.0
    drops: Dict[str, int] = field(default_factory=dict)
    spawn_timer: float = 0.0
    spawned: bool = False

    def is_spawner(self) -> bool:
        return self.tipo == "entrada_esgoto.png"

@dataclass
class TileData:
    col: int
    row: int
    tipo: str

@dataclass
class EntityRef:
    ent: Any

class WorldLogico:
    def __init__(self, tile_size: int = 75, tile_height_ratio: float = 0.8, offset_x: float = 0.0, offset_y: float = 0.0):
        self.linhas: int = 0
        self.colunas: int = 0
        self.tile_size = tile_size
        self.tile_height = tile_size * tile_height_ratio
        self.offset_x = offset_x
        self.offset_y = offset_y

        self.tiles: List[TileData] = []
        self.objetos: List[ObjData] = []
        self.entidades: List[EntityRef] = []
        self.player_ref: Optional[EntityRef] = None

        self.masmorra: Dict[int, Dict[str, Any]] = {}
        self.descida_dungeon: Optional[Tuple[int,int]] = None
        self.subida_dungeon: Optional[Tuple[int,int]] = None

        self.padrao = {
            "spawner": {
                'esgoto': "entrada_esgoto.png",
                None: "entrada_esgoto.png"
            },
            "obj": {
                'esgoto': "veneno.png",
                None: "pedra.png"
            },
            "grid": {
                'esgoto': "ladrilhos_esgoto.png",
                None: "terra.png"
            }
        }

        self.nivel = 0
        self.type = None
        self.lista_modificadores = ["coleta", "combate"]
        self.mapa_modificador = "coleta"
        self.boss_ref = None

        self._events: List[Dict[str, Any]] = []


    def _obj_props_from_tipo(self, tipo: str) -> Dict[str, Any]:
        props = {"colisivel": True, "quebravel": False, "dano_colisao": 0.0, "drops": {}}
        if tipo == "pedra.png":
            props["quebravel"] = True
            props["resistencia"] = 23
            apatita = random.randint(0, 6) - 4
            mica = random.randint(0, 5) - 3
            if apatita > 0:
                props["drops"]["apatita"] = apatita
            if mica > 0:
                props["drops"]["mica"] = mica
        elif tipo == "veneno.png":
            props["colisivel"] = False
            props["dano_colisao"] = 0.075
            props["resistencia"] = 0
        elif tipo in ("entrada_esgoto.png", "descer_esgoto.png", "subir_esgoto.png"):
            props["colisivel"] = True
            props["resistencia"] = 0
        else:
            props["resistencia"] = 0
        return props

    def _grid_to_world_pos(self, col: int, row: int) -> Tuple[float, float]:
        x = self.offset_x + (col * self.tile_size)
        y = self.offset_y + (row * self.tile_height)
        return (x, y)

    def _obj_hitbox(self, obj: ObjData) -> Tuple[float, float, float, float]:
        x, y = self._grid_to_world_pos(obj.col, obj.row)
        w = self.tile_size
        h = self.tile_height
        if obj.tipo == 'pedra.png':
            return (x + (w * 0.15), y + (h * 0.5), w * 0.7, h * 0.6)
        elif obj.tipo in ('entrada_esgoto.png', 'descer_esgoto.png', 'veneno.png', 'subir_esgoto.png'):
            return (x + (w * 0.2), y + (h * 0.7), w * 0.6, h * 0.4)
        else:
            return (x, y, w, h)

    def _entity_hitbox(self, ent) -> Tuple[float, float, float, float]:
        return ent.get_hitbox()

    def _collision(self, hb1, hb2) -> bool:
        x1, y1, w1, h1 = hb1
        x2, y2, w2, h2 = hb2
        return (x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2)

    def create(self, xm: int, ym: int, type: Optional[str] = None):
        type = 'esgoto' if type is None else type
        self.type = type

        combate_nivel = 1
        if self.mapa_modificador == "combate":
            combate_nivel = 2.5
        elif self.mapa_modificador == "coleta":
            combate_nivel = 1

        if type == "esgoto":
            if self.nivel <= 0:
                self.nivel = 1
            if self.nivel not in self.masmorra:
                self.masmorra[self.nivel] = {}
            if self.nivel > 0:
                self.subida_dungeon = self.descida_dungeon
            y = random.randint(0, xm - 1)
            x = random.randint(0, ym - 1)
            self.descida_dungeon = (x, y)
            if self.descida_dungeon == self.subida_dungeon:
                y = random.randint(0, xm - 1)
                x = random.randint(0, ym - 1)
                self.descida_dungeon = (x, y)
            if self.nivel == 10:
                combate_nivel = 7

        if type is None:
            self.nivel = 0

        grid_padrao = self.padrao["grid"][type]
        objeto_padrao = self.padrao["obj"][type]
        spawner_padrao = self.padrao["spawner"][type]

        self.linhas = xm
        self.colunas = ym

        self.tiles = []
        self.objetos = []

        for row in range(self.linhas):
            for col in range(self.colunas):
                self.tiles.append(TileData(col=col, row=row, tipo=grid_padrao))

        if self.player_ref:
            px, py = self.offset_x, self.offset_y
            self.player_ref.ent.x = px
            self.player_ref.ent.y = py
            self.entidades = [self.player_ref]
        else:
            self.entidades = []

        for row in range(self.linhas):
            for col in range(self.colunas):
                if self.descida_dungeon == (col, row):
                    tipo = "descer_esgoto.png"
                    props = self._obj_props_from_tipo(tipo)
                    obj = ObjData(col=col, row=row, tipo=tipo, resistencia=props.get("resistencia", 0), ativado=False, colisivel=props["colisivel"], quebravel=props["quebravel"], dano_colisao=props["dano_colisao"], drops=props["drops"])
                    self.objetos.append(obj)
                    continue
                if self.subida_dungeon == (col, row):
                    tipo = "subir_esgoto.png"
                    props = self._obj_props_from_tipo(tipo)
                    obj = ObjData(col=col, row=row, tipo=tipo, resistencia=props.get("resistencia", 0), ativado=False, colisivel=props["colisivel"], quebravel=props["quebravel"], dano_colisao=props["dano_colisao"], drops=props["drops"])
                    self.objetos.append(obj)
                    continue
                r = random.randint(0, 10)
                if r == 0:
                    if not ((col == 0 or col == 1) and (row == 0 or row == 1)):
                        m = random.randint(0, 100)
                        if m < (10 + self.nivel) * combate_nivel:
                            tipo = spawner_padrao
                        else:
                            tipo = objeto_padrao
                        props = self._obj_props_from_tipo(tipo)
                        obj = ObjData(col=col, row=row, tipo=tipo, resistencia=props.get("resistencia",0), ativado=False, colisivel=props["colisivel"], quebravel=props["quebravel"], dano_colisao=props["dano_colisao"], drops=props["drops"])
                        if obj.is_spawner():
                            obj.spawn_timer = 0.5 * random.uniform(0.8, 1.2)
                        self.objetos.append(obj)

        self.masmorra[self.nivel] = {
            "tiles": [(t.col, t.row, t.tipo) for t in self.tiles],
            "objs": [(o.col, o.row, o.tipo, o.resistencia, o.ativado) for o in self.objetos]
        }

        if self.nivel == 10:
            self._events.append({"type":"gerar_boss"})

    def carregar_mapa(self, sala: Dict[str, Any]):
        if not sala:
            return
        self.tiles = [TileData(col=c, row=r, tipo=t) for (c,r,t) in sala.get("tiles",[])]
        self.objetos = []
        for (c, r, tipo, resistencia, ativado) in sala.get("objs", []):
            props = self._obj_props_from_tipo(tipo)
            obj = ObjData(col=c, row=r, tipo=tipo, resistencia=resistencia, ativado=ativado, colisivel=props["colisivel"], quebravel=props["quebravel"], dano_colisao=props["dano_colisao"], drops=props["drops"])
            if obj.is_spawner():
                obj.spawn_timer = 0.5 * random.uniform(0.8, 1.2)
            self.objetos.append(obj)

    def re_map(self, type: Optional[str], nivel: int = 1):
        if type is None:
            type = 'esgoto'
        if type == self.type:
            self.nivel += nivel
        else:
            self.type = type
            self.nivel += nivel

        self.entidades = [e for e in self.entidades if e is self.player_ref]

        self.mapa_modificador = random.choice(self.lista_modificadores)

        if self.nivel < 0 or self.nivel > 10:
            self.type = None
            self.nivel = 0

        if self.nivel in self.masmorra:
            self.carregar_mapa(self.masmorra[self.nivel])
        else:
            xm = self.linhas or 10
            ym = self.colunas or 10
            self.create(xm, ym, type)

    def add_objects(self, tipo: str, grid: Tuple[int,int]):
        col, row = grid
        props = self._obj_props_from_tipo(tipo + ".png") if not tipo.endswith(".png") else self._obj_props_from_tipo(tipo)
        tipo_full = tipo if tipo.endswith(".png") else tipo + ".png"
        obj = ObjData(col=col, row=row, tipo=tipo_full, resistencia=props.get("resistencia",0), ativado=False, colisivel=props["colisivel"], quebravel=props["quebravel"], dano_colisao=props["dano_colisao"], drops=props["drops"])
        self.objetos.append(obj)
        self._events.append({"type":"add_object","obj":obj})


    def _apply_tile_limits(self, ent):
        right_limit = self.offset_x + (self.colunas * self.tile_size) - (ent.largura * 0.75)
        left_limit = self.offset_x - (ent.largura * 0.25)
        bottom_limit = self.offset_y
        top_limit = self.offset_y + (self.linhas * self.tile_height) - (ent.altura / 2)

        if ent.x > right_limit:
            ent.x = right_limit
        elif ent.x < left_limit:
            ent.x = left_limit
        if ent.y < bottom_limit:
            ent.y = bottom_limit
        elif ent.y > top_limit:
            ent.y = top_limit

    def _resolve_object_collision(self, ent, obj: ObjData):
        if obj.tipo == 'veneno.png':
            gx = int((ent.centro_hitbox()[0] - self.offset_x) / self.tile_size)
            gy = int((ent.centro_hitbox()[1] - self.offset_y) / self.tile_height)
            if (gx, gy) == (obj.col, obj.row):
                ent.vida -= obj.dano_colisao
                self._events.append({"type":"dano","target":ent,"amount":obj.dano_colisao})
        if obj.tipo in ('descer_esgoto.png','subir_esgoto.png'):
            alive_nonplayer = [e for e in self.entidades if e is not self.player_ref and e.ent.vivo]
            if not alive_nonplayer and self.player_ref:
                nivel = -1 if obj.tipo == 'subir_esgoto.png' else 1
                self._events.append({"type":"remap","nivel":nivel,"map_type":"esgoto"})
        if obj.quebravel:
            if obj.resistencia <= 0:
                self._events.append({"type":"obj_quebrado","obj":obj})
                try:
                    self.objetos.remove(obj)
                except ValueError:
                    pass

    def verificar_colisao_horizontal(self, ent, dt: float):
        original_x = ent.x
        ent.x += ent.speed_x * ent.velocidade * dt
        ent_hit = self._entity_hitbox(ent)

        for obj in list(self.objetos):
            obj_hb = self._obj_hitbox(obj)
            if self._collision(ent_hit, obj_hb):
                self._resolve_object_collision(ent, obj)
                if obj.colisivel:
                    ent.x = original_x
                    ent.speed_x = 0
                    ent_hit = self._entity_hitbox(ent)
                    obj_x, obj_y = self._grid_to_world_pos(obj.col, obj.row)
                    ent.x = obj_x + self.tile_size
                    ent.speed_x = 0
                    ent_hit = self._entity_hitbox(ent)

        for ref in self.entidades:
            other = ref.ent
            if other is ent:
                continue
            if not other.vivo:
                continue
            other_hit = self._entity_hitbox(other)
            if self._collision(ent_hit, other_hit):
                if not ent.i_frames:
                    ent.vida -= other.dano_contato if hasattr(other,"dano_contato") else 0
                    self._events.append({"type":"dano","target":ent,"amount": other.dano_contato if hasattr(other,"dano_contato") else 0})
                if not other.i_frames:
                    other.vida -= ent.dano_contato if hasattr(ent,"dano_contato") else 0
                    self._events.append({"type":"dano","target":other,"amount": ent.dano_contato if hasattr(ent,"dano_contato") else 0})
                ent.x = original_x
                ent.speed_x = 0

    def verificar_colisao_vertical(self, ent, dt: float):
        original_y = ent.y
        ent.y += ent.speed_y * ent.velocidade * dt
        ent_hit = self._entity_hitbox(ent)

        for obj in list(self.objetos):
            obj_hb = self._obj_hitbox(obj)
            if self._collision(ent_hit, obj_hb):
                self._resolve_object_collision(ent, obj)
                if obj.colisivel:
                    ent.y = original_y
                    ent.speed_y = 0
                    ent_hit = self._entity_hitbox(ent)
                    if self._collision(ent_hit, obj_hb):
                        ent.y = self._grid_to_world_pos(obj.col, obj.row)[1]
                        ent.speed_y = 0

        for ref in self.entidades:
            other = ref.ent
            if other is ent:
                continue
            other_hit = self._entity_hitbox(other)
            if self._collision(ent_hit, other_hit):
                ent.y = original_y
                ent.speed_y = 0

    def grid_verify(self, ent):
        gx = int((ent.centro_hitbox()[0] - self.offset_x) / self.tile_size)
        gy = int((ent.centro_hitbox()[1] - self.offset_y) / self.tile_height)
        gx = max(0, min(self.colunas - 1, gx))
        gy = max(0, min(self.linhas - 1, gy))
        ent.grid = (gx, gy)

    def update(self, dt: float):
        self._events.clear()

        for ref in list(self.entidades):
            ent = ref.ent
            if hasattr(ent, "update"):
                ent.update(dt)

            self.verificar_colisao_horizontal(ent, dt)
            self.verificar_colisao_vertical(ent, dt)
            self._apply_tile_limits(ent)
            ent.hitbox = ent.get_hitbox()
            self.grid_verify(ent)

        for obj in list(self.objetos):
            if obj.is_spawner() and not obj.spawned:
                obj.spawn_timer -= dt
                if obj.spawn_timer <= 0:
                    if not obj.ativado and random.randint(1,10) > 5:
                        wx, wy = self._grid_to_world_pos(obj.col, obj.row)
                        self._events.append({"type":"spawn_entity","entity_type":"rato","pos":(wx, wy),"obj":obj})
                        obj.ativado = True
                        obj.spawned = True

        return list(self._events)

    def drain_events(self) -> List[Dict[str,Any]]:
        ev = list(self._events)
        self._events.clear()
        return ev

    def export_current_masmorra(self):
        return {
            "tiles": [(t.col, t.row, t.tipo) for t in self.tiles],
            "objs": [(o.col, o.row, o.tipo, o.resistencia, o.ativado) for o in self.objetos]
        }

    def set_player(self, player_ent):
        ref = EntityRef(ent=player_ent)
        self.player_ref = ref
        if ref not in self.entidades:
            self.entidades.insert(0, ref)
        return ref
    
    def add_entity(self, ent):
        ref = EntityRef(ent=ent)

        if any(r.ent is ent for r in self.entidades):
            return ref

        self.entidades.append(ref)
        return ref
