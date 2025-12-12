from datetime import datetime
from src.dao.venda_dao import VendaDAO
from src.dao.venda_item_dao import VendaItemDAO
from src.dao.cliente_dao import ClienteDAO
from src.dao.produto_dao import ProdutoDAO
from src.dao.categoria_dao import CategoriaDAO

class RelatorioAvancado:

    @staticmethod
    def parse_data(data_str):
        try:
            return datetime.strptime(data_str, '%d/%m/%Y')
        except Exception:
            return None

    @staticmethod
    def vendas_por_periodo(data_inicio_str, data_fim_str):
        data_inicio = RelatorioAvancado.parse_data(data_inicio_str)
        data_fim = RelatorioAvancado.parse_data(data_fim_str)
        if not data_inicio or not data_fim:
            return []
        vendas = VendaDAO.listar()
        resultado = []
        for v in vendas:
            try:
                parts = v.data.split(' ')
                data_venda = RelatorioAvancado.parse_data(parts[0])
                if data_venda and data_inicio <= data_venda <= data_fim:
                    resultado.append(v)
            except Exception:
                pass
        return resultado

    @staticmethod
    def vendas_por_cliente(cliente_id):
        return VendaDAO.listar_por_cliente(cliente_id)

    @staticmethod
    def vendas_por_categoria(categoria_id):
        resultado = []
        vendas = VendaDAO.listar()
        for v in vendas:
            itens = VendaItemDAO.listar_por_venda(v.id)
            for item in itens:
                prod = ProdutoDAO.listar_id(item.id_produto)
                if prod and prod.id_categoria == categoria_id:
                    if v not in resultado:
                        resultado.append(v)
                    break
        return resultado

    @staticmethod
    def vendas_por_status(status):
        return [v for v in VendaDAO.listar() if v.status.lower() == status.lower()]

    @staticmethod
    def vendas_por_forma_pagamento(forma_pagamento):
        return [v for v in VendaDAO.listar() if v.forma_pagamento.lower() == forma_pagamento.lower()]

    @staticmethod
    def calcular_totais(vendas):
        total_geral = sum((v.total for v in vendas))
        qtd_vendas = len(vendas)
        qtd_itens = 0
        for v in vendas:
            itens = VendaItemDAO.listar_por_venda(v.id)
            qtd_itens += sum((item.quantidade for item in itens))
        return {'total_geral': total_geral, 'quantidade_vendas': qtd_vendas, 'quantidade_itens': qtd_itens, 'ticket_medio': total_geral / qtd_vendas if qtd_vendas > 0 else 0}

    @staticmethod
    def produtos_mais_vendidos(limite=10):
        vendas = VendaDAO.listar()
        vendas_por_produto = {}
        for v in vendas:
            itens = VendaItemDAO.listar_por_venda(v.id)
            for item in itens:
                if item.id_produto not in vendas_por_produto:
                    vendas_por_produto[item.id_produto] = {'quantidade': 0, 'faturamento': 0.0}
                vendas_por_produto[item.id_produto]['quantidade'] += item.quantidade
                vendas_por_produto[item.id_produto]['faturamento'] += item.quantidade * item.valor_unitario
        ordenados = sorted(vendas_por_produto.items(), key=lambda x: x[1]['quantidade'], reverse=True)
        return ordenados[:limite]

    @staticmethod
    def clientes_mais_ativos(limite=10):
        clientes = ClienteDAO.listar()
        clientes_por_gasto = {}
        for c in clientes:
            vendas = VendaDAO.listar_por_cliente(c.id)
            if vendas:
                total = sum((v.total for v in vendas))
                clientes_por_gasto[c.id] = {'nome': c.nome, 'email': c.email, 'total_gasto': total, 'quantidade_compras': len(vendas)}
        ordenados = sorted(clientes_por_gasto.items(), key=lambda x: x[1]['total_gasto'], reverse=True)
        return ordenados[:limite]

    @staticmethod
    def categoria_mais_vendida():
        categorias = CategoriaDAO.listar()
        categoria_faturamento = {}
        for cat in categorias:
            vendas = RelatorioAvancado.vendas_por_categoria(cat.id)
            total = sum((v.total for v in vendas))
            if total > 0:
                categoria_faturamento[cat.id] = {'nome': cat.descricao, 'faturamento': total, 'quantidade_vendas': len(vendas)}
        if not categoria_faturamento:
            return None
        melhor = max(categoria_faturamento.items(), key=lambda x: x[1]['faturamento'])
        return melhor

    @staticmethod
    def faturamento_por_mes():
        vendas = VendaDAO.listar()
        faturamento_mes = {}
        for v in vendas:
            try:
                parts = v.data.split(' ')
                data_parts = parts[0].split('/')
                mes_ano = f'{data_parts[1]}/{data_parts[2]}'
                if mes_ano not in faturamento_mes:
                    faturamento_mes[mes_ano] = {'total': 0.0, 'quantidade_vendas': 0}
                faturamento_mes[mes_ano]['total'] += v.total
                faturamento_mes[mes_ano]['quantidade_vendas'] += 1
            except Exception:
                pass
        return faturamento_mes
