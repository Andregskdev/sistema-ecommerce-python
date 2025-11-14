from dao.cliente_dao import ClienteDAO
from dao.categoria_dao import CategoriaDAO
from dao.produto_dao import ProdutoDAO
from dao.venda_dao import VendaDAO
from dao.venda_item_dao import VendaItemDAO

from models.cliente import Cliente
from models.categoria import Categoria
from models.produto import Produto
from models.venda import Venda
from models.venda_item import VendaItem


class UI:
    cliente_logado = None  
    carrinho = {}          

    @staticmethod
    def iniciar():
        ClienteDAO.abrir()
        CategoriaDAO.abrir()
        ProdutoDAO.abrir()
        VendaDAO.abrir()
        VendaItemDAO.abrir()

    @staticmethod
    def main():
        UI.iniciar()
        while True:
            if UI.cliente_logado is None:
                print("\n--- Sistema de Comércio Eletrônico (Visitante) ---")
                print("1 - Entrar no Sistema")
                print("2 - Abrir Conta (Novo Cliente)")
                print("0 - Sair")
                opc = input("Escolha: ").strip()

                if opc == '1':
                    UI.entrar_no_sistema()
                elif opc == '2':
                    UI.abrir_conta()
                elif opc == '0':
                    print("Saindo...")
                    break
                else:
                    print("Opção inválida.")
            elif UI.cliente_logado.get_email() == 'admin@admin.com':
                UI.menu_admin()
            else:
                UI.menu_cliente()

    @staticmethod
    def entrar_no_sistema():
        email = input("Digite seu e-mail: ").strip()
        
        if email == 'admin@admin.com':
            UI.cliente_logado = Cliente(id=-1, nome="Admin", email="admin@admin.com")
            print("Login de Administrador bem-sucedido.")
            return
        clientes = ClienteDAO.listar()
        cliente_encontrado = next((c for c in clientes if c.get_email() == email), None)
        
        if cliente_encontrado:
            UI.cliente_logado = cliente_encontrado
            UI.carrinho.clear() 
            print(f"Login bem-sucedido! Bem-vindo(a), {UI.cliente_logado.get_nome()}.")
        else:
            print("Cliente não encontrado.")

    @staticmethod
    def abrir_conta():
        print("\n--- Cadastro de Novo Cliente ---")
        UI.inserir_cliente(admin_mode=False) 

    @staticmethod
    def logout():
        print(f"Saindo da conta de {UI.cliente_logado.get_nome()}...")
        UI.cliente_logado = None
        UI.carrinho.clear()

    @staticmethod
    def menu_cliente():
        while UI.cliente_logado:
            print(f"\n--- Menu Cliente: {UI.cliente_logado.get_nome()} ---")
            print(f"Carrinho: {len(UI.carrinho)} item(ns)")
            print("1 - Listar Produtos (Tarefa 1)")
            print("2 - Inserir Produto no Carrinho (Tarefa 2)")
            print("3 - Visualizar Carrinho (Tarefa 3)")
            print("4 - Comprar Carrinho (Tarefa 4)")
            print("5 - Listar Minhas Compras (Tarefa 5)")
            print("0 - Sair (Logout)")
            opc = input("Escolha: ").strip()

            if opc == '1': UI.listar_produtos()
            elif opc == '2': UI.inserir_no_carrinho()
            elif opc == '3': UI.visualizar_carrinho()
            elif opc == '4': UI.comprar_carrinho()
            elif opc == '5': UI.listar_minhas_compras()
            elif opc == '0': UI.logout(); break
            else: print("Opção inválida.")

    @staticmethod
    def listar_produtos():
        lista = ProdutoDAO.listar()
        if not lista: print("Nenhum produto cadastrado."); return
        print("\n--- Produtos Disponíveis ---")
        for p in lista:
            print(f"ID: {p.get_id()} | {p.get_nome()} | R$ {p.get_preco():.2f} | Estoque: {p.get_estoque()}")

    @staticmethod
    def inserir_no_carrinho():
        UI.listar_produtos()
        try:
            pid = int(input("ID do produto a adicionar: "))
            produto = ProdutoDAO.listar_id(pid)
            if not produto:
                print("Produto não encontrado."); return
            
            qtd = int(input("Quantidade: "))
            if qtd <= 0:
                print("Quantidade deve ser positiva."); return
            if qtd > produto.get_estoque():
                print(f"Estoque insuficiente. Disponível: {produto.get_estoque()}"); return

            if pid in UI.carrinho:
                UI.carrinho[pid] += qtd
            else:
                UI.carrinho[pid] = qtd
            produto.set_estoque(produto.get_estoque() - qtd)
            ProdutoDAO.atualizar(produto) 

            print(f"{qtd}x {produto.get_nome()} adicionado(s) ao carrinho.")

        except ValueError:
            print("Entrada inválida (ID e Quantidade devem ser números).")

    @staticmethod
    def visualizar_carrinho():
        if not UI.carrinho:
            print("Carrinho está vazio."); return
        
        print("\n--- Meu Carrinho ---")
        total_carrinho = 0.0
        for pid, qtd in UI.carrinho.items():
            produto = ProdutoDAO.listar_id(pid)
            if produto:
                nome = produto.get_nome()
                preco_unit = produto.get_preco()
                subtotal = preco_unit * qtd
                total_carrinho += subtotal
                print(f"- {nome} | Qtd: {qtd} | Preço Unit: R$ {preco_unit:.2f} | Total Item: R$ {subtotal:.2f}")
            else:
                print(f"- [Produto ID {pid} removido do sistema]")
        
        print("-" * 20)
        print(f"Valor Total do Carrinho: R$ {total_carrinho:.2f}")

    @staticmethod
    def comprar_carrinho():
        if not UI.carrinho:
            print("Carrinho está vazio."); return
        
        print("Finalizando a compra...")
        total_venda = 0.0
        itens_ids = []

        for pid, qtd in UI.carrinho.items():
            produto = ProdutoDAO.listar_id(pid)
            if not produto:
                print(f"Ignorando produto ID {pid} (não encontrado).")
                continue
            
            preco_unit = produto.get_preco()
            item = VendaItem(None, pid, qtd, preco_unit, None)
            VendaItemDAO.inserir(item) 
            itens_ids.append(item.get_id())
            total_venda += preco_unit * qtd
            
        if not itens_ids:
            print("Compra não pôde ser finalizada (itens inválidos).")
            UI.carrinho.clear()
            return
        venda = Venda(None, UI.cliente_logado.get_id(), None, total_venda, itens_ids, "Processando")
        VendaDAO.inserir(venda) 

        venda_id = venda.get_id()
        for iid in itens_ids:
            item = VendaItemDAO.listar_id(iid)
            if item:
                item.set_venda_id(venda_id)
                VendaItemDAO.atualizar(item) 

        print(f"\nCompra registrada com sucesso! ID da Venda: {venda.get_id()} | Total: R$ {total_venda:.2f}")
        UI.carrinho.clear()

    @staticmethod
    def listar_minhas_compras():
        vendas = VendaDAO.listar_por_cliente(UI.cliente_logado.get_id())
        if not vendas:
            print("Você ainda não possui compras."); return
        
        print("\n--- Minhas Compras ---")
        for v in vendas:
            UI.mostrar_detalhes_venda(v)

    @staticmethod
    def menu_admin():
        while UI.cliente_logado and UI.cliente_logado.get_email() == 'admin@admin.com':
            print("\n--- Menu Administrador ---")
            print("1 - Gerenciar Clientes")
            print("2 - Gerenciar Categorias")
            print("3 - Gerenciar Produtos")
            print("4 - Gerenciar Vendas")
            print("0 - Sair (Logout)")
            opc = input("Escolha: ").strip()

            if opc == '1': UI.menu_admin_clientes()
            elif opc == '2': UI.menu_admin_categorias()
            elif opc == '3': UI.menu_admin_produtos()
            elif opc == '4': UI.menu_admin_vendas()
            elif opc == '0': UI.logout(); break
            else: print("Opção inválida.")

    @staticmethod
    def menu_admin_clientes():
        while True:
            print("\n--- ADMIN: CLIENTES ---")
            print("1 - Listar")
            print("2 - Inserir")
            print("3 - Atualizar")
            print("4 - Excluir")
            print("0 - Voltar")
            opc = input("Escolha: ").strip()
            if opc == '1': UI.listar_clientes()
            elif opc == '2': UI.inserir_cliente(admin_mode=True)
            elif opc == '3': UI.atualizar_cliente()
            elif opc == '4': UI.excluir_cliente()
            elif opc == '0': break
            else: print("Opção inválida.")

    @staticmethod
    def listar_clientes():
        lista = ClienteDAO.listar()
        if not lista: print("Nenhum cliente cadastrado."); return
        for c in lista: print(c)

    @staticmethod
    def inserir_cliente(admin_mode=False):
        nome = input("Nome: ")
        email = input("Email: ")
        
        if email == 'admin@admin.com':
            print("E-mail 'admin@admin.com' é reservado."); return
        if any(c.get_email() == email for c in ClienteDAO.listar()):
            print("Este e-mail já está em uso."); return

        telefone = input("Telefone: ")
        cliente = ClienteDAO.inserir(Cliente(None, nome, email, telefone))
        print("Cliente inserido com sucesso.")
        
        if not admin_mode:
            UI.cliente_logado = cliente
            print(f"Cadastro realizado! Bem-vindo(a), {cliente.get_nome()}.")

    @staticmethod
    def atualizar_cliente():
        id = int(input("ID do cliente: "))
        c = ClienteDAO.listar_id(id)
        if not c:
            print("Cliente não encontrado."); return
        if c.get_email() == 'admin@admin.com':
            print("Não é possível alterar o Admin."); return
        
        nome = input(f"Nome [{c.get_nome()}]: ") or c.get_nome()
        email = input(f"Email [{c.get_email()}]: ") or c.get_email()
        telefone = input(f"Telefone [{c.get_telefone()}]: ") or c.get_telefone()
        
        if email != c.get_email() and any(cl.get_email() == email for cl in ClienteDAO.listar()):
            print("Este e-mail já está em uso por outra conta."); return

        c.set_nome(nome)
        c.set_email(email)
        c.set_telefone(telefone)
        ClienteDAO.atualizar(c)
        print("Cliente atualizado.")

    @staticmethod
    def excluir_cliente():
        id = int(input("ID do cliente a excluir: "))
        c = ClienteDAO.listar_id(id)
        if not c:
            print("Cliente não encontrado."); return
        if c.get_email() == 'admin@admin.com':
            print("Não é possível excluir o Admin."); return
            
        if ClienteDAO.excluir(id): print("Cliente excluído.")
        else: print("Erro ao excluir.")

    @staticmethod
    def menu_admin_categorias():
        while True:
            print("\n--- ADMIN: CATEGORIAS ---")
            print("1 - Listar")
            print("2 - Inserir")
            print("3 - Atualizar")
            print("4 - Excluir")
            print("0 - Voltar")
            opc = input("Escolha: ").strip()
            if opc == '1': UI.listar_categorias()
            elif opc == '2': UI.inserir_categoria()
            elif opc == '3': UI.atualizar_categoria()
            elif opc == '4': UI.excluir_categoria()
            elif opc == '0': break
            else: print("Opção inválida.")

    @staticmethod
    def listar_categorias():
        lista = CategoriaDAO.listar()
        if not lista: print("Nenhuma categoria cadastrada."); return
        for c in lista: print(c)

    @staticmethod
    def inserir_categoria():
        nome = input("Nome: ")
        descricao = input("Descrição: ")
        CategoriaDAO.inserir(Categoria(None, nome, descricao))
        print("Categoria inserida com sucesso.")

    @staticmethod
    def atualizar_categoria():
        id = int(input("ID da categoria: "))
        c = CategoriaDAO.listar_id(id)
        if not c:
            print("Categoria não encontrada."); return
        nome = input(f"Nome [{c.get_nome()}]: ") or c.get_nome()
        descricao = input(f"Descrição [{c.get_descricao()}]: ") or c.get_descricao()
        c.set_nome(nome)
        c.set_descricao(descricao)
        CategoriaDAO.atualizar(c)
        print("Categoria atualizada.")

    @staticmethod
    def excluir_categoria():
        id = int(input("ID da categoria a excluir: "))
        # TODO: Adicionar validação para não excluir categoria em uso
        if CategoriaDAO.excluir(id): print("Categoria excluída.")
        else: print("Categoria não encontrada.")

    @staticmethod
    def menu_admin_produtos():
        while True:
            print("\n--- ADMIN: PRODUTOS ---")
            print("1 - Listar")
            print("2 - Inserir")
            print("3 - Atualizar")
            print("4 - Excluir")
            print("5 - Reajustar Preços (Tarefa 8)")
            print("0 - Voltar")
            opc = input("Escolha: ").strip()
            if opc == '1': UI.listar_produtos()
            elif opc == '2': UI.inserir_produto()
            elif opc == '3': UI.atualizar_produto()
            elif opc == '4': UI.excluir_produto()
            elif opc == '5': UI.reajustar_precos()
            elif opc == '0': break
            else: print("Opção inválida.")

    @staticmethod
    def inserir_produto():
        try:
            nome = input("Nome: ")
            descricao = input("Descrição: ")
            preco = float(input("Preço: "))
            estoque = int(input("Estoque: ")) 
            categoria_id = input("ID da categoria (ou vazio): ")
            categoria_id = int(categoria_id) if categoria_id else None
            # TODO: Validar se categoria_id existe
            ProdutoDAO.inserir(Produto(None, nome, descricao, preco, estoque, categoria_id))
            print("Produto inserido com sucesso.")
        except ValueError:
            print("Entrada inválida (Preço e Estoque devem ser números).")

    @staticmethod
    def atualizar_produto():
        try:
            id = int(input("ID do produto: "))
            p = ProdutoDAO.listar_id(id)
            if not p:
                print("Produto não encontrado."); return
            
            nome = input(f"Nome [{p.get_nome()}]: ") or p.get_nome()
            descricao = input(f"Descrição [{p.get_descricao()}]: ") or p.get_descricao()
            preco = input(f"Preço [{p.get_preco()}]: ") or p.get_preco()
            estoque = input(f"Estoque [{p.get_estoque()}]: ") or p.get_estoque() 
            categoria_id = input(f"Categoria ID [{p.get_categoria_id()}]: ") or p.get_categoria_id()
            
            p.set_nome(nome)
            p.set_descricao(descricao)
            p.set_preco(float(preco))
            p.set_estoque(int(estoque)) 
            p.set_categoria_id(int(categoria_id) if categoria_id else None)
            ProdutoDAO.atualizar(p)
            print("Produto atualizado.")
        except ValueError:
            print("Entrada inválida (Preço e Estoque devem ser números).")

    @staticmethod
    def excluir_produto():
        id = int(input("ID do produto a excluir: "))
        # TODO: Adicionar validação para não excluir produto em vendas
        if ProdutoDAO.excluir(id): print("Produto excluído.")
        else: print("Produto não encontrado.")

    @staticmethod
    def reajustar_precos():
        try:
            percentual = float(input("Digite o percentual de reajuste (ex: 10 para 10%, -5 para -5%): "))
            ProdutoDAO.reajustar_precos(percentual)
            print("Preços reajustados com sucesso.")
        except ValueError:
            print("Entrada inválida. Digite um número.")

    @staticmethod
    def menu_admin_vendas():
        while True:
            print("\n--- ADMIN: VENDAS ---")
            print("1 - Listar Todas as Vendas (Tarefa 6)")
            print("2 - Atualizar Status da Venda (Tarefa 7)")
            print("3 - Excluir Venda (CUIDADO)")
            print("0 - Voltar")
            opc = input("Escolha: ").strip()
            if opc == '1': UI.listar_todas_as_vendas()
            elif opc == '2': UI.atualizar_status_venda()
            elif opc == '3': UI.excluir_venda()
            elif opc == '0': break
            else: print("Opção inválida.")

    @staticmethod
    def listar_todas_as_vendas():
        vendas = VendaDAO.listar()
        if not vendas:
            print("Nenhuma venda registrada."); return
        
        print("\n--- Todas as Vendas Registradas ---")
        for v in vendas:
            cliente = ClienteDAO.listar_id(v.get_cliente_id())
            nome_cliente = cliente.get_nome() if cliente else "(Cliente Excluído)"
            print(f"\nCliente: {nome_cliente} (ID: {v.get_cliente_id()})")
            UI.mostrar_detalhes_venda(v)

    @staticmethod
    def atualizar_status_venda():
        try:
            id = int(input("ID da venda a atualizar: "))
            venda = VendaDAO.listar_id(id)
            if not venda:
                print("Venda não encontrada."); return
            
            print(f"Status atual: {venda.get_status()}")
            novo_status = input("Novo status (ex: Enviado, Entregue, Cancelado): ")
            if not novo_status:
                print("Status não pode ser vazio."); return

            venda.set_status(novo_status)
            VendaDAO.atualizar(venda)
            print("Status da venda atualizado.")
        except ValueError:
            print("ID inválido.")

    @staticmethod
    def excluir_venda():
        try:
            id = int(input("ID da venda a excluir: "))
            venda = VendaDAO.listar_id(id)
            if not venda:
                print("Venda não encontrada."); return
            
            for iid in venda.get_itens_ids():
                VendaItemDAO.excluir(iid)

            VendaDAO.excluir(id)
            print("Venda e itens associados excluídos.")
        except ValueError:
            print("ID inválido.")

    @staticmethod
    def mostrar_detalhes_venda(v: Venda):
        """Função auxiliar para exibir detalhes de uma venda."""
        print(f"  Venda ID: {v.get_id()} | Data: {v.get_data()} | Status: {v.get_status()} | Total: R$ {v.get_total():.2f}")
        print("  Itens:")
        for iid in v.get_itens_ids():
            item = VendaItemDAO.listar_id(iid)
            if item:
                prod = ProdutoDAO.listar_id(item.get_produto_id())
                nome_prod = prod.get_nome() if prod else "(Produto excluído)"
                print(f"   - {nome_prod} (ID: {item.get_produto_id()}) | Qtd: {item.get_quantidade()} | Preço Unit: R$ {item.get_preco_unitario():.2f}")
            else:
                print(f"   - (Item {iid} excluído)")


if __name__ == "__main__":
    UI.main()