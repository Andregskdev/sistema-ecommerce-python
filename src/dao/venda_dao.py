import json
import os
from src.models.venda import Venda

class VendaDAO:
    lista = []
    arquivo = 'data/vendas.json'

    @classmethod
    def inserir(cls, obj):
        cls.lista.append(obj)
        cls.salvar()

    @classmethod
    def listar(cls):
        return cls.lista

    @classmethod
    def listar_por_cliente(cls, id_cliente):
        return [v for v in cls.lista if v.id_cliente == id_cliente]

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
                    v = Venda()
                    v.__dict__.update(d)
                    cls.lista.append(v)

    @classmethod
    def salvar(cls):
        os.makedirs('data', exist_ok=True)
        with open(cls.arquivo, 'w') as f:
            json.dump([vars(obj) for obj in cls.lista], f, indent=4)

    @classmethod
    def atualizar(cls, obj_novo):
        for i, obj in enumerate(cls.lista):
            if obj.id == obj_novo.id:
                cls.lista[i] = obj_novo
                cls.salvar()
                return
