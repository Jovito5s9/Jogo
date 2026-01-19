import random
class passiva:#classe padrao para as passivas
    id="base"
    def __init__(self,ent):
        self.ent=self.ent
        self.event=""
        self.schedule_interval=0
        self.skill=None
    
    def on_add(self):
        if self.event:
            if self.event=='vida':
                self.self.ent.bind(vida=self.skill)
            if self.event=='dano':
                self.self.ent.bind(dano_causado=self.skill)

        

#habilidades passivas(condicionais):
class panico(passiva):#basicamente tu fica mais rapido ao apanhar
    def __init__(self, ent):
        super().__init__(self.ent)
        self.id="panico"
        self.event="vida"
    def skill(self, *args):
        if self.ent.i_frames:
            self.ent.speed_x*=2
            self.ent.speed_y*=2


class vampirismo(passiva):#basicamente tu fica mais rapido ao apanhar
    def __init__(self, ent):
        super().__init__(self.ent)
        self.id="vampirismo"
        self.event="dano"
    def skill(self, *args):#roubar vida ao atacar
        if self.ent.dano_causado:
            self.ent.vida=self.ent.vida+self.ent.dano_causado
            self.ent.dano_causado=0


class esguio(passiva):#basicamente tu fica mais rapido ao apanhar
    def __init__(self, ent):
        super().__init__(self.ent)
        self.id="esguio"
        self.schedule_interval=0.5
    def skill(self, *args):#pra desviar ocasionamente de ataques// vou ajeitar dps pra depender da sorte(novo atributo)
        if not self.ent.i_frames:
            new_i_frames=random.randint(0,200)
            if new_i_frames<=1:
                random_i_frames_time=random.randint(1,10)/20
                backup_ent_if_time=self.ent.i_frames_time
                self.ent.i_frames_time=random_i_frames_time
                self.ent.i_frames=True
                self.ent.i_frames_time=backup_ent_if_time


SKILLS = {
    "panico":panico,
    "vampirismo":vampirismo,
    "esguio":esguio
}#so esse dicionario aq vai ser importado(ele que vai trabalhar para gerenciar as habilidades)
