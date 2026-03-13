# Templates de Teste ProBat -- Padroes Completos

Este arquivo contem 6 templates completos e funcionais para testes ProBat no Protheus.
Cada template inclui codigo ADVPL pronto para uso com comentarios explicativos.

---

## Template 1 -- Teste de Funcao Pura

Funcoes puras recebem parametros e retornam valores sem efeitos colaterais.
Nao acessam banco de dados, nao gravam arquivos, nao dependem de estado externo.
Sao os testes mais rapidos e simples de escrever.

```advpl
#include "Protheus.ch"

/*/{Protheus.doc} CalcDesc_Test
Testes para a funcao U_CalcDesconto que calcula desconto sobre um valor.
A funcao recebe valor base e percentual, retornando o valor com desconto.
Regras: valor negativo retorna 0, desconto > 100 retorna 0, desconto < 0 retorna valor original.
@type Function
@author Equipe Desenvolvimento
@since 01/01/2025
/*/
User Function CalcDesc_Test()
    Local oResult := FWTestSuite():New("CalcDesconto - Funcao Pura")

    // ----------------------------------------------------------
    // Registro dos casos de teste -- caminho feliz
    // ----------------------------------------------------------
    oResult:AddTest("Deve calcular 10% de desconto sobre 100", ;
        {|| Test_Desconto10(oResult)})

    oResult:AddTest("Deve calcular 50% de desconto sobre 200", ;
        {|| Test_Desconto50(oResult)})

    oResult:AddTest("Deve retornar valor cheio quando desconto e zero", ;
        {|| Test_DescontoZero(oResult)})

    oResult:AddTest("Deve retornar zero quando desconto e 100%", ;
        {|| Test_Desconto100(oResult)})

    // ----------------------------------------------------------
    // Registro dos casos de teste -- caminho de erro
    // ----------------------------------------------------------
    oResult:AddTest("Deve retornar zero para valor negativo", ;
        {|| Test_ValorNegativo(oResult)})

    oResult:AddTest("Deve retornar zero para desconto acima de 100", ;
        {|| Test_DescontoInvalido(oResult)})

    oResult:AddTest("Deve retornar valor original para desconto negativo", ;
        {|| Test_DescontoNegativo(oResult)})

    // Executa todos os testes registrados
    oResult:Run()
Return oResult

// ----------------------------------------------------------
// Caso 1: Desconto padrao de 10%
// Entrada: valor=100, desconto=10
// Esperado: 100 - (100 * 10 / 100) = 90
// ----------------------------------------------------------
Static Function Test_Desconto10(oResult)
    Local nResultado := U_CalcDesconto(100, 10)
    oResult:IsEqual(nResultado, 90, ;
        "10% de desconto sobre 100 deve resultar 90")
Return

// ----------------------------------------------------------
// Caso 2: Desconto de 50%
// Entrada: valor=200, desconto=50
// Esperado: 200 - (200 * 50 / 100) = 100
// ----------------------------------------------------------
Static Function Test_Desconto50(oResult)
    Local nResultado := U_CalcDesconto(200, 50)
    oResult:IsEqual(nResultado, 100, ;
        "50% de desconto sobre 200 deve resultar 100")
Return

// ----------------------------------------------------------
// Caso 3: Desconto zero -- valor deve permanecer intacto
// Entrada: valor=150, desconto=0
// Esperado: 150
// ----------------------------------------------------------
Static Function Test_DescontoZero(oResult)
    Local nResultado := U_CalcDesconto(150, 0)
    oResult:IsEqual(nResultado, 150, ;
        "Desconto zero sobre 150 deve retornar 150 intacto")
Return

// ----------------------------------------------------------
// Caso 4: Desconto de 100% -- valor deve zerar
// Entrada: valor=250, desconto=100
// Esperado: 0
// ----------------------------------------------------------
Static Function Test_Desconto100(oResult)
    Local nResultado := U_CalcDesconto(250, 100)
    oResult:IsEqual(nResultado, 0, ;
        "100% de desconto sobre 250 deve resultar zero")
Return

// ----------------------------------------------------------
// Caso 5: Valor negativo -- funcao deve rejeitar
// Entrada: valor=-50, desconto=10
// Esperado: 0
// ----------------------------------------------------------
Static Function Test_ValorNegativo(oResult)
    Local nResultado := U_CalcDesconto(-50, 10)
    oResult:IsEqual(nResultado, 0, ;
        "Valor negativo deve retornar zero independente do desconto")
Return

// ----------------------------------------------------------
// Caso 6: Desconto acima de 100% -- invalido
// Entrada: valor=100, desconto=150
// Esperado: 0
// ----------------------------------------------------------
Static Function Test_DescontoInvalido(oResult)
    Local nResultado := U_CalcDesconto(100, 150)
    oResult:IsEqual(nResultado, 0, ;
        "Desconto acima de 100% deve retornar zero")
Return

// ----------------------------------------------------------
// Caso 7: Desconto negativo -- retorna valor original
// Entrada: valor=100, desconto=-10
// Esperado: 100
// ----------------------------------------------------------
Static Function Test_DescontoNegativo(oResult)
    Local nResultado := U_CalcDesconto(100, -10)
    oResult:IsEqual(nResultado, 100, ;
        "Desconto negativo deve retornar valor original sem alteracao")
Return
```

---

## Template 2 -- Teste de Acesso a Dados

Testa funcoes que leem ou gravam registros no banco de dados.
O Setup cria registros com prefixo ZZZ_TEST_ usando RecLock.
O Teardown remove tudo via TCSqlExec DELETE.
A funcao sob teste opera sobre os dados criados.

```advpl
#include "Protheus.ch"

/*/{Protheus.doc} BuscCli_Test
Testes para a funcao U_BuscaCliente que consulta dados de cliente.
A funcao recebe codigo do cliente e retorna array com {nome, cidade, UF}.
Retorna NIL se cliente nao encontrado.
@type Function
@author Equipe Desenvolvimento
@since 01/01/2025
/*/
User Function BuscCli_Test()
    Local oResult := FWTestSuite():New("BuscaCliente - Acesso a Dados")

    // Caminho feliz
    oResult:AddTest("Deve retornar dados do cliente existente", ;
        {|| Test_ClienteExiste(oResult)})

    oResult:AddTest("Deve retornar nome correto do cliente", ;
        {|| Test_NomeCliente(oResult)})

    // Caminho de erro
    oResult:AddTest("Deve retornar NIL para cliente inexistente", ;
        {|| Test_ClienteInexiste(oResult)})

    oResult:Run()
Return oResult

// ----------------------------------------------------------
// Setup: cria um cliente de teste na tabela SA1
// Usa RecLock com .T. para incluir novo registro
// Todos os campos-chave usam prefixo ZZZ_TEST_
// ----------------------------------------------------------
Static Function Setup_BuscaCli()
    Local cFilial := xFilial("SA1")

    SA1->(dbSetOrder(1)) // Filial + Codigo + Loja
    If !SA1->(dbSeek(cFilial + "ZZZ_TEST_C01" + "01"))
        RecLock("SA1", .T.)
            SA1->A1_FILIAL := cFilial
            SA1->A1_COD    := "ZZZ_TEST_C01"
            SA1->A1_LOJA   := "01"
            SA1->A1_NOME   := "ZZZ_TEST_MARIA DA SILVA"
            SA1->A1_NREDUZ := "ZZZ_TEST_MARIA"
            SA1->A1_MUN    := "CURITIBA"
            SA1->A1_EST    := "PR"
            SA1->A1_TIPO   := "F"
            SA1->A1_CGC    := "12345678909"
            SA1->A1_END    := "RUA TESTE PROBAT 456"
        SA1->(MsUnlock())
    EndIf
Return

// ----------------------------------------------------------
// Teardown: remove todos os registros de teste via SQL
// O filtro LIKE 'ZZZ_TEST_%' garante que so dados de teste
// sejam removidos, nunca dados reais do sistema
// ----------------------------------------------------------
Static Function Teardown_BuscaCli()
    TCSqlExec("DELETE FROM " + RetSqlName("SA1") + ;
        " WHERE A1_COD LIKE 'ZZZ_TEST_%' AND D_E_L_E_T_ = ' '")
Return

// ----------------------------------------------------------
// Caso 1: Buscar cliente que existe no banco
// Setup cria o cliente, funcao deve encontra-lo
// Assert verifica que retorno nao e NIL
// ----------------------------------------------------------
Static Function Test_ClienteExiste(oResult)
    // Limpa e recria dados
    Teardown_BuscaCli()
    Setup_BuscaCli()

    // Executa a funcao sob teste
    Local aRet := U_BuscaCliente("ZZZ_TEST_C01")

    // Valida que retornou dados (nao NIL)
    oResult:IsNotNil(aRet, ;
        "Busca por cliente ZZZ_TEST_C01 deve retornar dados, nao NIL")

    // Limpa dados de teste
    Teardown_BuscaCli()
Return

// ----------------------------------------------------------
// Caso 2: Verificar nome retornado
// O array retornado deve conter o nome correto na posicao 1
// ----------------------------------------------------------
Static Function Test_NomeCliente(oResult)
    Teardown_BuscaCli()
    Setup_BuscaCli()

    Local aRet := U_BuscaCliente("ZZZ_TEST_C01")

    // aRet[1] deve conter o nome do cliente
    oResult:IsEqual(aRet[1], "ZZZ_TEST_MARIA DA SILVA", ;
        "Nome do cliente ZZZ_TEST_C01 deve ser ZZZ_TEST_MARIA DA SILVA")

    Teardown_BuscaCli()
Return

// ----------------------------------------------------------
// Caso 3: Buscar cliente que nao existe
// Funcao deve retornar NIL para codigo inexistente
// ----------------------------------------------------------
Static Function Test_ClienteInexiste(oResult)
    Teardown_BuscaCli()
    // NAO chama Setup -- queremos garantir que nao existe

    Local aRet := U_BuscaCliente("ZZZ_TEST_X99")

    oResult:IsNil(aRet, ;
        "Busca por cliente inexistente ZZZ_TEST_X99 deve retornar NIL")

    Teardown_BuscaCli()
Return
```

---

## Template 3 -- Teste de Model MVC

Testa modelos MVC do Protheus usando FWLoadModel.
Configura operacao (inclusao, alteracao), define valores nos campos
e valida o modelo com VldData().

```advpl
#include "Protheus.ch"

/*/{Protheus.doc} MvcProd_Test
Testes para o Model MVC de cadastro de produtos (MATA010).
Valida inclusao de produto via Model, verificando campos obrigatorios
e regras de validacao do modelo.
@type Function
@author Equipe Desenvolvimento
@since 01/01/2025
/*/
User Function MvcProd_Test()
    Local oResult := FWTestSuite():New("Model MVC - Cadastro Produto")

    // Caminho feliz
    oResult:AddTest("Deve validar inclusao de produto com dados completos", ;
        {|| Test_InclusaoOk(oResult)})

    // Caminho de erro
    oResult:AddTest("Deve rejeitar produto sem descricao", ;
        {|| Test_SemDescricao(oResult)})

    oResult:AddTest("Deve rejeitar produto com tipo invalido", ;
        {|| Test_TipoInvalido(oResult)})

    oResult:Run()
Return oResult

// ----------------------------------------------------------
// Teardown: remove produtos de teste criados pelo Model
// ----------------------------------------------------------
Static Function Teardown_MvcProd()
    TCSqlExec("DELETE FROM " + RetSqlName("SB1") + ;
        " WHERE B1_COD LIKE 'ZZZ_TEST_%'")
    TCSqlExec("DELETE FROM " + RetSqlName("SB5") + ;
        " WHERE B5_COD LIKE 'ZZZ_TEST_%'")
Return

// ----------------------------------------------------------
// Caso 1: Inclusao valida de produto via Model MVC
// Carrega o model, define operacao como inclusao,
// preenche todos os campos obrigatorios e valida
// ----------------------------------------------------------
Static Function Test_InclusaoOk(oResult)
    Local oModel  := Nil
    Local lValid  := .F.
    Local aErros  := {}

    // Limpa dados anteriores
    Teardown_MvcProd()

    // Carrega o model MVC do cadastro de produtos
    oModel := FWLoadModel("MATA010")

    // Define operacao como inclusao (novo registro)
    oModel:SetOperation(MODEL_OPERATION_INSERT)

    // Ativa o model para permitir preenchimento
    oModel:Activate()

    // Preenche os campos obrigatorios do model
    // O primeiro parametro identifica o sub-modelo (formfield)
    oModel:SetValue("SB1MASTER", "B1_COD",    "ZZZ_TEST_P01")
    oModel:SetValue("SB1MASTER", "B1_DESC",   "ZZZ_TEST_PRODUTO PROBAT")
    oModel:SetValue("SB1MASTER", "B1_TIPO",   "PA")   // Produto Acabado
    oModel:SetValue("SB1MASTER", "B1_UM",     "UN")   // Unidade
    oModel:SetValue("SB1MASTER", "B1_LOCPAD", "01")   // Armazem padrao
    oModel:SetValue("SB1MASTER", "B1_GRUPO",  "0001") // Grupo de produto

    // Valida o model -- deve retornar .T. com dados completos
    lValid := oModel:VldData()

    // Assertion: model deve ser valido
    oResult:IsTrue(lValid, ;
        "Model de produto com todos os campos obrigatorios deve ser valido")

    // Se nao validou, captura erros para diagnostico
    If !lValid
        aErros := oModel:GetErrorMessage()
    EndIf

    // Desativa o model (libera recursos)
    oModel:DeActivate()

    // Limpa dados criados
    Teardown_MvcProd()
Return

// ----------------------------------------------------------
// Caso 2: Rejeitar produto sem descricao
// B1_DESC e obrigatorio -- model nao deve validar sem ele
// ----------------------------------------------------------
Static Function Test_SemDescricao(oResult)
    Local oModel := Nil
    Local lValid := .F.

    Teardown_MvcProd()

    oModel := FWLoadModel("MATA010")
    oModel:SetOperation(MODEL_OPERATION_INSERT)
    oModel:Activate()

    // Preenche campos EXCETO descricao (B1_DESC)
    oModel:SetValue("SB1MASTER", "B1_COD",    "ZZZ_TEST_P02")
    oModel:SetValue("SB1MASTER", "B1_TIPO",   "PA")
    oModel:SetValue("SB1MASTER", "B1_UM",     "UN")
    oModel:SetValue("SB1MASTER", "B1_LOCPAD", "01")
    // B1_DESC NAO preenchido propositalmente

    lValid := oModel:VldData()

    // Assertion: model NAO deve validar sem descricao
    oResult:IsFalse(lValid, ;
        "Model de produto sem descricao nao deve ser validado")

    oModel:DeActivate()
    Teardown_MvcProd()
Return

// ----------------------------------------------------------
// Caso 3: Rejeitar produto com tipo invalido
// B1_TIPO deve ser um valor valido da tabela 02
// ----------------------------------------------------------
Static Function Test_TipoInvalido(oResult)
    Local oModel := Nil
    Local lValid := .F.

    Teardown_MvcProd()

    oModel := FWLoadModel("MATA010")
    oModel:SetOperation(MODEL_OPERATION_INSERT)
    oModel:Activate()

    oModel:SetValue("SB1MASTER", "B1_COD",    "ZZZ_TEST_P03")
    oModel:SetValue("SB1MASTER", "B1_DESC",   "ZZZ_TEST_PRODUTO TIPO INVALIDO")
    oModel:SetValue("SB1MASTER", "B1_TIPO",   "XX")  // Tipo invalido
    oModel:SetValue("SB1MASTER", "B1_UM",     "UN")
    oModel:SetValue("SB1MASTER", "B1_LOCPAD", "01")

    lValid := oModel:VldData()

    // Assertion: model NAO deve validar com tipo invalido
    oResult:IsFalse(lValid, ;
        "Model de produto com tipo XX invalido nao deve ser validado")

    oModel:DeActivate()
    Teardown_MvcProd()
Return
```

---

## Template 4 -- Teste de Endpoint REST

Testa metodos REST chamando a funcao diretamente, sem requisicao HTTP.
Monta o JsonObject de request, invoca a funcao e valida status e resposta.

```advpl
#include "Protheus.ch"

/*/{Protheus.doc} RstCli_Test
Testes para o endpoint REST de consulta de clientes.
O endpoint GET /api/v1/clientes/:codigo retorna dados do cliente em JSON.
A funcao U_RSTCLI01 recebe JsonObject e retorna JsonObject com status.
@type Function
@author Equipe Desenvolvimento
@since 01/01/2025
/*/
User Function RstCli_Test()
    Local oResult := FWTestSuite():New("REST Endpoint - Consulta Cliente")

    // Caminho feliz
    oResult:AddTest("Deve retornar cliente existente com status 200", ;
        {|| Test_GetClienteOk(oResult)})

    oResult:AddTest("Deve retornar campos corretos no JSON", ;
        {|| Test_CamposJson(oResult)})

    // Caminho de erro
    oResult:AddTest("Deve retornar 404 para cliente inexistente", ;
        {|| Test_ClienteNotFound(oResult)})

    oResult:AddTest("Deve retornar 400 para codigo vazio", ;
        {|| Test_CodigoVazio(oResult)})

    oResult:Run()
Return oResult

// ----------------------------------------------------------
// Setup: cria cliente de teste para as consultas REST
// ----------------------------------------------------------
Static Function Setup_RstCli()
    Local cFilial := xFilial("SA1")

    SA1->(dbSetOrder(1))
    If !SA1->(dbSeek(cFilial + "ZZZ_TEST_R01" + "01"))
        RecLock("SA1", .T.)
            SA1->A1_FILIAL := cFilial
            SA1->A1_COD    := "ZZZ_TEST_R01"
            SA1->A1_LOJA   := "01"
            SA1->A1_NOME   := "ZZZ_TEST_CLIENTE REST"
            SA1->A1_NREDUZ := "ZZZ_TEST_REST"
            SA1->A1_MUN    := "SAO PAULO"
            SA1->A1_EST    := "SP"
            SA1->A1_CGC    := "11222333000181"
            SA1->A1_TIPO   := "J"
        SA1->(MsUnlock())
    EndIf
Return

// ----------------------------------------------------------
// Teardown: remove dados de teste
// ----------------------------------------------------------
Static Function Teardown_RstCli()
    TCSqlExec("DELETE FROM " + RetSqlName("SA1") + ;
        " WHERE A1_COD LIKE 'ZZZ_TEST_%'")
Return

// ----------------------------------------------------------
// Caso 1: GET cliente existente -- deve retornar status 200
// Monta JsonObject simulando parametros da requisicao
// Chama a funcao REST diretamente (sem HTTP)
// ----------------------------------------------------------
Static Function Test_GetClienteOk(oResult)
    Local oRequest  := JsonObject():New()
    Local oResponse := Nil
    Local nStatus   := 0

    Teardown_RstCli()
    Setup_RstCli()

    // Monta o objeto de request simulando parametros de URL
    oRequest["codigo"] := "ZZZ_TEST_R01"
    oRequest["loja"]   := "01"

    // Chama a funcao REST diretamente -- nao faz chamada HTTP
    // A funcao retorna um JsonObject com "status" e "data"
    oResponse := U_RSTCLI01(oRequest)

    // Extrai o status da resposta
    nStatus := oResponse["status"]

    // Assertion: status deve ser 200 (sucesso)
    oResult:IsEqual(nStatus, 200, ;
        "GET cliente ZZZ_TEST_R01 existente deve retornar status 200")

    Teardown_RstCli()
Return

// ----------------------------------------------------------
// Caso 2: Verificar campos no JSON de resposta
// O campo "data" deve conter nome, cidade e UF do cliente
// ----------------------------------------------------------
Static Function Test_CamposJson(oResult)
    Local oRequest  := JsonObject():New()
    Local oResponse := Nil
    Local oData     := Nil

    Teardown_RstCli()
    Setup_RstCli()

    oRequest["codigo"] := "ZZZ_TEST_R01"
    oRequest["loja"]   := "01"

    oResponse := U_RSTCLI01(oRequest)
    oData     := oResponse["data"]

    // Assertion: campo nome deve estar presente e correto
    oResult:IsEqual(oData["nome"], "ZZZ_TEST_CLIENTE REST", ;
        "Campo nome no JSON deve ser ZZZ_TEST_CLIENTE REST")

    Teardown_RstCli()
Return

// ----------------------------------------------------------
// Caso 3: Cliente inexistente -- deve retornar status 404
// ----------------------------------------------------------
Static Function Test_ClienteNotFound(oResult)
    Local oRequest  := JsonObject():New()
    Local oResponse := Nil

    Teardown_RstCli()
    // NAO chama Setup -- cliente nao deve existir

    oRequest["codigo"] := "ZZZ_TEST_X99"
    oRequest["loja"]   := "01"

    oResponse := U_RSTCLI01(oRequest)

    oResult:IsEqual(oResponse["status"], 404, ;
        "GET cliente inexistente ZZZ_TEST_X99 deve retornar status 404")

    Teardown_RstCli()
Return

// ----------------------------------------------------------
// Caso 4: Codigo vazio -- deve retornar status 400 (bad request)
// ----------------------------------------------------------
Static Function Test_CodigoVazio(oResult)
    Local oRequest  := JsonObject():New()
    Local oResponse := Nil

    oRequest["codigo"] := ""
    oRequest["loja"]   := "01"

    oResponse := U_RSTCLI01(oRequest)

    oResult:IsEqual(oResponse["status"], 400, ;
        "GET com codigo vazio deve retornar status 400 bad request")
Return
```

---

## Template 5 -- Teste de Job/Worker

Testa rotinas de processamento em background (Jobs, Schedules, Workers).
Prepara o estado inicial no banco, executa a funcao do Worker diretamente
(sem scheduler) e verifica o estado resultante apos processamento.

```advpl
#include "Protheus.ch"

/*/{Protheus.doc} WrkFat_Test
Testes para o Worker de faturamento automatico WORKER_FATURA.
O Worker processa pedidos de venda com status "L" (liberado)
e gera notas fiscais automaticamente.
@type Function
@author Equipe Desenvolvimento
@since 01/01/2025
/*/
User Function WrkFat_Test()
    Local oResult := FWTestSuite():New("Worker Faturamento - Job Test")

    // Caminho feliz
    oResult:AddTest("Deve faturar pedido liberado", ;
        {|| Test_FaturaPedido(oResult)})

    oResult:AddTest("Deve atualizar status do pedido apos faturamento", ;
        {|| Test_StatusPosFat(oResult)})

    // Caminho de erro
    oResult:AddTest("Deve ignorar pedido ja faturado", ;
        {|| Test_PedidoJaFaturado(oResult)})

    oResult:Run()
Return oResult

// ----------------------------------------------------------
// Setup: cria pedido de venda de teste com status Liberado
// Cria registros em SC5 (cabecalho) e SC6 (itens)
// ----------------------------------------------------------
Static Function Setup_WrkFat()
    Local cFilial := xFilial("SC5")

    // Cabecalho do pedido (SC5)
    SC5->(dbSetOrder(1))
    If !SC5->(dbSeek(cFilial + "ZZZ_TEST_F01"))
        RecLock("SC5", .T.)
            SC5->C5_FILIAL  := cFilial
            SC5->C5_NUM     := "ZZZ_TEST_F01"
            SC5->C5_CLIENTE := "ZZZ_TEST_C01"
            SC5->C5_LOJACLI := "01"
            SC5->C5_CONDPAG := "001"
            SC5->C5_EMISSAO := Date()
            SC5->C5_LIBEROK := "L"  // Status: Liberado para faturamento
        SC5->(MsUnlock())
    EndIf

    // Item do pedido (SC6)
    SC6->(dbSetOrder(1))
    If !SC6->(dbSeek(cFilial + "ZZZ_TEST_F01" + "01"))
        RecLock("SC6", .T.)
            SC6->C6_FILIAL  := cFilial
            SC6->C6_NUM     := "ZZZ_TEST_F01"
            SC6->C6_ITEM    := "01"
            SC6->C6_PRODUTO := "ZZZ_TEST_P01"
            SC6->C6_QTDVEN  := 10
            SC6->C6_PRCVEN  := 50.00
            SC6->C6_VALOR   := 500.00
            SC6->C6_TES     := "501"
            SC6->C6_LOCAL   := "01"
        SC6->(MsUnlock())
    EndIf

    // Cria cliente referenciado pelo pedido (SA1)
    Local cFilSA1 := xFilial("SA1")
    SA1->(dbSetOrder(1))
    If !SA1->(dbSeek(cFilSA1 + "ZZZ_TEST_C01" + "01"))
        RecLock("SA1", .T.)
            SA1->A1_FILIAL := cFilSA1
            SA1->A1_COD    := "ZZZ_TEST_C01"
            SA1->A1_LOJA   := "01"
            SA1->A1_NOME   := "ZZZ_TEST_CLIENTE WORKER"
            SA1->A1_NREDUZ := "ZZZ_TEST_WRK"
            SA1->A1_TIPO   := "J"
            SA1->A1_CGC    := "33444555000199"
        SA1->(MsUnlock())
    EndIf
Return

// ----------------------------------------------------------
// Teardown: remove todos os dados de teste em todas as tabelas
// Ordem: primeiro dependentes, depois principais
// ----------------------------------------------------------
Static Function Teardown_WrkFat()
    // Itens do pedido
    TCSqlExec("DELETE FROM " + RetSqlName("SC6") + ;
        " WHERE C6_NUM LIKE 'ZZZ_TEST_%'")

    // Cabecalho do pedido
    TCSqlExec("DELETE FROM " + RetSqlName("SC5") + ;
        " WHERE C5_NUM LIKE 'ZZZ_TEST_%'")

    // Notas fiscais geradas (se houver)
    TCSqlExec("DELETE FROM " + RetSqlName("SF2") + ;
        " WHERE F2_DOC LIKE 'ZZZ_TEST_%'")

    // Cliente de teste
    TCSqlExec("DELETE FROM " + RetSqlName("SA1") + ;
        " WHERE A1_COD LIKE 'ZZZ_TEST_%'")
Return

// ----------------------------------------------------------
// Caso 1: Worker deve faturar pedido com status Liberado
// Prepara pedido liberado, executa worker, verifica nota gerada
// ----------------------------------------------------------
Static Function Test_FaturaPedido(oResult)
    Local cFilial := xFilial("SF2")
    Local lNotaGerada := .F.

    Teardown_WrkFat()
    Setup_WrkFat()

    // Executa a funcao do Worker diretamente -- sem schedule
    // O Worker busca pedidos com C5_LIBEROK = "L" e gera NF
    U_WORKER_FATURA()

    // Verifica se a nota fiscal foi gerada na SF2
    SF2->(dbSetOrder(1))
    lNotaGerada := SF2->(dbSeek(cFilial + "ZZZ_TEST_F01"))

    oResult:IsTrue(lNotaGerada, ;
        "Worker deve gerar nota fiscal para pedido ZZZ_TEST_F01 liberado")

    Teardown_WrkFat()
Return

// ----------------------------------------------------------
// Caso 2: Status do pedido deve mudar apos faturamento
// Apos o Worker processar, C5_LIBEROK deve mudar de "L" para "F"
// ----------------------------------------------------------
Static Function Test_StatusPosFat(oResult)
    Local cFilial := xFilial("SC5")
    Local cStatus := ""

    Teardown_WrkFat()
    Setup_WrkFat()

    // Executa o Worker
    U_WORKER_FATURA()

    // Verifica o status atualizado do pedido
    SC5->(dbSetOrder(1))
    If SC5->(dbSeek(cFilial + "ZZZ_TEST_F01"))
        cStatus := SC5->C5_LIBEROK
    EndIf

    oResult:IsEqual(cStatus, "F", ;
        "Status do pedido ZZZ_TEST_F01 deve ser F (faturado) apos Worker")

    Teardown_WrkFat()
Return

// ----------------------------------------------------------
// Caso 3: Worker deve ignorar pedido ja faturado
// Cria pedido com status "F" -- Worker nao deve processa-lo novamente
// ----------------------------------------------------------
Static Function Test_PedidoJaFaturado(oResult)
    Local cFilial := xFilial("SC5")

    Teardown_WrkFat()
    Setup_WrkFat()

    // Altera status para "F" (ja faturado)
    SC5->(dbSetOrder(1))
    If SC5->(dbSeek(cFilial + "ZZZ_TEST_F01"))
        RecLock("SC5", .F.)
            SC5->C5_LIBEROK := "F"
        SC5->(MsUnlock())
    EndIf

    // Executa o Worker -- nao deve processar este pedido
    U_WORKER_FATURA()

    // Verifica que status permanece "F" (nao foi reprocessado)
    SC5->(dbSetOrder(1))
    SC5->(dbSeek(cFilial + "ZZZ_TEST_F01"))

    oResult:IsEqual(SC5->C5_LIBEROK, "F", ;
        "Pedido ZZZ_TEST_F01 ja faturado nao deve ser reprocessado pelo Worker")

    Teardown_WrkFat()
Return
```

---

## Template 6 -- Teste de Integracao (Multi-Modulo)

Testa fluxos que atravessam multiplos modulos e tabelas.
Cria registros em cascata na ordem de dependencia, dispara o processo
e verifica os efeitos em todas as tabelas envolvidas.
Teardown limpa na ordem reversa de criacao.

```advpl
#include "Protheus.ch"

/*/{Protheus.doc} FlxVnd_Test
Teste de integracao do fluxo completo de vendas:
Cadastro de cliente (SA1) -> Produto (SB1) -> Pedido de Venda (SC5/SC6)
-> Liberacao -> Faturamento (SF2/SD2) -> Financeiro (SE1)
Verifica que todos os modulos se comunicam corretamente.
@type Function
@author Equipe Desenvolvimento
@since 01/01/2025
/*/
User Function FlxVnd_Test()
    Local oResult := FWTestSuite():New("Fluxo Vendas - Integracao Multi-Modulo")

    // Caminho feliz: fluxo completo
    oResult:AddTest("Deve gerar titulo financeiro apos faturamento", ;
        {|| Test_FluxoCompleto(oResult)})

    oResult:AddTest("Deve manter consistencia entre NF e financeiro", ;
        {|| Test_ConsistenciaValor(oResult)})

    // Caminho de erro
    oResult:AddTest("Deve bloquear faturamento sem estoque", ;
        {|| Test_SemEstoque(oResult)})

    oResult:Run()
Return oResult

// ----------------------------------------------------------
// Setup Cascata: cria registros na ordem de dependencia
// 1. Cliente (SA1) -- nao depende de ninguem
// 2. Produto (SB1) -- nao depende de ninguem
// 3. Saldo de estoque (SB2) -- depende de SB1
// 4. Pedido cabecalho (SC5) -- depende de SA1
// 5. Pedido item (SC6) -- depende de SC5 e SB1
// ----------------------------------------------------------
Static Function Setup_FlxVnd()
    Local cFilSA1 := xFilial("SA1")
    Local cFilSB1 := xFilial("SB1")
    Local cFilSB2 := xFilial("SB2")
    Local cFilSC5 := xFilial("SC5")
    Local cFilSC6 := xFilial("SC6")

    // -------------------------------------------------------
    // Passo 1: Cliente
    // -------------------------------------------------------
    SA1->(dbSetOrder(1))
    If !SA1->(dbSeek(cFilSA1 + "ZZZ_TEST_I01" + "01"))
        RecLock("SA1", .T.)
            SA1->A1_FILIAL := cFilSA1
            SA1->A1_COD    := "ZZZ_TEST_I01"
            SA1->A1_LOJA   := "01"
            SA1->A1_NOME   := "ZZZ_TEST_CLIENTE INTEGRACAO"
            SA1->A1_NREDUZ := "ZZZ_TEST_INT"
            SA1->A1_TIPO   := "J"
            SA1->A1_CGC    := "55666777000100"
            SA1->A1_END    := "AV INTEGRACAO 1000"
            SA1->A1_MUN    := "SAO PAULO"
            SA1->A1_EST    := "SP"
        SA1->(MsUnlock())
    EndIf

    // -------------------------------------------------------
    // Passo 2: Produto
    // -------------------------------------------------------
    SB1->(dbSetOrder(1))
    If !SB1->(dbSeek(cFilSB1 + "ZZZ_TEST_I01"))
        RecLock("SB1", .T.)
            SB1->B1_FILIAL := cFilSB1
            SB1->B1_COD    := "ZZZ_TEST_I01"
            SB1->B1_DESC   := "ZZZ_TEST_PRODUTO INTEGRACAO"
            SB1->B1_TIPO   := "PA"
            SB1->B1_UM     := "UN"
            SB1->B1_LOCPAD := "01"
            SB1->B1_GRUPO  := "0001"
            SB1->B1_PRV1   := 100.00
        SB1->(MsUnlock())
    EndIf

    // -------------------------------------------------------
    // Passo 3: Saldo de estoque (para permitir faturamento)
    // -------------------------------------------------------
    SB2->(dbSetOrder(1))
    If !SB2->(dbSeek(cFilSB2 + "ZZZ_TEST_I01" + "01"))
        RecLock("SB2", .T.)
            SB2->B2_FILIAL := cFilSB2
            SB2->B2_COD    := "ZZZ_TEST_I01"
            SB2->B2_LOCAL  := "01"
            SB2->B2_QATU   := 100  // 100 unidades em estoque
            SB2->B2_QEMP   := 0
            SB2->B2_RESERVA:= 0
        SB2->(MsUnlock())
    EndIf

    // -------------------------------------------------------
    // Passo 4: Pedido de venda -- cabecalho
    // -------------------------------------------------------
    SC5->(dbSetOrder(1))
    If !SC5->(dbSeek(cFilSC5 + "ZZZ_TEST_I01"))
        RecLock("SC5", .T.)
            SC5->C5_FILIAL  := cFilSC5
            SC5->C5_NUM     := "ZZZ_TEST_I01"
            SC5->C5_CLIENTE := "ZZZ_TEST_I01"
            SC5->C5_LOJACLI := "01"
            SC5->C5_CONDPAG := "001"
            SC5->C5_EMISSAO := Date()
            SC5->C5_LIBEROK := "L"  // Liberado para faturamento
        SC5->(MsUnlock())
    EndIf

    // -------------------------------------------------------
    // Passo 5: Pedido de venda -- item
    // -------------------------------------------------------
    SC6->(dbSetOrder(1))
    If !SC6->(dbSeek(cFilSC6 + "ZZZ_TEST_I01" + "01"))
        RecLock("SC6", .T.)
            SC6->C6_FILIAL  := cFilSC6
            SC6->C6_NUM     := "ZZZ_TEST_I01"
            SC6->C6_ITEM    := "01"
            SC6->C6_PRODUTO := "ZZZ_TEST_I01"
            SC6->C6_QTDVEN  := 5
            SC6->C6_PRCVEN  := 100.00
            SC6->C6_VALOR   := 500.00  // 5 x 100
            SC6->C6_TES     := "501"
            SC6->C6_LOCAL   := "01"
        SC6->(MsUnlock())
    EndIf
Return

// ----------------------------------------------------------
// Teardown Cascata Reversa: limpa na ordem inversa de criacao
// Remove primeiro as tabelas dependentes, depois as principais
// Isso evita violacoes de integridade referencial
// ----------------------------------------------------------
Static Function Teardown_FlxVnd()
    // 1. Financeiro (ultimo na cadeia)
    TCSqlExec("DELETE FROM " + RetSqlName("SE1") + ;
        " WHERE E1_NUM LIKE 'ZZZ_TEST_%'")

    // 2. Duplicatas/Itens NF
    TCSqlExec("DELETE FROM " + RetSqlName("SD2") + ;
        " WHERE D2_DOC LIKE 'ZZZ_TEST_%'")

    // 3. Notas fiscais
    TCSqlExec("DELETE FROM " + RetSqlName("SF2") + ;
        " WHERE F2_DOC LIKE 'ZZZ_TEST_%'")

    // 4. Itens do pedido
    TCSqlExec("DELETE FROM " + RetSqlName("SC6") + ;
        " WHERE C6_NUM LIKE 'ZZZ_TEST_%'")

    // 5. Cabecalho do pedido
    TCSqlExec("DELETE FROM " + RetSqlName("SC5") + ;
        " WHERE C5_NUM LIKE 'ZZZ_TEST_%'")

    // 6. Saldo de estoque
    TCSqlExec("DELETE FROM " + RetSqlName("SB2") + ;
        " WHERE B2_COD LIKE 'ZZZ_TEST_%'")

    // 7. Produto
    TCSqlExec("DELETE FROM " + RetSqlName("SB1") + ;
        " WHERE B1_COD LIKE 'ZZZ_TEST_%'")

    // 8. Cliente (primeiro criado, ultimo removido)
    TCSqlExec("DELETE FROM " + RetSqlName("SA1") + ;
        " WHERE A1_COD LIKE 'ZZZ_TEST_%'")
Return

// ----------------------------------------------------------
// Caso 1: Fluxo completo -- deve gerar titulo financeiro
// Cria dados completos, executa faturamento, verifica SE1
// ----------------------------------------------------------
Static Function Test_FluxoCompleto(oResult)
    Local cFilSE1 := xFilial("SE1")
    Local lTituloGerado := .F.

    Teardown_FlxVnd()
    Setup_FlxVnd()

    // Executa o processo de faturamento
    // Funcao que processa pedidos liberados e gera NF + financeiro
    U_ProcessaFaturamento("ZZZ_TEST_I01")

    // Verifica se o titulo financeiro foi gerado na SE1
    SE1->(dbSetOrder(1))
    lTituloGerado := SE1->(dbSeek(cFilSE1 + "ZZZ_TEST_I01"))

    oResult:IsTrue(lTituloGerado, ;
        "Fluxo de venda completo deve gerar titulo financeiro em SE1")

    Teardown_FlxVnd()
Return

// ----------------------------------------------------------
// Caso 2: Valor do titulo deve ser consistente com a NF
// O valor do titulo em SE1 deve bater com o total da NF em SF2
// ----------------------------------------------------------
Static Function Test_ConsistenciaValor(oResult)
    Local cFilSF2 := xFilial("SF2")
    Local cFilSE1 := xFilial("SE1")
    Local nValorNF    := 0
    Local nValorTit   := 0

    Teardown_FlxVnd()
    Setup_FlxVnd()

    // Executa faturamento
    U_ProcessaFaturamento("ZZZ_TEST_I01")

    // Busca valor da NF
    SF2->(dbSetOrder(1))
    If SF2->(dbSeek(cFilSF2 + "ZZZ_TEST_I01"))
        nValorNF := SF2->F2_VALBRUT
    EndIf

    // Busca valor do titulo financeiro
    SE1->(dbSetOrder(1))
    If SE1->(dbSeek(cFilSE1 + "ZZZ_TEST_I01"))
        nValorTit := SE1->E1_VALOR
    EndIf

    // Assertion: valores devem ser iguais (consistencia entre modulos)
    oResult:IsEqual(nValorNF, nValorTit, ;
        "Valor da NF (SF2) deve ser igual ao valor do titulo (SE1) = 500.00")

    Teardown_FlxVnd()
Return

// ----------------------------------------------------------
// Caso 3: Faturamento sem estoque deve ser bloqueado
// Remove saldo antes de tentar faturar
// ----------------------------------------------------------
Static Function Test_SemEstoque(oResult)
    Local cFilSF2 := xFilial("SF2")
    Local lNotaGerada := .F.

    Teardown_FlxVnd()
    Setup_FlxVnd()

    // Zera o estoque para forcar o bloqueio
    TCSqlExec("UPDATE " + RetSqlName("SB2") + ;
        " SET B2_QATU = 0 WHERE B2_COD = 'ZZZ_TEST_I01'")

    // Tenta faturar -- deve falhar por falta de estoque
    U_ProcessaFaturamento("ZZZ_TEST_I01")

    // Verifica que a nota NAO foi gerada
    SF2->(dbSetOrder(1))
    lNotaGerada := SF2->(dbSeek(cFilSF2 + "ZZZ_TEST_I01"))

    oResult:IsFalse(lNotaGerada, ;
        "Faturamento sem estoque nao deve gerar nota fiscal")

    Teardown_FlxVnd()
Return
```

---

## Resumo dos Templates

| Template | Tipo | Usa Banco | Setup/Teardown | Tabelas |
|---|---|---|---|---|
| 1 | Funcao Pura | Nao | Nao necessario | Nenhuma |
| 2 | Acesso a Dados | Sim | Sim | SA1 |
| 3 | Model MVC | Sim | Sim | SB1, SB5 |
| 4 | Endpoint REST | Sim | Sim | SA1 |
| 5 | Job/Worker | Sim | Sim | SA1, SC5, SC6, SF2 |
| 6 | Integracao | Sim | Sim (cascata) | SA1, SB1, SB2, SC5, SC6, SF2, SD2, SE1 |

### Regras Aplicaveis a Todos os Templates

1. Arquivo deve terminar com `_test.prw` ou `_test.tlpp`
2. Entry point e `User Function` retornando `oResult`
3. Dados de teste sempre com prefixo `ZZZ_TEST_`
4. Limpeza via `TCSqlExec DELETE ... LIKE 'ZZZ_TEST_%'`
5. Cada teste e independente (Setup + Teardown proprio)
6. Cobrir caminho feliz e caminho de erro
7. Mensagens de assertion descritivas em portugues
8. Um conceito logico por assertion
