import json, os
from models.venda import Venda

class VendaDAO:
    arquivo = 'vendas.json'
    lista = []
    proximo_id = 1

    @classmethod
    def inserir(cls, venda: Venda):
        venda.set_id(cls.proximo_id)
        cls.lista.append(venda)
        cls.proximo_id += 1
        cls.salvar() 
        return venda

    @classmethod
    def listar(cls):
        return cls.lista

    @classmethod
    def listar_id(cls, id):
        return next((v for v in cls.lista if v.get_id() == id), None)

    @classmethod
    def listar_por_cliente(cls, cliente_id):
        return [v for v in cls.lista if v.get_cliente_id() == cliente_id]

    @classmethod
    def atualizar(cls, venda):
        for i, v in enumerate(cls.lista):
            if v.get_id() == venda.get_id():
                cls.lista[i] = venda
                cls.salvar() 
                return True
        return False

    @classmethod
    def excluir(cls, id):
        original = len(cls.lista)
        cls.lista = [v for v in cls.lista if v.get_id() != id]
        if len(cls.lista) < original:
            cls.salvar() 
            return True
        return False

    @classmethod
    def abrir(cls):
        if not os.path.exists(cls.arquivo):
            cls.salvar()
            return
        with open(cls.arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            cls.lista = []
            for d in dados:
                venda = Venda(d['id'], d['cliente_id'], d['data'], d['total'], d['itens_ids'], d.get('status', 'Processando'))
                cls.lista.append(venda)
            cls.proximo_id = (max((v.get_id() for v in cls.lista), default=0) + 1)

    @classmethod
    def salvar(cls):
        with open(cls.arquivo, 'w', encoding='utf-8') as f:
            json.dump([{
                "id": v.get_id(),
                "cliente_id": v.get_cliente_id(),
                "data": v.get_data(),
                "total": v.get_total(),
                "itens_ids": v.get_itens_ids(),
                "status": v.get_status() 
            } for v in cls.lista], f, indent=2, ensure_ascii=False)