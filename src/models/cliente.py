class Cliente:

    def __init__(self, id=0, nome='', email='', fone=''):
        self.id = id
        self.nome = nome
        self.email = email
        self.fone = fone

    def __str__(self):
        return f'ID: {self.id} | Nome: {self.nome} | Email: {self.email} | Fone: {self.fone}'

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

    def get_nome(self):
        return self.nome

    def set_nome(self, nome):
        self.nome = nome

    def get_email(self):
        return self.email

    def set_email(self, email):
        self.email = email

    def get_fone(self):
        return self.fone

    def set_fone(self, fone):
        self.fone = fone
