import math

def distancia(ent1, ent2):
    x1, y1 = ent1.centro_hitbox()
    x2, y2 = ent2.centro_hitbox()
    return math.dist((x1, y1), (x2, y2))


def atacar(atacante, alvo, dano, repulsao):
    if not alvo.vivo or alvo.i_frames:
        return

    alvo.receber_dano(dano)

    if atacante.facing_right:
        alvo.x += repulsao
    else:
        alvo.x -= repulsao
