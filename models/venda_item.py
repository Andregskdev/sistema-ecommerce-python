class VendaItem:
    def __init__(self, id=None, produto_id=None, quantidade=0, preco_unitario=0.0, venda_id=None):
        self.__id = id
        self.__produto_id = produto_id
        self.__quantidade = quantidade
        self.__preco_unitario = preco_unitario
        self.__venda_id = venda_id

    def get_id(self): return self.__id
    def set_id(self, id): self.__id = id

    def get_produto_id(self): return self.__produto_id
    def set_produto_id(self, produto_id): self.__produto_id = produto_id

    def get_quantidade(self): return self.__quantidade
    def set_quantidade(self, quantidade): self.__quantidade = quantidade

    def get_preco_unitario(self): return self.__preco_unitario
    def set_preco_unitario(self, preco_unitario): self.__preco_unitario = preco_unitario

    def get_venda_id(self): return self.__venda_id
    def set_venda_id(self, venda_id): self.__venda_id = venda_id

    def __str__(self):
        return f"VendaItem [id={self.__id}, produto_id={self.__produto_id}, qtd={self.__quantidade}, preco={self.__preco_unitario}]"
