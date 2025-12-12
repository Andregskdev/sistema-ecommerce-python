class VendaItem:

    def __init__(self, id=0, id_venda=0, id_produto=0, quantidade=0, valor_unitario=0.0):
        self.id = id
        self.id_venda = id_venda
        self.id_produto = id_produto
        self.quantidade = quantidade
        self.valor_unitario = valor_unitario

    def __str__(self):
        return f'Item ID: {self.id} | Venda ID: {self.id_venda} | Prod ID: {self.id_produto} | Qtd: {self.quantidade} | Unit: {self.valor_unitario}'

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

    def get_id_venda(self):
        return self.id_venda

    def set_id_venda(self, id_venda):
        self.id_venda = id_venda

    def get_id_produto(self):
        return self.id_produto

    def set_id_produto(self, id_produto):
        self.id_produto = id_produto

    def get_quantidade(self):
        return self.quantidade

    def set_quantidade(self, quantidade):
        self.quantidade = quantidade

    def get_valor_unitario(self):
        return self.valor_unitario

    def set_valor_unitario(self, valor_unitario):
        self.valor_unitario = valor_unitario
