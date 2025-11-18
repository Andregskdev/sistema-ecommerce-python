import json
import os
from src.models.produto import Produto

class ProdutoDAO:
    lista = []
    arquivo = "data/produtos.json"

    @classmethod
    def inserir(cls, obj):
        cls.lista.append(obj)
        cls.salvar()

    @classmethod
    def listar(cls):
        return cls.lista

    @classmethod
    def listar_id(cls, id):
        for obj in cls.lista:
            if obj.id == id: return obj
        return None

    @classmethod
    def atualizar(cls, obj_novo):
        for i, obj in enumerate(cls.lista):
            if obj.id == obj_novo.id:
                cls.lista[i] = obj_novo
                cls.salvar()
                return

    @classmethod
    def excluir(cls, obj):
        if obj in cls.lista:
            cls.lista.remove(obj)
            cls.salvar()

    @classmethod
    def abrir(cls):
        cls.lista = []
        if os.path.exists(cls.arquivo):
            with open(cls.arquivo, "r") as f:
                dados = json.load(f)
                for d in dados:
                    p = Produto()
                    p.__dict__.update(d)
                    cls.lista.append(p)

    @classmethod
    def salvar(cls):
        os.makedirs("data", exist_ok=True)
        with open(cls.arquivo, "w") as f:
            json.dump([vars(obj) for obj in cls.lista], f, indent=4)