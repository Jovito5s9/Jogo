from core.entity.basic_ent import BasicEnt
from core.entity.interact import perseguir, rastrear
from utils.resourcesPath import resource_path

from kivy.clock import Clock
import random


class Ratona(BasicEnt):
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
        self.list_drops["gosma_misteriosa"] = 1

    def get_hitbox(self, *args):
        x = self.x + (self.width * 0.16)
        y = self.y + (self.height * 0.1)
        width = self.width * 0.68
        height = self.height * 0.6
        self.get_center_hitbox(x, y, width, height)
        return [x, y, width, height]

    def add_player(self, *args):
        try:
            self.player = self.world.player
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
        self.x += self.velocidade * (x / abs(x))
        self.y += self.velocidade * (y / abs(y))
