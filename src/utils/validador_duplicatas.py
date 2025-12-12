from src.dao.cliente_dao import ClienteDAO
from src.dao.categoria_dao import CategoriaDAO
from src.dao.produto_dao import ProdutoDAO

class ValidadorDuplicatas:

    @staticmethod
    def validar_id_unico(lista, novo_id):
        return not any((obj.id == novo_id for obj in lista))

    @staticmethod
    def validar_email_unico(lista, email):
        return not any((obj.email == email for obj in lista))

    @staticmethod
    def validar_descricao_categoria_unica(lista, descricao):
        return not any((obj.descricao.lower() == descricao.lower() for obj in lista))

    @staticmethod
    def obter_proximo_id(lista):
        if not lista:
            return 1
        return max([obj.id for obj in lista]) + 1

    @staticmethod
    def remover_duplicatas_clientes():
        clientes = ClienteDAO.listar()
        if not clientes:
            return 0
        ids_vistos = set()
        clientes_unicos = []
        duplicatas = []
        for cliente in clientes:
            if cliente.id not in ids_vistos:
                ids_vistos.add(cliente.id)
                clientes_unicos.append(cliente)
            else:
                duplicatas.append(cliente)
        if duplicatas:
            ClienteDAO.lista = clientes_unicos
            ClienteDAO.salvar()
            return len(duplicatas)
        return 0

    @staticmethod
    def remover_duplicatas_categorias():
        categorias = CategoriaDAO.listar()
        if not categorias:
            return 0
        ids_vistos = set()
        categorias_unicas = []
        duplicatas = []
        for categoria in categorias:
            if categoria.id not in ids_vistos:
                ids_vistos.add(categoria.id)
                categorias_unicas.append(categoria)
            else:
                duplicatas.append(categoria)
        if duplicatas:
            CategoriaDAO.lista = categorias_unicas
            CategoriaDAO.salvar()
            return len(duplicatas)
        return 0

    @staticmethod
    def remover_duplicatas_produtos():
        produtos = ProdutoDAO.listar()
        if not produtos:
            return 0
        ids_vistos = set()
        produtos_unicos = []
        duplicatas = []
        for produto in produtos:
            if produto.id not in ids_vistos:
                ids_vistos.add(produto.id)
                produtos_unicos.append(produto)
            else:
                duplicatas.append(produto)
        if duplicatas:
            ProdutoDAO.lista = produtos_unicos
            ProdutoDAO.salvar()
            return len(duplicatas)
        return 0

    @staticmethod
    def limpar_todas_duplicatas():
        dup_clientes = ValidadorDuplicatas.remover_duplicatas_clientes()
        dup_categorias = ValidadorDuplicatas.remover_duplicatas_categorias()
        dup_produtos = ValidadorDuplicatas.remover_duplicatas_produtos()
        return {'clientes': dup_clientes, 'categorias': dup_categorias, 'produtos': dup_produtos, 'total': dup_clientes + dup_categorias + dup_produtos}
