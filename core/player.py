from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.properties import OptionProperty, BooleanProperty, NumericProperty

import random
import json
import os
from utils.resourcesPath import resource_path
from core.BitCoreSkills import SKILLS

class Barra(Widget):
    modificador = NumericProperty(100)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cor = ([1, 0, 0, 1])
        self.w = 1
        self.h = 1
        with self.canvas:
            self.color = Color(*self.cor)
            self.rect = Rectangle(
                pos=self.pos,
                size=(self.w * (self.modificador / 100) + 1, self.h),
            )
        self.bind(pos=self.atualizar)
        self.bind(modificador=self.atualizar)
        self.bind(size=self.atualizar)

    def atualizar(self, *args):
        # Posiciona o rect relativo ao centro horizontal definido por self.w
        self.rect.pos = (self.x - (self.w / 2), self.y)
        self.rect.size = (self.w * (self.modificador / 100) + 1, self.h)


class BasicEnt(Image):
    vida = NumericProperty(1)
    i_frames = BooleanProperty(False)
    estado = OptionProperty("idle", options=("idle", "running", "atacando", "morto"))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # propriedades padrão
        self.size = (32, 32)
        self.pos = (100, 100)
        self.size_hint = (None, None)
        self.frame_width = 32
        self.frame_height = 32
        self.recompensa = 0
        self.i_frames_time = 0.8
        self.tamanho = 1
        self.vida_maxima = 100
        self.vida = self.vida_maxima
        self.vivo = True
        self.ataque_name = ""
        self.repulsao = 10
        self.power = 5
        self.dano = self.power
        self.atacando = False
        self.alcance_fisico = 70
        self.dano_contato = 0
        self.velocidade = 3
        self.speed_x = 0
        self.speed_y = 0
        self.facing_right = True
        self.idle_frames = 1
        self.running_frames = 1
        self.atacando_frames = 1
        self.alvo = False
        self.player = None
        self.hitbox = ()
        self.center_hitbox_x = 0
        self.center_hitbox_y = 0
        self.sources = {}
        self.list_drops = {}
        self.droped = False
        self.inventario = {}
        self.grid = []
        self.skills_slots = {}
        self.skills_ativas = {}
        self.dano_causado=0

        # atributos de animação (inicialmente vazios)
        self.sprite_sheet = None
        self.total_frames = 1
        self.current_frame = 0

    def atualizar(self, *args):
        # Carrega o sprite sheet
        self.sprite_sheet = self.carregar_sprite("idle")
        if not self.sprite_sheet:
            return

        self.total_frames = self.idle_frames
        self.current_frame = 0

        # Ajusta o tamanho do Image (o próprio BasicEnt é a Image)
        self.width = self.frame_width * self.tamanho
        self.height = self.frame_height * self.tamanho
        self.allow_stretch = True
        self.keep_ratio = False

        # Atualiza hitbox
        self.hitbox = self.get_hitbox()

        # Inicia com o primeiro frame
        self.update_texture()

        # Agendar a animação
        Clock.schedule_interval(self.animation, 0.15)

        # Barra de vida
        self.barra_vida = Barra(size=(self.width, 10), pos=(self.center_x, self.center_y))
        self.barra_vida.w = self.width / 3
        self.barra_vida.h = 10
        # Como BasicEnt é um Image (Widget), podemos adicionar a barra como filho
        try:
            self.add_widget(self.barra_vida)
        except Exception:
            # Se for usado em contexto onde add_widget não é apropriado, ignore silenciosamente
            pass

    def move_x(self, *args):
        if self.vivo:
            self.x += self.speed_x * self.velocidade

    def move_y(self, *args):
        if self.vivo:
            self.y += self.speed_y * self.velocidade

    def atualizar_pos(self, *args):
        if not self.vivo:
            return
        if self.speed_x > 0:
            self.facing_right = True
        elif self.speed_x < 0:
            self.facing_right = False
        if self.atacando:
            self.estado = "atacando"
        elif self.speed_x != 0 or self.speed_y:
            self.estado = "running"
        else:
            self.estado = "idle"
        # atualiza posição da barra de vida (se existir)
        try:
            self.barra_vida.pos = (self.center_x, self.center_y)
        except Exception:
            pass
        self.hitbox = self.get_hitbox()

    def on_estado(self, *args):
        if not self.vivo:
            self.sprite_sheet = self.carregar_sprite("morto")
            self.total_frames = 1
            return
        if self.estado == "atacando":
            self.sprite_sheet = self.carregar_sprite(self.ataque_name)
            self.total_frames = self.atacando_frames
        elif self.estado == "idle":
            self.sprite_sheet = self.carregar_sprite("idle")
            self.total_frames = self.idle_frames
        elif self.estado == "running":
            self.sprite_sheet = self.carregar_sprite("running")
            self.total_frames = self.running_frames
        if not self.sprite_sheet:
            return
        self.current_frame = 0
        self.update_texture()

    def carregar_sprite(self, key):
        source = self.sources.get(key)
        if not source or not os.path.exists(source):
            return None
        img = Image(source=source)
        return img.texture

    def update_texture(self):
        if not self.sprite_sheet:
            return
        x = int(self.frame_width * self.current_frame)
        y = 0

        # get_region aceita coordenadas e tamanho; suporta invertendo largura para flip
        if self.facing_right:
            tex = self.sprite_sheet.get_region(x, y, int(self.frame_width), int(self.frame_height))
        else:
            # flip horizontal
            tex = self.sprite_sheet.get_region(x + int(self.frame_width), y, -int(self.frame_width), int(self.frame_height))

        # aplica a textura ao próprio Image
        self.texture = tex

    def animation(self, dt):
        if not self.total_frames:
            return
        self.current_frame = (self.current_frame + 1) % self.total_frames
        self.update_texture()

    def get_center_hitbox(self, x, y, w, h):
        self.center_hitbox_x, self.center_hitbox_y = (x + w / 2, y + h / 2)

    def get_hitbox(self, *args):
        # calcula hitbox relativo ao tamanho atual do sprite (self.width/self.height)
        x = self.x + (self.width * 0.25)
        y = self.y + (self.height * 0.1)
        width = self.width * 0.5
        height = self.height * 0.35
        self.get_center_hitbox(x, y, width, height)
        return [x, y, width, height]

    def perder_i_frames(self, *args):
        self.i_frames = False

    def on_i_frames(self, *args):
        if self.i_frames:
            Clock.schedule_once(self.perder_i_frames, self.i_frames_time)

    def drop(self, *args):
        if not self.list_drops or self.droped:
            return
        self.recive_itens(self.list_drops)
        self.droped = True

    def recive_itens(self, list_drops):
        for drop, quantidade in list_drops.items():
            if quantidade == 0:
                pass
            # garante que parent e parent.player existam
            try:
                self.parent.player.inventario[drop] = self.parent.player.inventario.get(drop, 0) + quantidade
                self.save_data("inventario", {drop: self.parent.player.inventario[drop]})
            except Exception:
                pass

    def morrer(self, *args):
        self.vivo = False
        self.estado = "morto"
        self.speed_x = 0
        self.speed_y = 0
        if not self.parent.player == self:
            self.drop()

    def on_vida(self, *args):
        self.i_frames = True
        vida_mod = 100 * self.vida / self.vida_maxima
        if vida_mod < 0:
            vida_mod = 0
        try:
            self.barra_vida.modificador = vida_mod
        except Exception:
            pass
        if self.vida <= 0:
            self.morrer()
        
    def carregar_skill(self, skill):
        cls = SKILLS[skill]
        passiva = cls(self)

        passiva.on_add()

        if passiva.schedule_interval:
            passiva._clock = Clock.schedule_interval(
                passiva.skill,
                passiva.schedule_interval
            )
        self.skills_ativas[skill] = passiva

        

    def rodar_skills(self):
        for slot, skill_name in self.skills_slots.items():
            if skill_name not in self.skills_ativas:
                self.carregar_skill(skill_name)

            

    def save_data(self, item, key):
        path = resource_path("saved/player.json")
        if not os.path.exists(path):
            data = {}
        else:
            with open(path, "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = {}
        encontrado = False
        if item in data:
            if isinstance(data[item], list):
                if key not in data[item]:
                    data[item].append(key)
            elif isinstance(data[item], dict):
                data[item].update(key)
            else:
                data[item] = key
            encontrado = True
        else:
            for k, v in data.items():
                if isinstance(v, dict):
                    if item in v:
                        v[item] = key
                        encontrado = True
                        break
                elif isinstance(v, list):
                    if item in v:
                        v.append(key)
                        encontrado = True
                        break
        if not encontrado:
            data[item] = key
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)


def mover(ent, dx, dy):
    ent.speed_x = dx
    ent.speed_y = dy


def perseguir(rastreador):
    dx = 0
    dy = 0
    try:
        if rastreador.player.center_hitbox_x > rastreador.center_hitbox_x:
            dx = 1
        elif rastreador.player.center_hitbox_x < rastreador.center_hitbox_x:
            dx = -1
        if rastreador.player.center_hitbox_y > rastreador.center_hitbox_y:
            dy = 1
        elif rastreador.player.center_hitbox_y < rastreador.center_hitbox_y:
            dy = -1
    except Exception:
        pass
    mover(rastreador, dx, dy)


def rastrear(rastreador):
    if not rastreador.player:
        return

    d = distancia(rastreador)
    if d > 0 and d <= rastreador.raio_visao:
        rastreador.alvo = True


def atacar(atacante, alvo=None):
    if alvo is None:
        if not atacante.player:
            return
        alvo = atacante.player
    if not alvo.i_frames:
        atacante.estado = "atacando"
        knockback = 1
        if not alvo.vivo:
            knockback = 2
        if atacante.facing_right:
            alvo.x += atacante.repulsao * knockback
        else:
            alvo.x -= atacante.repulsao * knockback
        alvo.y += atacante.speed_y * atacante.repulsao * knockback
        atacante.speed_x = 0
        atacante.speed_y = 0
        alvo.vida -= atacante.dano
    return


def distancia(ent1, ent2=None):
    try:
        if ent2 is None:
            d1 = ent1.player.center_hitbox_x - ent1.center_hitbox_x
            d2 = ent1.player.center_hitbox_y - ent1.center_hitbox_y
            return ((d1 * d1 + d2 * d2) ** 0.5)
        else:
            d1 = ent2.center_hitbox_x - ent1.center_hitbox_x
            d2 = ent2.center_hitbox_y - ent1.center_hitbox_y
            return ((d1 * d1 + d2 * d2) ** 0.5)
    except Exception:
        return 0


# funcao destinada a colocar as possibilidades de acoes de entidades basicas
def ia_base():
    acoes = {
        "perseguir": perseguir,
        "rastrear": rastrear,
        "atacar": atacar
    }
    return acoes


class Rato(BasicEnt):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sources["idle"] = resource_path("assets/sprites/rato/idle.png")
        self.sources["running"] = resource_path("assets/sprites/rato/running.png")
        self.sources["morto"] = resource_path("assets/sprites/rato/morto.png")
        self.sources["garras"] = resource_path("assets/sprites/rato/garras.png")
        self.idle_frames = 2
        self.running_frames = 2
        self.atacando_frames = 2
        self.tamanho = 2.8

        self.atualizar()
        self.acoes = ia_base()
        Clock.schedule_interval(self.ia, 1 / 10)
        Clock.schedule_once(self.add_player, 2)
        self.atributos()

    def atributos(self, *args):
        self.raio_visao = 300
        self.vida_maxima = 30
        self.vida = 30
        self.dano = 5
        self.velocidade = 1.5
        self.list_drops["carne"] = random.randint(0, 2)

    def add_player(self, *args):
        try:
            self.player = self.parent.player
        except Exception:
            self.player = None

    def ia(self, *args):
        if not self.vivo:
            return
        if self.alvo:
            if distancia(self) <= self.alcance_fisico and not self.atacando:
                self.ataque_name = "garras"
                self.acoes["atacar"](self)
                self.atacando = True
                Clock.schedule_once(self.atualizar_atacando, 0.4)
            else:
                self.acoes["perseguir"](self)
        else:
            self.acoes["rastrear"](self)

    def atualizar_atacando(self, *args):
        self.atacando = False
        if self.speed_x or self.speed_y:
            self.estado = "running"
        else:
            self.estado = "idle"


class Rata_mae(BasicEnt):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sources["idle"] = resource_path("assets/sprites/rata_mae/idle.png")
        self.sources["preparing"] = resource_path("assets/sprites/rata_mae/preparing.png")
        self.sources["rolling"] = resource_path("assets/sprites/rata_mae/rolling.png")
        self.sources["morto"] = resource_path("assets/sprites/rata_mae/dead.png")
        self.idle_frames = 3
        self.running_frames = 3
        self.atacando_frames = 3
        self.tamanho = 3.5
        self.alvo_pos = []

        self.atualizar()
        self.acoes = {
            "perseguir": perseguir,
            "rastrear": rastrear,
            "atacar": self.preparar_rolar
        }
        self.investida = None
        Clock.schedule_interval(self.ia, 1 / 10)
        Clock.schedule_once(self.add_player, 1)
        self.atributos()
        self.frame_width = 96
        self.frame_height = 64

    def atributos(self, *args):
        self.raio_visao = 700
        self.vida_maxima = 450
        self.vida = 450
        self.dano_contato = 5
        self.velocidade = 1.5
        self.alcance_fisico = 450
        self.list_drops["carne"] = random.randint(3, 7)

    def get_hitbox(self, *args):
        x = self.x + (self.width * 0.16)
        y = self.y + (self.height * 0.1)
        width = self.width * 0.68
        height = self.height * 0.6
        self.get_center_hitbox(x, y, width, height)
        return [x, y, width, height]

    def add_player(self, *args):
        try:
            self.player = self.parent.player
        except Exception:
            self.player = None

    def ia(self, *args):
        if not self.vivo:
            return
        if self.alvo:
            if not self.atacando:
                self.acoes["atacar"]()
        else:
            self.acoes["rastrear"](self)

    def preparar_rolar(self, *args):
        if self.atacando:
            return
        try:
            self.alvo_pos = self.player.pos
        except Exception:
            self.alvo_pos = [0, 0]
        self.estado = "atacando"
        self.ataque_name = "preparing"
        self.atacando = True
        Clock.schedule_once(self.rolar, 0.3)

    def rolar(self, *args):
        self.ataque_name = "rolling"
        self.velocidade *= 2
        self.investida = Clock.schedule_interval(self.acelerar, 0.05)
        Clock.schedule_once(self.parar_rolar, 1)

    def parar_rolar(self, *args):
        self.atacando = False
        self.estado = "idle"
        self.velocidade /= 2

        if self.investida:
            self.investida.cancel()
            self.investida = None

    def acelerar(self, *args):
        perseguir(self)
        x, y = self.alvo_pos
        if x == 0: x = 1
        if y == 0: y = 1
        # mover-se na direção do alvo
        self.x += self.velocidade * (x / abs(x))
        self.y += self.velocidade * (y / abs(y))


class Player(BasicEnt):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sources["idle"] = resource_path("assets/sprites/player/idle.png")
        self.sources["running"] = resource_path("assets/sprites/player/running.png")
        self.sources["morto"] = resource_path("assets/sprites/player/morto.png")
        self.sources["soco"] = resource_path("assets/sprites/player/soco.png")
        self.sources["soco_forte"] = resource_path("assets/sprites/player/soco_forte.png")
        self.idle_frames = 2
        self.running_frames = 4
        self.atacando_frames = 3
        self.tamanho = 4

        self.atualizar()
        self.repulsao = 20
        self.alcance_fisico = 100
        self.skills_slots={
            "1": "vampirismo",
            #"2": "panico",
            #"3": "esguio"
            }
        self.acoes = {
            "soco_normal": self.soco_normal,
            "soco_forte": self.soco_forte
        }
        self.acao = ""
        Clock.schedule_interval(self.verificar_acao, 1 / 20)
        self.rodar_skills()

    def soco_normal(self, *args):
        if self.atacando:
            self.acao = ""
            return
        self.ataque_name = "soco"
        self.atacar()
        Clock.schedule_once(self.remover_ataque, 0.4)

    def atacar(self, *args):
        if self.atacando:
            self.acao = ""
            return
        self.atacando = True
        repulsao = self.repulsao
        if self.ataque_name == "soco_forte":
            self.dano = self.power * 1.2
            self.repulsao = 1.5 * self.repulsao
        # percorre entidades no parent (se definido)
        try:
            ents = self.parent.ents
        except Exception:
            ents = []
        for ent in ents:
            if not ent == self:
                if distancia(self, ent) <= self.alcance_fisico:
                    if self.facing_right and ent.x >= self.x:
                        atacar(self, ent)
                    elif not self.facing_right and ent.x <= self.x:
                        atacar(self, ent)
        self.dano_causado=self.dano
        self.dano = self.power
        self.repulsao = repulsao

    def remover_ataque(self, *args):
        self.atacando = False
        if self.speed_x or self.speed_y:
            self.estado = "running"
        else:
            self.estado = "idle"

    def soco_forte(self, *args):
        if self.atacando:
            self.acao = ""
            return
        try:
            alvo_x, alvo_y = self.grid
        except Exception:
            alvo_x, alvo_y = (0, 0)
        if self.facing_right:
            alvo_x += 1
        else:
            alvo_x -= 1
        try:
            obj_list = self.parent.obj_list
        except Exception:
            obj_list = []
        for obj in obj_list:
            if obj.linha == alvo_y and obj.coluna == alvo_x and obj.quebravel:
                obj.resistencia -= self.power
            if (obj.coluna, obj.linha) == tuple(self.grid) and obj.quebravel:
                obj.resistencia -= self.power

        self.ataque_name = "soco_forte"
        self.atacar()
        Clock.schedule_once(self.remover_ataque, 0.8)

    def verificar_acao(self, *args):
        if not self.acao or not self.vivo:
            return

        action = self.acoes.get(self.acao)
        if action and callable(action):
            try:
                action()
            except Exception as e:
                print("Erro ao executar ação", self.acao, ":", e)
        else:
            self.acao = ""
