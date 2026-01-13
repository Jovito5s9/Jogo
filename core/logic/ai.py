from .combat import distancia

def perseguir(ent, alvo):
    ent.speed_x = 1 if alvo.x > ent.x else -1
    ent.speed_y = 1 if alvo.y > ent.y else -1


def rastrear(ent, alvo, raio):
    return distancia(ent, alvo) <= raio
