import json
import os
import hashlib

class AdminAuth:
    arquivo_admins = 'data/admins.json'

    @staticmethod
    def hash_senha(senha):
        return hashlib.sha256(senha.encode()).hexdigest()

    @staticmethod
    def carregar_admins():
        if os.path.exists(AdminAuth.arquivo_admins):
            with open(AdminAuth.arquivo_admins, 'r') as f:
                return json.load(f)
        return []

    @staticmethod
    def salvar_admins(admins):
        os.makedirs('data', exist_ok=True)
        with open(AdminAuth.arquivo_admins, 'w') as f:
            json.dump(admins, f, indent=4)

    @staticmethod
    def criar_admin_padrao():
        admins = AdminAuth.carregar_admins()
        if admins:
            return
        admin_padrao = {'usuario': 'admin', 'senha': AdminAuth.hash_senha('admin123')}
        admins.append(admin_padrao)
        AdminAuth.salvar_admins(admins)
        print('✓ Admin padrão criado!')
        print('  Usuário: admin')
        print('  Senha: admin123')
        print('  (Altere a senha após primeiro login!)')

    @staticmethod
    def autenticar(usuario, senha):
        admins = AdminAuth.carregar_admins()
        for admin in admins:
            if admin['usuario'] == usuario:
                if admin['senha'] == AdminAuth.hash_senha(senha):
                    return True
        return False

    @staticmethod
    def usuario_existe(usuario):
        admins = AdminAuth.carregar_admins()
        return any((admin['usuario'] == usuario for admin in admins))

    @staticmethod
    def criar_novo_admin(usuario, senha):
        if AdminAuth.usuario_existe(usuario):
            return (False, 'Usuário já existe!')
        admins = AdminAuth.carregar_admins()
        novo_admin = {'usuario': usuario, 'senha': AdminAuth.hash_senha(senha)}
        admins.append(novo_admin)
        AdminAuth.salvar_admins(admins)
        return (True, 'Admin criado com sucesso!')

    @staticmethod
    def alterar_senha(usuario, senha_antiga, senha_nova):
        if not AdminAuth.autenticar(usuario, senha_antiga):
            return (False, 'Senha atual incorreta!')
        admins = AdminAuth.carregar_admins()
        for admin in admins:
            if admin['usuario'] == usuario:
                admin['senha'] = AdminAuth.hash_senha(senha_nova)
                AdminAuth.salvar_admins(admins)
                return (True, 'Senha alterada com sucesso!')
        return (False, 'Usuário não encontrado!')

    @staticmethod
    def listar_admins():
        admins = AdminAuth.carregar_admins()
        return [{'usuario': admin['usuario']} for admin in admins]
