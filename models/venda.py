from datetime import datetime

class Venda:
    def __init__(self, id=None, cliente_id=None, data=None, total=0.0, itens_ids=None, status="Processando"): # <--- 'status' ADICIONADO
        self.__id = id
        self.__cliente_id = cliente_id
        self.__data = data or datetime.now().isoformat()
        self.__total = total
        self.__itens_ids = itens_ids or []
        self.__status = status  
    
    def get_id(self):
        return self.__id
    def set_id(self, id):
        self.__id = id

    def get_cliente_id(self):
        return self.__cliente_id
    def set_cliente_id(self, cliente_id):
        self.__cliente_id = cliente_id

    def get_data(self):
        return self.__data
    def set_data(self, data):
        self.__data = data

    def get_total(self):
        return self.__total
    def set_total(self, total):
        self.__total = total

    def get_itens_ids(self):
        return self.__itens_ids
    def set_itens_ids(self, itens_ids):
        self.__itens_ids = itens_ids

    def get_status(self): 
        return self.__status
    def set_status(self, status):  
        self.__status = status

    def __str__(self):
        return f"Venda [id={self.__id}, cliente_id={self.__cliente_id}, data={self.__data}, total={self.__total}, status='{self.__status}', itens={self.__itens_ids}]"