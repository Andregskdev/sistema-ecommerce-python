class Cliente:
    def __init__(self, id=None, nome='', email='', telefone=''):
        self.__id = id
        self.__nome = nome
        self.__email = email
        self.__telefone = telefone
    def get_id(self):
        return self.__id
    def set_id(self, id):
        self.__id = id

    def get_nome(self):
        return self.__nome
    def set_nome(self, nome):
        self.__nome = nome
    
    def get_email(self):
        return self.__email
    def set_email(self, email):
        self.__email = email
    
    def get_telefone(self):
        return self.__telefone
    def set_telefone(self, telefone):
        self.__telefone = telefone
    
    def __str__(self):
        return f"Cliente [id={self.__id}, nome='{self.__nome}', email='{self.__email}', telefone='{self.__telefone}']"