---
name: patch
description: Gera patch PTM/UPD/PAK dos fontes compilados no servidor Protheus do projeto atual
arguments:
  - name: args
    description: Nome do patch e/ou arquivos (opcional)
    required: false
---

Gere um patch dos fontes no servidor Protheus do projeto atual.

## Instrucoes

### 1. Detectar projeto

Identifique o projeto atual pelo diretorio de trabalho. Execute:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tds-discover.sh --detect "$(pwd)"
```

Se nao detectar, liste com `--list` e pergunte ao usuario.

### 2. Identificar recursos

- Se `$ARGUMENTS` especifica nomes de fontes, use-os (ex: `XPTO.tlpp,XPTO2.prw`)
- Se nao, identifique os arquivos .tlpp/.prw editados/compilados na conversa atual
- Os nomes devem incluir a extensao (ex: `meu_fonte.tlpp`)
- Separe multiplos recursos com virgula

### 3. Nome do patch

- Se `$ARGUMENTS` inclui um nome (palavra sem extensao .tlpp/.prw), use-o
- Caso contrario, sugira um nome baseado no contexto:
  - Nome da rotina principal (ex: `MATA010`)
  - Descricao curta do que foi feito (ex: `fix_validacao_nf`)
  - Nome do ticket se mencionado na conversa
- Pergunte ao usuario: "Sugiro o nome `<sugestao>`. Quer usar esse ou prefere outro?"
- O sufixo `_AAAAMMDD_HHMMSS` sera adicionado automaticamente pelo script

### 4. Verificar credenciais

Mesmo fluxo do `/compile` — verificar se existem credenciais para o servidor, pedir senha se nao existir.

### 5. Gerar patch

Execute:
```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tds-patch.sh <PROJETO> <recursos> <nomePatch> PTM
```

### 6. Reportar

Mostre o caminho completo do patch gerado, incluindo o nome final com timestamp.

## Exemplo de uso

- `/patch` — gera patch dos fontes da conversa, sugere nome
- `/patch XPTO.tlpp MeuPatch` — gera patch com nome especifico
- `/patch XPTO.tlpp,XPTO2.prw CorrecaoNF` — multiplos fontes com nome
