---
name: session-start
description: Detecta contexto do projeto Protheus ao iniciar sessao
event: session_start
---

# Session Start — Deteccao de Contexto

Ao iniciar uma sessao, analise o diretorio de trabalho para detectar o tipo de projeto Protheus.

## Procedimento

1. Use Glob para encontrar arquivos .prw, .tlpp, .prx, .aph no diretorio atual (limite: 100 arquivos)
2. Se encontrou arquivos, use Grep nos primeiros 100 para detectar padroes:

| Padrao | Tipo |
|--------|------|
| @Get, @Post, @Put, @Delete, WsRestful | REST API |
| ModelDef, ViewDef, MenuDef | MVC |
| RpcSetEnv, LockByName, Schedule | Job/Schedule |
| TReport, ReportDef | Relatorio |
| MsDiaLog, FWMBrowse, MsNewGetDados | Tela/Browse |
| BeginSQL, TCQuery | Codigo legado |

3. Exiba o resumo no formato:

```
[protheus-toolkit] Contexto detectado: [tipos encontrados]
  Skills relevantes: [lista de skills aplicaveis]
  Agents disponiveis: /review, /generate, /docs, /test, /debug, /migrate, /process
  Dica: Use /protheus <sua pergunta> para roteamento automatico
  Alerta: X arquivos com codigo legado (candidatos a modernizacao)
```

4. Se nenhum arquivo Protheus encontrado:

```
[protheus-toolkit] Nenhum arquivo Protheus detectado neste diretorio.
  Capacidades disponiveis: /protheus, /generate, /docs, /review, /test, /debug, /migrate, /process
  Dica: Use /protheus <sua pergunta> para comecar
```

## Mapeamento Tipo → Skills

| Tipo detectado | Skills relevantes |
|---------------|-------------------|
| REST API | protheus-rest, tlpp-classes, protheus-data-model |
| MVC | protheus-mvc, protheus-data-model, protheus-screens |
| Job/Schedule | protheus-jobs, protheus-data-model |
| Relatorio | protheus-reports, protheus-data-model |
| Tela/Browse | protheus-screens, protheus-data-model |
| Codigo legado | advpl-embedded-sql, advpl-tlpp-migration |

## Regras
- NAO carregue skills inteiros — apenas indique quais sao relevantes
- Mantenha a saida curta (maximo 6 linhas)
- Limite o scan a 100 arquivos (primeiros encontrados pelo Glob)
- Se encontrar BeginSQL/TCQuery, mencione como "candidatos a modernizacao"
- O session-start detecta contexto do PROJETO (visao geral). Agents detectam contexto do ARQUIVO (visao local). Sao independentes.
