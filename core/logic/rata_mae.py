from core.logic.entity import EntidadeLogica
from core.logic.ai import perseguir, rastrear
from core.logic.combat import atacar

class RataMaeLogica(EntidadeLogica):
    def __init__(self):
        super().__init__()

        self.vida_maxima = 450
        self.vida = 450
        self.velocidade = 1.5
        self.dano = 5
        self.repulsao = 15

        self.raio_visao = 700
        self.alcance_fisico = 450

        self.alvo = None
        self.atacando = False
        self.tempo_rolando = 0

    def update(self, dt):
        if not self.vivo or not self.alvo:
            return

        if rastrear(self, self.alvo, self.raio_visao):
            if not self.atacando:
                self.preparar_rolar()
        self.mover(dt)

        if self.atacando:
            self.tempo_rolando += dt
            if self.tempo_rolando > 1:
                self.parar_rolar()

    def preparar_rolar(self):
        self.estado = "atacando"
        self.atacando = True
        self.velocidade *= 2

    def parar_rolar(self):
        self.estado = "idle"
        self.atacando = False
        self.velocidade /= 2
        self.tempo_rolando = 0
