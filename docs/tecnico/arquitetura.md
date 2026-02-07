##### [retornar para o README](../../README.md)

---

## Estrutura do projeto

├── core/<br>
|   ├─── world.py<br>
|   ├─── player.py<br>
|   └─── BitCoreSkills.py<br>
|<br>
├── utils/<br>
|   ├─── joystick.py<br>
|   ├─── customizedButton.py<br>
|   └─── resourcesPath.py<br>
|<br>
├── utils/<br>
|   └─── itens_db.py<br>
|<br>
├── game.py<br>
└── main.py<br>

##### fucionalidades principais de se citar

* world.py: cria as logicas de mundo, mapa, colisões e adiciona as entidades
* player.py: onde está localizada a classe basica de entidades, de player e das demais entidades
* BitCoreSkills: classes de skills e criação simples de skills
* resourcesPath.py: módulo complementar para deploy funcionar corretamente(chamar para todos os assets)
* itens_db.py: dict estático para gerenciamento de itens(relaciona nome com source, descrição, raridade, skill se tiver, etc)
* game.py: cria as janelas, telas e interfaces do jogo, liga tudo
* main.py: inicializa o jogo como app

*Obs: muitas tarefas ainda estão atribuidas a esses arquivos ainda, mas uma separação será realizada, os planos 
são de separação de responsabilidades além de trocar orientação de design de script(py) para dados(json)*

---

## Assets

Os assets do jogo estão organizados por tipo(sprites, tiles, UI) na pasta `assets/`.

O carregamento é centralizado para facilitar compatibilidade entre desenvolvimento e builds.
