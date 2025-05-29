import unittest
from datetime import datetime, timedelta, date
from uuid import uuid4

from models import Produto, ItemEstoque, CupomFiscal, DetalheProdutoCupom
from stock_management import (
    adicionar_produto_por_codigo_de_barras,
    adicionar_produtos_por_cupom_fiscal,
    remover_produto_por_codigo_de_barras,
)

class TestStockManagement(unittest.TestCase):

    def setUp(self):
        self.produtos_cadastrados: list[Produto] = []
        self.estoque: list[ItemEstoque] = []

    def test_adicionar_produto_novo_por_codigo_de_barras(self):
        """Testa adicionar um produto completamente novo."""
        barcode = "123456789"
        nome = "Produto Novo Teste"
        marca = "Marca Teste"
        unidade = "un"
        
        ts_antes = datetime.now() - timedelta(seconds=1)
        produto, item_estoque = adicionar_produto_por_codigo_de_barras(
            barcode, self.produtos_cadastrados, self.estoque, nome, marca, unidade
        )
        ts_depois = datetime.now() + timedelta(seconds=1)

        self.assertEqual(len(self.produtos_cadastrados), 1)
        self.assertEqual(len(self.estoque), 1)
        self.assertIs(produto, self.produtos_cadastrados[0])
        self.assertIs(item_estoque, self.estoque[0])

        self.assertEqual(produto.codigo_de_barras, barcode)
        self.assertEqual(produto.nome, nome)
        self.assertEqual(produto.marca, marca)
        self.assertEqual(produto.unidade, unidade)
        self.assertTrue(ts_antes <= produto.criado_em <= ts_depois)
        self.assertTrue(ts_antes <= produto.atualizado_em <= ts_depois)
        # Ao criar, os timestamps devem ser virtualmente idênticos.
        # Não usar assertIs pois podem ser objetos diferentes com microssegundos de diferença.
        self.assertLess((produto.atualizado_em - produto.criado_em), timedelta(seconds=1))


        self.assertEqual(item_estoque.produto_id, produto.id)
        self.assertEqual(item_estoque.quantidade, 1)
        self.assertTrue(ts_antes <= item_estoque.adicionado_em <= ts_depois)
        self.assertTrue(ts_antes <= item_estoque.ultima_atualizacao <= ts_depois)
        self.assertLess((item_estoque.ultima_atualizacao - item_estoque.adicionado_em), timedelta(seconds=1))


    def test_adicionar_produto_existente_sem_item_estoque_por_codigo_de_barras(self):
        """Testa adicionar produto cadastrado mas sem item de estoque."""
        barcode = "987654321"
        produto_preexistente = Produto(nome="Produto Preexistente", codigo_de_barras=barcode)
        self.produtos_cadastrados.append(produto_preexistente)
        
        ts_antes_modificacao = datetime.now() - timedelta(seconds=1)
        produto_preexistente.atualizado_em = ts_antes_modificacao # Simular que foi atualizado antes

        produto_retornado, item_estoque = adicionar_produto_por_codigo_de_barras(
            barcode, self.produtos_cadastrados, self.estoque
        )
        ts_depois_modificacao = datetime.now() + timedelta(seconds=1)

        self.assertEqual(len(self.produtos_cadastrados), 1) # Não deve adicionar novo produto
        self.assertEqual(len(self.estoque), 1)
        self.assertIs(produto_retornado, produto_preexistente)
        
        self.assertTrue(produto_retornado.atualizado_em >= ts_antes_modificacao) # Deve ser atualizado
        self.assertTrue(ts_antes_modificacao <= produto_retornado.atualizado_em <= ts_depois_modificacao)


        self.assertEqual(item_estoque.produto_id, produto_preexistente.id)
        self.assertEqual(item_estoque.quantidade, 1)
        self.assertTrue(ts_antes_modificacao <= item_estoque.adicionado_em <= ts_depois_modificacao)
        self.assertTrue(ts_antes_modificacao <= item_estoque.ultima_atualizacao <= ts_depois_modificacao)

    def test_adicionar_produto_com_item_estoque_existente_por_codigo_de_barras(self):
        """Testa adicionar produto que já tem item de estoque (incrementar)."""
        barcode = "1122334455"
        produto_existente = Produto(nome="Produto com Estoque", codigo_de_barras=barcode)
        self.produtos_cadastrados.append(produto_existente)
        item_estoque_preexistente = ItemEstoque(produto_id=produto_existente.id, quantidade=2)
        self.estoque.append(item_estoque_preexistente)

        # Simular timestamps antigos
        ts_antigo_produto = produto_existente.atualizado_em
        ts_antigo_item = item_estoque_preexistente.ultima_atualizacao
        
        produto_retornado, item_estoque_retornado = adicionar_produto_por_codigo_de_barras(
            barcode, self.produtos_cadastrados, self.estoque
        )

        self.assertEqual(len(self.produtos_cadastrados), 1)
        self.assertEqual(len(self.estoque), 1)
        self.assertIs(produto_retornado, produto_existente)
        self.assertIs(item_estoque_retornado, item_estoque_preexistente)

        self.assertEqual(item_estoque_retornado.quantidade, 3)
        self.assertTrue(produto_retornado.atualizado_em > ts_antigo_produto)
        self.assertTrue(item_estoque_retornado.ultima_atualizacao > ts_antigo_item)

    def test_adicionar_produtos_novos_por_cupom_fiscal(self):
        """Testa adicionar produtos de um cupom onde todos são novos."""
        detalhes_cupom = [
            DetalheProdutoCupom(nome_produto_cupom="Produto Cupom A", quantidade_cupom=2.0),
            DetalheProdutoCupom(nome_produto_cupom="Produto Cupom B", quantidade_cupom=1.0),
        ]
        cupom = CupomFiscal(
            dados_qr_code="QRDATA123",
            data_compra_cupom=date(2023, 10, 26),
            detalhes_produtos_cupom=detalhes_cupom
        )
        ts_antes = datetime.now() - timedelta(seconds=1)
        resultados = adicionar_produtos_por_cupom_fiscal(cupom, self.produtos_cadastrados, self.estoque)
        ts_depois = datetime.now() + timedelta(seconds=1)

        self.assertEqual(len(resultados), 2)
        self.assertEqual(len(self.produtos_cadastrados), 2)
        self.assertEqual(len(self.estoque), 2)

        # Produto A
        produto_a, item_a = resultados[0]
        self.assertEqual(produto_a.nome, "Produto Cupom A")
        self.assertTrue(produto_a.codigo_de_barras.startswith("SEM_COD_BARRAS_"))
        self.assertEqual(item_a.quantidade, 2)
        self.assertEqual(item_a.produto_id, produto_a.id)
        self.assertEqual(item_a.id_cupom_fiscal_origem, cupom.id)
        self.assertEqual(item_a.data_compra, cupom.data_compra_cupom)
        self.assertTrue(ts_antes <= produto_a.criado_em <= ts_depois)
        self.assertTrue(ts_antes <= item_a.adicionado_em <= ts_depois)


        # Produto B
        produto_b, item_b = resultados[1]
        self.assertEqual(produto_b.nome, "Produto Cupom B")
        self.assertEqual(item_b.quantidade, 1)
        self.assertEqual(item_b.produto_id, produto_b.id)
        self.assertEqual(item_b.id_cupom_fiscal_origem, cupom.id)

    def test_adicionar_produtos_cupom_com_existentes_e_novos(self):
        """Testa cupom com mix de produtos novos e já cadastrados (com e sem estoque)."""
        # Produto pré-existente com estoque
        prod_exist_com_estoque = Produto(nome="Arroz 1kg", codigo_de_barras="BC1")
        item_exist_com_estoque = ItemEstoque(produto_id=prod_exist_com_estoque.id, quantidade=3)
        self.produtos_cadastrados.append(prod_exist_com_estoque)
        self.estoque.append(item_exist_com_estoque)
        ts_antigo_prod_exist_com_estoque = prod_exist_com_estoque.atualizado_em
        ts_antigo_item_exist_com_estoque = item_exist_com_estoque.ultima_atualizacao


        # Produto pré-existente sem estoque
        prod_exist_sem_estoque = Produto(nome="Feijão 500g", codigo_de_barras="BC2")
        self.produtos_cadastrados.append(prod_exist_sem_estoque)
        ts_antigo_prod_exist_sem_estoque = prod_exist_sem_estoque.atualizado_em

        detalhes_cupom = [
            DetalheProdutoCupom(nome_produto_cupom="Arroz 1kg", quantidade_cupom=2.0), # Existente com estoque
            DetalheProdutoCupom(nome_produto_cupom="Feijão 500g", quantidade_cupom=1.0), # Existente sem estoque
            DetalheProdutoCupom(nome_produto_cupom="Macarrão 500g", quantidade_cupom=3.0), # Novo
        ]
        cupom = CupomFiscal(
            dados_qr_code="QRDATA_MIX",
            data_compra_cupom=date(2023, 10, 27),
            detalhes_produtos_cupom=detalhes_cupom
        )
        
        ts_antes_add = datetime.now() - timedelta(seconds=1)
        resultados = adicionar_produtos_por_cupom_fiscal(cupom, self.produtos_cadastrados, self.estoque)
        ts_depois_add = datetime.now() + timedelta(seconds=1)

        self.assertEqual(len(resultados), 3)
        self.assertEqual(len(self.produtos_cadastrados), 3) # 2 preexistentes + 1 novo
        self.assertEqual(len(self.estoque), 3) # 1 item atualizado + 1 item novo para prod_exist_sem_estoque + 1 item novo para prod_novo

        # Arroz (existente com estoque)
        p_arroz, i_arroz = next(r for r in resultados if r[0].nome == "Arroz 1kg")
        self.assertIs(p_arroz, prod_exist_com_estoque)
        self.assertIs(i_arroz, item_exist_com_estoque)
        self.assertEqual(i_arroz.quantidade, 3 + 2)
        self.assertEqual(i_arroz.id_cupom_fiscal_origem, cupom.id)
        self.assertTrue(p_arroz.atualizado_em > ts_antigo_prod_exist_com_estoque)
        self.assertTrue(i_arroz.ultima_atualizacao > ts_antigo_item_exist_com_estoque)


        # Feijão (existente sem estoque)
        p_feijao, i_feijao = next(r for r in resultados if r[0].nome == "Feijão 500g")
        self.assertIs(p_feijao, prod_exist_sem_estoque)
        self.assertEqual(i_feijao.quantidade, 1)
        self.assertEqual(i_feijao.produto_id, p_feijao.id)
        self.assertEqual(i_feijao.id_cupom_fiscal_origem, cupom.id)
        self.assertTrue(p_feijao.atualizado_em > ts_antigo_prod_exist_sem_estoque)
        self.assertTrue(ts_antes_add <= i_feijao.adicionado_em <= ts_depois_add)


        # Macarrão (novo)
        p_macarrao, i_macarrao = next(r for r in resultados if r[0].nome == "Macarrão 500g")
        self.assertEqual(i_macarrao.quantidade, 3)
        self.assertEqual(i_macarrao.produto_id, p_macarrao.id)
        self.assertEqual(i_macarrao.id_cupom_fiscal_origem, cupom.id)
        self.assertTrue(ts_antes_add <= p_macarrao.criado_em <= ts_depois_add)
        self.assertTrue(ts_antes_add <= i_macarrao.adicionado_em <= ts_depois_add)


    def test_remover_produto_em_estoque(self):
        """Testa remover um produto que está em estoque."""
        barcode = "REM123"
        produto = Produto(nome="Produto para Remover", codigo_de_barras=barcode)
        self.produtos_cadastrados.append(produto)
        item_estoque = ItemEstoque(produto_id=produto.id, quantidade=3)
        self.estoque.append(item_estoque)

        ts_antigo_produto = produto.atualizado_em
        ts_antigo_item = item_estoque.ultima_atualizacao

        item_retornado = remover_produto_por_codigo_de_barras(barcode, self.produtos_cadastrados, self.estoque)

        self.assertIsNotNone(item_retornado)
        self.assertIs(item_retornado, item_estoque)
        self.assertEqual(item_retornado.quantidade, 2) # type: ignore
        self.assertEqual(len(self.estoque), 1) # Ainda deve estar no estoque
        self.assertTrue(produto.atualizado_em > ts_antigo_produto)
        self.assertTrue(item_retornado.ultima_atualizacao > ts_antigo_item) # type: ignore

    def test_remover_produto_ate_zerar_estoque(self):
        """Testa remover produto até quantidade ser zero (deve sair do estoque)."""
        barcode = "REM_ZERAR"
        produto = Produto(nome="Produto para Zerar", codigo_de_barras=barcode)
        self.produtos_cadastrados.append(produto)
        item_estoque = ItemEstoque(produto_id=produto.id, quantidade=1)
        self.estoque.append(item_estoque)
        
        ts_antigo_produto = produto.atualizado_em
        ts_antigo_item = item_estoque.ultima_atualizacao

        item_retornado = remover_produto_por_codigo_de_barras(barcode, self.produtos_cadastrados, self.estoque)

        self.assertIsNone(item_retornado) # Deve retornar None pois foi removido
        self.assertEqual(len(self.estoque), 0) # Deve ser removido da lista
        self.assertTrue(produto.atualizado_em > ts_antigo_produto)
        # O item_estoque original foi modificado antes de ser potencialmente removido,
        # então seu timestamp ultima_atualizacao teria sido atualizado.
        # Não podemos verificar item_estoque.ultima_atualizacao diretamente se ele foi removido,
        # mas podemos verificar o timestamp do produto.

    def test_remover_produto_nao_cadastrado(self):
        """Testa remover produto que não está em produtos_cadastrados."""
        item_retornado = remover_produto_por_codigo_de_barras("NAO_EXISTE", self.produtos_cadastrados, self.estoque)
        self.assertIsNone(item_retornado)
        self.assertEqual(len(self.estoque), 0)

    def test_remover_produto_cadastrado_sem_item_estoque(self):
        """Testa remover produto cadastrado mas sem item de estoque."""
        barcode = "SEM_ESTOQUE"
        produto = Produto(nome="Produto Sem Estoque", codigo_de_barras=barcode)
        self.produtos_cadastrados.append(produto)
        
        item_retornado = remover_produto_por_codigo_de_barras(barcode, self.produtos_cadastrados, self.estoque)
        self.assertIsNone(item_retornado)
        self.assertEqual(len(self.estoque), 0)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
