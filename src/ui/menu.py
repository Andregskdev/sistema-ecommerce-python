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
from src.ui.view import View
from src.auth.admin_auth import AdminAuth
from src.utils.validador_duplicatas import ValidadorDuplicatas
from src.utils.filtro_produtos import FiltrodeProdutos
from src.dao.carrinho_dao import CarrinhoDAO
from src.utils.relatorio_avancado import RelatorioAvancado

class UI:
    carrinho = []
    cliente_atual_id = 0
    admin_atual = None

    @staticmethod
    def main():
        AdminAuth.criar_admin_padrao()
        ClienteDAO.abrir()
        CategoriaDAO.abrir()
        ProdutoDAO.abrir()
        VendaDAO.abrir()
        VendaItemDAO.abrir()
        CarrinhoDAO.abrir()
        resultado = ValidadorDuplicatas.limpar_todas_duplicatas()
        if resultado['total'] > 0:
            print(f'\n⚠️  DUPLICATAS REMOVIDAS:')
            print(f"   - Clientes: {resultado['clientes']}")
            print(f"   - Categorias: {resultado['categorias']}")
            print(f"   - Produtos: {resultado['produtos']}")
        while True:
            View.exibir_menu_principal()
            opcao = View.obter_entrada('Opção')
            if opcao == '1':
                UI.menu_cliente_principal()
            elif opcao == '2':
                UI.menu_admin_principal()
            elif opcao == '0':
                View.exibir_mensagem('Encerrando sistema...')
                break
            else:
                View.exibir_erro('Opção inválida.')

    @staticmethod
    def menu_cliente_principal():
        if UI.cliente_atual_id == 0:
            while True:
                View.exibir_mensagem('\n--- ACESSO CLIENTE ---')
                View.exibir_mensagem('1. Fazer Login')
                View.exibir_mensagem('2. Criar Novo Cadastro')
                View.exibir_mensagem('0. Voltar')
                opcao_acesso = View.obter_entrada('Opção')
                if opcao_acesso == '1':
                    UI.login_cliente()
                    if UI.cliente_atual_id != 0:
                        break
                elif opcao_acesso == '2':
                    UI.cadastro_cliente()
                    if UI.cliente_atual_id != 0:
                        break
                elif opcao_acesso == '0':
                    return
                else:
                    View.exibir_erro('Opção inválida.')
        while True:
            View.exibir_menu_cliente()
            op = View.obter_entrada(f'Opção (Logado: {UI.cliente_atual_id})')
            if op == '1':
                UI.listar_produtos_vitrine()
            elif op == '2':
                UI.adicionar_carrinho()
            elif op == '3':
                View.exibir_carrinho(UI.carrinho)
            elif op == '4':
                UI.finalizar_compra()
            elif op == '5':
                View.exibir_historico_compras(VendaDAO.listar_por_cliente(UI.cliente_atual_id))
            elif op == '6':
                UI.remover_do_carrinho()
            elif op == '7':
                UI.editar_perfil_cliente()
            elif op == '0':
                UI.cliente_atual_id = 0
                UI.carrinho = []
                break
            else:
                View.exibir_erro('Opção inválida.')

    @staticmethod
    def login_cliente():
        email = View.obter_entrada('Digite seu email')
        clientes = [c for c in ClienteDAO.listar() if c.email == email]
        if not clientes:
            View.exibir_erro('Cliente não encontrado!')
            return
        UI.cliente_atual_id = clientes[0].id
        try:
            UI.carrinho = CarrinhoDAO.get_cart(UI.cliente_atual_id)
        except Exception:
            UI.carrinho = []
        View.exibir_sucesso(f'Bem-vindo(a), {clientes[0].nome}!')

    @staticmethod
    def cadastro_cliente():
        try:
            View.exibir_mensagem('\n--- NOVO CADASTRO ---')
            clientes = ClienteDAO.listar()
            novo_id = ValidadorDuplicatas.obter_proximo_id(clientes)
            nome = View.obter_entrada('Nome completo')
            if not nome:
                View.exibir_erro('Nome não pode estar vazio.')
                return
            email = View.obter_entrada('Email')
            if not email or '@' not in email:
                View.exibir_erro('Email inválido.')
                return
            if not ValidadorDuplicatas.validar_email_unico(clientes, email):
                View.exibir_erro('Este email já está cadastrado!')
                return
            fone = View.obter_entrada('Telefone')
            if not fone:
                View.exibir_erro('Telefone não pode estar vazio.')
                return
            novo_cliente = Cliente(novo_id, nome, email, fone)
            ClienteDAO.inserir(novo_cliente)
            UI.cliente_atual_id = novo_id
            View.exibir_sucesso(f'Cadastro realizado com sucesso! Bem-vindo(a), {nome}!')
        except Exception as e:
            View.exibir_erro(f'Erro ao cadastrar: {str(e)}')

    @staticmethod
    def listar_produtos_vitrine():
        while True:
            View.exibir_categorias_disponiveis()
            id_cat = View.obter_entrada_numerica('Escolha uma categoria (0=Todas)')
            if id_cat is None:
                continue
            if id_cat != 0:
                cat = CategoriaDAO.listar_id(id_cat)
                if not cat:
                    View.exibir_erro('Categoria não encontrada!')
                    continue
            produtos = FiltrodeProdutos.obter_produtos_por_categoria(id_cat)
            if id_cat == 0:
                View.exibir_vitrine_produtos(produtos)
            else:
                View.exibir_vitrine_filtrada(produtos, id_cat)
            if not View.obter_confirmacao('Deseja filtrar outra categoria?'):
                break

    @staticmethod
    def adicionar_carrinho():
        UI.listar_produtos_vitrine()
        try:
            id_prod = View.obter_entrada_numerica('Digite o ID do produto para adicionar')
            if id_prod is None:
                return
            prod = ProdutoDAO.listar_id(id_prod)
            if not prod:
                View.exibir_erro('Produto não encontrado.')
                return
            if prod.estoque <= 0:
                View.exibir_erro('Produto esgotado!')
                return
            qtd = View.obter_entrada_numerica(f'Quantidade desejada (Máx {prod.estoque})')
            if qtd is None or qtd <= 0 or qtd > prod.estoque:
                View.exibir_erro('Quantidade inválida.')
                return
            item_existente = next((i for i in UI.carrinho if i.id_produto == id_prod), None)
            if item_existente:
                if item_existente.quantidade + qtd > prod.estoque:
                    View.exibir_erro('Estoque insuficiente para adicionar mais itens deste produto.')
                else:
                    item_existente.quantidade += qtd
                    View.exibir_sucesso('Quantidade atualizada no carrinho!')
                    if UI.cliente_atual_id != 0:
                        try:
                            CarrinhoDAO.salvar_cart(UI.cliente_atual_id, UI.carrinho)
                        except Exception:
                            pass
            else:
                novo_item = VendaItem(0, 0, id_prod, qtd, prod.preco)
                UI.carrinho.append(novo_item)
                View.exibir_sucesso('Produto adicionado ao carrinho!')
                if UI.cliente_atual_id != 0:
                    try:
                        CarrinhoDAO.salvar_cart(UI.cliente_atual_id, UI.carrinho)
                    except Exception:
                        pass
        except ValueError:
            View.exibir_erro('Digite apenas números.')

    @staticmethod
    def remover_do_carrinho():
        if not UI.carrinho:
            View.exibir_mensagem('Seu carrinho está vazio.')
            return
        View.exibir_mensagem('\n--- REMOVER / AJUSTAR ITEM DO CARRINHO ---')
        for item in UI.carrinho:
            prod = ProdutoDAO.listar_id(item.id_produto)
            nome = prod.descricao if prod else f'Produto {item.id_produto}'
            print(f'ID Produto: {item.id_produto} | {nome} | Quantidade: {item.quantidade}')
        id_prod = View.obter_entrada_numerica('Digite o ID do produto que deseja remover/ajustar')
        if id_prod is None:
            return
        item = next((i for i in UI.carrinho if i.id_produto == id_prod), None)
        if not item:
            View.exibir_erro('Produto não encontrado no carrinho.')
            return
        if View.obter_confirmacao('Deseja remover este item do carrinho?'):
            UI.carrinho.remove(item)
            View.exibir_sucesso('Item removido do carrinho.')
            if UI.cliente_atual_id != 0:
                if UI.carrinho:
                    CarrinhoDAO.salvar_cart(UI.cliente_atual_id, UI.carrinho)
                else:
                    CarrinhoDAO.delete_cart(UI.cliente_atual_id)
            return
        novo_qtd = View.obter_entrada_numerica('Digite a nova quantidade (0 para remover)')
        if novo_qtd is None:
            return
        if novo_qtd == 0:
            UI.carrinho.remove(item)
            View.exibir_sucesso('Item removido do carrinho.')
            if UI.cliente_atual_id != 0:
                if UI.carrinho:
                    CarrinhoDAO.salvar_cart(UI.cliente_atual_id, UI.carrinho)
                else:
                    CarrinhoDAO.delete_cart(UI.cliente_atual_id)
            return
        prod = ProdutoDAO.listar_id(item.id_produto)
        if prod and novo_qtd > prod.estoque:
            View.exibir_erro(f'Estoque insuficiente. Estoque atual: {prod.estoque}')
            return
        if novo_qtd < 0:
            View.exibir_erro('Quantidade inválida.')
            return
        item.quantidade = novo_qtd
        View.exibir_sucesso('Quantidade atualizada no carrinho.')
        if UI.cliente_atual_id != 0:
            try:
                CarrinhoDAO.salvar_cart(UI.cliente_atual_id, UI.carrinho)
            except Exception:
                pass

    @staticmethod
    def editar_perfil_cliente():
        if UI.cliente_atual_id == 0:
            View.exibir_erro('Nenhum cliente logado.')
            return
        c = ClienteDAO.listar_id(UI.cliente_atual_id)
        if not c:
            View.exibir_erro('Cliente não encontrado.')
            return
        View.exibir_mensagem('\n--- EDITAR PERFIL ---')
        novo_nome = View.obter_entrada(f'Nome ({c.nome})') or c.nome
        novo_email = View.obter_entrada(f'Email ({c.email})') or c.email
        if novo_email != c.email:
            if '@' not in novo_email:
                View.exibir_erro('Email inválido.')
                return
            outros = [cl for cl in ClienteDAO.listar() if cl.id != c.id]
            if not ValidadorDuplicatas.validar_email_unico(outros, novo_email):
                View.exibir_erro('Este email já está em uso por outro cliente.')
                return
        novo_fone = View.obter_entrada(f'Fone ({c.fone})') or c.fone
        c.nome = novo_nome
        c.email = novo_email
        c.fone = novo_fone
        ClienteDAO.atualizar(c)
        View.exibir_sucesso('Perfil atualizado com sucesso.')

    @staticmethod
    def finalizar_compra():
        total = View.exibir_carrinho(UI.carrinho)
        if not UI.carrinho:
            return
        if not View.obter_confirmacao('Deseja confirmar a compra?'):
            return
        forma_pgto = View.obter_entrada('Forma de Pagamento (Pix/Cartão/Boleto)')
        novo_id_venda = VendaDAO.get_proximo_id()
        venda = Venda(novo_id_venda, UI.cliente_atual_id, None, total, forma_pgto, 'Confirmada')
        VendaDAO.inserir(venda)
        prox_id_item = VendaItemDAO.get_proximo_id()
        for item in UI.carrinho:
            item.id = prox_id_item
            item.id_venda = novo_id_venda
            VendaItemDAO.inserir(item)
            prox_id_item += 1
            prod = ProdutoDAO.listar_id(item.id_produto)
            if prod:
                prod.estoque -= item.quantidade
                ProdutoDAO.atualizar(prod)
        View.exibir_sucesso('Compra realizada com sucesso!')
        try:
            CarrinhoDAO.delete_cart(UI.cliente_atual_id)
        except Exception:
            pass
        UI.carrinho = []

    @staticmethod
    def menu_admin_principal():
        if UI.admin_atual is None:
            if not UI.login_admin():
                return
        while True:
            View.exibir_mensagem(f'\n--- PAINEL ADMINISTRADOR (Logado: {UI.admin_atual}) ---')
            View.exibir_mensagem('1. Gerenciar Clientes')
            View.exibir_mensagem('2. Gerenciar Categorias')
            View.exibir_mensagem('3. Gerenciar Produtos')
            View.exibir_mensagem('4. Relatório de Todas as Vendas')
            View.exibir_mensagem('5. Gerenciar Admins')
            View.exibir_mensagem('6. Relatórios Avançados')
            View.exibir_mensagem('0. Logout')
            op = View.obter_entrada('Opção')
            if op == '1':
                UI.menu_crud_cliente()
            elif op == '2':
                UI.menu_crud_categoria()
            elif op == '3':
                UI.menu_crud_produto()
            elif op == '4':
                UI.relatorio_vendas()
            elif op == '5':
                UI.menu_gerenciar_admins()
            elif op == '6':
                UI.menu_relatorios_avancados()
            elif op == '0':
                UI.admin_atual = None
                View.exibir_sucesso('Deslogado do painel de admin.')
                break
            else:
                View.exibir_erro('Opção inválida.')

    @staticmethod
    def login_admin():
        try:
            View.exibir_mensagem('\n--- LOGIN ADMINISTRADOR ---')
            usuario = View.obter_entrada('Usuário')
            senha = View.obter_senha('Senha')
            if AdminAuth.autenticar(usuario, senha):
                UI.admin_atual = usuario
                View.exibir_sucesso(f'Bem-vindo, {usuario}!')
                return True
            else:
                View.exibir_erro('Usuário ou senha incorretos!')
                return False
        except Exception as e:
            View.exibir_erro(f'Erro na autenticação: {str(e)}')
            return False

    @staticmethod
    def menu_gerenciar_admins():
        while True:
            View.exibir_mensagem('\n-- GERENCIAR ADMINS --')
            View.exibir_mensagem('1. Listar Admins')
            View.exibir_mensagem('2. Criar Novo Admin')
            View.exibir_mensagem('3. Alterar Minha Senha')
            View.exibir_mensagem('0. Voltar')
            op = View.obter_entrada('Opção')
            if op == '1':
                admins = AdminAuth.listar_admins()
                View.exibir_mensagem('\n--- ADMINS DO SISTEMA ---')
                for admin in admins:
                    print(f"   - {admin['usuario']}")
            elif op == '2':
                novo_usuario = View.obter_entrada('Novo usuário admin')
                if not novo_usuario:
                    View.exibir_erro('Usuário não pode estar vazio.')
                    continue
                nova_senha = View.obter_senha('Senha do novo admin')
                if not nova_senha or len(nova_senha) < 4:
                    View.exibir_erro('Senha deve ter pelo menos 4 caracteres.')
                    continue
                sucesso, mensagem = AdminAuth.criar_novo_admin(novo_usuario, nova_senha)
                if sucesso:
                    View.exibir_sucesso(mensagem)
                else:
                    View.exibir_erro(mensagem)
            elif op == '3':
                senha_atual = View.obter_senha('Digite sua senha atual')
                nova_senha = View.obter_senha('Digite a nova senha')
                if not nova_senha or len(nova_senha) < 4:
                    View.exibir_erro('Senha deve ter pelo menos 4 caracteres.')
                    continue
                sucesso, mensagem = AdminAuth.alterar_senha(UI.admin_atual, senha_atual, nova_senha)
                if sucesso:
                    View.exibir_sucesso(mensagem)
                else:
                    View.exibir_erro(mensagem)
            elif op == '0':
                break
            else:
                View.exibir_erro('Opção inválida.')

    @staticmethod
    def relatorio_vendas():
        View.exibir_mensagem('--- RELATÓRIO GERAL DE VENDAS (ADMIN) ---')
        vendas = VendaDAO.listar()
        if not vendas:
            View.exibir_mensagem('Nenhuma venda registrada no sistema.')
            return
        for v in vendas:
            cli = ClienteDAO.listar_id(v.id_cliente)
            nome_cli = cli.nome if cli else 'Desconhecido'
            print(f'ID: {v.id} | Data: {v.data} | Cli: {nome_cli} | R$ {v.total:.2f} | {v.forma_pagamento}')
        if View.obter_confirmacao('Deseja alterar o status de alguma venda?'):
            id_venda = View.obter_entrada_numerica('ID da venda para alterar')
            if id_venda is None:
                return
            venda = VendaDAO.listar_id(id_venda) if hasattr(VendaDAO, 'listar_id') else next((x for x in VendaDAO.listar() if x.id == id_venda), None)
            if not venda:
                View.exibir_erro('Venda não encontrada.')
                return
            print(f'Venda atual - ID: {venda.id} | Status: {venda.status}')
            novo_status = View.obter_entrada('Novo status (Confirmada/Pendente/Cancelada)')
            if not novo_status:
                View.exibir_erro('Status inválido.')
                return
            venda.status = novo_status
            VendaDAO.atualizar(venda)
            View.exibir_sucesso('Status da venda atualizado.')

    @staticmethod
    def menu_crud_cliente():
        View.exibir_mensagem('-- GERENCIAR CLIENTES --')
        View.exibir_mensagem('1. Listar | 2. Inserir | 3. Atualizar | 4. Excluir')
        op = View.obter_entrada('Opção')
        if op == '1':
            for c in ClienteDAO.listar():
                print(c)
        elif op == '2':
            try:
                clientes = ClienteDAO.listar()
                novo_id = ValidadorDuplicatas.obter_proximo_id(clientes)
                nome = View.obter_entrada('Nome')
                email = View.obter_entrada('Email')
                if not email or '@' not in email:
                    View.exibir_erro('Email inválido.')
                    return
                if not ValidadorDuplicatas.validar_email_unico(clientes, email):
                    View.exibir_erro('Este email já existe no sistema!')
                    return
                fone = View.obter_entrada('Fone')
                c = Cliente(novo_id, nome, email, fone)
                ClienteDAO.inserir(c)
                View.exibir_sucesso('Cliente salvo!')
            except ValueError:
                View.exibir_erro('Erro nos valores.')
        elif op == '3':
            id = View.obter_entrada_numerica('ID para alterar')
            if id is None:
                return
            c = ClienteDAO.listar_id(id)
            if c:
                c.nome = View.obter_entrada(f'Nome ({c.nome})') or c.nome
                novo_email = View.obter_entrada(f'Email ({c.email})')
                if novo_email:
                    if '@' not in novo_email:
                        View.exibir_erro('Email inválido.')
                        return
                    clientes = [cl for cl in ClienteDAO.listar() if cl.id != id]
                    if not ValidadorDuplicatas.validar_email_unico(clientes, novo_email):
                        View.exibir_erro('Este email já está em uso por outro cliente!')
                        return
                    c.email = novo_email
                c.fone = View.obter_entrada(f'Fone ({c.fone})') or c.fone
                ClienteDAO.atualizar(c)
                View.exibir_sucesso('Cliente atualizado.')
            else:
                View.exibir_erro('Cliente não encontrado.')
        elif op == '4':
            id = View.obter_entrada_numerica('ID para excluir')
            if id is None:
                return
            c = ClienteDAO.listar_id(id)
            if c:
                ClienteDAO.excluir(c)
                View.exibir_sucesso('Cliente removido.')
            else:
                View.exibir_erro('Cliente não encontrado.')

    @staticmethod
    def menu_crud_categoria():
        View.exibir_mensagem('-- GERENCIAR CATEGORIAS --')
        View.exibir_mensagem('1. Listar | 2. Inserir | 3. Atualizar | 4. Excluir')
        op = View.obter_entrada('Opção')
        if op == '1':
            for c in CategoriaDAO.listar():
                print(c)
        elif op == '2':
            try:
                categorias = CategoriaDAO.listar()
                novo_id = ValidadorDuplicatas.obter_proximo_id(categorias)
                descricao = View.obter_entrada('Descrição')
                if not ValidadorDuplicatas.validar_descricao_categoria_unica(categorias, descricao):
                    View.exibir_erro('Esta categoria já existe!')
                    return
                c = Categoria(novo_id, descricao)
                CategoriaDAO.inserir(c)
                View.exibir_sucesso('Categoria salva!')
            except ValueError:
                View.exibir_erro('Erro nos valores.')
        elif op == '3':
            id = View.obter_entrada_numerica('ID para alterar')
            if id is None:
                return
            c = CategoriaDAO.listar_id(id)
            if c:
                nova_desc = View.obter_entrada(f'Descrição ({c.descricao})')
                if nova_desc:
                    categorias = [cat for cat in CategoriaDAO.listar() if cat.id != id]
                    if not ValidadorDuplicatas.validar_descricao_categoria_unica(categorias, nova_desc):
                        View.exibir_erro('Esta descrição já está em uso!')
                        return
                    c.descricao = nova_desc
                CategoriaDAO.atualizar(c)
                View.exibir_sucesso('Categoria atualizada.')
            else:
                View.exibir_erro('Categoria não encontrada.')
        elif op == '4':
            id = View.obter_entrada_numerica('ID para excluir')
            if id is None:
                return
            c = CategoriaDAO.listar_id(id)
            if c:
                CategoriaDAO.excluir(c)
                View.exibir_sucesso('Categoria removida.')
            else:
                View.exibir_erro('Categoria não encontrada.')

    @staticmethod
    def menu_crud_produto():
        View.exibir_mensagem('-- GERENCIAR PRODUTOS --')
        View.exibir_mensagem('1. Listar | 2. Inserir | 3. Atualizar | 4. Excluir')
        op = View.obter_entrada('Opção')
        if op == '1':
            for p in ProdutoDAO.listar():
                cat = CategoriaDAO.listar_id(p.id_categoria)
                cat_nome = cat.descricao if cat else 'Sem Categoria'
                print(f'{p} [Categoria: {cat_nome}]')
        elif op == '2':
            try:
                produtos = ProdutoDAO.listar()
                novo_id = ValidadorDuplicatas.obter_proximo_id(produtos)
                desc = View.obter_entrada('Descrição')
                preco = float(View.obter_entrada('Preço'))
                estoque = View.obter_entrada_numerica('Estoque')
                if estoque is None:
                    return
                View.exibir_mensagem('\nCategorias disponíveis:')
                for cat in CategoriaDAO.listar():
                    print(cat)
                id_cat = View.obter_entrada_numerica('ID da Categoria')
                if id_cat is None:
                    return
                p = Produto(novo_id, desc, preco, estoque, id_cat)
                ProdutoDAO.inserir(p)
                View.exibir_sucesso('Produto salvo!')
            except ValueError:
                View.exibir_erro('Erro nos valores numéricos.')
        elif op == '3':
            id = View.obter_entrada_numerica('ID para alterar')
            if id is None:
                return
            p = ProdutoDAO.listar_id(id)
            if p:
                p.descricao = View.obter_entrada(f'Descrição ({p.descricao})') or p.descricao
                novo_preco = View.obter_entrada(f'Preço ({p.preco})')
                if novo_preco:
                    p.preco = float(novo_preco)
                novo_estoque = View.obter_entrada(f'Estoque ({p.estoque})')
                if novo_estoque:
                    p.estoque = int(novo_estoque)
                nova_cat = View.obter_entrada(f'ID Categoria ({p.id_categoria})')
                if nova_cat:
                    p.id_categoria = int(nova_cat)
                ProdutoDAO.atualizar(p)
                View.exibir_sucesso('Produto atualizado.')
            else:
                View.exibir_erro('Produto não encontrado.')
        elif op == '4':
            id = View.obter_entrada_numerica('ID para excluir')
            if id is None:
                return
            p = ProdutoDAO.listar_id(id)
            if p:
                ProdutoDAO.excluir(p)
                View.exibir_sucesso('Produto removido.')
            else:
                View.exibir_erro('Produto não encontrado.')

    @staticmethod
    def menu_relatorios_avancados():
        while True:
            print('\n--- RELATÓRIOS AVANÇADOS ---')
            print('1. Vendas por Período')
            print('2. Vendas por Cliente')
            print('3. Vendas por Categoria')
            print('4. Vendas por Status')
            print('5. Produtos Mais Vendidos')
            print('6. Clientes Mais Ativos')
            print('7. Categoria Mais Vendida')
            print('8. Faturamento por Mês')
            print('0. Voltar')
            op = View.obter_entrada('Opção')
            if op == '1':
                data_inicio = View.obter_entrada('Data início (DD/MM/YYYY)')
                data_fim = View.obter_entrada('Data fim (DD/MM/YYYY)')
                try:
                    vendas = RelatorioAvancado.vendas_por_periodo(data_inicio, data_fim)
                    if vendas:
                        totais = RelatorioAvancado.calcular_totais(vendas)
                        View.exibir_relatorio_periodo(vendas, data_inicio, data_fim)
                        View.exibir_totais_relatorio(totais)
                    else:
                        View.exibir_mensagem('Nenhuma venda encontrada neste período.')
                except Exception as e:
                    View.exibir_erro(f'Erro ao gerar relatório: {str(e)}')
            elif op == '2':
                id_cliente = View.obter_entrada_numerica('ID do cliente')
                if id_cliente is None:
                    continue
                cliente = ClienteDAO.listar_id(id_cliente)
                if not cliente:
                    View.exibir_erro('Cliente não encontrado.')
                    continue
                View.exibir_vendas_cliente_detalhado(id_cliente, cliente.nome)
            elif op == '3':
                id_categoria = View.obter_entrada_numerica('ID da categoria')
                if id_categoria is None:
                    continue
                categoria = CategoriaDAO.listar_id(id_categoria)
                if not categoria:
                    View.exibir_erro('Categoria não encontrada.')
                    continue
                vendas = RelatorioAvancado.vendas_por_categoria(id_categoria)
                if vendas:
                    print(f'\n--- Vendas - Categoria: {categoria.descricao} ---')
                    totais = RelatorioAvancado.calcular_totais(vendas)
                    print(f'\nTotal de vendas: {len(vendas)}')
                    print(f"Faturamento total: R$ {totais['total_geral']:.2f}")
                    print(f"Ticket médio: R$ {totais['ticket_medio']:.2f}\n")
                    print(f"{'ID':<5} {'Data':<12} {'Cliente':<25} {'Total':<15}")
                    print('-' * 60)
                    for v in vendas:
                        cli = ClienteDAO.listar_id(v.id_cliente)
                        nome_cli = cli.nome if cli else 'Desconhecido'
                        print(f'{v.id:<5} {v.data:<12} {nome_cli:<25} R$ {v.total:>12.2f}')
                        from src.dao.venda_item_dao import VendaItemDAO
                        itens = VendaItemDAO.listar_por_venda(v.id)
                        for item in itens:
                            prod = ProdutoDAO.listar_id(item.id_produto)
                            if prod.id_categoria == id_categoria:
                                subtotal = item.quantidade * item.valor_unitario
                                print(f'   • {prod.descricao} ({item.quantidade}x) = R$ {subtotal:.2f}')
                        print()
                else:
                    View.exibir_mensagem('Nenhuma venda encontrada nesta categoria.')
            elif op == '4':
                status = View.obter_entrada('Status da venda (ex: Pendente, Confirmada, Entregue)')
                vendas = RelatorioAvancado.vendas_por_status(status)
                if vendas:
                    print(f'\n--- VENDAS COM STATUS: {status} ---')
                    totais = RelatorioAvancado.calcular_totais(vendas)
                    View.exibir_totais_relatorio(totais)
                    for v in vendas:
                        cli = ClienteDAO.listar_id(v.id_cliente)
                        nome_cli = cli.nome if cli else 'Desconhecido'
                        print(f'ID: {v.id} | Data: {v.data} | Cliente: {nome_cli} | Total: R$ {v.total:.2f}')
                else:
                    View.exibir_mensagem(f"Nenhuma venda com status '{status}'.")
            elif op == '5':
                limite = View.obter_entrada_numerica('Limite de produtos (padrão 10)')
                if limite is None:
                    limite = 10
                produtos = RelatorioAvancado.produtos_mais_vendidos(limite)
                View.exibir_produtos_mais_vendidos(produtos)
            elif op == '6':
                limite = View.obter_entrada_numerica('Limite de clientes (padrão 10)')
                if limite is None:
                    limite = 10
                clientes = RelatorioAvancado.clientes_mais_ativos(limite)
                View.exibir_clientes_mais_ativos(clientes)
            elif op == '7':
                categoria = RelatorioAvancado.categoria_mais_vendida()
                View.exibir_categoria_mais_vendida(categoria)
            elif op == '8':
                faturamento = RelatorioAvancado.faturamento_por_mes()
                View.exibir_faturamento_por_mes(faturamento)
            elif op == '0':
                break
            else:
                View.exibir_erro('Opção inválida.')
