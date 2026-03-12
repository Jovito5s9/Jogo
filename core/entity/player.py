from kivy.clock import Clock
from core.entity.basic_ent import BasicEnt
from core.entity.interact import atacar, distancia
from utils.resourcesPath import resource_path

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

        self.respawning=False

        self.atualizar()
        self.repulsao = 20
        self.alcance_fisico = 100
        self.acoes = {
            "soco_normal": self.soco_normal,
            "soco_forte": self.soco_forte
        }
        self.acao = ""
        Clock.schedule_interval(self.verificar_acao, 1 / 20)
        Clock.schedule_interval(self.check_vida, 1 / 3)
        self.load_data()

        if not self.bitcores:
            self.bitcores = {
            "núcleo ceifador de energia": 1,
            "núcleo do instinto de pânico": 1,
            "núcleo da esquiva aleatória": 1,
            "núcleo do punho explosivo":1,
            "núcleo da vitalidade extendida":1
        }# so pra garantir que o user vai conseguir testar antes de ter metodo de obtenção em si
    
    def respawn(self,*args):
        self.i_frames=True
        self.vida=self.vida_maxima
        self.vivo=True
        self.estado="idle"
        self.world.respawn_player()
        self.respawning=False

    def check_vida(self,*args):
        if self.vivo:
            return
        if self.respawning:
            return
        self.respawning=True
        Clock.schedule_once(self.respawn, 3)

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
        # percorre entidades no parent
        try:
            ents = self.world.ents
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
            obj_list = self.world.map.obj_list
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
            except Exception:
                pass
        else:
            self.acao = ""
