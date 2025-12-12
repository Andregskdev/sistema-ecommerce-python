class Produto:

    def __init__(self, id=0, descricao='', preco=0.0, estoque=0, id_categoria=0):
        self.id = id
        self.descricao = descricao
        self.preco = preco
        self.estoque = estoque
        self.id_categoria = id_categoria

    def __str__(self):
        return f'ID: {self.id} | Produto: {self.descricao} | R$ {self.preco:.2f} | Qtd: {self.estoque} | CatID: {self.id_categoria}'

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

    def get_descricao(self):
        return self.descricao

    def set_descricao(self, descricao):
        self.descricao = descricao

    def get_preco(self):
        return self.preco

    def set_preco(self, preco):
        self.preco = preco

    def get_estoque(self):
        return self.estoque

    def set_estoque(self, estoque):
        self.estoque = estoque

    def get_id_categoria(self):
        return self.id_categoria

    def set_id_categoria(self, id_categoria):
        self.id_categoria = id_categoria
