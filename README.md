# claude-tdn

Pesquise e consulte a documentacao do [TOTVS Protheus](https://www.totvs.com/protheus/) direto do [TDN (TOTVS Developer Network)](https://tdn.totvs.com) nas suas conversas com o Claude Code.

## O que faz

Este plugin da ao Claude Code duas ferramentas:

- **tdn_search** - Pesquisa paginas no TDN por palavra-chave (ex: "FWRest", "TReport", "MsExecAuto")
- **tdn_fetch** - Busca o conteudo completo de qualquer pagina do TDN em Markdown

Basta perguntar ao Claude sobre qualquer funcao, classe ou conceito do Protheus, e ele automaticamente pesquisa no TDN e traz a documentacao para a conversa.

## Instalacao

### 1. Pre-requisitos

Voce precisa do **Python 3.9+** instalado:

- **Linux/WSL**: Geralmente ja vem instalado. Verifique com `python3 --version`
- **macOS**: `brew install python3`
- **Windows**: Baixe em [python.org](https://www.python.org/downloads/)

### 2. Adicionar o marketplace

No Claude Code, rode:

```
/plugin marketplace add Johnnni/claude-tdn
```

### 3. Instalar o plugin

```
/plugin install claude-tdn@Johnnni-claude-tdn
```

Ou pelo menu interativo: rode `/plugin` > aba **Marketplaces** > adicione `Johnnni/claude-tdn` > aba **Discover** > instale.

### 4. Rodar o setup

Apos instalar o plugin, rode o script de setup para instalar as dependencias Python:

```bash
bash ~/.claude/plugins/cache/claude-tdn/claude-tdn/*/scripts/setup.sh
```

### 5. Reiniciar o Claude Code

Feche e reabra o Claude Code (ou inicie uma nova sessao) para ativar as ferramentas do TDN.

## Como usar

Pergunte naturalmente:

- "Busca a documentacao do FWRest no TDN"
- "O que faz a classe TReport?"
- "Como usar o MsExecAuto?"
- "Quais os parametros do DbSelectArea?"
- "Pesquisa no TDN sobre ponto de entrada"

O Claude vai automaticamente pesquisar no TDN e mostrar a documentacao relevante.

## Como funciona

O plugin roda um servidor MCP local em Python que:

1. Usa a API REST do Confluence (TDN) para pesquisar paginas
2. Busca o HTML fonte da pagina e converte para Markdown limpo
3. Retorna o conteudo para o Claude Code analisar

## Resolucao de problemas

### "Virtual environment not found"

Rode o script de setup:
```bash
bash ~/.claude/plugins/cache/claude-tdn/claude-tdn/*/scripts/setup.sh
```

### Ferramentas nao aparecem

1. Verifique se o plugin esta instalado: rode `/mcp` no Claude Code
2. Reinicie o Claude Code
3. Confirme que o Python 3 esta disponivel: `python3 --version`

### Pesquisa nao retorna resultados

- Tente palavras-chave diferentes
- Use o nome exato da funcao/classe
- Verifique sua conexao com a internet

## Licenca

MIT

## Autor

[Johnnni](https://github.com/Johnnni)
