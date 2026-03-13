---
name: probat-testing
description: Framework ProBat de testes automatizados para ADVPL/TLPP no Protheus. Cobertura completa de padroes, assertions, templates e boas praticas para criacao de testes unitarios e de integracao.
---

# ProBat Testing Framework para ADVPL/TLPP

## 1. Visao Geral do Framework

O **ProBat** e o framework oficial da TOTVS para testes automatizados no ambiente Protheus. Ele permite a criacao de testes unitarios, de integracao e funcionais para codigo ADVPL e TLPP.

### Conceitos Fundamentais

- **Framework oficial**: ProBat e mantido pela TOTVS e integrado ao ecossistema Protheus
- **Classe principal**: `FWTestSuite` -- gerencia a suite de testes, registra casos e coleta resultados
- **Execucao**: Testes podem ser executados via SmartClient, REST API ou pipeline CI/CD
- **Relatorios**: O framework gera relatorios automaticos com resultados de cada assertion

### Convencoes de Nomenclatura

| Elemento | Convencao | Exemplo |
|---|---|---|
| Arquivo de teste | `*_test.prw` ou `*_test.tlpp` | `calculo_desconto_test.prw` |
| Funcao de entrada | `U_<NomeTest>()` | `User Function CalcDesc_Test()` |
| Funcao de caso | `Test_<Descricao>()` | `Static Function Test_CalcValor()` |
| Prefixo de dados | `ZZZ_TEST_` | `ZZZ_TEST_CLI001` |

### Estrutura Minima Obrigatoria

Todo arquivo de teste deve conter:

1. `#include "Protheus.ch"` -- include obrigatorio
2. Uma `User Function` que retorna `oResult` -- ponto de entrada do ProBat
3. Instancia de `FWTestSuite` -- gerenciador da suite
4. Pelo menos um teste registrado com `AddTest()`
5. Chamada a `oResult:Run()` antes do `Return`

### Ciclo de Vida da Execucao

```
1. ProBat localiza funcoes U_*_Test()
2. Executa a User Function
3. FWTestSuite:New() cria a suite
4. AddTest() registra cada caso de teste
5. Run() executa todos os casos registrados
6. Cada caso chama assertions (IsEqual, IsTrue, etc.)
7. oResult acumula resultados (pass/fail)
8. Return oResult devolve ao ProBat para relatorio
```

---

## 2. Estrutura de Teste Completa

O exemplo abaixo demonstra a estrutura padrao de um teste ProBat funcional:

```advpl
#include "Protheus.ch"

/*/{Protheus.doc} XPTO_Test
Testes para a funcao de calculo de desconto U_CalcDesconto.
@type Function
@author Equipe Desenvolvimento
@since 01/01/2025
/*/
User Function XPTO_Test()
    Local oResult := FWTestSuite():New("XPTO Tests")

    oResult:AddTest("Deve calcular valor correto", {|| Test_CalcValor(oResult)})
    oResult:AddTest("Deve rejeitar valor negativo", {|| Test_ValorNeg(oResult)})

    oResult:Run()
Return oResult

Static Function Test_CalcValor(oResult)
    Local nValor := U_CalcDesconto(100, 10) // 10% de 100
    oResult:IsEqual(nValor, 90, "Desconto de 10% sobre 100 deve resultar 90")
Return

Static Function Test_ValorNeg(oResult)
    Local nValor := U_CalcDesconto(-50, 10)
    oResult:IsEqual(nValor, 0, "Valor negativo deve retornar zero")
Return
```

### Explicacao dos Componentes

- **`FWTestSuite():New("Nome")`**: Cria uma nova suite de testes com nome descritivo
- **`AddTest(descricao, bloco)`**: Registra um caso de teste com descricao legivel e code block
- **`Run()`**: Executa todos os casos registrados na ordem de adicao
- **`Return oResult`**: Retorna o objeto com resultados para o ProBat processar

---

## 3. Assertions Disponiveis

O `FWTestSuite` oferece 6 metodos de assertion para validacao:

### 3.1 IsEqual(valor, esperado, mensagem)

Verifica se dois valores sao iguais. Funciona com numeros, strings, datas e logicos.

```advpl
// Comparacao numerica
oResult:IsEqual(nTotal, 150.00, "Total do pedido deve ser 150.00")

// Comparacao de string
oResult:IsEqual(cStatus, "OK", "Status da operacao deve ser OK")

// Comparacao de data
oResult:IsEqual(dVenc, dDataBase + 30, "Vencimento deve ser 30 dias apos database")

// Comparacao logica
oResult:IsEqual(lAtivo, .T., "Cliente deve estar ativo apos cadastro")
```

### 3.2 IsTrue(expressao, mensagem)

Verifica se uma expressao resulta em `.T.` (verdadeiro).

```advpl
// Verificar se valor esta dentro de faixa
oResult:IsTrue(nDesconto >= 0 .And. nDesconto <= 100, "Desconto deve estar entre 0 e 100")

// Verificar existencia de registro
oResult:IsTrue(SA1->(dbSeek(xFilial("SA1") + cCodCli)), "Cliente deve existir na base")

// Verificar se string contem substring
oResult:IsTrue("ERRO" $ cMensagem, "Mensagem deve conter a palavra ERRO")
```

### 3.3 IsFalse(expressao, mensagem)

Verifica se uma expressao resulta em `.F.` (falso).

```advpl
// Verificar que operacao invalida nao foi aceita
oResult:IsFalse(lResultado, "Operacao com dados invalidos nao deve ser aceita")

// Verificar que registro nao existe
oResult:IsFalse(SA1->(dbSeek(xFilial("SA1") + "ZZZ999")), "Cliente inexistente nao deve ser encontrado")

// Verificar que lista esta vazia
oResult:IsFalse(Len(aErros) > 0, "Nao deve haver erros na validacao")
```

### 3.4 IsNil(valor, mensagem)

Verifica se um valor e NIL (nulo/nao atribuido).

```advpl
// Verificar retorno nulo para busca sem resultado
Local xRet := U_BuscaCliente("INEXISTENTE")
oResult:IsNil(xRet, "Busca por cliente inexistente deve retornar NIL")

// Verificar que campo opcional nao foi preenchido
oResult:IsNil(cObs, "Campo observacao deve ser NIL quando nao informado")
```

### 3.5 IsNotNil(valor, mensagem)

Verifica se um valor NAO e NIL.

```advpl
// Verificar que objeto foi criado
Local oModel := FWLoadModel("COMP011MVC")
oResult:IsNotNil(oModel, "Model MVC deve ser instanciado com sucesso")

// Verificar que funcao retornou valor
Local cResult := U_GeraProtocolo()
oResult:IsNotNil(cResult, "Geracao de protocolo deve retornar valor")
```

### 3.6 HasError(bloco, mensagem)

Verifica se um bloco de codigo gera erro (excecao). Util para testar tratamento de erros.

```advpl
// Verificar que divisao por zero gera erro
oResult:HasError({|| U_Dividir(100, 0)}, "Divisao por zero deve gerar erro controlado")

// Verificar que parametro invalido gera erro
oResult:HasError({|| U_CriaCliente("")}, "Criar cliente sem codigo deve gerar erro")

// Verificar que acesso invalido gera erro
oResult:HasError({|| U_AcessarModulo("INVALIDO")}, "Acesso a modulo invalido deve gerar erro")
```

---

## 4. Padrao Setup/Teardown

Para testes que necessitam de dados no banco, utilize o padrao Setup/Teardown para criar e limpar dados de teste.

### Exemplo Completo com Setup e Teardown

```advpl
#include "Protheus.ch"

User Function CadCli_Test()
    Local oResult := FWTestSuite():New("Cadastro Cliente Tests")

    oResult:AddTest("Deve incluir cliente com sucesso", {|| Test_IncluiCli(oResult)})
    oResult:AddTest("Deve rejeitar CNPJ duplicado", {|| Test_CNPJDup(oResult)})

    oResult:Run()
Return oResult

// ----------------------------------------------------------------
// Setup: cria registros de teste no banco
// ----------------------------------------------------------------
Static Function Setup_Cliente()
    Local cFilial := xFilial("SA1")

    // Cria cliente de teste com prefixo ZZZ_TEST_
    SA1->(dbSetOrder(1))
    If !SA1->(dbSeek(cFilial + "ZZZ_TEST_001" + "01"))
        RecLock("SA1", .T.)
            SA1->A1_FILIAL := cFilial
            SA1->A1_COD    := "ZZZ_TEST_001"
            SA1->A1_LOJA   := "01"
            SA1->A1_NOME   := "ZZZ_TEST_CLIENTE TESTE PROBAT"
            SA1->A1_NREDUZ := "ZZZ_TEST_CLI"
            SA1->A1_TIPO   := "F"
            SA1->A1_CGC    := "00000000191"
            SA1->A1_END    := "RUA TESTE PROBAT 123"
            SA1->A1_MUN    := "SAO PAULO"
            SA1->A1_EST    := "SP"
        SA1->(MsUnlock())
    EndIf
Return

// ----------------------------------------------------------------
// Teardown: remove TODOS os registros de teste via SQL
// ----------------------------------------------------------------
Static Function Teardown_Cliente()
    // Remove todos os registros com prefixo ZZZ_TEST_
    TCSqlExec("DELETE FROM " + RetSqlName("SA1") + " WHERE A1_COD LIKE 'ZZZ_TEST_%'")

    // Garante que nao ficou lixo em tabelas relacionadas
    TCSqlExec("DELETE FROM " + RetSqlName("SA2") + " WHERE A2_COD LIKE 'ZZZ_TEST_%'")
Return

Static Function Test_IncluiCli(oResult)
    // Setup
    Teardown_Cliente() // Limpa antes para garantir estado limpo
    Setup_Cliente()

    // Execucao
    SA1->(dbSetOrder(1))
    Local lFound := SA1->(dbSeek(xFilial("SA1") + "ZZZ_TEST_001" + "01"))

    // Assertions
    oResult:IsTrue(lFound, "Cliente ZZZ_TEST_001 deve existir apos inclusao")
    oResult:IsEqual(SA1->A1_NOME, "ZZZ_TEST_CLIENTE TESTE PROBAT", "Nome do cliente deve ser o cadastrado")

    // Teardown
    Teardown_Cliente()
Return

Static Function Test_CNPJDup(oResult)
    // Setup
    Teardown_Cliente()
    Setup_Cliente()

    // Execucao: tenta incluir outro cliente com mesmo CNPJ
    Local lResult := U_IncluiCliente("ZZZ_TEST_002", "01", "00000000191")

    // Assertions
    oResult:IsFalse(lResult, "Inclusao com CNPJ duplicado nao deve ser aceita")

    // Teardown
    Teardown_Cliente()
Return
```

### Regras do Setup/Teardown

1. **Sempre limpe antes E depois**: Chame Teardown no inicio e no fim de cada teste
2. **Prefixo obrigatorio**: Todo dado de teste usa `ZZZ_TEST_` para facil identificacao
3. **SQL para limpeza**: Use `TCSqlExec` com `DELETE` e filtro `LIKE 'ZZZ_TEST_%'`
4. **Sem dependencia entre testes**: Cada teste cria seus proprios dados
5. **RecLock para criacao**: Use `RecLock(tabela, .T.)` para inserir registros

---

## 5. Templates por Tipo de Teste

O ProBat suporta diversos tipos de teste. Cada tipo possui um template especifico com estrutura otimizada.

> **Nota**: Codigo completo de cada template esta disponivel em `references/test-patterns.md`

### 5.1 Teste de Funcao Pura

Testa funcoes que recebem parametros e retornam valores sem efeitos colaterais (sem acesso a banco, sem gravacao). Ideal para funcoes de calculo, validacao de formato, conversao de dados.

- Nao requer Setup/Teardown
- Assertions diretas no retorno da funcao
- Execucao rapida e isolada

### 5.2 Teste de Acesso a Dados

Testa funcoes que leem ou gravam registros no banco de dados. Requer criacao previa de dados de teste e limpeza posterior.

- Setup cria registros com prefixo `ZZZ_TEST_`
- Funcao sob teste opera sobre os dados criados
- Teardown remove registros via `TCSqlExec DELETE`

### 5.3 Teste de Endpoint REST

Testa metodos REST do Protheus chamando a funcao diretamente (sem requisicao HTTP). Monta o `JsonObject` de request, chama o metodo e valida status e resposta.

- Cria `JsonObject` simulando o payload de entrada
- Chama a funcao REST diretamente (ex: `U_RSTA001()`)
- Valida status code e campos do JSON de resposta

### 5.4 Teste de Job/Worker

Testa rotinas de processamento em background (Jobs, Schedules, Workers). Prepara o estado no banco, executa a funcao do Job diretamente e verifica o estado resultante.

- Setup prepara dados no estado inicial esperado
- Chama a funcao do Worker diretamente (sem schedule)
- Verifica estado final dos dados apos processamento

### 5.5 Teste de Model MVC

Testa models MVC do Protheus usando `FWLoadModel`. Configura a operacao, define valores nos campos e valida com `VldData()`.

- Carrega o model com `FWLoadModel("ID_DO_MODEL")`
- Define operacao com `SetOperation(MODEL_OPERATION_INSERT)`
- Preenche campos com `SetValue()`
- Valida com `VldData()` e verifica resultado

### 5.6 Teste de Integracao (Multi-Modulo)

Testa fluxos que atravessam multiplos modulos e tabelas. Cria registros em cascata, dispara o processo e verifica efeitos em todas as tabelas envolvidas.

- Setup cria registros em multiplas tabelas (ordem de dependencia)
- Executa o fluxo completo
- Verifica efeitos cascata em todas as tabelas
- Teardown limpa na ordem reversa de criacao

---

## 6. 8 Padroes Obrigatorios

Todo teste ProBat deve seguir estes 8 padroes sem excecao:

### Padrao 1: Testes Devem Ser Independentes

Cada teste deve funcionar isoladamente, sem depender da execucao ou resultado de outro teste.

```advpl
// CORRETO: cada teste cria seus proprios dados
Static Function Test_CalculoFrete(oResult)
    Local nFrete := U_CalcFrete(100.00, "SP", "RJ")
    oResult:IsEqual(nFrete, 15.00, "Frete SP-RJ para 100kg deve ser 15.00")
Return

// ERRADO: depende de variavel de outro teste
Static Function Test_CalculoFrete(oResult)
    // nPeso foi definido em outro teste -- NUNCA faca isso
    oResult:IsEqual(U_CalcFrete(nPeso, cOrigem, cDestino), 15.00, "Frete incorreto")
Return
```

### Padrao 2: Setup Cria Dados, Teardown Limpa Tudo

Nunca deixe dados de teste no banco apos a execucao.

```advpl
// Estrutura obrigatoria para testes com banco
Static Function Test_ComDados(oResult)
    Teardown_Dados()   // Limpa residuos anteriores
    Setup_Dados()      // Cria dados frescos

    // ... execucao e assertions ...

    Teardown_Dados()   // Limpa apos teste
Return
```

### Padrao 3: Nunca Teste Interface (UI)

ProBat testa logica de negocio, nao telas. Nunca use `MsDialog`, `Activate`, `Say`, `Get` em testes.

```advpl
// CORRETO: testa a regra de negocio diretamente
oResult:IsEqual(U_ValidaCPF("12345678909"), .T., "CPF valido deve retornar .T.")

// ERRADO: tenta interagir com tela
oDlg := MsDialog():New() // NUNCA em testes!
```

### Padrao 4: Dados de Teste Usam Prefixo "ZZZ_TEST_"

Todo registro criado para teste deve usar o prefixo `ZZZ_TEST_` em campos-chave.

```advpl
SA1->A1_COD    := "ZZZ_TEST_001"     // Codigo com prefixo
SA1->A1_NOME   := "ZZZ_TEST_FULANO"  // Nome com prefixo
SA1->A1_NREDUZ := "ZZZ_TEST_FUL"     // Nome reduzido com prefixo
```

### Padrao 5: Limpeza via TCSqlExec DELETE com Filtro ZZZ%

A limpeza deve ser feita via SQL direto para garantir remocao completa.

```advpl
// Padrao de limpeza -- sempre use LIKE 'ZZZ_TEST_%'
TCSqlExec("DELETE FROM " + RetSqlName("SA1") + " WHERE A1_COD LIKE 'ZZZ_TEST_%'")
TCSqlExec("DELETE FROM " + RetSqlName("SC5") + " WHERE C5_NUM LIKE 'ZZZ_TEST_%'")
TCSqlExec("DELETE FROM " + RetSqlName("SC6") + " WHERE C6_NUM LIKE 'ZZZ_TEST_%'")
```

### Padrao 6: Teste Caminho Feliz E Caminho de Erro

Todo teste deve cobrir o cenario de sucesso e o cenario de falha.

```advpl
// Caminho feliz
oResult:AddTest("Deve calcular desconto valido", {|| Test_DescontoOk(oResult)})

// Caminho de erro
oResult:AddTest("Deve rejeitar desconto acima de 100%", {|| Test_DescontoInvalido(oResult)})
oResult:AddTest("Deve rejeitar valor negativo", {|| Test_ValorNegativo(oResult)})
```

### Padrao 7: Mensagens de Assertion Descritivas

A mensagem deve descrever o que ERA ESPERADO, nao o que deu errado.

```advpl
// CORRETO: descreve o esperado
oResult:IsEqual(nTotal, 100, "Total do pedido com 2 itens de 50 deve ser 100")

// ERRADO: mensagem vaga
oResult:IsEqual(nTotal, 100, "Erro no total")

// ERRADO: mensagem tecnica demais
oResult:IsEqual(nTotal, 100, "nTotal <> 100")
```

### Padrao 8: Um Assert por Conceito Logico

Cada assertion deve validar UM aspecto logico. Se precisa testar multiplos aspectos, use multiplos testes.

```advpl
// CORRETO: cada teste valida um conceito
Static Function Test_NomeCliente(oResult)
    Local cNome := U_GetNomeCli("001")
    oResult:IsEqual(cNome, "JOAO DA SILVA", "Nome do cliente 001 deve ser JOAO DA SILVA")
Return

Static Function Test_StatusCliente(oResult)
    Local cStatus := U_GetStatusCli("001")
    oResult:IsEqual(cStatus, "A", "Status do cliente 001 deve ser Ativo")
Return

// ERRADO: mistura conceitos no mesmo teste
Static Function Test_Cliente(oResult)
    oResult:IsEqual(U_GetNomeCli("001"), "JOAO DA SILVA", "Nome")
    oResult:IsEqual(U_GetStatusCli("001"), "A", "Status")
    oResult:IsEqual(U_GetSaldoCli("001"), 1000, "Saldo")
Return
```

---

## 7. 7 Anti-Padroes a Evitar

### AP-01: Teste Dependente de Ordem de Execucao

```advpl
// ERRADO: Test_B depende de Test_A ter executado antes
Static Function Test_A(oResult)
    nValorGlobal := 42  // Define variavel global
    oResult:IsTrue(.T., "Setup feito")
Return

Static Function Test_B(oResult)
    oResult:IsEqual(nValorGlobal, 42, "Valor deve ser 42")  // Depende de Test_A!
Return
```

**Correcao**: Cada teste define suas proprias variaveis e dados.

### AP-02: Dados de Teste Permanentes no Banco

```advpl
// ERRADO: cria registro e nunca remove
Static Function Test_CriaCliente(oResult)
    RecLock("SA1", .T.)
        SA1->A1_COD  := "TEST001"
        SA1->A1_NOME := "CLIENTE TESTE"
    SA1->(MsUnlock())
    oResult:IsTrue(.T., "Cliente criado")
    // Cadê o Teardown? Dados ficam no banco para sempre!
Return
```

**Correcao**: Sempre implemente Teardown com `TCSqlExec DELETE`.

### AP-03: Teste de Interface Grafica

```advpl
// ERRADO: tenta criar e manipular dialogo em teste
Static Function Test_Tela(oResult)
    Local oDlg := MsDialog():New(0, 0, 300, 400, "Teste")
    Local oGet := MsGet():New(10, 10, {|| cValor})
    Activate(oDlg)  // Bloqueia execucao esperando input do usuario!
    oResult:IsTrue(.T., "Tela abriu")
Return
```

**Correcao**: Teste apenas a logica de negocio, nunca a interface.

### AP-04: Assert Sem Mensagem Descritiva

```advpl
// ERRADO: mensagens vagas ou ausentes
Static Function Test_Calculo(oResult)
    oResult:IsEqual(nVal, 100, "Erro")
    oResult:IsTrue(lOk, "Falhou")
    oResult:IsEqual(cCod, "A", "")  // Mensagem vazia!
Return
```

**Correcao**: Use mensagens que descrevam o valor esperado e o contexto.

### AP-05: Multiplos Conceitos em Um Unico Teste

```advpl
// ERRADO: testa inclusao, alteracao e exclusao no mesmo teste
Static Function Test_CRUD_Completo(oResult)
    // Inclusao
    U_IncluiProduto("ZZZ_TEST_001", "PROD TESTE", 10.00)
    oResult:IsTrue(ExisteProd("ZZZ_TEST_001"), "Inclusao OK")

    // Alteracao
    U_AlteraProduto("ZZZ_TEST_001", "PROD ALTERADO", 20.00)
    oResult:IsEqual(GetNomeProd("ZZZ_TEST_001"), "PROD ALTERADO", "Alteracao OK")

    // Exclusao
    U_ExcluiProduto("ZZZ_TEST_001")
    oResult:IsFalse(ExisteProd("ZZZ_TEST_001"), "Exclusao OK")
Return
```

**Correcao**: Separe em Test_Inclusao, Test_Alteracao e Test_Exclusao.

### AP-06: Dados de Teste Sem Prefixo Identificavel

```advpl
// ERRADO: codigo de teste parece dado real
Static Function Setup_Produto()
    RecLock("SB1", .T.)
        SB1->B1_COD := "000001"  // Pode conflitar com dado real!
        SB1->B1_DESC := "PRODUTO TESTE"
    SB1->(MsUnlock())
Return
```

**Correcao**: Use `ZZZ_TEST_000001` para evitar conflito com dados reais.

### AP-07: Teste que Depende de Dados Existentes no Banco

```advpl
// ERRADO: assume que cliente "000001" existe no banco
Static Function Test_BuscaCliente(oResult)
    Local cNome := U_GetNomeCli("000001")  // E se nao existir neste ambiente?
    oResult:IsEqual(cNome, "JOAO", "Nome deve ser JOAO")
Return
```

**Correcao**: O Setup deve criar o registro "ZZZ_TEST_001" antes de busca-lo.

---

## 8. Referencia Rapida

### Checklist para Criar um Novo Teste

- [ ] Arquivo nomeado como `*_test.prw` ou `*_test.tlpp`
- [ ] `#include "Protheus.ch"` no topo
- [ ] `User Function` retornando `oResult`
- [ ] `FWTestSuite():New()` com nome descritivo
- [ ] Testes registrados com `AddTest()`
- [ ] `oResult:Run()` antes do `Return`
- [ ] Setup cria dados com prefixo `ZZZ_TEST_`
- [ ] Teardown limpa com `TCSqlExec DELETE`
- [ ] Mensagens de assertion descritivas
- [ ] Caminho feliz E caminho de erro cobertos
- [ ] Testes independentes entre si

### Assertions -- Resumo

| Metodo | Verifica | Uso Tipico |
|---|---|---|
| `IsEqual(a, b, msg)` | `a == b` | Comparar valores de retorno |
| `IsTrue(expr, msg)` | `expr == .T.` | Validar condicoes verdadeiras |
| `IsFalse(expr, msg)` | `expr == .F.` | Validar condicoes falsas |
| `IsNil(val, msg)` | `val == NIL` | Verificar retorno nulo |
| `IsNotNil(val, msg)` | `val != NIL` | Verificar que retornou algo |
| `HasError(blk, msg)` | Bloco gera erro | Testar tratamento de excecao |
