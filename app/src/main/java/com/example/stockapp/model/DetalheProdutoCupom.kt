package com.example.stockapp.model

// No UUID or Date imports needed for this class based on the Python definition.

data class DetalheProdutoCupom(
    val nome_produto_cupom: String,
    val quantidade_cupom: Double, // Python float maps to Kotlin Double
    val preco_unitario_cupom: Double? = null
)
