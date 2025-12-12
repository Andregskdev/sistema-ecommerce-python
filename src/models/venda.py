from datetime import datetime

class Venda:

    def __init__(self, id=0, id_cliente=0, data=None, total=0.0, forma_pagamento='Pix', status='Pendente'):
        self.id = id
        self.id_cliente = id_cliente
        self.data = data if data else datetime.now().strftime('%d/%m/%Y %H:%M')
        self.total = total
        self.forma_pagamento = forma_pagamento
        self.status = status

    def __str__(self):
        return f'Venda ID: {self.id} | Data: {self.data} | Cliente: {self.id_cliente} | Total: R$ {self.total:.2f} | Pagto: {self.forma_pagamento} | Status: {self.status}'

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

    def get_id_cliente(self):
        return self.id_cliente

    def set_id_cliente(self, id_cliente):
        self.id_cliente = id_cliente
