# Especificação de Design da Interface do Usuário: Aplicativo de Gerenciamento de Despensa

Este documento descreve o design da interface do usuário (UI) para o aplicativo de gerenciamento de despensa. O objetivo é fornecer um guia textual claro para o desenvolvimento da UI.

## 1. Tela Principal do Estoque (Home Screen)

Esta é a tela principal onde o usuário visualiza os itens atualmente em estoque.

*   **Título da Tela:** "Minha Despensa" ou "Estoque Atual"

*   **Visualização da Lista de Itens:**
    *   **Layout:** Lista vertical rolável. Cada item da lista representa um `ItemEstoque` com informações do `Produto` associado.
    *   **Componente de Item da Lista:**
        *   **Nome do Produto:** Em destaque (fonte maior ou em negrito).
        *   **Quantidade em Estoque:** Exibido claramente (ex: "Quantidade: 3 unidades", "500g").
        *   **Marca do Produto:** (Opcional) Exibido abaixo do nome do produto, com fonte menor.
        *   **Data de Validade:**
            *   Exibir a `data_validade_especifica` se disponível, caso contrário, a `data_de_validade_padrao` do produto.
            *   **Destaque para Validade Próxima:** Itens com data de validade próxima (ex: nos próximos 7 dias) devem ter um indicador visual (ex: ícone de alerta, cor de fundo diferente na data, texto da data em vermelho).
            *   Formato da data: "Val: DD/MM/AAAA".
        *   **Imagem do Produto:** (Opcional) Uma miniatura da `url_imagem` do produto, à esquerda do nome. Se não houver imagem, um ícone placeholder.
    *   **Estado Vazio:** Se não houver itens no estoque, exibir uma mensagem amigável (ex: "Sua despensa está vazia. Adicione itens usando os botões abaixo!").

*   **Ações Rápidas (Barra de Ações ou Botões Flutuantes - FAB):**
    *   Estes botões devem estar facilmente acessíveis, possivelmente em uma barra inferior ou como um menu de Botão de Ação Flutuante (FAB).
    *   **Botão/Ícone "Escanear Código de Barras para Adicionar":**
        *   Ícone: Representação de um código de barras com um "+".
        *   Texto (se houver espaço): "Adicionar por Código".
        *   Ação: Abre a "Tela de Leitura de Código de Barras" no modo "Adicionar".
    *   **Botão/Ícone "Escanear Código de Barras para Remover":**
        *   Ícone: Representação de um código de barras com um "-".
        *   Texto (se houver espaço): "Remover por Código".
        *   Ação: Abre a "Tela de Leitura de Código de Barras" no modo "Remover".
    *   **Botão/Ícone "Escanear QR Code de Cupom Fiscal":**
        *   Ícone: Representação de um QR Code.
        *   Texto (se houver espaço): "Adicionar por Cupom".
        *   Ação: Abre a "Tela de Leitura de QR Code (Cupom Fiscal)".

*   **Navegação (Opcional):**
    *   Ao tocar em um item da lista, o usuário navega para a "Tela de Detalhes do Produto" (se implementada) para ver mais informações ou editar o item específico.

*   **Indicadores e Filtros (Opcional, na parte superior da lista):**
    *   **Filtro "Validade Próxima":** Botão ou toggle para exibir apenas itens com validade próxima.
    *   **Filtro "Baixo Estoque":** Botão ou toggle para exibir apenas itens com quantidade abaixo de um certo limite (ex: quantidade <= 1).
    *   **Barra de Pesquisa:** Campo de texto para pesquisar produtos pelo nome.

## 2. Tela de Leitura de Código de Barras

Esta tela é usada para escanear códigos de barras para adicionar ou remover produtos.

*   **Título da Tela:** "Escanear Código de Barras" (pode incluir "para Adicionar" ou "para Remover" dependendo do modo).

*   **Interface da Câmera:**
    *   A maior parte da tela será uma visualização ao vivo da câmera do dispositivo.

*   **Guia de Leitura:**
    *   Um overlay gráfico no centro da visualização da câmera (ex: um retângulo ou uma linha horizontal/vertical) para ajudar o usuário a alinhar o código de barras.
    *   Texto instrutivo próximo à guia (ex: "Posicione o código de barras aqui").

*   **Feedback:**
    *   **Sucesso:** Vibração curta e/ou um bipe sonoro breve. Um overlay visual temporário (ex: um contorno verde ao redor do código detectado) pode ser exibido.
    *   **Falha:** (Opcional) Feedback sutil se muitos frames não resultarem em detecção, ou se o código for inválido.

*   **Entrada Manual:**
    *   Botão/Link "Digitar Código Manualmente".
    *   Ação: Abre um diálogo ou uma nova seção na tela com um campo de texto para o usuário digitar o código de barras. Botão "Confirmar" para submeter o código digitado.

*   **Fluxo Pós-Leitura (Modo Adicionar):**
    *   **Produto Novo (código não cadastrado):**
        *   A tela (ou um diálogo sobreposto) exibe o código de barras lido.
        *   Formulário com os seguintes campos para o usuário preencher:
            *   **Nome do Produto:** (Obrigatório) Campo de texto.
            *   **Marca:** (Opcional) Campo de texto.
            *   **Unidade:** (Opcional, ex: "kg", "L", "unidade") Campo de texto ou dropdown.
            *   (Opcional) `data_de_validade_padrao` e `url_imagem`.
        *   Botão "Adicionar ao Estoque".
        *   Ação do Botão: Salva o novo `Produto` e o `ItemEstoque` inicial (quantidade 1). Retorna à Tela Principal.
    *   **Produto Existente (código já cadastrado):**
        *   Exibe uma mensagem de confirmação (ex: um "toast" ou um diálogo breve).
        *   Texto: "+1 [NomeDoProduto] ([MarcaDoProduto]) adicionado ao estoque."
        *   A tela pode retornar automaticamente para a Tela Principal ou aguardar um novo escaneamento.

*   **Fluxo Pós-Leitura (Modo Remover):**
    *   **Produto não encontrado no estoque (ou produto não cadastrado):**
        *   Mensagem: "Produto com código [codigo_de_barras] não encontrado no estoque."
    *   **Produto Encontrado e Removido:**
        *   Mensagem de confirmação: "-1 [NomeDoProduto] removido do estoque."
        *   Se a quantidade chegar a zero: "Última unidade de [NomeDoProduto] removida. Item fora de estoque."
    *   A tela pode retornar automaticamente para a Tela Principal ou aguardar um novo escaneamento.

*   **Botão de Cancelar/Voltar:** Para fechar a tela de escaneamento e retornar à Tela Principal.

## 3. Tela de Leitura de QR Code (Cupom Fiscal)

Esta tela é usada para escanear QR Codes de cupons fiscais para adicionar múltiplos produtos.

*   **Título da Tela:** "Escanear QR Code do Cupom Fiscal"

*   **Interface da Câmera:**
    *   Visualização ao vivo da câmera, similar à tela de leitura de código de barras.

*   **Guia de Leitura:**
    *   Overlay gráfico para ajudar no alinhamento do QR code (ex: um quadrado central).
    *   Texto instrutivo: "Posicione o QR Code do cupom aqui".

*   **Feedback:**
    *   **Sucesso:** Vibração e/ou bipe. Overlay visual temporário.
    *   **Falha/QR Code Inválido:** Mensagem de erro (ex: "QR Code inválido ou não reconhecido como cupom fiscal").

*   **Fluxo Pós-Leitura:**
    *   Após a leitura bem-sucedida e o processamento inicial do QR Code (extração da URL/dados):
    *   **Exibição de Progresso:** Um indicador de carregamento breve pode ser exibido enquanto os dados do cupom são analisados (ex: "Processando dados do cupom...").
    *   **Tela de Confirmação/Revisão:**
        *   **Título:** "Itens do Cupom Fiscal" ou "Confirme os Produtos".
        *   **Data da Compra do Cupom:** Exibida no topo (ex: "Compra realizada em: DD/MM/AAAA").
        *   **Nome da Loja (se disponível):** Exibido.
        *   **Lista de Produtos Identificados:**
            *   Layout: Lista vertical rolável.
            *   Cada item da lista representa um `DetalheProdutoCupom`.
            *   **Nome do Produto (do cupom):** `nome_produto_cupom`.
            *   **Quantidade (do cupom):** `quantidade_cupom`.
            *   **(Opcional) Checkbox de Seleção:** Por padrão, todos os itens vêm marcados. O usuário pode desmarcar itens que não deseja adicionar ao estoque.
        *   **Botão "Adicionar Selecionados ao Estoque" (ou "Adicionar Todos ao Estoque" se não houver seleção individual):**
            *   Ação: Processa cada item selecionado conforme a lógica de `adicionar_produtos_por_cupom_fiscal`.
                *   Para cada item, verifica se o produto já existe no cadastro (pelo nome ou, idealmente, se o cupom fornecer um código de barras).
                *   Se não existe, um novo `Produto` é criado (pode ser necessário pedir mais detalhes ao usuário posteriormente ou usar placeholders).
                *   `ItemEstoque` é criado/atualizado com a quantidade do cupom e `id_cupom_fiscal_origem`.
            *   Após a adição, exibe uma mensagem de sucesso (ex: "X itens adicionados ao estoque!") e retorna à Tela Principal.
        *   **Botão "Cancelar":** Retorna à Tela Principal sem adicionar itens.

## 4. Tela de Detalhes do Produto (Opcional)

Esta tela permite visualizar e editar informações detalhadas de um produto e seu item de estoque.

*   **Título da Tela:** "Detalhes do Produto" ou o nome do produto.

*   **Visualização de Informações:**
    *   Exibe todos os campos do `Produto`:
        *   Nome do Produto
        *   Código de Barras
        *   Marca
        *   Unidade
        *   Data de Validade Padrão
        *   URL da Imagem (exibida como imagem, se válida)
        *   Criado em / Atualizado em
    *   Exibe informações do `ItemEstoque` associado:
        *   Quantidade Atual
        *   Data da Compra (se houver)
        *   Data de Validade Específica (se houver)
        *   ID do Cupom Fiscal de Origem (se houver)
        *   Adicionado em / Última Atualização

*   **Ações de Edição:**
    *   **Botão "Editar":**
        *   Ação: Transforma os campos relevantes em editáveis (ou navega para uma tela de edição separada).
        *   Campos editáveis podem incluir:
            *   Nome do Produto, Marca, Unidade (para o `Produto`).
            *   Quantidade, Data de Validade Específica (para o `ItemEstoque`).
        *   Botões "Salvar Alterações" e "Cancelar Edição".
    *   **Botão "Remover Item do Estoque" (ou "-1"):**
        *   Ação: Decrementa a quantidade do item. Se chegar a zero, pode perguntar se deseja remover completamente o `ItemEstoque` (similar à lógica de "Remover por Código de Barras").
        *   Confirmação: "Tem certeza que deseja remover uma unidade de [NomeDoProduto]?"
    *   **Botão "Excluir Produto" (Mais drástico, requer cuidado):**
        *   Ação: Remove o `Produto` do cadastro e todos os `ItemEstoque` associados.
        *   Confirmação: "Tem certeza que deseja excluir [NomeDoProduto] permanentemente? Isso removerá todo o histórico de estoque deste produto."

*   **Navegação:**
    *   Botão "Voltar" para retornar à Tela Principal do Estoque.

Este documento serve como base para o design da UI. Detalhes como cores exatas, fontes e layout preciso serão definidos durante o processo de desenvolvimento da UI, possivelmente com o auxílio de ferramentas de design.
