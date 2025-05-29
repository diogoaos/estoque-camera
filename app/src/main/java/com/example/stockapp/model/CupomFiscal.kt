package com.example.stockapp.model

import java.util.Date
import java.util.UUID
// DetalheProdutoCupom is in the same package, so direct import is not strictly necessary
// but can be added for clarity if preferred:
// import com.example.stockapp.model.DetalheProdutoCupom

data class CupomFiscal(
    val dados_qr_code: String,
    val data_compra_cupom: Date,
    val detalhes_produtos_cupom: List<DetalheProdutoCupom>,
    val nome_loja: String? = null,
    val id: UUID = UUID.randomUUID(),
    val processado_em: Date = Date()
)
