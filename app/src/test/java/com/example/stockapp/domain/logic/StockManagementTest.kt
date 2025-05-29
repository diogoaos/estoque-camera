package com.example.stockapp.domain.logic

import com.example.stockapp.model.CupomFiscal
import com.example.stockapp.model.DetalheProdutoCupom
import com.example.stockapp.model.ItemEstoque
import com.example.stockapp.model.Produto
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import java.util.Calendar
import java.util.Date
import java.util.UUID
import kotlin.math.abs

class StockManagementTest {

    private lateinit var produtosCadastrados: MutableList<Produto>
    private lateinit var estoque: MutableList<ItemEstoque>

    @Before
    fun setUp() {
        produtosCadastrados = mutableListOf()
        estoque = mutableListOf()
    }

    private fun createDate(year: Int, month: Int, day: Int): Date {
        return Calendar.getInstance().apply {
            set(year, month - 1, day, 0, 0, 0) // Calendar month is 0-indexed
            clear(Calendar.MILLISECOND)
        }.time
    }

    @Test
    fun `adicionar produto novo por código de barras`() {
        val barcode = "123456789"
        val nome = "Produto Novo Teste"
        val marca = "Marca Teste"
        val unidade = "UN"

        val tsAntes = Date(System.currentTimeMillis() - 1000)
        val (produto, itemEstoque) = adicionarProdutoPorCodigoDeBarras(
            codigoDeBarras = barcode,
            produtosCadastrados = produtosCadastrados,
            estoque = estoque,
            nomeProduto = nome,
            marcaProduto = marca,
            unidadeProduto = unidade
        )
        val tsDepois = Date(System.currentTimeMillis() + 1000)

        assertEquals(1, produtosCadastrados.size)
        assertEquals(1, estoque.size)
        assertSame(produtosCadastrados[0], produto)
        assertSame(estoque[0], itemEstoque)

        assertEquals(nome, produto.nome)
        assertEquals(barcode, produto.codigo_de_barras)
        assertEquals(marca, produto.marca)
        assertEquals(unidade, produto.unidade)
        assertNull(produto.data_de_validade_padrao)
        assertNull(produto.url_imagem)
        assertNotNull(produto.id)
        assertTrue(produto.criado_em.time >= tsAntes.time && produto.criado_em.time <= tsDepois.time)
        assertTrue(produto.atualizado_em.time >= tsAntes.time && produto.atualizado_em.time <= tsDepois.time)
        assertTrue(abs(produto.atualizado_em.time - produto.criado_em.time) < 1000)


        assertEquals(produto.id, itemEstoque.produto_id)
        assertEquals(1, itemEstoque.quantidade)
        assertNull(itemEstoque.data_compra)
        assertNull(itemEstoque.data_validade_especifica)
        assertNull(itemEstoque.id_cupom_fiscal_origem)
        assertNotNull(itemEstoque.id)
        assertTrue(itemEstoque.adicionado_em.time >= tsAntes.time && itemEstoque.adicionado_em.time <= tsDepois.time)
        assertTrue(itemEstoque.ultima_atualizacao.time >= tsAntes.time && itemEstoque.ultima_atualizacao.time <= tsDepois.time)
        assertTrue(abs(itemEstoque.ultima_atualizacao.time - itemEstoque.adicionado_em.time) < 1000)
    }

    @Test
    fun `adicionar produto existente por código de barras`() {
        val existingBarcode = "987654321"
        val existingNome = "Produto Existente"
        val pExistente = Produto(
            nome = existingNome,
            codigo_de_barras = existingBarcode
        )
        produtosCadastrados.add(pExistente)
        val ieExistente = ItemEstoque(produto_id = pExistente.id, quantidade = 1)
        estoque.add(ieExistente)

        val tsAntes = Date(System.currentTimeMillis() - 1000)
        val (produto, itemEstoque) = adicionarProdutoPorCodigoDeBarras(
            codigoDeBarras = existingBarcode,
            produtosCadastrados = produtosCadastrados,
            estoque = estoque
        )
        val tsDepois = Date(System.currentTimeMillis() + 1000)

        assertEquals(1, produtosCadastrados.size)
        assertEquals(1, estoque.size)
        assertSame(pExistente, produto) // Should be the same instance from the list
        assertSame(ieExistente, itemEstoque) // Should be the same instance

        // Check if the product in the list was updated
        val produtoNaLista = produtosCadastrados.find { it.id == pExistente.id }!!
        assertTrue(produtoNaLista.atualizado_em.time >= tsAntes.time && produtoNaLista.atualizado_em.time <= tsDepois.time)
        assertTrue(produtoNaLista.atualizado_em.time > pExistente.criado_em.time || produtoNaLista.quantidade == 2) // Assuming quantidade check means it was processed

        assertEquals(2, itemEstoque.quantidade)
        assertTrue(itemEstoque.ultima_atualizacao.time >= tsAntes.time && itemEstoque.ultima_atualizacao.time <= tsDepois.time)
        assertTrue(itemEstoque.ultima_atualizacao.time > ieExistente.adicionado_em.time || itemEstoque.quantidade == 2)
    }
    
    @Test
    fun `adicionar produto existente por código de barras mas sem item de estoque previo`() {
        val existingBarcode = "111222333"
        val existingNome = "Produto Sem Estoque Inicial"
        val pExistente = Produto(
            nome = existingNome,
            codigo_de_barras = existingBarcode
        )
        produtosCadastrados.add(pExistente)
        // No ItemEstoque for pExistente initially

        val tsAntes = Date(System.currentTimeMillis() - 1000)
        val (produto, itemEstoque) = adicionarProdutoPorCodigoDeBarras(
            codigoDeBarras = existingBarcode,
            produtosCadastrados = produtosCadastrados,
            estoque = estoque,
            nomeProduto = "Nome que não deve ser usado", // Ignored if product exists
            marcaProduto = "Marca que não deve ser usada"
        )
        val tsDepois = Date(System.currentTimeMillis() + 1000)

        assertEquals(1, produtosCadastrados.size)
        assertEquals(1, estoque.size) // New itemestoque created
        assertSame(pExistente, produto) // Should be the same instance
        assertNotSame(null, itemEstoque) // Ensure new item was created
        assertEquals(pExistente.id, itemEstoque.produto_id)


        val produtoNaLista = produtosCadastrados.find { it.id == pExistente.id }!!
        assertTrue(produtoNaLista.atualizado_em.time >= tsAntes.time && produtoNaLista.atualizado_em.time <= tsDepois.time)
        
        assertEquals(1, itemEstoque.quantidade)
        assertTrue(itemEstoque.adicionado_em.time >= tsAntes.time && itemEstoque.adicionado_em.time <= tsDepois.time)
        assertTrue(itemEstoque.ultima_atualizacao.time >= tsAntes.time && itemEstoque.ultima_atualizacao.time <= tsDepois.time)
        assertTrue(abs(itemEstoque.ultima_atualizacao.time - itemEstoque.adicionado_em.time) < 1000)
    }

    @Test
    fun `adicionar produtos por cupom fiscal com produtos novos e existentes`() {
        // Produto existente
        val pArrozCadastrado = Produto(nome = "Arroz 1kg", codigo_de_barras = "ARROZ123")
        produtosCadastrados.add(pArrozCadastrado)
        val ieArrozCadastrado = ItemEstoque(produto_id = pArrozCadastrado.id, quantidade = 2)
        estoque.add(ieArrozCadastrado)

        val dataCompraCupom = createDate(2023, 10, 26)
        val cupom = CupomFiscal(
            dados_qr_code = "QRCODE_TESTE_COMPLETO",
            data_compra_cupom = dataCompraCupom,
            nome_loja = "Supermercado Teste",
            detalhes_produtos_cupom = listOf(
                DetalheProdutoCupom(nome_produto_cupom = "Arroz 1kg", quantidade_cupom = 1.0, preco_unitario_cupom = 5.0), // Existente
                DetalheProdutoCupom(nome_produto_cupom = "Feijão Preto 500g", quantidade_cupom = 2.0, preco_unitario_cupom = 3.50), // Novo
                DetalheProdutoCupom(nome_produto_cupom = "Óleo de Soja 900ml", quantidade_cupom = 1.0, preco_unitario_cupom = 7.25)  // Novo
            )
        )

        val tsAntes = Date(System.currentTimeMillis() - 1000)
        val resultados = adicionarProdutosPorCupomFiscal(cupom, produtosCadastrados, estoque)
        val tsDepois = Date(System.currentTimeMillis() + 1000)

        assertEquals(3, resultados.size)
        assertEquals(3, produtosCadastrados.size) // Arroz + Feijão + Óleo
        assertEquals(3, estoque.size)

        // Arroz (existente)
        val (pArroz, iArroz) = resultados.first { it.first.nome == "Arroz 1kg" }
        assertSame(pArrozCadastrado, pArroz) // Check if it's the same instance updated
        val pArrozNaLista = produtosCadastrados.find {it.id == pArrozCadastrado.id}!!
        assertTrue(pArrozNaLista.atualizado_em.time >= tsAntes.time && pArrozNaLista.atualizado_em.time <= tsDepois.time)
        assertEquals(2 + 1, iArroz.quantidade) // 2 iniciais + 1 do cupom
        assertEquals(cupom.id, iArroz.id_cupom_fiscal_origem)
        assertEquals(dataCompraCupom, iArroz.data_compra)
        assertTrue(iArroz.ultima_atualizacao.time >= tsAntes.time && iArroz.ultima_atualizacao.time <= tsDepois.time)

        // Feijão (novo)
        val (pFeijao, iFeijao) = resultados.first { it.first.nome == "Feijão Preto 500g" }
        assertNotNull(produtosCadastrados.find { it.id == pFeijao.id })
        assertEquals("Feijão Preto 500g", pFeijao.nome)
        assertTrue(pFeijao.codigo_de_barras.startsWith("SEM_COD_BARRAS_"))
        assertTrue(pFeijao.criado_em.time >= tsAntes.time && pFeijao.criado_em.time <= tsDepois.time)
        assertEquals(2, iFeijao.quantidade)
        assertEquals(cupom.id, iFeijao.id_cupom_fiscal_origem)
        assertEquals(dataCompraCupom, iFeijao.data_compra)
        assertTrue(iFeijao.adicionado_em.time >= tsAntes.time && iFeijao.adicionado_em.time <= tsDepois.time)
        
        // Óleo (novo)
        val (pOleo, iOleo) = resultados.first { it.first.nome == "Óleo de Soja 900ml" }
        assertNotNull(produtosCadastrados.find { it.id == pOleo.id })
        assertEquals("Óleo de Soja 900ml", pOleo.nome)
        assertTrue(pOleo.codigo_de_barras.startsWith("SEM_COD_BARRAS_"))
        assertEquals(1, iOleo.quantidade)
        assertEquals(cupom.id, iOleo.id_cupom_fiscal_origem)
    }

    @Test
    fun `remover produto existente com quantidade suficiente`() {
        val barcode = "PROD_REM_001"
        val p = Produto(nome = "Produto a Remover", codigo_de_barras = barcode)
        produtosCadastrados.add(p)
        val ie = ItemEstoque(produto_id = p.id, quantidade = 3)
        estoque.add(ie)

        val tsAntes = Date(System.currentTimeMillis() - 1000)
        val itemEstoqueRestante = removerProdutoPorCodigoDeBarras(barcode, produtosCadastrados, estoque)
        val tsDepois = Date(System.currentTimeMillis() + 1000)

        assertNotNull(itemEstoqueRestante)
        assertEquals(2, itemEstoqueRestante!!.quantidade)
        assertEquals(ie.id, itemEstoqueRestante.id) // Should be the same item, modified
        assertTrue(itemEstoqueRestante.ultima_atualizacao.time >= tsAntes.time && itemEstoqueRestante.ultima_atualizacao.time <= tsDepois.time)
        
        // Check if product in list was updated (if logic included it - current Kotlin code doesn't update product on removal)
        // val produtoNaLista = produtosCadastrados.find { it.id == p.id }!!
        // assertTrue(produtoNaLista.atualizado_em.time >= tsAntes.time && produtoNaLista.atualizado_em.time <= tsDepois.time)

        assertEquals(1, estoque.size) // Item still in stock
    }

    @Test
    fun `remover produto existente ate zerar estoque`() {
        val barcode = "PROD_REM_002"
        val p = Produto(nome = "Produto a Zerar", codigo_de_barras = barcode)
        produtosCadastrados.add(p)
        val ie = ItemEstoque(produto_id = p.id, quantidade = 1)
        estoque.add(ie)

        val itemEstoqueRestante = removerProdutoPorCodigoDeBarras(barcode, produtosCadastrados, estoque)

        assertNull(itemEstoqueRestante)
        assertEquals(0, estoque.size) // Item removed from stock
    }

    @Test
    fun `remover produto nao cadastrado`() {
        val itemEstoqueRestante = removerProdutoPorCodigoDeBarras("CODIGO_INEXISTENTE", produtosCadastrados, estoque)
        assertNull(itemEstoqueRestante)
        assertEquals(0, produtosCadastrados.size)
        assertEquals(0, estoque.size)
    }

    @Test
    fun `remover produto cadastrado mas sem estoque`() {
        val barcode = "PROD_SEM_ESTOQUE_003"
        val p = Produto(nome="Produto Cadastrado Sem Estoque", codigo_de_barras = barcode)
        produtosCadastrados.add(p)
        // No item in estoque for this product

        val itemEstoqueRestante = removerProdutoPorCodigoDeBarras(barcode, produtosCadastrados, estoque)
        assertNull(itemEstoqueRestante)
        assertEquals(1, produtosCadastrados.size)
        assertEquals(0, estoque.size)
    }
}
