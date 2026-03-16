
def mover(ent, dx, dy):
    ent.speed_x = dx
    ent.speed_y = dy


def perseguir(rastreador):
    dx = 0
    dy = 0
    try:
        if rastreador.player.center_hitbox_x > rastreador.center_hitbox_x:
            dx = 1
        elif rastreador.player.center_hitbox_x < rastreador.center_hitbox_x:
            dx = -1
        if rastreador.player.center_hitbox_y > rastreador.center_hitbox_y:
            dy = 1
        elif rastreador.player.center_hitbox_y < rastreador.center_hitbox_y:
            dy = -1
    except Exception:
        pass
    mover(rastreador, dx, dy)


def rastrear(rastreador):
    if not rastreador.player:
        return

    d = distancia(rastreador)
    if d > 0 and d <= rastreador.raio_visao:
        rastreador.alvo = True


def atacar(atacante, alvo=None, force_damage=False):
    if alvo is None:
        if not atacante.player:
            return
        alvo = atacante.player
    if not alvo.i_frames or force_damage:
        atacante.estado = "atacando"
        knockback = 1
        if not alvo.vivo:
            knockback = 1.5
        if atacante.facing_right:
            alvo.x += atacante.repulsao * knockback
        else:
            alvo.x -= atacante.repulsao * knockback
        alvo.y += atacante.speed_y * atacante.repulsao * knockback
        atacante.speed_x = 0
        atacante.speed_y = 0
        alvo.vida -= atacante.dano
    return


def distancia(ent1, ent2=None):
    try:
        if ent2 is None:
            d1 = ent1.player.center_hitbox_x - ent1.center_hitbox_x
            d2 = ent1.player.center_hitbox_y - ent1.center_hitbox_y
            return ((d1 * d1 + d2 * d2) ** 0.5)
        else:
            d1 = ent2.center_hitbox_x - ent1.center_hitbox_x
            d2 = ent2.center_hitbox_y - ent1.center_hitbox_y
            return ((d1 * d1 + d2 * d2) ** 0.5)
    except Exception:
        return 0

def autodestruct(atacante):
    for ent in atacante.world.ents:
        if distancia(atacante,ent)<=atacante.alcance_fisico*2:
            atacar(atacante=atacante, alvo=ent, force_damage=True)
    atacante.autodestruct()


# funcao destinada a colocar as possibilidades de acoes de entidades basicas
def ia_base():
    acoes = {
        "perseguir": perseguir,
        "rastrear": rastrear,
        "atacar": atacar,
        "autodestruct": autodestruct
    }
    return acoes

