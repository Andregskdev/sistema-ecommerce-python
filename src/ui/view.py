from src.dao.categoria_dao import CategoriaDAO
from src.dao.produto_dao import ProdutoDAO

class View:

    @staticmethod
    def exibir_menu_principal():
        print('\n=== SISTEMA DE E-COMMERCE ===')
        print('1. Acesso Cliente (Comprar)')
        print('2. Acesso Admin (Cadastros e Relatórios)')
        print('0. Sair')

    @staticmethod
    def exibir_menu_cliente():
        print('\n--- Menu Cliente ---')
        print('1. Listar Produtos (Vitrine)')
        print('2. Adicionar Produto ao Carrinho')
        print('3. Visualizar Carrinho')
        print('4. Finalizar Compra (Checkout)')
        print('5. Minhas Compras Anteriores')
        print('6. Remover Item do Carrinho')
        print('7. Editar Perfil')
        print('0. Sair / Logout')

    @staticmethod
    def exibir_menu_admin():
        print('\n--- Painel Administrador ---')
        print('1. Gerenciar Clientes')
        print('2. Gerenciar Categorias')
        print('3. Gerenciar Produtos')
        print('4. Relatório de Todas as Vendas')
        print('0. Voltar')

    @staticmethod
    def exibir_vitrine_produtos(produtos):
        print('\n--- Vitrine de Produtos ---')
        if not produtos:
            print('Nenhum produto cadastrado.')
            return
        for p in produtos:
            status = f'Estoque: {p.estoque}' if p.estoque > 0 else 'INDISPONÍVEL'
            cat = CategoriaDAO.listar_id(p.id_categoria)
            nome_cat = cat.descricao if cat else 'Geral'
            print(f'ID: {p.id:<3} | {p.descricao:<30} | R$ {p.preco:>8.2f} | {status:<15} | {nome_cat}')

    @staticmethod
    def exibir_carrinho(carrinho):
        print('\n--- Seu Carrinho ---')
        if not carrinho:
            print('Seu carrinho está vazio.')
            return 0.0
        total_geral = 0.0
        print(f"\n{'Produto':<35} {'Qtd':<6} {'Unit':<12} {'Subtotal':<15}")
        print('-' * 80)
        for item in carrinho:
            prod = ProdutoDAO.listar_id(item.id_produto)
            subtotal = item.quantidade * item.valor_unitario
            total_geral += subtotal
            print(f'{prod.descricao:<35} {item.quantidade:<6} R$ {item.valor_unitario:>8.2f}  R$ {subtotal:>12.2f}')
        print('-' * 80)
        print(f"{'TOTAL A PAGAR:':<45} R$ {total_geral:>12.2f}")
        return total_geral

    @staticmethod
    def exibir_historico_compras(vendas):
        print('\n--- Histórico de Compras ---')
        if not vendas:
            print('Nenhuma compra encontrada.')
            return
        from src.dao.venda_item_dao import VendaItemDAO
        for v in vendas:
            print(f'\nVenda #{v.id} | Data: {v.data} | Total: R$ {v.total:.2f} | Status: {v.status}')
            itens = VendaItemDAO.listar_por_venda(v.id)
            for i in itens:
                p = ProdutoDAO.listar_id(i.id_produto)
                print(f'   • {p.descricao} ({i.quantidade}x)')

    @staticmethod
    def exibir_mensagem(mensagem):
        print(f'\n{mensagem}')

    @staticmethod
    def exibir_erro(erro):
        print(f'Erro: {erro}')

    @staticmethod
    def exibir_sucesso(mensagem):
        print(f'Sucesso: {mensagem}')

    @staticmethod
    def obter_entrada(prompt):
        return input(f'\n{prompt}: ')

    @staticmethod
    def obter_entrada_numerica(prompt):
        try:
            return int(input(f'\n{prompt}: '))
        except ValueError:
            print('Erro: Digite apenas números.')
            return None

    @staticmethod
    def obter_confirmacao(prompt='Confirma esta ação?'):
        resposta = input(f'\n{prompt} (S/N): ').upper()
        return resposta == 'S'

    @staticmethod
    def obter_senha(prompt='Digite a senha'):
        import getpass
        return getpass.getpass(f'\n{prompt}: ')

    @staticmethod
    def exibir_categorias_disponiveis():
        categorias = CategoriaDAO.listar()
        print('\n--- Categorias Disponíveis ---')
        print('0. Todas as categorias')
        if not categorias:
            print('Nenhuma categoria cadastrada.')
            return
        for cat in categorias:
            print(f'{cat.id}. {cat.descricao}')

    @staticmethod
    def exibir_vitrine_filtrada(produtos, id_categoria):
        cat = CategoriaDAO.listar_id(id_categoria)
        titulo = f'PRODUTOS - {cat.descricao.upper()}' if cat else 'PRODUTOS'
        print(f'\n--- {titulo} ---')
        if not produtos:
            print('Nenhum produto nesta categoria.')
            return
        for p in produtos:
            status = f'Estoque: {p.estoque}' if p.estoque > 0 else 'INDISPONÍVEL'
            print(f'ID: {p.id:<3} | {p.descricao:<30} | R$ {p.preco:>8.2f} | {status}')

    @staticmethod
    def exibir_relatorio_periodo(vendas, data_inicio, data_fim):
        print(f'\n--- Relatório de Vendas ({data_inicio} a {data_fim}) ---')
        if not vendas:
            print('Nenhuma venda encontrada neste período.')
            return
        from src.dao.cliente_dao import ClienteDAO
        from src.dao.venda_item_dao import VendaItemDAO
        total_geral = sum((v.total for v in vendas))
        print(f'\nTotal de vendas: {len(vendas)}')
        print(f'Faturamento total: R$ {total_geral:.2f}')
        media = total_geral / len(vendas) if vendas else 0
        print(f'Ticket médio: R$ {media:.2f}\n')
        print(f"{'ID':<5} {'Data':<12} {'Cliente':<25} {'Total':<15} {'Status':<15}")
        print('-' * 80)
        for v in vendas:
            cli = ClienteDAO.listar_id(v.id_cliente)
            nome_cli = cli.nome if cli else 'Desconhecido'
            print(f'{v.id:<5} {v.data:<12} {nome_cli:<25} R$ {v.total:>12.2f}  {v.status:<15}')
            itens = VendaItemDAO.listar_por_venda(v.id)
            if itens:
                print(f"  {'Produto':<50} {'Qtd':<8} {'Unit':<12} {'Subtotal':<12}")
                for item in itens:
                    prod = ProdutoDAO.listar_id(item.id_produto)
                    subtotal = item.quantidade * item.valor_unitario
                    print(f'  {prod.descricao:<50} {item.quantidade:<8} R$ {item.valor_unitario:>8.2f}  R$ {subtotal:>10.2f}')
            print()

    @staticmethod
    def exibir_produtos_mais_vendidos(produtos):
        print('\n--- Produtos Mais Vendidos ---')
        if not produtos:
            print('Nenhum produto vendido.')
            return
        from src.dao.produto_dao import ProdutoDAO
        print(f"\n{'#':<3} {'Produto':<35} {'Qtd':<10} {'Faturamento':<15}")
        print('-' * 80)
        for i, (prod_id, dados) in enumerate(produtos, 1):
            prod = ProdutoDAO.listar_id(prod_id)
            nome = prod.descricao if prod else f'Produto {prod_id}'
            qtd = dados['quantidade']
            far = dados['faturamento']
            print(f'{i:<3} {nome:<35} {qtd:<10} R$ {far:>12.2f}')
            print(f'   - Faturamento: R$ {far:.2f}\n')

    @staticmethod
    def exibir_clientes_mais_ativos(clientes):
        print('\n--- Clientes Mais Ativos ---')
        if not clientes:
            print('Nenhum cliente encontrado.')
            return
        from src.dao.venda_dao import VendaDAO
        from src.dao.venda_item_dao import VendaItemDAO
        print(f"\n{'#':<3} {'Nome':<30} {'Email':<30} {'Total Gasto':<15} {'Compras':<10}")
        print('-' * 80)
        for i, (cli_id, dados) in enumerate(clientes, 1):
            nome = dados['nome']
            email = dados['email']
            total = dados['total_gasto']
            qtd_compras = dados['quantidade_compras']
            print(f'{i:<3} {nome:<30} {email:<30} R$ {total:>12.2f}  {qtd_compras:<10}')
            vendas = VendaDAO.listar()
            vendas_cliente = [v for v in vendas if v.id_cliente == cli_id]
            if vendas_cliente:
                produtos_comprados = {}
                for venda in vendas_cliente:
                    itens = VendaItemDAO.listar_por_venda(venda.id)
                    for item in itens:
                        prod = ProdutoDAO.listar_id(item.id_produto)
                        if prod.descricao not in produtos_comprados:
                            produtos_comprados[prod.descricao] = 0
                        produtos_comprados[prod.descricao] += item.quantidade
                print(f'  Produtos comprados:')
                for prod_nome, qtd in sorted(produtos_comprados.items()):
                    print(f'    • {prod_nome} ({qtd}x)')
            print()

    @staticmethod
    def exibir_faturamento_por_mes(faturamento_mes):
        print('\n--- Faturamento por Mês ---')
        if not faturamento_mes:
            print('Nenhum dado de faturamento encontrado.')
            return
        print(f"\n{'Mês':<15} {'Faturamento':<20} {'Vendas':<10}")
        print('-' * 80)
        total_geral = 0
        for mes in sorted(faturamento_mes.keys()):
            dados = faturamento_mes[mes]
            total = dados['total']
            qtd = dados['quantidade_vendas']
            print(f'{mes:<15} R$ {total:>15.2f}  {qtd:<10}')
            total_geral += total
        print('-' * 80)
        print(f"{'TOTAL GERAL':<15} R$ {total_geral:>15.2f}")

    @staticmethod
    def exibir_totais_relatorio(totais):
        print('\n--- Resumo ---')
        qtd_vendas = totais['quantidade_vendas']
        qtd_itens = totais['quantidade_itens']
        total = totais['total_geral']
        ticket = totais['ticket_medio']
        print(f'\nTotal de vendas: {qtd_vendas}')
        print(f'Total de itens: {qtd_itens}')
        print(f'Faturamento: R$ {total:.2f}')
        print(f'Ticket médio: R$ {ticket:.2f}')

    @staticmethod
    def exibir_categoria_mais_vendida(categoria):
        print('\n--- Categoria Mais Vendida ---')
        if not categoria:
            print('Nenhuma categoria vendida.')
            return
        cat_id = categoria['id']
        cat = CategoriaDAO.listar_id(cat_id)
        nome_cat = cat.descricao if cat else f'Categoria {cat_id}'
        far = categoria['faturamento']
        qtd = categoria['quantidade_vendas']
        print(f'\nCategoria: {nome_cat}')
        print(f'Faturamento: R$ {far:.2f}')
        print(f'Quantidade de vendas: {qtd}')

    @staticmethod
    def exibir_vendas_cliente_detalhado(cliente_id, cliente_nome):
        from src.dao.venda_dao import VendaDAO
        from src.dao.venda_item_dao import VendaItemDAO
        print(f'\n--- Compras Detalhadas - {cliente_nome} ---')
        vendas = VendaDAO.listar()
        vendas_cliente = [v for v in vendas if v.id_cliente == cliente_id]
        if not vendas_cliente:
            print('Este cliente não realizou nenhuma compra.')
            return
        total_cliente = sum((v.total for v in vendas_cliente))
        qtd_itens_total = 0
        print(f'\nTotal gasto: R$ {total_cliente:.2f}')
        print(f'Total de compras: {len(vendas_cliente)}\n')
        for idx, venda in enumerate(vendas_cliente, 1):
            print(f'Compra #{venda.id} | Data: {venda.data} | Status: {venda.status}')
            print(f"{'Produto':<50} {'Qtd':<8} {'Unit':<12} {'Subtotal':<12}")
            print('-' * 80)
            itens = VendaItemDAO.listar_por_venda(venda.id)
            venda_subtotal = 0
            for item in itens:
                prod = ProdutoDAO.listar_id(item.id_produto)
                subtotal = item.quantidade * item.valor_unitario
                venda_subtotal += subtotal
                qtd_itens_total += item.quantidade
                print(f'{prod.descricao:<50} {item.quantidade:<8} R$ {item.valor_unitario:>8.2f}  R$ {subtotal:>10.2f}')
            print(f"{'TOTAL DA COMPRA':<50} {'':<8} {'':<12} R$ {venda_subtotal:>10.2f}")
            print()
        print(f"{'RESUMO DO CLIENTE':-^82}")
        print(f'Total de itens comprados: {qtd_itens_total}')
        print(f'Total gasto: R$ {total_cliente:.2f}')
        print(f'Ticket médio: R$ {total_cliente / len(vendas_cliente):.2f}')
