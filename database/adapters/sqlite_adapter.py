import sqlite3
import os
from database.adapters.adapter_base import AdapterBase

class SQLiteAdapter(AdapterBase):
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._ensure_tables()  # Garante estrutura e insere exemplos

    def _ensure_tables(self):
        self._create_or_alter_usuarios()
        self._create_or_alter_veiculos()
        self._create_or_alter_servicos()
        self._create_or_alter_ordens()
        self._create_or_alter_itens_ordem()
        self._insert_servicos_exemplo()
        self.conn.commit()

    def _create_or_alter_usuarios(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL,
                cpf TEXT UNIQUE
            )
        """)

    def _create_or_alter_veiculos(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS veiculos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                modelo TEXT NOT NULL,
                placa TEXT UNIQUE NOT NULL
            )
        """)

    def _create_or_alter_servicos(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS servicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descricao TEXT NOT NULL,
                preco REAL NOT NULL
            )
        """)

    def _create_or_alter_ordens(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ordens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER,
                veiculo_id INTEGER,
                status TEXT DEFAULT 'Em andamento',
                orcamento REAL DEFAULT 0.0,
                FOREIGN KEY (cliente_id) REFERENCES usuarios (id),
                FOREIGN KEY (veiculo_id) REFERENCES veiculos (id)
            )
        """)
        # Verifica e recria se incompleta
        try:
            self.cursor.execute("PRAGMA table_info(ordens)")
            columns = [row[1] for row in self.cursor.fetchall()]
            if 'cliente_id' not in columns or 'veiculo_id' not in columns or 'orcamento' not in columns:
                print("Tabela ordens incompleta. Recriando...")
                self.cursor.execute("DROP TABLE IF EXISTS ordens")
                self.conn.commit()
                self.cursor.execute("""
                    CREATE TABLE ordens (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cliente_id INTEGER,
                        veiculo_id INTEGER,
                        status TEXT DEFAULT 'Em andamento',
                        orcamento REAL DEFAULT 0.0,
                        FOREIGN KEY (cliente_id) REFERENCES usuarios (id),
                        FOREIGN KEY (veiculo_id) REFERENCES veiculos (id)
                    )
                """)
                self.conn.commit()
        except Exception as e:
            print(f"Erro ao verificar/alterar tabela ordens: {e}")

    def _create_or_alter_itens_ordem(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS itens_ordem (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ordem_id INTEGER,
                servico_id INTEGER,
                FOREIGN KEY (ordem_id) REFERENCES ordens (id),
                FOREIGN KEY (servico_id) REFERENCES servicos (id)
            )
        """)

    def _insert_servicos_exemplo(self):
        self.cursor.execute("SELECT COUNT(*) FROM servicos")
        count = self.cursor.fetchone()[0]
        if count == 0:
            servicos_exemplo = [
                ('Troca de Óleo', 50.0),
                ('Alinhamento e Balanceamento', 80.0),
                ('Troca de Freios', 200.0),
                ('Revisão Geral', 150.0),
                ('Lavagem', 30.0)
            ]
            for desc, preco in servicos_exemplo:
                self.cursor.execute("INSERT INTO servicos (descricao, preco) VALUES (?, ?)", (desc, preco))
            print("Serviços de exemplo inseridos no banco (5 itens).")
            self.conn.commit()
        else:
            print(f"Serviços já existem no banco ({count} itens).")

    # IMPLEMENTAÇÃO DOS MÉTODOS ABSTRATOS (obrigatórios para herdar de AdapterBase)
    def insert(self, table, data):
        keys = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        sql = f"INSERT INTO {table} ({keys}) VALUES ({placeholders})"
        try:
            self.cursor.execute(sql, list(data.values()))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro no INSERT em {table}: {e}")
            self.conn.rollback()
            raise

    def get_all(self, table):
        self.cursor.execute(f"SELECT * FROM {table}")
        return self.cursor.fetchall()

    def get_by_id(self, table, id):
        self.cursor.execute(f"SELECT * FROM {table} WHERE id = ?", (id,))
        return self.cursor.fetchone()

    def update(self, table, id, data):
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE id = ?"
        values = list(data.values()) + [id]
        self.cursor.execute(sql, values)
        self.conn.commit()

    def delete(self, table, id):
        self.cursor.execute(f"DELETE FROM {table} WHERE id = ?", (id,))
        self.conn.commit()

    # MÉTODOS EXTRAS PARA ORDEM DE SERVIÇO (não abstratos, mas úteis)
    def insert_itens_ordem(self, ordem_id, servicos_ids):
        for servico_id in servicos_ids:
            self.insert("itens_ordem", {'ordem_id': ordem_id, 'servico_id': servico_id})

    def get_servicos_by_ids(self, servicos_ids):
        if not servicos_ids:
            return 0.0
        placeholders = ', '.join(['?' for _ in servicos_ids])
        self.cursor.execute(f"SELECT preco FROM servicos WHERE id IN ({placeholders})", servicos_ids)
        precos = [row[0] for row in self.cursor.fetchall()]
        return sum(precos)