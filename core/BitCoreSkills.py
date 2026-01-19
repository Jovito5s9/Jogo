import random
class passiva:#classe padrao para as passivas
    id="base"
    event=None
    schedule_interval=None

    def __init__(self,ent):
        self.ent=ent
    
    def on_add(self):
        if self.event:
            if self.event=='vida':
                self.ent.bind(vida=self.skill)



#habilidades passivas(condicionais):
class panico(passiva):#basicamente tu fica mais rapido ao apanhar
    def __init__(self, ent):
        super().__init__(ent)
        self.id="panico"
        self.event="vida"
    def skill(self, *args):
        if self.ent.i_frames:
            self.ent.speed_x*=1.5
            self.ent.speed_y*=1.5


class vampirismo(passiva):#basicamente tu fica mais rapido ao apanhar
    def __init__(self, ent):
        super().__init__(ent)
        self.id="vampirismo"
        self.schedule_interval=0.3
    def skill(self, *args):#roubar vida ao atacar
        if self.ent.dano_causado:
            self.ent.vida=self.ent.vida+self.ent.dano_causado
            self.ent.dano_causado=0


class esguio(passiva):#basicamente tu fica mais rapido ao apanhar
    def __init__(self, ent):
        super().__init__(ent)
        self.id="esguio"
        self.schedule_interval=0.1
    def skill(self, *args):#pra desviar ocasionamente de ataques// vou ajeitar dps pra depender da sorte(novo atributo)
        if not self.ent.i_frames:
            new_i_frames=random.randint(0,200)
            if new_i_frames<=1:
                random_i_frames_time=random.randint(1,10)/20
                random_i_frames_time=10
                backup_ent_if_time=self.ent.i_frames_time
                self.ent.i_frames_time=random_i_frames_time
                self.ent.i_frames=True
                self.ent.i_frames_time=backup_ent_if_time


SKILLS = {
    "panico":panico,
    "vampirismo":vampirismo,
    "esguio":esguio
}#so esse dicionario aq vai ser importado(ele que vai trabalhar para gerenciar as habilidades)
