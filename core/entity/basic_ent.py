from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.properties import OptionProperty, BooleanProperty, NumericProperty

import json
import os
from utils.resourcesPath import resource_path
from core.BitCoreSkills import SKILLS
from saved.itens_db import ITENS

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
        self.bitcores = {}
        self.skills_slots = {}
        self.skills_ativas = {}
        self.max_skills = 2
        self.dano_causado=0
        if self.parent:
            self.world = self.parent.parent.parent
        else:
            self.world = None
            self.procurar_parent()

        # atributos de animação (inicialmente vazios)
        self.sprite_sheet = None
        self.total_frames = 1
        self.current_frame = 0
    
    def procurar_parent(self, *args):
        if self.parent:
            self.world = self.parent.parent.parent
            print(self.world.player)
        else:
            Clock.schedule_once(self.procurar_parent, 0.2)
            

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
        if not hasattr(self.world.player, "inventario"):
            return
        
        for drop, quantidade in list_drops.items():
            if quantidade <= 0:
                continue
            # garante que parent e parent.player existam
            
            self.world.player.inventario[drop] = self.world.player.inventario.get(drop, 0) + quantidade
            if hasattr(self.world.player, "save_data"):
                self.world.player.save_data("inventario", {drop: self.world.player.inventario[drop]})

    def morrer(self, *args):
        self.vivo = False
        self.estado = "morto"
        self.speed_x = 0
        self.speed_y = 0
        if not self.world.player == self:
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
        
    def receber_bitcore(self, bitcore_id, qtd=1):
        self.bitcores[bitcore_id] = self.bitcores.get(bitcore_id, 0) + qtd
        self.save_data("bitcores", {bitcore_id: self.bitcores[bitcore_id]})
    
    def equipar_bitcore(self, skill_id):

        if skill_id in self.skills_slots.values():
            return False

        slot_livre = None
        for i in range(1, self.max_skills + 1):
            s = str(i)
            if s not in self.skills_slots:
                slot_livre = s
                break

        if slot_livre is None:
            return False

        self.skills_slots[slot_livre] = skill_id
        self.save_data("equipaveis", None)
        self.rodar_skills()
        return True


    def desequipar_slot(self, slot):
        slot = str(slot)

        if slot in self.skills_slots:
            del self.skills_slots[slot]

        self.save_data("equipaveis", None)
        self.rodar_skills()


    def rodar_skills(self):
        valid_equipped = {}
        for slot, skill_id in list(self.skills_slots.items()):
            try:
                idx = int(slot)
            except Exception:
                continue
            if 1 <= idx <= self.max_skills:
                valid_equipped[slot] = skill_id
                if skill_id not in self.skills_ativas:
                    self._ativar_skill(skill_id)

        equipped_set = set(valid_equipped.values())
        for skill_id in list(self.skills_ativas.keys()):
            if skill_id not in equipped_set:
                self._desativar_skill(skill_id)

            
    def _ativar_skill(self, skill_id):
        cls = SKILLS.get(skill_id)
        if not cls:
            return

        passiva = cls(self)
        passiva.on_add()
        self.skills_ativas[skill_id] = passiva
    
    def _desativar_skill(self, skill_id):
        passiva = self.skills_ativas.get(skill_id)
        if not passiva:
            return

        passiva.on_remove()
        del self.skills_ativas[skill_id]


    def save_data(self, item, key=None):
        path = resource_path("saved/player.json")

        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except Exception:
            data = {}

        if item == "equipaveis":
            equip_map = {}
            itens_equip = ITENS.get("equipaveis", {})

            for slot, skill_id in list(getattr(self, "skills_slots", {}).items()):
                try:
                    idx = int(slot)
                except Exception:
                    continue

                if not (1 <= idx <= self.max_skills):
                    continue

                found_name = None
                for item_name, item_data in itens_equip.items():
                    if item_data.get("skill") == skill_id:
                        found_name = item_name
                        break

                if found_name:
                    equip_map[str(idx)] = found_name

            data["equipaveis"] = equip_map

        elif item == "bitcores":

            if isinstance(key, dict):
                data.setdefault("bitcores", {})
                for k, v in key.items():
                    data["bitcores"][k] = v
            else:
                data["bitcores"] = key

        elif item == "inventario":

            if isinstance(key, dict):
                data.setdefault("inventario", {})

                for k, v in key.items():
                    data["inventario"][k] = v
            else:
                data["inventario"] = key

        else:

            if isinstance(key, dict):
                data.setdefault(item, {})
                for k, v in key.items():
                    data[item][k] = v
            else:
                data[item] = key
        try:
            with open(path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            print("Erro ao salvar player.json:", e)



    def load_data(self, *args):
            path = resource_path("saved/player.json")

            if not os.path.exists(path):
                return

            try:
                with open(path, "r", encoding="utf-8") as file:
                    data = json.load(file)
            except (json.JSONDecodeError, OSError):
                return

            inventario = data.get("inventario")
            if isinstance(inventario, dict):
                for item, quantidade in inventario.items():
                    if isinstance(quantidade, int) and quantidade > 0:
                        self.inventario[item] = quantidade

            bitcores = data.get("bitcores")
            if isinstance(bitcores, dict):
                for bc, qtd in bitcores.items():
                    if isinstance(qtd, int) and qtd > 0:
                        self.bitcores[bc] = qtd

            equipaveis = data.get("equipaveis")
            if isinstance(equipaveis, dict):
                for slot, nome_item in equipaveis.items():
                    try:
                        idx = int(slot)
                    except Exception:
                        continue
                    if not (1 <= idx <= self.max_skills):
                        continue

                    item_data = ITENS.get("equipaveis", {}).get(nome_item)
                    if not item_data:
                        continue

                    skill_id = item_data.get("skill")
                    if skill_id in SKILLS:
                        self.skills_slots[str(idx)] = skill_id

            self.rodar_skills()
