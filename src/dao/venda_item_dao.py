import json
import os
from src.models.venda_item import VendaItem

class VendaItemDAO:
    lista = []
    arquivo = 'data/vendas_itens.json'

    @classmethod
    def inserir(cls, obj):
        cls.lista.append(obj)
        cls.salvar()

    @classmethod
    def listar_por_venda(cls, id_venda):
        return [item for item in cls.lista if item.id_venda == id_venda]

    @classmethod
    def listar(cls):
        return cls.lista

    @classmethod
    def get_proximo_id(cls):
        if not cls.lista:
            return 1
        return cls.lista[-1].id + 1

    @classmethod
    def abrir(cls):
        cls.lista = []
        if os.path.exists(cls.arquivo):
            with open(cls.arquivo, 'r') as f:
                dados = json.load(f)
                for d in dados:
                    item = VendaItem()
                    item.__dict__.update(d)
                    cls.lista.append(item)

    @classmethod
    def salvar(cls):
        os.makedirs('data', exist_ok=True)
        with open(cls.arquivo, 'w') as f:
            json.dump([vars(obj) for obj in cls.lista], f, indent=4)
