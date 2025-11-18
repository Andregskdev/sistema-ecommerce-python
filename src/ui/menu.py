from src.models.cliente import Cliente
from src.models.categoria import Categoria
from src.models.produto import Produto
from src.models.venda import Venda
from src.models.venda_item import VendaItem

from src.dao.cliente_dao import ClienteDAO
from src.dao.categoria_dao import CategoriaDAO
from src.dao.produto_dao import ProdutoDAO
from src.dao.venda_dao import VendaDAO
from src.dao.venda_item_dao import VendaItemDAO

class UI:
    carrinho = []         # Lista em memória para o carrinho atual
    cliente_atual_id = 0  # 0 significa deslogado ou admin

    @staticmethod
    def main():
        # 1. Carregar dados dos arquivos JSON
        ClienteDAO.abrir()
        CategoriaDAO.abrir()
        ProdutoDAO.abrir()
        VendaDAO.abrir()
        VendaItemDAO.abrir()
        
        while True:
            print("\n=== SISTEMA DE E-COMMERCE COMPLETO ===")
            print("1. Acesso Cliente (Comprar)")
            print("2. Acesso Admin (Cadastros e Relatórios)")
            print("0. Sair")
            opcao = input("Opção: ")

            if opcao == '1': UI.menu_cliente_principal()
            elif opcao == '2': UI.menu_admin_principal()
            elif opcao == '0': 
                print("Encerrando sistema...")
                break
            else: 
                print("Opção inválida.")

    # =================================================================
    # ÁREA DO CLIENTE (Vendas, Carrinho, Checkout)
    # =================================================================
    @staticmethod
    def menu_cliente_principal():
        # Simples sistema de Login
        if UI.cliente_atual_id == 0:
            email = input("\n--- LOGIN CLIENTE ---\nDigite seu email: ")
            # Busca cliente pelo email
            clientes = [c for c in ClienteDAO.listar() if c.email == email]
            if not clientes:
                print("Cliente não encontrado! Cadastre-se através do menu Admin.")
                return
            UI.cliente_atual_id = clientes[0].id
            print(f"Bem-vindo(a), {clientes[0].nome}!")

        while True:
            print(f"\n--- MENU CLIENTE (Logado: {UI.cliente_atual_id}) ---")
            print("1. Listar Produtos (Vitrine)")
            print("2. Adicionar Produto ao Carrinho")
            print("3. Visualizar Carrinho")
            print("4. Finalizar Compra (Checkout)")
            print("5. Minhas Compras Anteriores")
            print("0. Sair / Logout")
            
            op = input("Opção: ")
            if op == '1': UI.listar_produtos_vitrine()
            elif op == '2': UI.adicionar_carrinho()
            elif op == '3': UI.visualizar_carrinho()
            elif op == '4': UI.finalizar_compra()
            elif op == '5': UI.listar_minhas_compras()
            elif op == '0': 
                UI.cliente_atual_id = 0
                UI.carrinho = [] # Limpa carrinho ao sair
                break

    @staticmethod
    def listar_produtos_vitrine():
        print("\n--- VITRINE DE PRODUTOS ---")
        produtos = ProdutoDAO.listar()
        if not produtos:
            print("Nenhum produto cadastrado.")
        for p in produtos:
            status = f"Estoque: {p.estoque}" if p.estoque > 0 else "INDISPONÍVEL"
            cat = CategoriaDAO.listar_id(p.id_categoria)
            nome_cat = cat.descricao if cat else "Geral"
            print(f"ID: {p.id} | {p.descricao} | R$ {p.preco:.2f} | {status} | Categoria: {nome_cat}")

    @staticmethod
    def adicionar_carrinho():
        UI.listar_produtos_vitrine()
        try:
            id_prod = int(input("\nDigite o ID do produto para adicionar: "))
            prod = ProdutoDAO.listar_id(id_prod)

            if not prod:
                print("Produto não encontrado.")
                return
            if prod.estoque <= 0:
                print("Produto esgotado!")
                return

            qtd = int(input(f"Quantidade desejada (Máx {prod.estoque}): "))
            if qtd <= 0 or qtd > prod.estoque:
                print("Quantidade inválida.")
                return

            # Verifica se já existe no carrinho para somar
            item_existente = next((i for i in UI.carrinho if i.id_produto == id_prod), None)
            
            if item_existente:
                if item_existente.quantidade + qtd > prod.estoque:
                    print("Estoque insuficiente para adicionar mais itens deste produto.")
                else:
                    item_existente.quantidade += qtd
                    print("Quantidade atualizada no carrinho!")
            else:
                # Cria novo item (id=0 e id_venda=0 pois ainda não foi salvo no banco)
                novo_item = VendaItem(0, 0, id_prod, qtd, prod.preco)
                UI.carrinho.append(novo_item)
                print("Produto adicionado ao carrinho!")

        except ValueError:
            print("Erro: Digite apenas números.")

    @staticmethod
    def visualizar_carrinho():
        print("\n--- SEU CARRINHO ---")
        if not UI.carrinho:
            print("Seu carrinho está vazio.")
            return 0.0

        total_geral = 0.0
        for item in UI.carrinho:
            prod = ProdutoDAO.listar_id(item.id_produto)
            subtotal = item.quantidade * item.valor_unitario
            total_geral += subtotal
            print(f"- {prod.descricao} | Qtd: {item.quantidade} | Unit: R$ {item.valor_unitario:.2f} | Subtotal: R$ {subtotal:.2f}")
        
        print(f"-----------------------------------")
        print(f"TOTAL A PAGAR: R$ {total_geral:.2f}")
        return total_geral

    @staticmethod
    def finalizar_compra():
        total = UI.visualizar_carrinho()
        if not UI.carrinho: return

        if input("\nDeseja confirmar a compra? (S/N): ").upper() != 'S':
            return

        forma_pgto = input("Forma de Pagamento (Pix/Cartão/Boleto): ")

        # 1. Gerar Venda
        novo_id_venda = VendaDAO.get_proximo_id()
        venda = Venda(novo_id_venda, UI.cliente_atual_id, None, total, forma_pgto, "Confirmada")
        VendaDAO.inserir(venda)

        # 2. Salvar Itens e Baixar Estoque
        prox_id_item = VendaItemDAO.get_proximo_id()
        for item in UI.carrinho:
            item.id = prox_id_item
            item.id_venda = novo_id_venda
            VendaItemDAO.inserir(item)
            prox_id_item += 1

            # Baixa de Estoque
            prod = ProdutoDAO.listar_id(item.id_produto)
            if prod:
                prod.estoque -= item.quantidade
                ProdutoDAO.atualizar(prod)

        print("Compra realizada com sucesso!")
        UI.carrinho = [] # Limpa carrinho

    @staticmethod
    def listar_minhas_compras():
        print("\n--- HISTÓRICO DE COMPRAS ---")
        vendas = VendaDAO.listar_por_cliente(UI.cliente_atual_id)
        if not vendas: print("Nenhuma compra encontrada.")
        
        for v in vendas:
            print(f"\n[Venda #{v.id}] Data: {v.data} | Total: R$ {v.total:.2f} | Status: {v.status}")
            itens = VendaItemDAO.listar_por_venda(v.id)
            for i in itens:
                p = ProdutoDAO.listar_id(i.id_produto)
                print(f"   * {p.descricao} ({i.quantidade}x)")

    # =================================================================
    # ÁREA ADMINISTRATIVA (CRUDs e Relatórios)
    # =================================================================
    @staticmethod
    def menu_admin_principal():
        while True:
            print("\n--- PAINEL ADMINISTRADOR ---")
            print("1. Gerenciar Clientes")
            print("2. Gerenciar Categorias")
            print("3. Gerenciar Produtos")
            print("4. Relatório de Todas as Vendas")
            print("0. Voltar")
            op = input("Opção: ")

            if op == '1': UI.menu_crud_cliente()
            elif op == '2': UI.menu_crud_categoria()
            elif op == '3': UI.menu_crud_produto()
            elif op == '4': UI.relatorio_vendas()
            elif op == '0': break
            else: print("Opção inválida.")

    @staticmethod
    def relatorio_vendas():
        print("\n--- RELATÓRIO GERAL DE VENDAS (ADMIN) ---")
        vendas = VendaDAO.listar()
        if not vendas: print("Nenhuma venda registrada no sistema.")

        for v in vendas:
            cli = ClienteDAO.listar_id(v.id_cliente)
            nome_cli = cli.nome if cli else "Desconhecido"
            print(f"ID: {v.id} | Data: {v.data} | Cli: {nome_cli} | R$ {v.total:.2f} | {v.forma_pagamento}")

    # --- CRUD CLIENTE ---
    @staticmethod
    def menu_crud_cliente():
        print("\n-- GERENCIAR CLIENTES --")
        print("1. Listar | 2. Inserir | 3. Atualizar | 4. Excluir")
        op = input("Opção: ")
        if op == '1': 
            for c in ClienteDAO.listar(): print(c)
        elif op == '2':
            try:
                id = int(input("ID: "))
                c = Cliente(id, input("Nome: "), input("Email: "), input("Fone: "))
                ClienteDAO.inserir(c)
                print("Cliente salvo!")
            except ValueError: print("ID deve ser numérico.")
        elif op == '3':
            id = int(input("ID para alterar: "))
            c = ClienteDAO.listar_id(id)
            if c:
                c.nome = input(f"Nome ({c.nome}): ") or c.nome
                c.email = input(f"Email ({c.email}): ") or c.email
                c.fone = input(f"Fone ({c.fone}): ") or c.fone
                ClienteDAO.atualizar(c)
                print("Cliente atualizado.")
            else: print("Cliente não encontrado.")
        elif op == '4':
            id = int(input("ID para excluir: "))
            c = ClienteDAO.listar_id(id)
            if c: 
                ClienteDAO.excluir(c)
                print("Cliente removido.")
            else: print("Cliente não encontrado.")

    # --- CRUD CATEGORIA ---
    @staticmethod
    def menu_crud_categoria():
        print("\n-- GERENCIAR CATEGORIAS --")
        print("1. Listar | 2. Inserir | 3. Atualizar | 4. Excluir")
        op = input("Opção: ")
        if op == '1':
            for c in CategoriaDAO.listar(): print(c)
        elif op == '2':
            try:
                id = int(input("ID: "))
                c = Categoria(id, input("Descrição: "))
                CategoriaDAO.inserir(c)
                print("Categoria salva!")
            except ValueError: print("ID deve ser numérico.")
        elif op == '3':
            id = int(input("ID para alterar: "))
            c = CategoriaDAO.listar_id(id)
            if c:
                c.descricao = input(f"Descrição ({c.descricao}): ") or c.descricao
                CategoriaDAO.atualizar(c)
                print("Categoria atualizada.")
            else: print("Categoria não encontrada.")
        elif op == '4':
            id = int(input("ID para excluir: "))
            c = CategoriaDAO.listar_id(id)
            if c:
                CategoriaDAO.excluir(c)
                print("Categoria removida.")
            else: print("Categoria não encontrada.")

    # --- CRUD PRODUTO ---
    @staticmethod
    def menu_crud_produto():
        print("\n-- GERENCIAR PRODUTOS --")
        print("1. Listar | 2. Inserir | 3. Atualizar | 4. Excluir")
        op = input("Opção: ")
        if op == '1':
            for p in ProdutoDAO.listar():
                cat = CategoriaDAO.listar_id(p.id_categoria)
                cat_nome = cat.descricao if cat else "Sem Categoria"
                print(f"{p} [Categoria: {cat_nome}]")
        elif op == '2':
            try:
                id = int(input("ID: "))
                desc = input("Descrição: ")
                preco = float(input("Preço: "))
                estoque = int(input("Estoque: "))
                
                print("\nCategorias disponíveis:")
                for cat in CategoriaDAO.listar(): print(cat)
                id_cat = int(input("ID da Categoria: "))
                
                p = Produto(id, desc, preco, estoque, id_cat)
                ProdutoDAO.inserir(p)
                print("Produto salvo!")
            except ValueError: print("Erro nos valores numéricos.")
        elif op == '3':
            id = int(input("ID para alterar: "))
            p = ProdutoDAO.listar_id(id)
            if p:
                p.descricao = input(f"Descrição ({p.descricao}): ") or p.descricao
                
                novo_preco = input(f"Preço ({p.preco}): ")
                if novo_preco: p.preco = float(novo_preco)
                
                novo_estoque = input(f"Estoque ({p.estoque}): ")
                if novo_estoque: p.estoque = int(novo_estoque)
                
                nova_cat = input(f"ID Categoria ({p.id_categoria}): ")
                if nova_cat: p.id_categoria = int(nova_cat)
                
                ProdutoDAO.atualizar(p)
                print("Produto atualizado.")
            else: print("Produto não encontrado.")
        elif op == '4':
            id = int(input("ID para excluir: "))
            p = ProdutoDAO.listar_id(id)
            if p:
                ProdutoDAO.excluir(p)
                print("Produto removido.")
            else: print("Produto não encontrado.")