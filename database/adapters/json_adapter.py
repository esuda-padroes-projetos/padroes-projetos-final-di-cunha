import os
import json
from database.adapters.adapter_base import AdapterBase

class JSONAdapter(AdapterBase):
    def __init__(self, folder):
        self.folder = folder
        os.makedirs(folder, exist_ok=True)
        self._init_files()

    def _init_files(self):
        tables = ['usuarios', 'veiculos', 'servicos', 'ordens', 'itens_ordem']
        for table in tables:
            file_path = os.path.join(self.folder, f"{table}.json")
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump([], f)

    def _get_file(self, table):
        return os.path.join(self.folder, f"{table}.json")

    def _load(self, table):
        with open(self._get_file(table), 'r') as f:
            return json.load(f)

    def _save(self, table, data):
        with open(self._get_file(table), 'w') as f:
            json.dump(data, f, indent=4)

    # IMPLEMENTAÇÃO DOS MÉTODOS ABSTRATOS
    def insert(self, table, data):
        rows = self._load(table)
        data['id'] = len(rows) + 1
        rows.append(data)
        self._save(table, rows)
        return data['id']

    def get_all(self, table):
        return self._load(table)

    def get_by_id(self, table, id):
        rows = self._load(table)
        return next((row for row in rows if row['id'] == id), None)

    def update(self, table, id, data):
        rows = self._load(table)
        for row in rows:
            if row['id'] == id:
                row.update(data)
                break
        self._save(table, rows)

    def delete(self, table, id):
        rows = self._load(table)
        rows = [row for row in rows if row['id'] != id]
        self._save(table, rows)

    # MÉTODOS EXTRAS (adaptados para JSON)
    def insert_itens_ordem(self, ordem_id, servicos_ids):
        for servico_id in servicos_ids:
            self.insert("itens_ordem", {'ordem_id': ordem_id, 'servico_id': servico_id})

    def get_servicos_by_ids(self, servicos_ids):
        if not servicos_ids:
            return 0.0
        rows = self._load("servicos")
        precos = [row['preco'] for row in rows if row['id'] in servicos_ids]
        return sum(precos)