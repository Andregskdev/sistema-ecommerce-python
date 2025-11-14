class Produto:
    def __init__(self, id=None, nome='', descricao='', preco=0.0, estoque=0, categoria_id=None):
        self.__id = id
        self.__nome = nome
        self.__descricao = descricao
        self.__preco = preco
        self.__estoque = estoque 
        self.__categoria_id = categoria_id
    
    def get_id(self):
        return self.__id
    def set_id(self, id):
        self.__id = id

    def get_nome(self):
        return self.__nome
    def set_nome(self, nome):
        self.__nome = nome

    def get_descricao(self):
        return self.__descricao
    def set_descricao(self, descricao):
        self.__descricao = descricao

    def get_preco(self):
        return self.__preco
    def set_preco(self, preco):
        self.__preco = preco

    def get_estoque(self):  
        return self.__estoque
    def set_estoque(self, estoque):  
        self.__estoque = estoque

    def get_categoria_id(self):
        return self.__categoria_id
    def set_categoria_id(self, categoria_id):
        self.__categoria_id = categoria_id

    def __str__(self):
        return f"Produto [id={self.__id}, nome='{self.__nome}', preco={self.__preco}, estoque={self.__estoque}, categoria_id={self.__categoria_id}]"