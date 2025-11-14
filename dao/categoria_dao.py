import json, os
from models.categoria import Categoria

class CategoriaDAO:
    arquivo = 'categorias.json'
    lista = []
    proximo_id = 1

    @classmethod
    def inserir(cls, categoria: Categoria):
        """Insere uma nova categoria e define ID automaticamente."""
        categoria.set_id(cls.proximo_id)
        cls.lista.append(categoria)
        cls.proximo_id += 1
        return categoria

    @classmethod
    def listar(cls):
        """Retorna todas as categorias em memória."""
        return cls.lista

    @classmethod
    def listar_id(cls, id):
        """Retorna uma categoria pelo seu ID."""
        return next((c for c in cls.lista if c.get_id() == id), None)

    @classmethod
    def atualizar(cls, categoria):
        """Atualiza uma categoria existente."""
        for i, c in enumerate(cls.lista):
            if c.get_id() == categoria.get_id():
                cls.lista[i] = categoria
                return True
        return False

    @classmethod
    def excluir(cls, id):
        """Exclui uma categoria com base no ID."""
        original = len(cls.lista)
        cls.lista = [c for c in cls.lista if c.get_id() != id]
        return len(cls.lista) < original

    @classmethod
    def abrir(cls):
        """Carrega as categorias salvas no arquivo JSON."""
        if not os.path.exists(cls.arquivo):
            cls.salvar()
            return
        with open(cls.arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            cls.lista = [Categoria(**d) for d in dados]
            cls.proximo_id = (max((c.get_id() for c in cls.lista), default=0) + 1)

    @classmethod
    def salvar(cls):
        """Salva a lista de categorias no arquivo JSON."""
        with open(cls.arquivo, 'w', encoding='utf-8') as f:
            json.dump([{
                "id": c.get_id(),
                "nome": c.get_nome(),
                "descricao": c.get_descricao()
            } for c in cls.lista], f, indent=2, ensure_ascii=False)
