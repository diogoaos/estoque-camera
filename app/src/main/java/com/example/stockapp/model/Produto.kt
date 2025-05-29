package com.example.stockapp.model

import java.util.Date
import java.util.UUID

data class Produto(
    val nome: String,
    val codigo_de_barras: String,
    val marca: String? = null,
    val unidade: String? = null,
    val data_de_validade_padrao: Date? = null,
    val url_imagem: String? = null,
    val id: UUID = UUID.randomUUID(),
    val criado_em: Date = Date(),
    val atualizado_em: Date = Date()
)

// Note: In a more complex scenario, if 'atualizado_em' should be updated
// on every modification of a Produto instance, rather than just at creation,
// you would typically handle that outside the data class (e.g., in a repository or service layer)
// or by providing a copy() method with updated timestamp, as data classes are primarily for holding data.
// For this conversion, 'atualizado_em' is set at creation time like 'criado_em'
// to match the Python class's __init__ behavior where both are set initially.
