##### [retornar para o README](../../README.md)

---

## Estrutura do projeto

├── core/<br>
|   └─── entity/<br>
|    ---└─── player.json/<br>
|    ---└─── basic_ent.json/<br>
|    ---└─── ent_factory.json/<br>
|    ---└─── interact.json/<br>
|    ---└─── npc.json/<br>
|    ---└─── boss.json/<br>
|   ├─── world.py<br>
|   ├─── camera.py<br>
|   └─── BitCoreSkills.py<br>
|   └─── map.py<br>
|   └─── tiles.py<br>
|<br>
├── utils/<br>
|   ├─── joystick.py<br>
|   ├─── customizedButton.py<br>
|   └─── resourcesPath.py<br>
|<br>
├── content/<br>
|   └─── ents/<br>
|    ---└─── ent.json/<br>
|   └─── itens/<br>
|    ---└─── linguage.json/<br>
|   └─── maps/<br>
|    ---└─── map.json/<br>
|   └─── ui/<br>
|    ---└─── linguage.json/<br>
|<br>
├── screens/<br>
|   └─── shared.py<br>
|   └─── game_screen.py<br>
|   └─── menu_screen.py<br>
|   └─── config_screen.py<br>
|   └─── menu_pause.py<br>
|   └─── menu_player.py<br>
|<br>
├── game.py<br>
└── main.py<br>

##### fucionalidades principais de se citar

* core/world.py: é o motor principal, cria as logicas de mundo, mapa, colisões e adiciona as entidades
* core/BitCoreSkills: classes de skills e criação simples de skills
* core/entity/basic_ent.py: onde está localizada a classe basica de entidades e funcionalidades relevantes para construção
* core/entity/ent_factory.py: construtor de entidades com uso principal de Data-Driven(lendo .json simples) para construir e entregar entidades, ou .py no caso de bosses, NPCs e player
* utils/resourcesPath.py: módulo complementar para deploy funcionar corretamente(chamar para todos os assets)
* content/itens/linguage.json: dict, para a liguagem selecionada, usado para gerenciamento e tradução de itens(relaciona nome com source, descrição, raridade, skill se tiver, etc)
* content/maps/map.json: json contendo quantidade de linhas/colunas, onde cada tile e objeto ficará, entradas do mapa, colisores diferentes, backgrounds etc, para ser carregado
* content/ents/ent.json: json contendo stats, path dos sources, drops e comportamentos da entidade
* game.py: conecta as telas de screens/ de forma coesa
* main.py: inicializa o jogo como app


---

## Assets

Os assets do jogo estão organizados por tipo(sprites, tiles, UI) na pasta `assets/`.

O carregamento é centralizado para facilitar compatibilidade entre desenvolvimento e builds.
