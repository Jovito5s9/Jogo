from core.entity.basic_ent import BasicEnt
from core.entity.interact import ia_base
from utils.resourcesPath import resource_path
import importlib
import json
import os
from kivy.clock import Clock
import random

def load_ent_data(ent_name):
    ent_path = resource_path("content/ents/" + ent_name + ".json")
    try:
        with open(ent_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def _resolve_class(class_name):
    try:
        mod = importlib.import_module("core.entity.basic_ent")
        cls = getattr(mod, class_name)
        return cls
    except Exception:
        try:
            module_path, cls_name = class_name.rsplit(".", 1)
            mod = importlib.import_module(module_path)
            return getattr(mod, cls_name)
        except Exception:
            return BasicEnt

def _apply_sources(ent, sources_dict):
    if not sources_dict:
        return
    for key, src in sources_dict.items():
        if not src:
            continue
        full = resource_path(src)
        if os.path.exists(full):
            ent.sources[key] = full
        else:
            ent.sources[key] = src

def _apply_sprite_props(ent, sprite):
    if not sprite:
        return
    for k, v in sprite.items():
        try:
            if k in ("frame_width", "frame_height", "tamanho",
                     "idle_frames", "running_frames", "atacando_frames"):
                setattr(ent, k, v)
        except Exception:
            pass

def _apply_attributes(ent, atributos):
    if not atributos:
        return
    for k, v in atributos.items():
        try:
            setattr(ent, k, v)
        except Exception:
            pass

def _apply_drops(ent, drops):
    if not drops:
        return
    for item, val in drops.items():
        if isinstance(val, list) and len(val) >= 2:
            ent.list_drops[item] = random.randint(int(val[0]), int(val[1]))
        else:
            try:
                ent.list_drops[item] = int(val)
            except Exception:
                ent.list_drops[item] = 0

def _apply_inventario(ent, inv):
    if not inv:
        return
    ent.inventario.update(inv)

def _apply_bitcores(ent, bitcores):
    if not bitcores:
        return
    ent.bitcores.update(bitcores)

def _apply_equipaveis(ent, equip):
    if not equip:
        return
    ent.skills_slots.update(equip)

def _apply_acao_mapping(ent, acoes_list):
    pool = ia_base()

    print("Ações JSON:", acoes_list)
    print("Pool IA:", pool.keys())

    ent.acoes = {}

    for nome in acoes_list:
        fn = pool.get(nome)
        print("Procurando:", nome, "->", fn)

        if fn:
            ent.acoes[nome] = fn

    print("Ações finais:", ent.acoes)

def create_ent(ent_name, **kwargs):
    ent_data = load_ent_data(ent_name)
    if not ent_data:
        return None

    class_name = ent_data.get("class")
    if class_name:
        cls = _resolve_class(class_name)
    else:
        cls = BasicEnt

    ent = cls(**kwargs)

    _apply_sources(ent, ent_data.get("sources") or ent_data.get("sprites"))

    _apply_sprite_props(ent, ent_data.get("sprite"))

    _apply_attributes(ent, ent_data.get("atributos"))

    _apply_drops(ent, ent_data.get("drops"))
    _apply_inventario(ent, ent_data.get("inventario"))
    _apply_bitcores(ent, ent_data.get("bitcores"))
    _apply_equipaveis(ent, ent_data.get("equipaveis"))

    _apply_acao_mapping(ent, ent_data.get("acoes"))

    pos = ent_data.get("pos")
    if pos and isinstance(pos, (list, tuple)) and len(pos) >= 2:
        try:
            ent.pos = (pos[0], pos[1])
        except Exception:
            pass
    size = ent_data.get("size")
    if size and isinstance(size, (list, tuple)) and len(size) >= 2:
        try:
            ent.size = (size[0], size[1])
        except Exception:
            pass

    ai_interval = ent_data.get("ai_interval")
    if ai_interval and hasattr(ent, "ia"):
        try:
            Clock.schedule_interval(ent.ia, 1/ai_interval)
        except Exception:
            pass

    try:
        if hasattr(ent, "atualizar"):
            ent.atualizar()
    except Exception:
        pass

    try:
        if hasattr(ent, "rodar_skills"):
            ent.rodar_skills()
    except Exception:
        pass
    
    try:
        if hasattr(ent, "add_player"):
            Clock.schedule_once(ent.add_player, 1)
    except Exception:
        pass
    Clock.schedule_once(lambda dt: print(ent.player,"qooqowowo"), 2)
    return ent