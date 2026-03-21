# protheus-toolkit

Plugin para desenvolvimento [TOTVS Protheus](https://www.totvs.com/protheus/) com [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — skills, agents, commands e hooks para ADVPL/TLPP, com servidor MCP integrado para consulta de documentacao TDN e dicionario de dados.

## O que faz

O protheus-toolkit transforma o Claude Code num assistente especializado em Protheus. Ao instalar, voce ganha:

- **15 skills** que ativam automaticamente conforme o contexto da conversa
- **6 agents** context-aware com checklist de validacao automatica
- **10 slash commands** para workflows estruturados
- **3 hooks** de automacao (validacao sintatica, deteccao de projeto, encoding ASCII)
- **Servidor MCP** com 3 tools para consultar documentacao TDN e dicionario de tabelas em tempo real
- **TDS-CLI integration** para compilar, gerar patches e validar sintaxe direto pelo Claude Code

## Skills

As skills sao ativadas automaticamente conforme o que voce pede:

| Skill | Descricao |
|-------|-----------|
| `advpl-debugging` | Diagnostico de erros, logs, performance, locks |
| `advpl-embedded-sql` | BeginSQL/EndSQL, leitura e migracao de queries |
| `advpl-tlpp-language` | Funcoes nativas ADVPL/TLPP e xBase |
| `advpl-tlpp-migration` | Migracao de ADVPL procedural para TLPP OOP |
| `protheus-data-model` | Acesso a dados, queries, dicionario (10.630 tabelas) |
| `protheus-jobs` | Jobs agendados, processos batch, multi-thread |
| `protheus-mvc` | MVC Protheus (FWFormModel/FWFormView), 4 tipos de modelo |
| `protheus-reports` | Relatorios TReport, Excel, PDF |
| `protheus-rest` | APIs REST servidor e cliente, OAuth2, JSON |
| `protheus-screens` | Telas, dialogs, browses, grids editaveis |
| `teste-de-mesa` | Analise estatica de execucao simulada |
| `tlpp-classes` | Templates de classes TLPP/ADVPL |
| `code-review` | Code review com regras de qualidade, seguranca, performance |
| `tir-tests` | Testes automatizados TIR (TOTVS Interface Robot) via browser |
| `business-modules` | 8 modulos de negocio (Compras, Faturamento, Financeiro, Estoque, Fiscal, Contabilidade, Manutencao, PCP) |

## Agents

Agentes especializados com checklist de validacao automatica de 13 pontos:

| Agent | Funcao |
|-------|--------|
| Code Generator | Gera codigo com validacao automatica |
| Code Reviewer | Revisa qualidade, seguranca, performance |
| Debugger | Diagnostica erros sistematicamente |
| Migrator | Guia migracao ADVPL → TLPP |
| Docs Reference | Consulta documentacao TDN |
| Process Consultant | Orientacao de processos de negocio |

## Slash Commands

| Comando | Descricao |
|---------|-----------|
| `/protheus` | Roteador — direciona para skill/agent adequado |
| `/diagnose` | Diagnostico estruturado de erros |
| `/debug` | Debugging interativo |
| `/generate` | Geracao de codigo por tipo |
| `/migrate` | Workflow de migracao ADVPL → TLPP |
| `/review` | Code review |
| `/docs` | Consulta documentacao TDN |
| `/process` | Modelagem de processos de negocio |
| `/compile` | Compila fontes via TDS-CLI |
| `/patch` | Gera patch PTM via TDS-CLI |

## Servidor MCP

O protheus-toolkit inclui um servidor MCP (Model Context Protocol) que extende as capacidades do plugin com acesso a dados externos em tempo real:

| Tool | Descricao |
|------|-----------|
| `tdn_search` | Pesquisa paginas no TDN por palavra-chave (ex: "FWRest", "TReport") |
| `tdn_fetch` | Busca conteudo completo de pagina do TDN em Markdown |
| `dicionario_fetch` | Busca estrutura de tabela do dicionario Protheus (campos, indices, gatilhos) |

O servidor roda em Python com FastMCP e requer setup inicial (veja instalacao).

## TDS-CLI Integration

Integracao com o TDS-LS CLI (`advpls`) para operacoes diretas no servidor Protheus:

- **Validacao sintatica automatica** — hook PostToolUse roda `advpls appre` apos cada edicao de .tlpp/.prw
- **Compilacao** — `/compile` compila fontes no servidor do projeto
- **Geracao de patches** — `/patch` gera PTM com sufixo de timestamp
- **Credenciais seguras** — senhas criptografadas com Windows DPAPI
- **Auto-discovery** — detecta automaticamente o `advpls.exe` e mapeia projetos aos servidores

## Hooks

| Hook | Evento | Funcao |
|------|--------|--------|
| `check-ascii.sh` | PostToolUse | Valida encoding ASCII em arquivos .prw/.tlpp |
| `post-edit-validate.sh` | PostToolUse | Validacao sintatica via `advpls appre` |
| `session-start.md` | SessionStart | Detecta tipo do projeto e sugere skills relevantes |

## Instalacao

### Pre-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) instalado
- Python 3.9+ (para o servidor MCP)

### 1. Adicionar o marketplace

```
/plugin marketplace add Johnnni/protheus-toolkit
```

### 2. Instalar o plugin

```
/plugin install protheus-toolkit@protheus-toolkit
```

### 3. Setup do servidor MCP

```bash
bash ~/.claude/plugins/cache/protheus-toolkit/protheus-toolkit/*/plugins/claude-tdn/scripts/setup.sh
```

### 4. Reiniciar o Claude Code

Feche e reabra o Claude Code (ou inicie nova sessao) para ativar.

## Como usar

As skills ativam automaticamente pelo contexto da conversa:

- "Cria um Job de integracao" → skill `protheus-jobs`
- "Faz um endpoint REST" → skill `protheus-rest`
- "Cria um cadastro MVC master-detail" → skill `protheus-mvc`
- "Migra esse .prw pra TLPP" → skill `advpl-tlpp-migration`
- "Tem algum bug aqui?" → skill `teste-de-mesa`
- "Busca a documentacao do FWRest no TDN" → tool `tdn_search` + `tdn_fetch`
- "Qual a estrutura da SA1?" → tool `dicionario_fetch`

Ou use os slash commands diretamente: `/diagnose`, `/generate`, `/migrate`, `/compile`, `/patch`, etc.

## Resolucao de problemas

### "Virtual environment not found"

```bash
bash ~/.claude/plugins/cache/protheus-toolkit/protheus-toolkit/*/plugins/claude-tdn/scripts/setup.sh
```

### Ferramentas MCP nao aparecem

1. Verifique se o plugin esta instalado: rode `/plugin` no Claude Code
2. Reinicie o Claude Code
3. Confirme que Python 3 esta disponivel (`python3 --version`)

### TDS-CLI nao encontrado

O `advpls.exe` e descoberto automaticamente na extensao TDS do VS Code. Verifique se a extensao `totvs.tds-vscode` esta instalada.

## Creditos

Alguns agents e skills (code-review, business-modules) foram inspirados e extendidos a partir do [advpl-specialist](https://github.com/thalysjuvenal/advpl-specialist), criado por [Thalys Augusto](https://github.com/thalysjuvenal), licenciado sob a [MIT License](https://github.com/thalysjuvenal/advpl-specialist/blob/main/LICENSE). Veja o arquivo [NOTICE](NOTICE) para detalhes.

## Licenca

MIT - Veja o arquivo [LICENSE](LICENSE) para detalhes e o arquivo [NOTICE](NOTICE) para atribuicoes de terceiros.

## Autor

[Johnnni](https://github.com/Johnnni)
