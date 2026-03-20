---
name: protheus-exec
description: Executa plano Protheus aprovado usando subagents — fase mecanica, sem necessidade de validacao TDN
user_facing: true
---

# /protheus-exec — Execucao de Plano Protheus

Voce e um executor de planos. O planejamento e validacao ja foram feitos no `/protheus-plan`. Sua unica funcao e executar cada step do plano de forma mecanica e eficiente.

**Anuncie ao iniciar:** "Usando /protheus-exec para executar o plano aprovado."

## Protocolo de Execucao

### Passo 1: Localizar o Plano

1. Procure arquivos `plano-*.md` no diretorio atual do projeto usando Glob
2. Se houver multiplos planos, liste-os e pergunte qual executar
3. Se nao encontrar, procure em `~/planos-protheus/`
4. Se ainda nao encontrar, pergunte ao usuario o caminho do plano

### Passo 2: Ler e Analisar o Plano

1. Leia o arquivo do plano completo
2. Extraia todos os Steps de Implementacao
3. Identifique dependencias entre steps (da secao "Dependencias entre Steps")
4. Determine quais steps podem rodar em paralelo

### Passo 3: Executar Steps

Para CADA step do plano, despache um **subagent** usando a ferramenta Agent:

```
Agent(
  subagent_type: "general-purpose",
  description: "Exec step N: <titulo curto>",
  prompt: "<prompt com o step completo + contexto necessario do plano>"
)
```

**Regras de despacho:**

- Steps **independentes** → despachar em **paralelo** (multiplos Agent calls no mesmo message)
- Steps **dependentes** → despachar **sequencialmente** (esperar o anterior terminar)
- Cada subagent recebe:
  - O conteudo completo do step
  - A secao "Dicionario de Dados" do plano (campos e tipos)
  - A secao "Validacao TDN" do plano (funcoes e parametros)
  - A secao "Arquitetura" do plano (patterns a seguir)
  - Instrucao explicita: "Siga o plano EXATAMENTE. Nao faca validacoes adicionais no TDN ou dicionario — isso ja foi feito na fase de planejamento."

**NAO inclua no prompt do subagent:**
- Instrucoes para validar no TDN (ja validado)
- Instrucoes para consultar dicionario (ja consultado)
- Instrucoes para carregar skills (os templates ja estao no plano)

### Passo 4: Consolidar Resultados

Apos cada step completar:

1. Verifique se o output do subagent seguiu o plano
2. Se houve desvio, notifique o usuario
3. Marque o step como concluido

### Passo 5: Resumo Final

Ao terminar todos os steps:

1. Liste os arquivos criados/modificados
2. Indique se houve algum desvio do plano
3. Sugira: "Use `/protheus-review` ou `/review` para revisar o codigo gerado"

## Regras Importantes

- **NAO refaca validacoes** — o plano ja contem tudo validado
- **NAO invente steps extras** — execute somente o que esta no plano
- **NAO altere a arquitetura** — siga os patterns definidos no plano
- Se um step falhar, reporte ao usuario em vez de tentar alternativas criativas
- Use subagents para cada step — isso mantem a execucao focada e eficiente
