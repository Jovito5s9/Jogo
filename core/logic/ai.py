from core.logic.combat import distancia, atacar

def perseguir(ent, alvo):
    ent.speed_x = 1 if alvo.x > ent.x else -1
    ent.speed_y = 1 if alvo.y > ent.y else -1


def rastrear(ent, alvo, raio):
    return distancia(ent, alvo) <= raio


def atacar_corpo_a_corpo(ent, alvo):
    if distancia(ent, alvo) <= ent.alcance_fisico:
        atacar(ent, alvo, ent.dano, ent.repulsao)
        ent.estado = "atacando"
