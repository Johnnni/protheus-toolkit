# Design: Documentacao protheus-toolkit com Starlight

**Data:** 2026-03-15
**Status:** Aprovado

## Tecnologia

- **Astro + Starlight** — site estatico, deploy via GitHub Actions no GitHub Pages
- **URL:** `johnnni.github.io/protheus-toolkit/`

## Paleta de cores

- Primaria: azul escuro (#1a365d)
- Fundo: preto/cinza escuro (#0d1117, #161b22)
- Acento: verde escuro (#1a4d2e)
- Texto: cinza claro (#e6edf3)
- Dark mode como padrao

## Estrutura do site

```
Home (hero + features overview)
├── Instalacao
│   └── Pre-requisitos, marketplace, setup MCP, TDS-CLI
├── Skills (index com todas as 16)
│   ├── advpl-debugging
│   ├── advpl-embedded-sql
│   ├── advpl-tlpp-language
│   ├── advpl-tlpp-migration
│   ├── protheus-data-model
│   ├── protheus-jobs
│   ├── protheus-mvc
│   ├── protheus-reports
│   ├── protheus-rest
│   ├── protheus-screens
│   ├── teste-de-mesa
│   ├── tlpp-classes
│   ├── code-review
│   ├── probat-testing
│   ├── tir-tests
│   └── business-modules
├── Commands (pagina unica com todos os 11)
├── Agents (pagina unica com os 7)
├── MCP Tools
│   └── tdn_search, tdn_fetch, dicionario_fetch
└── TDS-CLI
    └── Validacao, /compile, /patch, credentials
```

## Conteudo das paginas de skills

Cada skill tera:
- Descricao / quando ativa automaticamente
- Exemplos de uso (frases que ativam a skill)
- Principais padroes e templates que ela oferece

## Idioma

Portugues com termos tecnicos em ingles.

## Deploy

GitHub Actions workflow — build automatico no push da branch `master`, deploy no GitHub Pages.

## Publico-alvo

Desenvolvedores Protheus que querem instalar e usar o plugin.
