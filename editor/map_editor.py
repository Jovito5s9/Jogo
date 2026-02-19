#!/usr/bin/env python3
"""
map_editor.py

Editor simples para mapas em JSON (formato compacto: uma lista por linha).

Formato esperado do JSON:
{
  "linhas": <int>,
  "colunas": <int>,
  "tiles": [[r,c,"image.png"], ...],
  "objs":  [[r,c,"image.png",rot,flag], ...]
}

Funcionalidades:
- carregar / salvar mantendo "uma lista por linha" no arrays de tiles/objs
- aumentar tamanho do mapa (adicionar linhas/colunas à direita/baixo)
- preencher coluna/linha/retângulo com um tile
- adicionar objs em coluna/linha
"""

import json
import argparse
from typing import Dict, Tuple, List, Any, Optional

# ---------------------------
# Utilitários de I/O compacta
# ---------------------------

def load_map(path: str) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_map_compact(data: Dict[str, Any], path: str) -> None:
    """
    Salva JSON mantendo arrays 'tiles' e 'objs' com um elemento por linha,
    para melhor legibilidade (cada lista em sua própria linha).
    Outros campos são serializados normalmente.
    """
    tiles = data.get('tiles', [])
    objs = data.get('objs', [])

    temp = dict(data)
    temp.pop('tiles', None)
    temp.pop('objs', None)

    # Serializa o "resto" (temp) com identação para reusar as linhas, mas trata
    # o caso temp == {} separadamente.
    prefix = json.dumps(temp, ensure_ascii=False, indent=4)

    # Monta o "corpo" do prefix sem a '}' final
    if prefix.strip() == '{}':
        prefix_body = '{'
    else:
        lines = prefix.splitlines()
        # remove última linha que deve ser "}"
        if lines and lines[-1].strip() == '}':
            lines = lines[:-1]
        prefix_body = '\n'.join(lines)

    with open(path, 'w', encoding='utf-8') as f:
        # escreve prefix_body
        if prefix_body.strip() == '':
            # caso improvável, escreve um objeto vazio aberto
            f.write('{\n')
        else:
            f.write(prefix_body + '\n')
            # se prefix_body contém outras chaves além de apenas "{", precisamos
            # garantir uma vírgula separando do próximo campo.
            last_non_empty = prefix_body.strip()
            if last_non_empty != '{' and not prefix_body.rstrip().endswith(','):
                f.write(',\n')

        # agora escrevemos os arrays na ordem desejada e garantindo vírgulas corretas
        arrays = [('tiles', tiles), ('objs', objs)]
        for idx, (name, arr) in enumerate(arrays):
            f.write('    "{}": [\n'.format(name))
            for i, item in enumerate(arr):
                dumped = json.dumps(item, ensure_ascii=False)
                comma = ',' if i < len(arr) - 1 else ''
                f.write('        ' + dumped + comma + '\n')
            f.write('    ]')
            # vírgula entre arrays (mas não depois do último)
            if idx < len(arrays) - 1:
                f.write(',\n')
            else:
                f.write('\n')

        # fecha o objeto JSON corretamente
        f.write('}\n')

# ---------------------------
# Estrutura em memória
# ---------------------------

class MapEditor:
    def __init__(self, data: Dict[str, Any]):
        """
        data: dicionário carregado do JSON do mapa
        """
        self.data = data
        self.rows = int(data.get('linhas', 0))
        self.cols = int(data.get('colunas', 0))
        # Representar tiles como dict[(r,c)] = image
        self.tiles: Dict[Tuple[int,int], str] = {}
        for t in data.get('tiles', []):
            r, c = int(t[0]), int(t[1])
            img = t[2]
            self.tiles[(r,c)] = img
        # objs: mantemos lista tal como está, mas permitimos adicionar
        self.objs: List[List[Any]] = [list(o) for o in data.get('objs', [])]

    # ---------------------------
    # Tamanho
    # ---------------------------
    def increase_size(self, add_rows: int = 0, add_cols: int = 0, fill_tile: str = "terra.png"):
        """
        Aumenta o tamanho do mapa adicionando 'add_rows' linhas abaixo
        e 'add_cols' colunas à direita. Preenche novas posições com fill_tile.
        Não altera coordenadas dos objetos existentes (eles ficam onde estavam).
        """
        if add_rows < 0 or add_cols < 0:
            raise ValueError("add_rows e add_cols devem ser >= 0")
        new_rows = self.rows + add_rows
        new_cols = self.cols + add_cols

        # preencher novas células
        for r in range(self.rows, new_rows):
            for c in range(0, new_cols):
                if (r, c) not in self.tiles:
                    self.tiles[(r, c)] = fill_tile
        for r in range(0, self.rows):
            for c in range(self.cols, new_cols):
                if (r, c) not in self.tiles:
                    self.tiles[(r, c)] = fill_tile

        self.rows = new_rows
        self.cols = new_cols
        self._sync_back()

    def set_size(self, new_rows: int, new_cols: int, fill_tile: str = "terra.png"):
        """
        Define um novo tamanho. Se menores, NÃO remove tiles/objs automaticamente
        (poderia haver objetos fora do novo limite).
        """
        add_rows = max(0, new_rows - self.rows)
        add_cols = max(0, new_cols - self.cols)
        self.increase_size(add_rows, add_cols, fill_tile)

    # ---------------------------
    # Preenchimentos rápidos
    # ---------------------------
    def fill_column(self, col: int, image: str):
        """Coloca `image` em todas as linhas na coluna `col` (cria tiles se ausente)."""
        if col < 0:
            raise ValueError("col deve ser >= 0")
        # Se a coluna está fora dos limites atuais, ampliar automaticamente
        if col >= self.cols:
            self.increase_size(add_cols=col - self.cols + 1, add_rows=0, fill_tile="terra.png")
        for r in range(0, self.rows):
            self.tiles[(r, col)] = image
        self._sync_back()

    def fill_row(self, row: int, image: str):
        """Coloca `image` em todas as colunas na linha `row` (cria tiles se ausente)."""
        if row < 0:
            raise ValueError("row deve ser >= 0")
        if row >= self.rows:
            self.increase_size(add_rows=row - self.rows + 1, add_cols=0, fill_tile="terra.png")
        for c in range(0, self.cols):
            self.tiles[(row, c)] = image
        self._sync_back()

    def fill_rect(self, r1: int, c1: int, r2: int, c2: int, image: str):
        """Preenche um retângulo inclusive com coordenadas r1..r2 e c1..c2."""
        if r2 < r1 or c2 < c1:
            raise ValueError("r2/c2 devem ser >= r1/c1")
        # Expandir se necessário
        need_rows = max(0, r2 - (self.rows - 1))
        need_cols = max(0, c2 - (self.cols - 1))
        if need_rows or need_cols:
            self.increase_size(add_rows=need_rows, add_cols=need_cols, fill_tile="terra.png")
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                self.tiles[(r, c)] = image
        self._sync_back()

    # ---------------------------
    # Adição de objetos (objs)
    # ---------------------------
    def add_obj(self, r: int, c: int, image: str, rot: int = 0, flag: bool = True):
        """Adiciona um objeto na lista objs (mantém formato original)."""
        self.objs.append([int(r), int(c), image, rot, bool(flag)])
        self._sync_back()

    def add_obj_column(self, col: int, image: str, rot: int = 0, flag: bool = True):
        """Adiciona um obj em cada linha na coluna col (r variando)."""
        if col >= self.cols:
            self.increase_size(add_cols=col - self.cols + 1, add_rows=0, fill_tile="terra.png")
        for r in range(0, self.rows):
            self.objs.append([r, col, image, rot, bool(flag)])
        self._sync_back()

    # ---------------------------
    # Sincronização e export
    # ---------------------------
    def _sync_back(self):
        """Reconstrói listas ordenadas e atualiza data com linhas/colunas."""
        # Reconstruir tiles list ordenada por linha, coluna
        tiles_list = []
        keys = sorted(self.tiles.keys())
        for (r, c) in keys:
            tiles_list.append([int(r), int(c), self.tiles[(r, c)]])
        # Reconstruir objs (já em formato de lista)
        objs_list = [list(o) for o in self.objs]

        self.data['linhas'] = int(self.rows)
        self.data['colunas'] = int(self.cols)
        self.data['tiles'] = tiles_list
        self.data['objs'] = objs_list

    # ---------------------------
    # Export helpers
    # ---------------------------
    def to_dict(self) -> Dict[str, Any]:
        # garante sync
        self._sync_back()
        return self.data

# ---------------------------
# CLI simples
# ---------------------------

def main():
    parser = argparse.ArgumentParser(description="Editor simples de mapas JSON (compacto).")
    parser.add_argument("file", help="arquivo JSON do mapa")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_inc = sub.add_parser("increase-size", help="Aumenta o tamanho do mapa")
    p_inc.add_argument("--add-rows", type=int, default=0)
    p_inc.add_argument("--add-cols", type=int, default=0)
    p_inc.add_argument("--fill", default="terra.png", help="tile para preencher novas células")

    p_col = sub.add_parser("fill-column", help="Preenche uma coluna com um tile")
    p_col.add_argument("col", type=int)
    p_col.add_argument("image")

    p_row = sub.add_parser("fill-row", help="Preenche uma linha com um tile")
    p_row.add_argument("row", type=int)
    p_row.add_argument("image")

    p_rect = sub.add_parser("fill-rect", help="Preenche um retângulo (inclusive)")
    p_rect.add_argument("r1", type=int)
    p_rect.add_argument("c1", type=int)
    p_rect.add_argument("r2", type=int)
    p_rect.add_argument("c2", type=int)
    p_rect.add_argument("image")

    p_addobjcol = sub.add_parser("add-obj-column", help="Adiciona um obj em cada linha da coluna")
    p_addobjcol.add_argument("col", type=int)
    p_addobjcol.add_argument("image")
    p_addobjcol.add_argument("--rot", type=int, default=0)
    p_addobjcol.add_argument("--flag", type=lambda s: s.lower() in ("1","true","yes"), default=True)

    parser.add_argument("--out", default=None, help="arquivo de saída (se omitido, sobrescreve o arquivo de entrada)")

    args = parser.parse_args()

    data = load_map(args.file)
    editor = MapEditor(data)

    if args.cmd == "increase-size":
        editor.increase_size(add_rows=args.add_rows, add_cols=args.add_cols, fill_tile=args.fill)
    elif args.cmd == "fill-column":
        editor.fill_column(args.col, args.image)
    elif args.cmd == "fill-row":
        editor.fill_row(args.row, args.image)
    elif args.cmd == "fill-rect":
        editor.fill_rect(args.r1, args.c1, args.r2, args.c2, args.image)
    elif args.cmd == "add-obj-column":
        editor.add_obj_column(args.col, args.image, rot=args.rot, flag=args.flag)
    else:
        raise RuntimeError("comando desconhecido")

    out_path = args.out or args.file
    save_map_compact(editor.to_dict(), out_path)
    print(f"Salvo em {out_path}")

# ---------------------------
# Exemplo de uso em Python
# ---------------------------
if __name__ == "__main__":
    main()