from datetime import date, datetime
from typing import List, Optional
from uuid import UUID, uuid4

class Produto:
    id: UUID
    nome: str
    codigo_de_barras: str
    marca: Optional[str] = None
    unidade: Optional[str] = None
    data_de_validade_padrao: Optional[date] = None
    url_imagem: Optional[str] = None
    criado_em: datetime
    atualizado_em: datetime

    def __init__(
        self,
        nome: str,
        codigo_de_barras: str,
        marca: Optional[str] = None,
        unidade: Optional[str] = None,
        data_de_validade_padrao: Optional[date] = None,
        url_imagem: Optional[str] = None,
    ):
        self.id = uuid4()
        self.nome = nome
        self.codigo_de_barras = codigo_de_barras
        self.marca = marca
        self.unidade = unidade
        self.data_de_validade_padrao = data_de_validade_padrao
        self.url_imagem = url_imagem
        self.criado_em = datetime.now()
        self.atualizado_em = datetime.now()

class ItemEstoque:
    id: UUID
    produto_id: UUID
    quantidade: int
    data_compra: Optional[date] = None
    data_validade_especifica: Optional[date] = None
    id_cupom_fiscal_origem: Optional[UUID] = None
    adicionado_em: datetime
    ultima_atualizacao: datetime

    def __init__(
        self,
        produto_id: UUID,
        quantidade: int,
        data_compra: Optional[date] = None,
        data_validade_especifica: Optional[date] = None,
        id_cupom_fiscal_origem: Optional[UUID] = None,
    ):
        self.id = uuid4()
        self.produto_id = produto_id
        self.quantidade = quantidade
        self.data_compra = data_compra
        self.data_validade_especifica = data_validade_especifica
        self.id_cupom_fiscal_origem = id_cupom_fiscal_origem
        self.adicionado_em = datetime.now()
        self.ultima_atualizacao = datetime.now()

class DetalheProdutoCupom:
    nome_produto_cupom: str
    quantidade_cupom: float # Pode ser float para casos como "0.5 kg"
    preco_unitario_cupom: Optional[float] = None

    def __init__(
        self,
        nome_produto_cupom: str,
        quantidade_cupom: float,
        preco_unitario_cupom: Optional[float] = None,
    ):
        self.nome_produto_cupom = nome_produto_cupom
        self.quantidade_cupom = quantidade_cupom
        self.preco_unitario_cupom = preco_unitario_cupom

class CupomFiscal:
    id: UUID
    dados_qr_code: str
    nome_loja: Optional[str] = None
    data_compra_cupom: date
    detalhes_produtos_cupom: List[DetalheProdutoCupom]
    processado_em: datetime

    def __init__(
        self,
        dados_qr_code: str,
        data_compra_cupom: date,
        detalhes_produtos_cupom: List[DetalheProdutoCupom],
        nome_loja: Optional[str] = None,
    ):
        self.id = uuid4()
        self.dados_qr_code = dados_qr_code
        self.data_compra_cupom = data_compra_cupom
        self.detalhes_produtos_cupom = detalhes_produtos_cupom
        self.nome_loja = nome_loja
        self.processado_em = datetime.now()
