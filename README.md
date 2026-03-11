# claude-tdn

Plugins para desenvolvimento [TOTVS Protheus](https://www.totvs.com/protheus/) com [Claude Code](https://docs.anthropic.com/en/docs/claude-code): documentacao TDN e toolkit ADVPL/TLPP.

## Plugins disponiveis

### 1. claude-tdn

Pesquise e consulte a documentacao do [TDN (TOTVS Developer Network)](https://tdn.totvs.com) direto nas suas conversas com o Claude Code.

**Ferramentas:**
- **tdn_search** - Pesquisa paginas no TDN por palavra-chave (ex: "FWRest", "TReport", "MsExecAuto")
- **tdn_fetch** - Busca o conteudo completo de qualquer pagina do TDN em Markdown

### 2. protheus-toolkit

Skills, comandos e padroes para desenvolvimento ADVPL/TLPP no Protheus.

**12 Skills:**

| Skill | Descricao |
|-------|-----------|
| `advpl-debugging` | Diagnostico de erros, logs, performance, locks |
| `advpl-embedded-sql` | BeginSQL/EndSQL, leitura e migracao de queries |
| `advpl-tlpp-language` | Funcoes nativas ADVPL/TLPP e xBase |
| `advpl-tlpp-migration` | Migracao de ADVPL procedural para TLPP OOP |
| `protheus-data-model` | Acesso a dados, queries, dicionarios, tabelas |
| `protheus-jobs` | Jobs agendados, processos batch, multi-thread |
| `protheus-mvc` | MVC Protheus (FWFormModel/FWFormView) |
| `protheus-reports` | Relatorios TReport, Excel, PDF |
| `protheus-rest` | APIs REST servidor e cliente, OAuth2, JSON |
| `protheus-screens` | Telas, dialogs, browses, grids editaveis |
| `teste-de-mesa` | Analise estatica de execucao simulada |
| `tlpp-classes` | Templates de classes TLPP/ADVPL |

**3 Slash Commands:**

| Comando | Descricao |
|---------|-----------|
| `/diagnose` | Diagnostico estruturado de erros |
| `/generate` | Gera codigo ADVPL/TLPP por tipo |
| `/migrate` | Workflow de migracao ADVPL para TLPP |

## Instalacao

### 1. Pre-requisitos

- **Claude Code** instalado
- **Python 3.9+** (necessario apenas para o plugin claude-tdn)

### 2. Adicionar o marketplace

```
/plugin marketplace add Johnnni/claude-tdn
```

### 3. Instalar os plugins

Instale um ou ambos:

```
/plugin install claude-tdn@claude-tdn
/plugin install protheus-toolkit@claude-tdn
```

### 4. Setup do claude-tdn (apenas se instalou o plugin de documentacao)

Rode o script para instalar as dependencias Python:

```bash
bash ~/.claude/plugins/cache/claude-tdn/claude-tdn/*/scripts/setup.sh
```

### 5. Reiniciar o Claude Code

Feche e reabra o Claude Code (ou inicie uma nova sessao) para ativar.

## Como usar

### Documentacao TDN

Pergunte naturalmente:

- "Busca a documentacao do FWRest no TDN"
- "O que faz a classe TReport?"
- "Como usar o MsExecAuto?"

### Protheus Toolkit

As skills sao ativadas automaticamente conforme o contexto:

- "Cria um Job de integracao" → skill `protheus-jobs`
- "Faz um endpoint REST" → skill `protheus-rest`
- "Cria um cadastro MVC master-detail" → skill `protheus-mvc`
- "Migra esse .prw pra TLPP" → skill `advpl-tlpp-migration`
- "Tem algum bug aqui?" → skill `teste-de-mesa`

Ou use os slash commands diretamente: `/diagnose`, `/generate`, `/migrate`.

## Resolucao de problemas

### "Virtual environment not found" (claude-tdn)

```bash
bash ~/.claude/plugins/cache/claude-tdn/claude-tdn/*/scripts/setup.sh
```

### Ferramentas ou skills nao aparecem

1. Verifique se o plugin esta instalado: rode `/plugin` no Claude Code
2. Reinicie o Claude Code
3. Para o claude-tdn: confirme que Python 3 esta disponivel (`python3 --version`)

## Creditos

Este projeto utiliza partes substanciais do [advpl-specialist](https://github.com/thalysjuvenal/advpl-specialist), criado por [Thalys Augusto](https://github.com/thalysjuvenal), licenciado sob a [MIT License](https://github.com/thalysjuvenal/advpl-specialist/blob/main/LICENSE).

## Licenca

MIT - Veja o arquivo [LICENSE](LICENSE) para detalhes e o arquivo [NOTICE](NOTICE) para atribuicoes de terceiros.

## Autor

[Johnnni](https://github.com/Johnnni)
