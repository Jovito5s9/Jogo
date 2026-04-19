from kivy.clock import Clock
from kivy.core.window import Window
from core.entity.basic_ent import BasicEnt, Menu_interact, Ballon as blln
from core.entity.interact import atacar, distancia
from utils.resourcesPath import resource_path

class DriverInteract(Menu_interact):
    def __init__(self, nome_npc="", escolhas=..., funcs=..., **kwargs):
        super().__init__(nome_npc, escolhas, funcs, **kwargs)
    
class Ballon(blln):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_release(self):
        if not self.parent:
            return
        self.parent.add_interact_menu()
        self.parent.remove_widget(self)


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

        self.driver_menu=None
        self.ballon=Ballon()

        self.drivers=[]
        self.drivers_cache=[]

        self.respawning=False

        self.menu_is_active=False

        self.atualizar()
        self.repulsao = 20
        self.alcance_fisico = 100
        self.ataque_forte_delay = 0.3
        self.acoes = {
            "soco_normal": self.soco_normal,
            "soco_forte": self.soco_forte
        }
        self.acao = ""
        Clock.schedule_interval(self.verificar_acao, 1 / 20)
        Clock.schedule_interval(self.check_vida, 1 / 3)
        self.load_data()

        Clock.schedule_interval(self.driver_atualizar,1/40)


        if not self.bitcores:
            self.bitcores = {
            "núcleo ceifador de energia": 1,
            "núcleo do instinto de pânico": 1,
            "núcleo da esquiva aleatória": 1,
            "núcleo do punho explosivo":1,
            "núcleo da vitalidade extendida":1
        }# so pra garantir que o user vai conseguir testar antes de ter metodo de obtenção em si
    
    def driver_atualizar(self,*args):
        if self.drivers==self.drivers_cache:
            return
        if self.menu_is_active:
            return
        self.add_ballon()

    def add_ballon(self,*args):
        std_size=100
        if not self.ballon in self.children:
            self.add_widget(self.ballon)
        self.ballon.pos=self.center_x - std_size/2,self.y+self.height*0.4
        self.ballon.size=(std_size,std_size)

    def add_interact_menu(self,*args):
        self.menu_is_active=True
        driver = [item for item in self.drivers if item not in self.drivers_cache]
        driver=driver[0]
        interactions_text=[
            f"instalar driver",
            "não instalar driver"
        ]
        interactions_funcs=[
            self.aceitar_driver,
            self.free_menu
        ]
        self.driver_menu=DriverInteract(nome_npc=driver,escolhas=interactions_text,funcs=interactions_funcs)
        self.world.parent.parent.add_widget(self.driver_menu)
    
    def aceitar_driver(self,*args):
        driver = [item for item in self.drivers if item not in self.drivers_cache]
        if not driver:
            return
        driver=driver[0]
        self.drivers_cache.append(driver)
        l=[]
        for i in self.drivers_cache:
            if not i in l:
                l.append(i)
        l.sort()
        self.drivers_cache=l
        self.free_menu()

    def free_menu(self,*args):
        self.menu_is_active=False
        if self.driver_menu in self.world.parent.parent.children:
            self.world.parent.parent.remove_widget(self.driver_menu)


    def unlock_skill(self,skill):
        self.drivers.append(skill)
        

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
        if self.ataque_name=="soco_forte":
            Clock.schedule_once(self.remover_atacando,self.ataque_forte_delay)
            self.ataque_delay=True
        else:
            self.remover_atacando()
        
        if self.speed_x or self.speed_y:
            self.estado = "running"
        else:
            self.estado = "idle"

    def remover_atacando(self,*args):
        self.atacando = False
        if self.ataque_delay:
            self.ataque_delay=False

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
        Clock.schedule_once(self.remover_ataque, 0.4)

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
