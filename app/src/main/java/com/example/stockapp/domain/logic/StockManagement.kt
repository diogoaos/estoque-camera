package com.example.stockapp.domain.logic

import com.example.stockapp.model.CupomFiscal
import com.example.stockapp.model.ItemEstoque
import com.example.stockapp.model.Produto
import java.util.Date
import java.util.UUID

fun adicionarProdutoPorCodigoDeBarras(
    codigoDeBarras: String,
    produtosCadastrados: MutableList<Produto>,
    estoque: MutableList<ItemEstoque>,
    nomeProduto: String? = null,
    marcaProduto: String? = null,
    unidadeProduto: String? = null
): Pair<Produto, ItemEstoque> {
    val produtoExistente = produtosCadastrados.find { it.codigo_de_barras == codigoDeBarras }
    val now = Date()

    if (produtoExistente != null) {
        // Kotlin data classes are immutable by default. To "update" them, you create a copy.
        // However, the Python code mutates existing objects in the list.
        // To mimic this direct mutation for 'atualizado_em', we'd have to replace the object in the list
        // or make 'atualizado_em' a var in the data class.
        // For simplicity in this conversion, and assuming 'atualizado_em' in Produto can be a var,
        // or if Produto is not a data class but a regular class with vars:
        // produtoExistente.atualizado_em = now // This line would require 'atualizado_em' to be a var.
        // If Produto must remain a data class with vals, this update should be handled by replacing the element:
        val produtoIndex = produtosCadastrados.indexOf(produtoExistente)
        if (produtoIndex != -1) {
            produtosCadastrados[produtoIndex] = produtoExistente.copy(atualizado_em = now)
        }
        val updatedProduto = produtosCadastrados[produtoIndex]


        val itemEstoqueExistente = estoque.find { it.produto_id == updatedProduto.id }

        if (itemEstoqueExistente != null) {
            // Similarly, for ItemEstoque's 'quantidade' and 'ultima_atualizacao'
            val itemIndex = estoque.indexOf(itemEstoqueExistente)
            if (itemIndex != -1) {
                val updatedItem = itemEstoqueExistente.copy(
                    quantidade = itemEstoqueExistente.quantidade + 1,
                    ultima_atualizacao = now
                )
                estoque[itemIndex] = updatedItem
                return Pair(updatedProduto, updatedItem)
            }
            // Fallback if index not found (should not happen if itemEstoqueExistente is from the list)
            return Pair(updatedProduto, itemEstoqueExistente) // Should be the updated one
        } else {
            val novoItemEstoque = ItemEstoque(
                produto_id = updatedProduto.id,
                quantidade = 1
                // adicionado_em and ultima_atualizacao get default current Date via constructor
            )
            estoque.add(novoItemEstoque)
            return Pair(updatedProduto, novoItemEstoque)
        }
    } else {
        val novoProduto = Produto(
            nome = nomeProduto ?: "Produto $codigoDeBarras",
            codigo_de_barras = codigoDeBarras,
            marca = marcaProduto,
            unidade = unidadeProduto
            // id, criado_em, atualizado_em get defaults via constructor
        )
        produtosCadastrados.add(novoProduto)

        val novoItemEstoque = ItemEstoque(
            produto_id = novoProduto.id,
            quantidade = 1
        )
        estoque.add(novoItemEstoque)
        return Pair(novoProduto, novoItemEstoque)
    }
}

fun adicionarProdutosPorCupomFiscal(
    cupom: CupomFiscal,
    produtosCadastrados: MutableList<Produto>,
    estoque: MutableList<ItemEstoque>
): List<Pair<Produto, ItemEstoque>> {
    val resultados = mutableListOf<Pair<Produto, ItemEstoque>>()
    val now = Date()

    for (detalheCupom in cupom.detalhes_produtos_cupom) {
        var produtoEncontrado = produtosCadastrados.find {
            it.nome.equals(detalheCupom.nome_produto_cupom, ignoreCase = true)
        }
        
        val itemEstoqueProcessado: ItemEstoque

        if (produtoEncontrado != null) {
            val produtoIndex = produtosCadastrados.indexOf(produtoEncontrado)
            if (produtoIndex != -1) {
                 val updatedProdutoOriginal = produtoEncontrado.copy(atualizado_em = now)
                 produtosCadastrados[produtoIndex] = updatedProdutoOriginal
                 produtoEncontrado = updatedProdutoOriginal // use the updated reference
            }

            val itemEstoqueExistente = estoque.find { it.produto_id == produtoEncontrado!!.id }

            if (itemEstoqueExistente != null) {
                val itemIndex = estoque.indexOf(itemEstoqueExistente)
                if (itemIndex != -1) {
                    val updatedItem = itemEstoqueExistente.copy(
                        quantidade = itemEstoqueExistente.quantidade + detalheCupom.quantidade_cupom.toInt(),
                        id_cupom_fiscal_origem = cupom.id,
                        ultima_atualizacao = now,
                        data_compra = cupom.data_compra_cupom
                    )
                    estoque[itemIndex] = updatedItem
                    itemEstoqueProcessado = updatedItem
                } else {
                     itemEstoqueProcessado = itemEstoqueExistente // Should not happen
                }
            } else {
                val novoItemEstoque = ItemEstoque(
                    produto_id = produtoEncontrado!!.id,
                    quantidade = detalheCupom.quantidade_cupom.toInt(),
                    id_cupom_fiscal_origem = cupom.id,
                    data_compra = cupom.data_compra_cupom
                )
                estoque.add(novoItemEstoque)
                itemEstoqueProcessado = novoItemEstoque
            }
            resultados.add(Pair(produtoEncontrado!!, itemEstoqueProcessado))
        } else {
            val placeholderBarcode = "SEM_COD_BARRAS_${UUID.randomUUID()}"
            val novoProduto = Produto(
                nome = detalheCupom.nome_produto_cupom,
                codigo_de_barras = placeholderBarcode
            )
            produtosCadastrados.add(novoProduto)

            val novoItemEstoque = ItemEstoque(
                produto_id = novoProduto.id,
                quantidade = detalheCupom.quantidade_cupom.toInt(),
                id_cupom_fiscal_origem = cupom.id,
                data_compra = cupom.data_compra_cupom
            )
            estoque.add(novoItemEstoque)
            resultados.add(Pair(novoProduto, novoItemEstoque))
        }
    }
    return resultados
}

fun removerProdutoPorCodigoDeBarras(
    codigoDeBarras: String,
    produtosCadastrados: List<Produto>, // Can be List if not modified here
    estoque: MutableList<ItemEstoque>
): ItemEstoque? {
    val produtoAlvo = produtosCadastrados.find { it.codigo_de_barras == codigoDeBarras }

    if (produtoAlvo == null) {
        return null
    }

    val itemEstoqueAlvo = estoque.find { it.produto_id == produtoAlvo.id }
    if (itemEstoqueAlvo == null) {
        return null
    }

    val itemEstoqueIndex = estoque.indexOf(itemEstoqueAlvo)
    val now = Date()

    // Update produtoAlvo's atualizado_em - requires it to be mutable or list to be updated
    // Assuming Produto in produtosCadastrados is effectively final here if list is not MutableList<Produto>
    // If produtosCadastrados was MutableList, we'd update:
    // val produtoIndex = produtosCadastrados.indexOf(produtoAlvo)
    // if (produtoIndex != -1) {
    //     produtosCadastrados[produtoIndex] = produtoAlvo.copy(atualizado_em = now)
    // }


    if (itemEstoqueAlvo.quantidade - 1 <= 0) {
        if (itemEstoqueIndex != -1) { // Should always be true if itemEstoqueAlvo was found
            estoque.removeAt(itemEstoqueIndex)
        }
        return null // Product removed from stock
    } else {
        if (itemEstoqueIndex != -1) {
            val updatedItem = itemEstoqueAlvo.copy(
                quantidade = itemEstoqueAlvo.quantidade - 1,
                ultima_atualizacao = now
            )
            estoque[itemEstoqueIndex] = updatedItem
            return updatedItem
        }
        return itemEstoqueAlvo // Should not reach here ideally
    }
}
