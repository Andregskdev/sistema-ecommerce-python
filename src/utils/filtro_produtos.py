from src.dao.produto_dao import ProdutoDAO
from src.dao.categoria_dao import CategoriaDAO

class FiltrodeProdutos:

    @staticmethod
    def obter_produtos_por_categoria(id_categoria):
        if id_categoria == 0:
            return ProdutoDAO.listar()
        return [p for p in ProdutoDAO.listar() if p.id_categoria == id_categoria]

    @staticmethod
    def obter_produtos_disponiveis():
        return [p for p in ProdutoDAO.listar() if p.estoque > 0]

    @staticmethod
    def obter_produtos_disponiveis_por_categoria(id_categoria):
        produtos = FiltrodeProdutos.obter_produtos_por_categoria(id_categoria)
        return [p for p in produtos if p.estoque > 0]

    @staticmethod
    def buscar_por_nome(termo):
        termo_lower = termo.lower()
        return [p for p in ProdutoDAO.listar() if termo_lower in p.descricao.lower()]

    @staticmethod
    def buscar_por_faixa_preco(preco_min, preco_max):
        return [p for p in ProdutoDAO.listar() if preco_min <= p.preco <= preco_max]

    @staticmethod
    def obter_produtos_ordenados_por_preco(crescente=True):
        produtos = ProdutoDAO.listar()
        return sorted(produtos, key=lambda p: p.preco, reverse=not crescente)

    @staticmethod
    def obter_categorias_com_produtos():
        produtos = ProdutoDAO.listar()
        ids_categorias = set((p.id_categoria for p in produtos))
        return [cat for cat in CategoriaDAO.listar() if cat.id in ids_categorias]
