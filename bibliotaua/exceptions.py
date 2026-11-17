class CupomInexistenteError(Exception):
    def __init__(self, codigo):
        super().__init__(
            f"Cupom '{codigo}' não encontrado no sistema."
        )


class ValorMinimoNaoAtingidoError(Exception):
    def __init__(self, codigo, minimo, subtotal):
        super().__init__(
            f"O cupom '{codigo}' exige pedido mínimo "
            f"de R$ {minimo:.2f}. "
            f"Subtotal atual: R$ {subtotal:.2f}."
        )


class CupomEsgotadoError(Exception):
    def __init__(self, codigo):
        super().__init__(
            f"O cupom '{codigo}' atingiu o limite de utilizações."
        )


class CupomInativoError(Exception):
    def __init__(self, codigo):
        super().__init__(f"O cupom '{codigo}' está inativo.")


class CupomExpiradoError(Exception):
    def __init__(self, codigo):
        super().__init__(f"O cupom '{codigo}' está expirado.")