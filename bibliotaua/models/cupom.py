from dataclasses import dataclass
from datetime import date
from enum import Enum

from bibliotaua.exceptions import (
    CupomEsgotadoError,
    CupomExpiradoError,
    CupomInativoError,
    ValorMinimoNaoAtingidoError
)


class TipoDesconto(Enum):
    PERCENTUAL = "PERCENTUAL"
    VALOR_FIXO = "VALOR_FIXO"


@dataclass
class Cupom:
    codigo: str
    tipo_desconto: TipoDesconto
    valor_desconto: float
    valor_minimo_pedido: float = 0.0
    limite_usos: int = 100
    usos_realizados: int = 0
    validade_ate: object = None
    ativo: bool = True
    id: int = None

    def __post_init__(self):
        self.codigo = self.codigo.strip().upper()

        if not isinstance(self.tipo_desconto, TipoDesconto):
            self.tipo_desconto = TipoDesconto(self.tipo_desconto)

    def pode_ser_aplicado_ao_pedido(self, subtotal):

        if not self.ativo:
            raise CupomInativoError(self.codigo)

        validade = (
            self.validade_ate
            if isinstance(self.validade_ate, date)
            else date.fromisoformat(str(self.validade_ate)[:10])
        )

        if validade < date.today():
            raise CupomExpiradoError(self.codigo)

        if self.usos_realizados >= self.limite_usos:
            raise CupomEsgotadoError(self.codigo)

        if subtotal < self.valor_minimo_pedido:
            raise ValorMinimoNaoAtingidoError(
                self.codigo,
                self.valor_minimo_pedido,
                subtotal
            )

        return True

    def calcular_desconto(self, subtotal):

        self.pode_ser_aplicado_ao_pedido(subtotal)

        if self.tipo_desconto == TipoDesconto.PERCENTUAL:
            desconto = subtotal * self.valor_desconto / 100
        else:
            desconto = self.valor_desconto

        return round(min(desconto, subtotal), 2)

    def registrar_uso(self):

        if not self.ativo:
            raise CupomInativoError(self.codigo)

        validade = (
            self.validade_ate
            if isinstance(self.validade_ate, date)
            else date.fromisoformat(str(self.validade_ate)[:10])
        )

        if validade < date.today():
            raise CupomExpiradoError(self.codigo)

        if self.usos_realizados >= self.limite_usos:
            raise CupomEsgotadoError(self.codigo)

        self.usos_realizados += 1