from dataclasses import dataclass

@dataclass
class EntidadeLogica:
    x: float = 0
    y: float = 0

    vida_maxima: float = 100
    vida: float = 100
    vivo: bool = True

    velocidade: float = 1.0
    speed_x: int = 0
    speed_y: int = 0

    estado: str = "idle"
    facing_right: bool = True

    power: float = 5
    dano: float = 5
    repulsao: float = 10
    alcance_fisico: float = 70

    i_frames: bool = False
    i_frames_time: float = 0.8

    largura: float = 32
    altura: float = 32

    def mover(self, dt: float):
        if not self.vivo:
            return

        self.x += self.speed_x * self.velocidade * dt
        self.y += self.speed_y * self.velocidade * dt

        if self.speed_x > 0:
            self.facing_right = True
        elif self.speed_x < 0:
            self.facing_right = False

        if self.speed_x or self.speed_y:
            self.estado = "running"
        else:
            self.estado = "idle"

    def receber_dano(self, dano: float):
        if not self.vivo or self.i_frames:
            return

        self.vida -= dano
        self.i_frames = True

        if self.vida <= 0:
            self.morrer()

    def morrer(self):
        self.vivo = False
        self.estado = "morto"
        self.speed_x = 0
        self.speed_y = 0

    def hitbox(self):
        x = self.x + (self.largura * 0.25)
        y = self.y + (self.altura * 0.1)
        w = self.largura * 0.5
        h = self.altura * 0.35
        return (x, y, w, h)

    def centro_hitbox(self):
        x, y, w, h = self.hitbox()
        return (x + w / 2, y + h / 2)
