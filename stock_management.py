from typing import List, Tuple, Optional
from uuid import uuid4, UUID
from datetime import datetime

from models import Produto, ItemEstoque, CupomFiscal, DetalheProdutoCupom

def adicionar_produto_por_codigo_de_barras(
    codigo_de_barras: str,
    produtos_cadastrados: List[Produto],
    estoque: List[ItemEstoque],
    nome_produto: Optional[str] = None,
    marca_produto: Optional[str] = None,
    unidade_produto: Optional[str] = None,
) -> Tuple[Produto, ItemEstoque]:
    """
    Adiciona um produto ao estoque utilizando seu código de barras.

    Se o produto já estiver cadastrado, incrementa a quantidade do item de estoque
    correspondente ou cria um novo item de estoque se não existir.
    Se o produto não estiver cadastrado, cria um novo produto e um novo item de estoque.

    Args:
        codigo_de_barras: O código de barras do produto.
        produtos_cadastrados: Lista de produtos já cadastrados.
        estoque: Lista de itens em estoque.
        nome_produto: Nome do produto (usado se o produto for novo).
        marca_produto: Marca do produto (usado se o produto for novo).
        unidade_produto: Unidade do produto (usado se o produto for novo).

    Returns:
        Uma tupla contendo o objeto Produto e o objeto ItemEstoque (novo ou atualizado).
    """
    produto_existente: Optional[Produto] = None
    for p in produtos_cadastrados:
        if p.codigo_de_barras == codigo_de_barras:
            produto_existente = p
            break

    item_estoque_existente: Optional[ItemEstoque] = None
    now = datetime.now()

    if produto_existente:
        produto_existente.atualizado_em = now
        # Produto já cadastrado, procurar no estoque
        for item in estoque:
            if item.produto_id == produto_existente.id:
                item_estoque_existente = item
                break
        
        if item_estoque_existente:
            item_estoque_existente.quantidade += 1
            item_estoque_existente.ultima_atualizacao = now
            return produto_existente, item_estoque_existente
        else:
            # Produto cadastrado, mas não há item de estoque para ele
            novo_item_estoque = ItemEstoque(
                produto_id=produto_existente.id,
                quantidade=1
            )
            # novo_item_estoque.ultima_atualizacao já é now() pelo construtor
            estoque.append(novo_item_estoque)
            return produto_existente, novo_item_estoque
    else:
        # Produto não cadastrado, criar novo produto e novo item de estoque
        # novo_produto e novo_item_estoque terão seus timestamps definidos por seus construtores
        novo_produto = Produto(
            nome=nome_produto if nome_produto else f"Produto {codigo_de_barras}",
            codigo_de_barras=codigo_de_barras,
            marca=marca_produto,
            unidade=unidade_produto
        )
        produtos_cadastrados.append(novo_produto)

        novo_item_estoque = ItemEstoque(
            produto_id=novo_produto.id,
            quantidade=1
        )
        estoque.append(novo_item_estoque)
        return novo_produto, novo_item_estoque

def adicionar_produtos_por_cupom_fiscal(
    cupom: CupomFiscal,
    produtos_cadastrados: List[Produto],
    estoque: List[ItemEstoque]
) -> List[Tuple[Produto, ItemEstoque]]:
    """
    Adiciona produtos ao estoque com base nos itens de um cupom fiscal.

    Para cada item no cupom, tenta encontrar um produto correspondente.
    Se encontrado, atualiza o estoque. Caso contrário, cria um novo produto e
    um novo item de estoque.

    Args:
        cupom: O objeto CupomFiscal contendo os detalhes dos produtos.
        produtos_cadastrados: Lista de produtos já cadastrados.
        estoque: Lista de itens em estoque.

    Returns:
        Uma lista de tuplas, cada uma contendo o Produto e o ItemEstoque
        adicionado/atualizado.
    """
    resultados: List[Tuple[Produto, ItemEstoque]] = []
    now = datetime.now()

    for detalhe_cupom in cupom.detalhes_produtos_cupom:
        produto_encontrado: Optional[Produto] = None
        # Lógica simples de correspondência pelo nome do produto no cupom
        # Em um sistema real, isso seria mais robusto (ex: por código de barras se disponível no cupom,
        # ou uma busca mais inteligente por nome/marca)
        for p_cadastrado in produtos_cadastrados:
            # Simplificação: considera que o nome no cupom é igual ao nome cadastrado
            # Em um cenário real, pode ser necessário normalizar strings, usar correspondência parcial, etc.
            if p_cadastrado.nome.lower() == detalhe_cupom.nome_produto_cupom.lower():
                produto_encontrado = p_cadastrado
                break
        
        item_estoque_processado: Optional[ItemEstoque] = None

        if produto_encontrado:
            produto_encontrado.atualizado_em = now
            # Produto já existe, verificar item de estoque
            item_estoque_existente: Optional[ItemEstoque] = None
            for item in estoque:
                if item.produto_id == produto_encontrado.id:
                    item_estoque_existente = item
                    break
            
            if item_estoque_existente:
                # Nota: ItemEstoque.quantidade é int. Se detalhe_cupom.quantidade_cupom for float (ex: 0.5 kg),
                # a conversão para int truncará (0.5 se tornará 0).
                # Se o sistema precisar de quantidades fracionadas, ItemEstoque.quantidade deve ser float.
                item_estoque_existente.quantidade += int(detalhe_cupom.quantidade_cupom)
                item_estoque_existente.id_cupom_fiscal_origem = cupom.id
                item_estoque_existente.ultima_atualizacao = now
                item_estoque_existente.data_compra = cupom.data_compra_cupom # Atualiza data da compra com a do cupom
                item_estoque_processado = item_estoque_existente
            else:
                # Produto cadastrado, mas não há item de estoque para ele
                novo_item_estoque = ItemEstoque(
                    produto_id=produto_encontrado.id,
                    quantidade=int(detalhe_cupom.quantidade_cupom), # Mesma nota sobre conversão para int
                    id_cupom_fiscal_origem=cupom.id,
                    data_compra=cupom.data_compra_cupom
                )
                # novo_item_estoque.ultima_atualizacao já é now() pelo construtor
                estoque.append(novo_item_estoque)
                item_estoque_processado = novo_item_estoque
            
            resultados.append((produto_encontrado, item_estoque_processado))

        else:
            # Produto não encontrado, criar novo Produto e novo ItemEstoque
            # novo_produto e novo_item_estoque terão seus timestamps definidos por seus construtores
            placeholder_barcode = f"SEM_COD_BARRAS_{uuid4()}"

            novo_produto = Produto(
                nome=detalhe_cupom.nome_produto_cupom,
                codigo_de_barras=placeholder_barcode,
                # marca e unidade podem ser desconhecidos ou extraídos se disponíveis no nome
            )
            # novo_produto.criado_em e atualizado_em são definidos no construtor
            produtos_cadastrados.append(novo_produto)

            novo_item_estoque = ItemEstoque(
                produto_id=novo_produto.id,
                quantidade=int(detalhe_cupom.quantidade_cupom), # Mesma nota sobre conversão para int
                id_cupom_fiscal_origem=cupom.id,
                data_compra=cupom.data_compra_cupom
            )
            # novo_item_estoque.adicionado_em e ultima_atualizacao são definidos no construtor
            estoque.append(novo_item_estoque)
            resultados.append((novo_produto, novo_item_estoque))
            item_estoque_processado = novo_item_estoque # Atribuído para consistência, embora não usado depois

    return resultados

def remover_produto_por_codigo_de_barras(
    codigo_de_barras: str,
    produtos_cadastrados: List[Produto],
    estoque: List[ItemEstoque]
) -> Optional[ItemEstoque]:
    """
    Remove uma unidade de um produto do estoque utilizando seu código de barras.

    Encontra o produto pelo código de barras, depois o item de estoque correspondente.
    Decrementa a quantidade do item de estoque. Se a quantidade chegar a zero,
    o item de estoque é removido da lista.

    Args:
        codigo_de_barras: O código de barras do produto a ser removido.
        produtos_cadastrados: Lista de produtos cadastrados (não é modificada).
        estoque: Lista de itens em estoque (pode ser modificada).

    Returns:
        O objeto ItemEstoque atualizado se a quantidade for > 0 após a remoção.
        None se o item de estoque for removido (quantidade se tornou 0),
        ou se o produto ou o item de estoque não forem encontrados.
    """
    produto_alvo: Optional[Produto] = None
    for p in produtos_cadastrados:
        if p.codigo_de_barras == codigo_de_barras:
            produto_alvo = p
            break

    if not produto_alvo:
        return None # Produto não encontrado

    item_estoque_alvo: Optional[ItemEstoque] = None
    item_estoque_index: Optional[int] = None
    for i, item in enumerate(estoque):
        if item.produto_id == produto_alvo.id:
            item_estoque_alvo = item
            item_estoque_index = i
            break
    
    if not item_estoque_alvo:
        return None # Item de estoque não encontrado para este produto

    # Decrementar quantidade
    item_estoque_alvo.quantidade -= 1
    item_estoque_alvo.ultima_atualizacao = datetime.now()
    produto_alvo.atualizado_em = datetime.now() # Embora não seja estritamente necessário pela docstring, é bom manter o produto atualizado.

    if item_estoque_alvo.quantidade <= 0:
        if item_estoque_index is not None: # Sempre será, se item_estoque_alvo foi encontrado
            estoque.pop(item_estoque_index)
        return None # Item removido do estoque
    else:
        return item_estoque_alvo
