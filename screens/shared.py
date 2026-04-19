import json
from utils.resourcesPath import resource_path
from kivy.core.window import Window

STD_font_size = 35

size = Window.height / 12.5

def configuracoes():
    global STD_font_size
    configs_path = resource_path("saved/configuracoes.json")
    try:
        with open(configs_path, "r", encoding="utf-8") as config:
            configs = json.load(config)
        if not "font" in configs:
            with open(configs_path, "w", encoding="utf-8") as config:
                configs["font"] = 35
                json.dump(configs, config)
        if not "linguagem" in configs:
            with open(configs_path, "w", encoding="utf-8") as config:
                configs["linguagem"] = "pt"
                json.dump(configs, config)
        if not "fps" in configs:
            with open(configs_path, "w", encoding="utf-8") as config:
                configs["fps"] = 60
                json.dump(configs, config)
    except Exception:
        newconfig = {
            "teclado": False,
            "linguagem": "pt",
            "font": 35,
            "fps": 60
        }
        configs = newconfig
        with open(configs_path, "w", encoding="utf-8") as config:
            json.dump(newconfig, config)

    if STD_font_size != configs["font"]:
        STD_font_size = configs["font"]

    return configs