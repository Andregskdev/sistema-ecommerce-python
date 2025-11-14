import json, os
from models.venda_item import VendaItem

class VendaItemDAO:
    arquivo = 'venda_itens.json'
    lista = []
    proximo_id = 1

    @classmethod
    def inserir(cls, item: VendaItem):
        """Insere um novo item de venda."""
        item.set_id(cls.proximo_id)
        cls.lista.append(item)
        cls.proximo_id += 1
        return item

    @classmethod
    def listar(cls):
        """Retorna todos os itens de venda."""
        return cls.lista

    @classmethod
    def listar_id(cls, id):
        """Busca um item de venda pelo ID."""
        return next((i for i in cls.lista if i.get_id() == id), None)

    @classmethod
    def atualizar(cls, item):
        """Atualiza um item de venda existente."""
        for idx, i in enumerate(cls.lista):
            if i.get_id() == item.get_id():
                cls.lista[idx] = item
                return True
        return False

    @classmethod
    def excluir(cls, id):
        """Remove um item de venda da lista."""
        original = len(cls.lista)
        cls.lista = [i for i in cls.lista if i.get_id() != id]
        return len(cls.lista) < original

    @classmethod
    def abrir(cls):
        """Carrega os itens de venda do arquivo JSON."""
        if not os.path.exists(cls.arquivo):
            cls.salvar()
            return
        with open(cls.arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            cls.lista = [VendaItem(**d) for d in dados]
            cls.proximo_id = (max((i.get_id() for i in cls.lista), default=0) + 1)

    @classmethod
    def salvar(cls):
        """Salva os itens de venda no arquivo JSON."""
        with open(cls.arquivo, 'w', encoding='utf-8') as f:
            json.dump([{
                "id": i.get_id(),
                "produto_id": i.get_produto_id(),
                "quantidade": i.get_quantidade(),
                "preco_unitario": i.get_preco_unitario(),
                "venda_id": i.get_venda_id()
            } for i in cls.lista], f, indent=2, ensure_ascii=False)
