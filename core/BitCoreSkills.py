import random
#habilidades passivas(condicionais):
def panico(ent):#basicamente tu fica mais rapido ao apanhar
    if ent.i_frames:
        ent.pos=(ent.x+ent.speed_x,ent.y+ent.speed_y)

def vamipirismo(ent):#roubar vida ao atacar
    if ent.dano_causado:
        ent.vida=ent.vida+ent.dano_causado

def esguio(ent):#pra desviar ocasionamente de ataques// vou ajeitar dps pra depender da sorte(novo atributo)
    if not ent.i_frames:
        new_i_frames=random.randint(0,2000)
        if new_i_frames<=1:
            random_i_frames_time=random.randint(1,10)/20
            backup_ent_if_time=ent.i_frames_time
            ent.i_frames_time=random_i_frames_time
            ent.i_frames=True
            ent.i_frames_time=backup_ent_if_time