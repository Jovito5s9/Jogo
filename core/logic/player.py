from .entity import EntidadeLogica
from .combat import atacar, distancia

class PlayerLogica(EntidadeLogica):
    def __init__(self):
        super().__init__()

        self.power = 5
        self.repulsao = 20
        self.alcance_fisico = 100

    def soco(self, entidades):
        for ent in entidades:
            if ent is self or not ent.vivo:
                continue

            if distancia(self, ent) <= self.alcance_fisico:
                atacar(self, ent, self.power, self.repulsao)
