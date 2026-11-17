import sqlite3
from datetime import date, datetime
from typing import List, Optional

from bibliotaua.models.cupom import Cupom, TipoDesconto
from bibliotaua.exceptions import CupomInexistenteError


class CupomRepository:

    def __init__(self, conexao: sqlite3.Connection):
        self.conn = conexao

    def _instanciar_cupom(self, row: sqlite3.Row) -> Cupom:

        return Cupom(
            id=row["id"],
            codigo=row["codigo"],
            tipo_desconto=TipoDesconto(row["tipo_desconto"]),
            valor_desconto=float(row["valor_desconto"]),
            valor_minimo_pedido=float(row["valor_minimo_pedido"]),
            limite_usos=int(row["limite_usos"]),
            usos_realizados=int(row["usos_realizados"]),
            validade_ate=row["validade_ate"],
            ativo=bool(row["ativo"])
        )

    def salvar(self, cupom: Cupom) -> Cupom:

        validade = (
            cupom.validade_ate.strftime("%Y-%m-%d")
            if isinstance(cupom.validade_ate, (date, datetime))
            else str(cupom.validade_ate)
        )

        valores = (
            cupom.codigo,
            cupom.tipo_desconto.value,
            cupom.valor_desconto,
            cupom.valor_minimo_pedido,
            cupom.limite_usos,
            cupom.usos_realizados,
            validade,
            int(cupom.ativo)
        )

        if cupom.id is None:

            cursor = self.conn.execute("""
                INSERT INTO cupons (
                    codigo,
                    tipo_desconto,
                    valor_desconto,
                    valor_minimo_pedido,
                    limite_usos,
                    usos_realizados,
                    validade_ate,
                    ativo
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, valores)

            cupom.id = cursor.lastrowid

        else:

            self.conn.execute("""
                UPDATE cupons SET
                    codigo = ?,
                    tipo_desconto = ?,
                    valor_desconto = ?,
                    valor_minimo_pedido = ?,
                    limite_usos = ?,
                    usos_realizados = ?,
                    validade_ate = ?,
                    ativo = ?
                WHERE id = ?
            """, valores + (cupom.id,))

        self.conn.commit()

        return cupom

    def buscar_por_codigo(self, codigo: str) -> Cupom:

        codigo_formatado = codigo.strip().upper()

        cursor = self.conn.execute(
            "SELECT * FROM cupons WHERE codigo = ?",
            (codigo_formatado,)
        )

        row = cursor.fetchone()

        if not row:
            raise CupomInexistenteError(codigo_formatado)

        return self._instanciar_cupom(row)

    def buscar_por_id(self, cupom_id: int) -> Optional[Cupom]:

        cursor = self.conn.execute(
            "SELECT * FROM cupons WHERE id = ?",
            (cupom_id,)
        )

        row = cursor.fetchone()

        if not row:
            return None

        return self._instanciar_cupom(row)

    def listar_todos(self) -> List[Cupom]:

        cursor = self.conn.execute(
            "SELECT * FROM cupons ORDER BY codigo ASC"
        )

        return [
            self._instanciar_cupom(row)
            for row in cursor.fetchall()
        ]

    def registrar_uso(self, codigo: str):

        try:
            self.conn.execute("BEGIN IMMEDIATE")

            cupom = self.buscar_por_codigo(codigo)

            # Validação da regra de domínio antes da escrita.
            cupom.registrar_uso()

            self.conn.execute(
                """
                UPDATE cupons
                SET usos_realizados = ?
                WHERE id = ?
                """,
                (cupom.usos_realizados, cupom.id)
            )

            self.conn.commit()

        except Exception:
            self.conn.rollback()
            raise