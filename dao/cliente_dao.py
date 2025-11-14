import json, os
from models.cliente import Cliente

class ClienteDAO:
    arquivo = 'clientes.json'
    lista = []
    proximo_id = 1

    @classmethod
    def inserir(cls, cliente: Cliente):
        cliente.set_id(cls.proximo_id)
        cls.lista.append(cliente)
        cls.proximo_id += 1
        return cliente

    @classmethod
    def listar(cls):
        return cls.lista

    @classmethod
    def listar_id(cls, id):
        return next((c for c in cls.lista if c.get_id() == id), None)

    @classmethod
    def atualizar(cls, cliente):
        for i, c in enumerate(cls.lista):
            if c.get_id() == cliente.get_id():
                cls.lista[i] = cliente
                return True
        return False

    @classmethod
    def excluir(cls, id):
        original = len(cls.lista)
        cls.lista = [c for c in cls.lista if c.get_id() != id]
        return len(cls.lista) < original

    @classmethod
    def abrir(cls):
        if not os.path.exists(cls.arquivo):
            cls.salvar()
            return
        with open(cls.arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            cls.lista = [Cliente(**d) for d in dados]
            cls.proximo_id = (max((c.get_id() for c in cls.lista), default=0) + 1)

    @classmethod
    def salvar(cls):
        with open(cls.arquivo, 'w', encoding='utf-8') as f:
            json.dump([{
                "id": c.get_id(),
                "nome": c.get_nome(),
                "email": c.get_email(),
                "telefone": c.get_telefone()
            } for c in cls.lista], f, indent=2, ensure_ascii=False)
