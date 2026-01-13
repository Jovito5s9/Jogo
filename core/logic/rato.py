from core.logic.entity import EntidadeLogica
from core.logic.ai import perseguir, rastrear, atacar_corpo_a_corpo

class RatoLogica(EntidadeLogica):
    def __init__(self):
        super().__init__()

        self.vida_maxima = 30
        self.vida = 30
        self.dano = 5
        self.velocidade = 1.5
        self.repulsao = 10
        self.alcance_fisico = 70
        self.raio_visao = 300

        self.alvo = None
        self.atacando = False

    def update(self, dt):
        if not self.vivo or not self.alvo:
            return

        if rastrear(self, self.alvo, self.raio_visao):
            if distancia := abs(self.alvo.x - self.x):
                if distancia <= self.alcance_fisico:
                    atacar_corpo_a_corpo(self, self.alvo)
                else:
                    perseguir(self, self.alvo)
        else:
            self.speed_x = 0
            self.speed_y = 0

        self.mover(dt)
