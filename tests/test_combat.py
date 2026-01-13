from core.logic.entity import EntidadeLogica
from core.logic.combat import atacar

def test_attack_reduces_life():
    a = EntidadeLogica(x=0, y=0)
    b = EntidadeLogica(x=10, y=0)

    atacar(a, b, dano=10, repulsao=0)

    assert b.vida == 90
