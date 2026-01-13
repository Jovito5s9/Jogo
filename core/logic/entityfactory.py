from core.logic.rata_mae import RataMaeLogica
from core.logic.rato import RatoLogica


class EntityFactory:
    @staticmethod
    def criar(tipo):
        if tipo == "rato":
            return RatoLogica()
        if tipo == "boss":
            return RataMaeLogica()
