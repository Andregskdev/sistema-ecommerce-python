class Categoria:
    def __init__(self, id=None, nome='', descricao=''):
        self.__id = id
        self.__nome = nome
        self.__descricao = descricao
    
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
    
    def __str__(self):
        return f"Categoria [id={self.__id}, nome='{self.__nome}', descricao='{self.__descricao}']"