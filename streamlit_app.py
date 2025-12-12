import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(__file__))
import streamlit as st
from src.dao.produto_dao import ProdutoDAO
from src.dao.categoria_dao import CategoriaDAO
from src.dao.cliente_dao import ClienteDAO
from src.dao.venda_dao import VendaDAO
from src.dao.venda_item_dao import VendaItemDAO
from src.dao.carrinho_dao import CarrinhoDAO
from src.utils.relatorio_avancado import RelatorioAvancado
from src.utils.validador_duplicatas import ValidadorDuplicatas
from src.models.cliente import Cliente
from src.models.produto import Produto
from src.models.categoria import Categoria
from src.models.venda import Venda
from src.models.venda_item import VendaItem

def carregar_dados():
    ProdutoDAO.abrir()
    CategoriaDAO.abrir()
    ClienteDAO.abrir()
    VendaDAO.abrir()
    VendaItemDAO.abrir()
    CarrinhoDAO.abrir()

def inicializar_sessao():
    if 'cliente_logado' not in st.session_state:
        st.session_state.cliente_logado = None
    if 'cart' not in st.session_state:
        st.session_state.cart = {}
    if 'admin_logado' not in st.session_state:
        st.session_state.admin_logado = False

def tela_login_cliente():
    st.title('Login - Cliente')
    col1, col2 = st.columns(2)
    with col1:
        email = st.text_input('Email')
    with col2:
        acao = st.radio('Acao', ['Entrar', 'Cadastrar'], label_visibility='collapsed')
    if acao == 'Entrar':
        if st.button('Login', key='login_btn'):
            clientes = [c for c in ClienteDAO.listar() if c.email == email]
            if clientes:
                st.session_state.cliente_logado = clientes[0]
                st.success(f'Bem-vindo, {clientes[0].nome}!')
                st.rerun()
            else:
                st.error('Cliente não encontrado')
    else:
        nome = st.text_input('Nome')
        fone = st.text_input('Telefone')
        if st.button('Cadastrar', key='cadastro_btn'):
            if ValidadorDuplicatas.validar_email_unico(email):
                novo_id = max([c.id for c in ClienteDAO.listar()], default=0) + 1
                novo_cliente = Cliente(novo_id, nome, email, fone)
                ClienteDAO.inserir(novo_cliente)
                st.success('Cliente cadastrado com sucesso!')
                st.rerun()
            else:
                st.error('Email já existe')

def tela_login_admin():
    st.title('Login - Admin')
    senha = st.text_input('Senha', type='password')
    if st.button('Login Admin', key='admin_login_btn'):
        from src.auth.admin_auth import AdminAuth
        if AdminAuth.verificar_senha(senha):
            st.session_state.admin_logado = True
            st.success('Login de admin realizado!')
            st.rerun()
        else:
            st.error('Senha de admin inválida')

def menu_cliente():
    st.sidebar.write(f'**Logado como:** {st.session_state.cliente_logado.nome}')
    if st.sidebar.button('Logout'):
        st.session_state.cliente_logado = None
        st.rerun()
    opcao = st.sidebar.selectbox('Menu Cliente', ['Vitrine', 'Carrinho', 'Histórico de Compras'])
    if opcao == 'Vitrine':
        tela_vitrine_cliente()
    elif opcao == 'Carrinho':
        tela_carrinho_cliente()
    elif opcao == 'Histórico de Compras':
        tela_historico_cliente()

def tela_vitrine_cliente():
    st.header('Vitrine de Produtos')
    produtos = ProdutoDAO.listar()
    categorias = {c.id: c.descricao for c in CategoriaDAO.listar()}
    cat_filtro = st.selectbox('Filtrar por categoria', ['-'] + [c.descricao for c in CategoriaDAO.listar()])
    if cat_filtro != '-':
        cat_id = next((c.id for c in CategoriaDAO.listar() if c.descricao == cat_filtro))
        produtos = [p for p in produtos if p.id_categoria == cat_id]
    for p in produtos:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.write(f'**{p.descricao}**')
        with col2:
            st.write(f'Preço: R$ {p.preco:.2f} | Estoque: {p.estoque}')
        with col3:
            qtd = st.number_input(f'Qtd_{p.id}', min_value=1, max_value=p.estoque or 999, value=1, key=f'q_{p.id}')
            if st.button('Adicionar', key=f'add_{p.id}'):
                cart = st.session_state.cart
                cart[str(p.id)] = cart.get(str(p.id), 0) + int(qtd)
                st.session_state.cart = cart
                st.success(f'{p.descricao} adicionado ao carrinho')

def tela_carrinho_cliente():
    st.header('Carrinho')
    cart = st.session_state.cart
    if not cart:
        st.info('Carrinho vazio')
        return
    tabela = []
    total = 0.0
    for pid_str, qty in cart.items():
        pid = int(pid_str)
        p = next((x for x in ProdutoDAO.listar() if x.id == pid), None)
        if not p:
            continue
        subtotal = float(p.preco) * int(qty)
        total += subtotal
        tabela.append({'ID': p.id, 'Produto': p.descricao, 'Qtd': qty, 'Preço': f'R$ {p.preco:.2f}', 'Subtotal': f'R$ {subtotal:.2f}'})
    st.dataframe(tabela)
    st.write(f'**Total: R$ {total:.2f}**')
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Finalizar Compra'):
            novo_id_venda = max([v.id for v in VendaDAO.listar()], default=0) + 1
            venda = Venda(novo_id_venda, st.session_state.cliente_logado.id, datetime.now().strftime('%d/%m/%Y %H:%M'), total, 'PIX', 'Pendente')
            VendaDAO.inserir(venda)
            for pid_str, qty in cart.items():
                pid = int(pid_str)
                p = next((x for x in ProdutoDAO.listar() if x.id == pid), None)
                if not p:
                    continue
                novo_id_item = max([it.id for it in VendaItemDAO.listar()], default=0) + 1
                item = VendaItem(novo_id_item, novo_id_venda, pid, int(qty), float(p.preco))
                VendaItemDAO.inserir(item)
            st.session_state.cart = {}
            st.success(f'Compra #{novo_id_venda} finalizada com sucesso!')
    with col2:
        if st.button('Limpar Carrinho'):
            st.session_state.cart = {}
            st.rerun()

def tela_historico_cliente():
    st.header('Histórico de Compras')
    cliente_id = st.session_state.cliente_logado.id
    vendas = VendaDAO.listar_por_cliente(cliente_id)
    if not vendas:
        st.info('Nenhuma compra realizada')
        return
    for v in vendas:
        with st.expander(f'Pedido #{v.id} - {v.data} - R$ {v.total:.2f}'):
            itens = VendaItemDAO.listar_por_venda(v.id)
            for item in itens:
                p = next((x for x in ProdutoDAO.listar() if x.id == item.id_produto), None)
                st.write(f"- {(p.descricao if p else 'Produto')}: {item.quantidade}x R$ {item.valor_unitario:.2f}")
            st.write(f'**Status:** {v.status} | **Pagamento:** {v.forma_pagamento}')

def menu_admin():
    st.sidebar.write('**Modo Admin**')
    if st.sidebar.button('Logout Admin'):
        st.session_state.admin_logado = False
        st.rerun()
    opcao = st.sidebar.selectbox('Menu Admin', ['Dashboard', 'Produtos', 'Categorias', 'Clientes', 'Vendas', 'Relatórios'])
    if opcao == 'Dashboard':
        tela_dashboard_admin()
    elif opcao == 'Produtos':
        tela_produtos_admin()
    elif opcao == 'Categorias':
        tela_categorias_admin()
    elif opcao == 'Clientes':
        tela_clientes_admin()
    elif opcao == 'Vendas':
        tela_vendas_admin()
    elif opcao == 'Relatórios':
        tela_relatorios_admin()

def tela_dashboard_admin():
    st.title('Dashboard Admin')
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric('Total de Produtos', len(ProdutoDAO.listar()))
    with col2:
        st.metric('Total de Clientes', len(ClienteDAO.listar()))
    with col3:
        st.metric('Total de Vendas', len(VendaDAO.listar()))

def tela_produtos_admin():
    st.title('Gerenciar Produtos')
    tab1, tab2 = st.tabs(['Listar', 'Adicionar/Editar'])
    with tab1:
        produtos = ProdutoDAO.listar()
        for p in produtos:
            with st.expander(f'{p.descricao} (ID: {p.id})'):
                st.write(f'Preço: R$ {p.preco:.2f}')
                st.write(f'Estoque: {p.estoque}')
                st.write(f'Categoria ID: {p.id_categoria}')
                if st.button(f'Deletar {p.id}', key=f'del_p_{p.id}'):
                    ProdutoDAO.deletar(p.id)
                    st.success('Produto deletado!')
                    st.rerun()
    with tab2:
        st.subheader('Novo Produto')
        descricao = st.text_input('Descrição')
        preco = st.number_input('Preço', min_value=0.0, step=0.01)
        estoque = st.number_input('Estoque', min_value=0, step=1)
        cat_id = st.number_input('ID Categoria', min_value=1, step=1)
        if st.button('Adicionar Produto'):
            novo_id = max([p.id for p in ProdutoDAO.listar()], default=0) + 1
            novo = Produto(novo_id, descricao, preco, estoque, cat_id)
            ProdutoDAO.inserir(novo)
            st.success('Produto adicionado!')
            st.rerun()

def tela_categorias_admin():
    st.title('Gerenciar Categorias')
    tab1, tab2 = st.tabs(['Listar', 'Adicionar'])
    with tab1:
        cats = CategoriaDAO.listar()
        for c in cats:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f'**{c.descricao}** (ID: {c.id})')
            with col2:
                if st.button(f'Del', key=f'del_c_{c.id}'):
                    CategoriaDAO.deletar(c.id)
                    st.success('Categoria deletada!')
                    st.rerun()
    with tab2:
        st.subheader('Nova Categoria')
        descricao = st.text_input('Descrição da Categoria')
        if st.button('Adicionar Categoria'):
            novo_id = max([c.id for c in CategoriaDAO.listar()], default=0) + 1
            nova = Categoria(novo_id, descricao)
            CategoriaDAO.inserir(nova)
            st.success('Categoria adicionada!')
            st.rerun()

def tela_clientes_admin():
    st.title('Gerenciar Clientes')
    clientes = ClienteDAO.listar()
    for c in clientes:
        with st.expander(f'{c.nome} ({c.email})'):
            st.write(f'ID: {c.id}')
            st.write(f'Telefone: {c.fone}')
            if st.button(f'Deletar {c.id}', key=f'del_cl_{c.id}'):
                ClienteDAO.deletar(c.id)
                st.success('Cliente deletado!')
                st.rerun()

def tela_vendas_admin():
    st.title('Gerenciar Vendas')
    vendas = VendaDAO.listar()
    for v in vendas:
        cliente = next((c for c in ClienteDAO.listar() if c.id == v.id_cliente), None)
        nome_cliente = cliente.nome if cliente else 'Desconhecido'
        with st.expander(f'Venda #{v.id} - {nome_cliente} - R$ {v.total:.2f}'):
            st.write(f'Data: {v.data}')
            st.write(f'Status: {v.status}')
            st.write(f'Pagamento: {v.forma_pagamento}')
            novo_status = st.selectbox('Novo Status', ['Pendente', 'Confirmada', 'Enviada', 'Entregue', 'Cancelada'], index=['Pendente', 'Confirmada', 'Enviada', 'Entregue', 'Cancelada'].index(v.status), key=f'status_{v.id}')
            if st.button(f'Atualizar Status', key=f'upd_status_{v.id}'):
                v.status = novo_status
                VendaDAO.atualizar(v)
                st.success('Status atualizado!')
                st.rerun()

def tela_relatorios_admin():
    st.title('Relatórios Avançados')
    rel_tipo = st.selectbox('Tipo de Relatório', ['Produtos Mais Vendidos', 'Clientes Mais Ativos', 'Faturamento por Mês', 'Vendas por Período', 'Vendas por Categoria'])
    if rel_tipo == 'Produtos Mais Vendidos':
        top = RelatorioAvancado.produtos_mais_vendidos(10)
        if top:
            rows = []
            for pid, info in top:
                p = next((x for x in ProdutoDAO.listar() if x.id == pid), None)
                rows.append({'Produto': p.descricao if p else '-', 'Qtd': info['quantidade'], 'Faturamento': f"R$ {info['faturamento']:.2f}"})
            st.dataframe(rows)
        else:
            st.info('Sem dados')
    elif rel_tipo == 'Clientes Mais Ativos':
        ativos = RelatorioAvancado.clientes_mais_ativos(10)
        if ativos:
            rows = []
            for cid, info in ativos:
                rows.append({'Cliente': info['nome'], 'Email': info['email'], 'Total Gasto': f"R$ {info['total_gasto']:.2f}", 'Compras': info['quantidade_compras']})
            st.dataframe(rows)
        else:
            st.info('Sem dados')
    elif rel_tipo == 'Faturamento por Mês':
        fatur = RelatorioAvancado.faturamento_por_mes()
        if fatur:
            rows = [{'Mês': k, 'Total': f"R$ {v['total']:.2f}", 'Vendas': v['quantidade_vendas']} for k, v in fatur.items()]
            st.dataframe(rows)
        else:
            st.info('Sem dados')
    elif rel_tipo == 'Vendas por Período':
        data_ini = st.date_input('Data Inicial')
        data_fim = st.date_input('Data Final')
        if st.button('Gerar Relatório'):
            vendas = RelatorioAvancado.vendas_por_periodo(data_ini.strftime('%d/%m/%Y'), data_fim.strftime('%d/%m/%Y'))
            if vendas:
                total = sum((v.total for v in vendas))
                st.write(f'**{len(vendas)} vendas | Total: R$ {total:.2f}**')
            else:
                st.info('Sem vendas neste período')
    elif rel_tipo == 'Vendas por Categoria':
        cat = st.selectbox('Selecione Categoria', [c.descricao for c in CategoriaDAO.listar()])
        if cat:
            cat_id = next((c.id for c in CategoriaDAO.listar() if c.descricao == cat))
            vendas = RelatorioAvancado.vendas_por_categoria(cat_id)
            if vendas:
                total = sum((v.total for v in vendas))
                st.write(f'**{len(vendas)} vendas | Total: R$ {total:.2f}**')
            else:
                st.info('Sem vendas nesta categoria')

def main():
    st.set_page_config(page_title='E-commerce', layout='wide')
    carregar_dados()
    inicializar_sessao()
    if st.sidebar.button('Admin'):
        st.session_state.admin_logado = True
        st.rerun()
    if st.session_state.admin_logado:
        if st.sidebar.button('Modo Cliente'):
            st.session_state.admin_logado = False
            st.rerun()
        menu_admin()
    elif st.session_state.cliente_logado:
        menu_cliente()
    else:
        col1, col2 = st.columns(2)
        with col1:
            tela_login_cliente()
        with col2:
            tela_login_admin()
if __name__ == '__main__':
    main()
