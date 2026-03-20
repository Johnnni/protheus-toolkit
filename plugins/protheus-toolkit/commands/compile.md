---
name: compile
description: Compila fontes ADVPL/TLPP no servidor Protheus do projeto atual via TDS-CLI
arguments:
  - name: files
    description: Arquivos para compilar (opcional - usa o arquivo atual se omitido). Pode incluir nome do servidor/ambiente no final (ex: "XPTO.prw local2410")
    required: false
---

Compile os fontes solicitados no servidor Protheus associado ao projeto atual.

## Instrucoes

### 1. Detectar projeto

**IMPORTANTE:** Se o usuario especificou um nome de servidor ou ambiente nos argumentos ou na mensagem
(ex: "compile no local2410", "compile no ambiente X"), esse nome tem PRIORIDADE sobre a deteccao automatica.

**Com servidor especificado pelo usuario:**

1. Execute `--list` para obter todos os projetos disponiveis
2. Faca match do nome informado pelo usuario contra os nomes de servidor listados (coluna do meio, case-insensitive)
3. Use o projeto correspondente

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tds-discover.sh --list
```

**Sem servidor especificado (deteccao automatica):**

Identifique o projeto atual pelo diretorio de trabalho. Execute:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tds-discover.sh --detect "$(pwd)"
```

Se o cache nao existir, execute `--refresh` primeiro. Se nao detectar projeto, liste os disponiveis com `--list` e pergunte ao usuario.

### 2. Identificar arquivos

- Se `$ARGUMENTS` especifica arquivos, use-os
- Se nao, use o(s) arquivo(s) .tlpp/.prw que foram editados na conversa atual
- Converta caminhos relativos para absolutos
- Separe multiplos arquivos com virgula

### 3. Verificar credenciais

Execute:
```bash
source ${CLAUDE_PLUGIN_ROOT}/scripts/tds-discover.sh
source ${CLAUDE_PLUGIN_ROOT}/scripts/tds-credentials.sh
SERVER_ID=$(tds_get project <PROJETO> serverId)
cred_exists "$SERVER_ID" && echo "ok" || echo "sem credencial"
```

Se nao existir credencial, pergunte a senha ao usuario com AskUserQuestion e salve:
```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tds-credentials.sh save "$SERVER_ID" "<senha>"
```

### 4. Compilar

Execute:
```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tds-compile.sh <PROJETO> <arquivos> T
```

### 5. Reportar resultado

Mostre se compilou com sucesso ou os erros encontrados. Se houver erro de autenticacao, pergunte a senha novamente.

## Exemplo de uso

- `/compile` — compila os arquivos editados na conversa (servidor detectado pelo diretorio)
- `/compile C:/PROJETOS/ASCENSUS/fontes/XPTO.tlpp` — compila arquivo especifico
- `/compile XPTO.tlpp,XPTO2.prw` — compila multiplos arquivos
- `/compile XPTO.tlpp local2410` — compila no servidor LOCAL2410 (ignora deteccao automatica)
- `/compile local2410` — compila arquivos da conversa no servidor LOCAL2410
