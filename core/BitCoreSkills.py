from kivy.clock import Clock
import random

class passiva:#classe padrao para as passivas
    id="base"
    event=None
    schedule_interval=None

    def __init__(self,ent):
        self.active=False
        self.ent=ent
        self._clock=None
    
    def on_add(self):
        self.active=True
        if self.event:
            self.bind_event()
        if self.schedule_interval:
            self._clock = Clock.schedule_interval(
                self.skill,
                self.schedule_interval
            )
    
    def on_remove(self,*args):
        self.active=False
        if self.event:
            self.unbind_event()
        if self._clock:
            self._clock.cancel()
            self._clock = None
    
    def bind_event(self):
        if self.event == "vida":
            self.ent.bind(vida=self.skill)

    def unbind_event(self):
        if self.event == "vida":
            self.ent.unbind(vida=self.skill)
    
    def skill(self, *args):
        pass



#habilidades passivas(condicionais):
class panico(passiva):#basicamente tu fica mais rapido ao apanhar
    def __init__(self, ent):
        super().__init__(ent)
        self.id = "panico"
        self.event = "vida"
        self._aplicado = False

    def skill(self, *args):
        if self.ent.i_frames and not self._aplicado:
            self.ent.velocidade *= 1.5
            self._aplicado = True
            Clock.schedule_once(self.remove_speed,0.7)
    
    def remove_speed(self,*args):
        if self._aplicado:
            self.ent.velocidade /= 1.5
            self._aplicado = False

    def on_remove(self, *args):
        if self._aplicado:
            self.ent.velocidade /= 1.5
        super().on_remove()



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
        if self.ent.i_frames:
            return

        if random.randint(0, 200) <= 1:
            self.ent.i_frames = True



SKILLS = {
    "panico":panico,
    "vampirismo":vampirismo,
    "esguio":esguio
}#so esse dicionario aq vai ser importado(ele que vai trabalhar para gerenciar as habilidades)
