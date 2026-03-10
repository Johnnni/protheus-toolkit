---
name: tdn-docs
description: Esta skill deve ser usada quando o usuario perguntar sobre documentacao do TOTVS Protheus, funcoes ADVPL/TLPP, classes do framework Protheus, ou mencionar "TDN", "busca no TDN", "documentacao do Protheus", "como funciona o FWRest", "parametros do MsExecAuto", "o que faz essa funcao", ou qualquer consulta de referencia da API TOTVS/Protheus. Tambem ativar quando o usuario perguntar "what does this function do" para funcoes especificas do Protheus.
---

# Consulta de Documentacao TDN

Pesquisar e consultar a documentacao oficial do TOTVS Protheus no TDN (TOTVS Developer Network) diretamente durante a conversa.

## Ferramentas Disponiveis

Duas ferramentas MCP estao disponiveis via servidor `tdn`:

### tdn_search

Pesquisa paginas no TDN por palavra-chave. Retorna uma lista de paginas com IDs, titulos e URLs.

**Quando usar:** Quando o usuario pergunta sobre uma funcao, classe ou conceito do Protheus e a pagina exata e desconhecida.

```
tdn_search(query="FWRest", limit=5)
```

### tdn_fetch

Busca o conteudo completo de uma pagina do TDN em Markdown. Aceita um ID de pagina (dos resultados da pesquisa) ou uma URL completa do TDN.

**Quando usar:** Apos identificar a pagina correta via pesquisa, ou quando o usuario fornece uma URL do TDN.

```
tdn_fetch(source="417696190")
tdn_fetch(source="https://tdn.totvs.com/display/framework/FWRest")
```

## Fluxo Recomendado

1. Quando o usuario perguntar sobre um topico do Protheus, usar `tdn_search` para encontrar paginas relevantes
2. Analisar os resultados e identificar a pagina mais relevante
3. Usar `tdn_fetch` para buscar a documentacao completa
4. Resumir as informacoes principais para o usuario, citando a URL de origem

## Dicas

- Pesquisar pelo nome da funcao/classe para resultados precisos (ex: "FWRest", "TReport", "MsExecAuto")
- Pesquisar por topico para resultados mais amplos (ex: "REST API", "relatorio", "ponto de entrada")
- O conteudo do TDN esta em portugues; termos em portugues geralmente retornam melhores resultados
- Paginas grandes podem retornar Markdown extenso; focar nas secoes relevantes para a pergunta do usuario
- Sempre fornecer a URL de origem para que o usuario possa visitar a pagina completa se necessario
