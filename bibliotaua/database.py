import sqlite3

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS livros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cupons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    tipo_desconto TEXT NOT NULL
        CHECK(tipo_desconto IN ('PERCENTUAL', 'VALOR_FIXO')),
    valor_desconto REAL NOT NULL CHECK(valor_desconto > 0),
    valor_minimo_pedido REAL NOT NULL DEFAULT 0.0
        CHECK(valor_minimo_pedido >= 0),
    limite_usos INTEGER NOT NULL DEFAULT 100
        CHECK(limite_usos > 0),
    usos_realizados INTEGER NOT NULL DEFAULT 0
        CHECK(usos_realizados >= 0),
    validade_ate TEXT NOT NULL,
    ativo INTEGER NOT NULL DEFAULT 1
        CHECK(ativo IN (0, 1))
);

CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    cupom_id INTEGER,
    subtotal REAL NOT NULL,
    desconto_aplicado REAL NOT NULL DEFAULT 0.0,
    total REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'CRIADO',
    data_criacao TEXT NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (cupom_id) REFERENCES cupons(id)
);
"""


def obter_conexao(caminho_db="bibliotaua.db"):
    conn = sqlite3.connect(caminho_db)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def inicializar_banco(caminho_db="bibliotaua.db"):
    with obter_conexao(caminho_db) as conn:
        conn.executescript(SCHEMA_SQL)


def popular_dados_iniciais(caminho_db="bibliotaua.db"):
    with obter_conexao(caminho_db) as conn:

        conn.execute("""
            INSERT OR IGNORE INTO clientes (id, nome)
            VALUES (1, 'Cliente de Teste')
        """)

        conn.execute("""
            INSERT OR IGNORE INTO livros (id, titulo)
            VALUES (1, 'Livro de Teste')
        """)

        conn.execute("""
            INSERT OR IGNORE INTO cupons
            (id, codigo, tipo_desconto, valor_desconto,
             valor_minimo_pedido, limite_usos,
             usos_realizados, validade_ate, ativo)
            VALUES
            (1, 'BEMVINDO10', 'PERCENTUAL', 10, 50, 100, 5, '2027-12-31', 1),
            (2, 'FEIRA20', 'VALOR_FIXO', 20, 80, 50, 12, '2027-12-31', 1),
            (3, 'SUPER30', 'PERCENTUAL', 30, 150, 20, 2, '2027-12-31', 1),
            (4, 'EXPIRADO2023', 'PERCENTUAL', 15, 0, 100, 0, '2023-01-01', 1),
            (5, 'ESGOTADO', 'VALOR_FIXO', 10, 0, 3, 3, '2027-12-31', 1),
            (6, 'INATIVO50', 'PERCENTUAL', 50, 0, 10, 0, '2027-12-31', 0)
        """)