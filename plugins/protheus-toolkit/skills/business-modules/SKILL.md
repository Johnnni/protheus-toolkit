---
name: business-modules
description: Referencia dos 8 principais modulos de negocio do TOTVS Protheus - Compras, Faturamento, Financeiro, Estoque, Fiscal, Contabilidade, Manutencao e PCP. Contem tabelas, rotinas, pontos de entrada, integracoes e regras de negocio para cada modulo.
---

# Modulos de Negocio - TOTVS Protheus

## Regra de Carregamento

Carregue no maximo **2 modulos** por consulta. Se o usuario perguntar sobre integracao entre modulos, carregue os dois modulos envolvidos. Se a pergunta for generica, identifique o modulo mais relevante pelo contexto.

## Tabela de Roteamento

Use as palavras-chave abaixo para identificar qual modulo carregar:

| Palavras-chave | Arquivo | Modulo |
|---|---|---|
| compras, compra, pedido compra, solicitacao compra, cotacao, fornecedor, SC1, SC7, SD1, SF1, SA2, SA5, SIGACOM, MATA105, MATA120, MATA103 | compras.md | Compras (COM) |
| faturamento, venda, pedido venda, nota fiscal saida, NF saida, liberacao, cliente, SC5, SC6, SC9, SF2, SD2, SA1, SIGAFAT, MATA410, MATA460 | faturamento.md | Faturamento (FAT) |
| financeiro, contas pagar, contas receber, titulo, bordero, baixa, banco, boleto, CNAB, PIX, SE1, SE2, SE5, SIGAFIN, FINA040, FINA050 | financeiro.md | Financeiro (FIN) |
| estoque, armazem, saldo, movimentacao, inventario, custo medio, lote, enderecamento, SB1, SB2, SD3, SIGAEST, MATA240, MATA260 | estoque.md | Estoque (EST) |
| fiscal, imposto, ICMS, IPI, PIS, COFINS, SPED, apuracao, TES, NCM, CFOP, CST, SF3, SF4, SFT, SIGAFIS, MATA950 | fiscal.md | Fiscal (FIS) |
| contabilidade, contabil, lancamento contabil, plano contas, balancete, DRE, centro custo, CT1, CT2, SIGACTB, CTBA010 | contabilidade.md | Contabilidade (CTB) |
| manutencao, equipamento, ordem servico, OS, preventiva, corretiva, MTBF, MTTR, ST9, STJ, SIGAMNT, MNTA400 | manutencao.md | Manutencao de Ativos (MNT) |
| pcp, producao, ordem producao, MRP, estrutura produto, apontamento, empenho, SC2, SD4, SG1, SIGAPCP, MATA650 | pcp.md | PCP |

## Tabela de Integracoes entre Modulos

Esta tabela mostra os fluxos automaticos entre modulos. Use-a para identificar quando carregar mais de um modulo.

| Modulo Origem | Modulo Destino | Tipo de Integracao | Descricao |
|---|---|---|---|
| Compras | Estoque | Entrada automatica | NF Entrada (SD1) gera movimentacao no estoque (SD3) e atualiza saldo (SB2) |
| Compras | Financeiro | Titulo a pagar | NF Entrada (SF1) gera titulo no contas a pagar (SE2) |
| Compras | Fiscal | Escrituracao | NF Entrada gera lancamento fiscal (SF3) |
| Faturamento | Estoque | Baixa automatica | NF Saida (SD2) gera movimentacao de saida (SD3) e atualiza saldo (SB2) |
| Faturamento | Financeiro | Titulo a receber | NF Saida (SF2) gera titulo no contas a receber (SE1) |
| Faturamento | Fiscal | Escrituracao | NF Saida gera lancamento fiscal (SF3) |
| Financeiro | Contabilidade | Lancamento contabil | Baixas e movimentacoes financeiras geram lancamentos contabeis (CT2) |
| Estoque | Contabilidade | Lancamento contabil | Movimentacoes de estoque geram lancamentos contabeis via LP |
| Fiscal | Contabilidade | Lancamento contabil | Apuracao de impostos gera lancamentos contabeis |
| PCP | Estoque | Requisicao/Devolucao | Empenho (SD4) consome material do estoque, apontamento gera entrada de produto acabado |
| PCP | Compras | Solicitacao automatica | MRP gera solicitacoes de compra (SC1) para itens comprados |
| Manutencao | Estoque | Requisicao pecas | OS consome pecas do estoque |
| Manutencao | Compras | Solicitacao pecas | OS pode gerar solicitacao de compra para pecas nao disponiveis |

## Uso

Quando o usuario perguntar sobre um modulo especifico, carregue o arquivo correspondente. Quando perguntar sobre integracao, carregue os dois modulos envolvidos. Exemplos:

- "Como funciona o pedido de compra?" -> Carregar compras.md
- "Como a NF de entrada atualiza o estoque?" -> Carregar compras.md + estoque.md
- "Preciso customizar o faturamento para calcular frete" -> Carregar faturamento.md
- "Qual PE usar para validar baixa de titulo?" -> Carregar financeiro.md
