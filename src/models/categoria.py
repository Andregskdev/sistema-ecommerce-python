class Categoria:

    def __init__(self, id=0, descricao=''):
        self.id = id
        self.descricao = descricao

    def __str__(self):
        return f'ID: {self.id} | Descrição: {self.descricao}'

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

    def get_descricao(self):
        return self.descricao

    def set_descricao(self, descricao):
        self.descricao = descricao
