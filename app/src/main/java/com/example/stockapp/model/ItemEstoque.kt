package com.example.stockapp.model

import java.util.Date
import java.util.UUID

data class ItemEstoque(
    val produto_id: UUID,
    val quantidade: Int,
    val data_compra: Date? = null,
    val data_validade_especifica: Date? = null,
    val id_cupom_fiscal_origem: UUID? = null,
    val id: UUID = UUID.randomUUID(),
    val adicionado_em: Date = Date(),
    val ultima_atualizacao: Date = Date()
)

// Similar to Produto.kt, 'ultima_atualizacao' is set at creation time
// to match the Python class's __init__ behavior. Updates would typically
// be handled by a repository or service layer.
