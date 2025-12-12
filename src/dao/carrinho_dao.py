import json
import os
from src.models.venda_item import VendaItem

class CarrinhoDAO:
    arquivo = 'data/carrinhos.json'
    _carrinhos = {}

    @classmethod
    def abrir(cls):
        cls._carrinhos = {}
        if os.path.exists(cls.arquivo):
            with open(cls.arquivo, 'r') as f:
                try:
                    dados = json.load(f)
                    cls._carrinhos = {int(k): v for k, v in dados.items()}
                except Exception:
                    cls._carrinhos = {}

    @classmethod
    def salvar_tudo(cls):
        os.makedirs(os.path.dirname(cls.arquivo) or 'data', exist_ok=True)
        dados = {str(k): v for k, v in cls._carrinhos.items()}
        with open(cls.arquivo, 'w') as f:
            json.dump(dados, f, indent=4)

    @classmethod
    def get_cart(cls, cliente_id):
        raw = cls._carrinhos.get(cliente_id, [])
        itens = []
        for d in raw:
            vi = VendaItem(0, 0, d.get('id_produto', 0), d.get('quantidade', 0), d.get('valor_unitario', 0.0))
            itens.append(vi)
        return itens

    @classmethod
    def salvar_cart(cls, cliente_id, itens):
        serializaveis = []
        for it in itens:
            serializaveis.append({'id_produto': it.id_produto, 'quantidade': it.quantidade, 'valor_unitario': it.valor_unitario})
        cls._carrinhos[cliente_id] = serializaveis
        cls.salvar_tudo()

    @classmethod
    def delete_cart(cls, cliente_id):
        if cliente_id in cls._carrinhos:
            del cls._carrinhos[cliente_id]
            cls.salvar_tudo()
