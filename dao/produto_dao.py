import json, os
from models.produto import Produto

class ProdutoDAO:
    arquivo = 'produtos.json'
    lista = []
    proximo_id = 1

    @classmethod
    def inserir(cls, produto: Produto):
        produto.set_id(cls.proximo_id)
        cls.lista.append(produto)
        cls.proximo_id += 1
        cls.salvar()  
        return produto

    @classmethod
    def listar(cls):
        return cls.lista

    @classmethod
    def listar_id(cls, id):
        return next((p for p in cls.lista if p.get_id() == id), None)

    @classmethod
    def atualizar(cls, produto):
        for i, p in enumerate(cls.lista):
            if p.get_id() == produto.get_id():
                cls.lista[i] = produto
                cls.salvar() 
                return True
        return False

    @classmethod
    def excluir(cls, id):
        original = len(cls.lista)
        cls.lista = [p for p in cls.lista if p.get_id() != id]
        if len(cls.lista) < original:
            cls.salvar() 
            return True
        return False

    @classmethod
    def reajustar_precos(cls, percentual):
        if not cls.lista:
            return
        for p in cls.lista:
            novo_preco = p.get_preco() * (1 + (percentual / 100))
            p.set_preco(round(novo_preco, 2))
        cls.salvar()

    @classmethod
    def abrir(cls):
        if not os.path.exists(cls.arquivo):
            cls.salvar()
            return
        with open(cls.arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            cls.lista = [Produto(d['id'], d['nome'], d['descricao'], d['preco'], d.get('estoque', 0), d['categoria_id']) for d in dados]
            cls.proximo_id = (max((p.get_id() for p in cls.lista), default=0) + 1)

    @classmethod
    def salvar(cls):
        with open(cls.arquivo, 'w', encoding='utf-8') as f:
            json.dump([{
                "id": p.get_id(),
                "nome": p.get_nome(),
                "descricao": p.get_descricao(),
                "preco": p.get_preco(),
                "estoque": p.get_estoque(),
                "categoria_id": p.get_categoria_id()
            } for p in cls.lista], f, indent=2, ensure_ascii=False)