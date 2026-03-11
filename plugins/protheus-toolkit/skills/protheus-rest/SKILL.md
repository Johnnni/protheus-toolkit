---
name: protheus-rest
description: >
  Guia para implementar e consumir APIs REST em ADVPL/TLPP no Protheus.
  Use esta skill SEMPRE que o usuario pedir para criar endpoints REST,
  consumir APIs externas, implementar autenticacao OAuth2/Bearer,
  ou trabalhar com JSON no Protheus. Cobre servidor REST com TLPP
  moderno (anotacoes @Get/@Post), WSRestful classico (manutencao),
  cliente HTTP com FWRest, HTTPQuote, paginacao, retry com backoff,
  parse de JSON com JsonObject, e anti-patterns como credenciais
  hardcoded e HTTP sem TLS.
---


---

## PARTE 1 — TEMPLATE SERVIDOR REST

### 1.1 Estrutura: TLPP Moderno com Anotacoes (PADRAO DO TIME)

O estilo **TLPP com anotacoes** e o padrao atual. Novos servicos REST devem usar este formato.

```tlpp
#Include "Tlpp-Rest.th"
#Include "Protheus.ch"
#include 'tlpp-core.th'

namespace custom.<projeto>.<modulo>.api

/*/{Protheus.doc} <NomeClasse>
Descricao do servico REST
@type class
@author <autor>
@since <data>
/*/

Class <NomeClasse>

    public Method New() CONSTRUCTOR

    @GET("/api/v1/<recurso>", description='Consulta <recurso>')
    public Method consultar() as logical

    @GET("/api/v1/<recurso>/:id", description='Consulta <recurso> por ID')
    public Method consultarPorId() as logical

    @POST("/api/v1/<recurso>", description='Inclusao de <recurso>')
    public Method incluir() as logical

    @PUT("/api/v1/<recurso>/:id", description='Alteracao de <recurso>')
    public Method alterar() as logical

    @DELETE("/api/v1/<recurso>/:id", description='Exclusao de <recurso>')
    public Method excluir() as logical

EndClass

Method New() class <NomeClasse>
Return Self
```

**Convencoes de rota:**
- Prefixo: `/api/v1/`
- Recurso em lowercase: `/api/v1/pedidovenda`
- Path params: `:id` — acessado via `oRest:getPathParamsRequest()`
- Versionamento no path: `/v1/`, `/v2/`

### 1.2 Includes Obrigatorios

```tlpp
#Include "Tlpp-Rest.th"    // Anotacoes @GET, @POST, etc.
#Include "Protheus.ch"     // Macros Protheus padrao
#include 'tlpp-core.th'    // Core TLPP
```

### 1.3 Metodo GET — Consulta Paginada (Template Completo)

```tlpp
Method consultar() as logical Class <NomeClasse>

    Local nStatusRestHTTP := 200 as numeric
    Local jQueryString    := JsonObject():new() as object
    Local jHeader         := JsonObject():new() as object
    Local oJson           := JsonObject():New() as object
    Local aList           := {} as array
    Local cAlias          := GetNextAlias() as character
    Local cQuery          as character
    Local nPagina         as numeric
    Local nTotalPagina    as numeric
    Local oCustomLog        := CustomLog():New() as object
    Local cIdtoken        := oCustomLog:IDTOKEN as character
    Local cFilBkp         := cFilAnt as character

    Private cErrorLog     := ""
    Private bLastError    := {|oError| cErrorLog := oError:Description + oError:ErrorStack, Break(oError)}
    ErrorBlock(bLastError)

    // 1. Leitura dos parametros
    jHeader      := oRest:GetHeaderRequest()
    jQueryString := oRest:getQueryRequest()
    cFilSel      := U_GetFilByCnpj(jHeader['CNPJ'])

    Begin Sequence

        // 2. Validar filial
        If Empty(cFilSel)
            nStatusRestHTTP := 400
            Break
        Endif
        cFilAnt := cFilSel

        // 3. Paginacao
        nPagina      := Iif(!Empty(jQueryString['Page']), Val(jQueryString['Page']), 1)
        nTotalPagina := Iif(!Empty(jQueryString['PageSize']), Val(jQueryString['PageSize']), 100)

        // 4. Montar query
        cQuery := " SELECT CAMPO1, CAMPO2 "
        cQuery += " FROM " + RetSqlName("TABELA") + " (NOLOCK) "
        cQuery += " WHERE D_E_L_E_T_ = ' ' "
        cQuery += " AND FILIAL = '" + xFilial("TABELA") + "' "

        // Filtros opcionais
        If !Empty(jQueryString['filtro1'])
            cQuery += " AND CAMPO1 = '" + jQueryString['filtro1'] + "' "
        Endif

        cQuery += " ORDER BY CAMPO1 "
        cQuery += " OFFSET (" + cValToChar(nPagina - 1) + " * " + cValToChar(nTotalPagina) + ") "
        cQuery += " ROWS FETCH NEXT " + cValToChar(nTotalPagina) + " ROWS ONLY "

        MPSysOpenQuery(ChangeQuery(cQuery), cAlias)

        // 5. Montar array de resultados
        Do while (cAlias)->(!eof())
            aAdd(aList, JsonObject():New())
            aList[Len(aList)]['campo1'] := Alltrim((cAlias)->CAMPO1)
            aList[Len(aList)]['campo2'] := Alltrim((cAlias)->CAMPO2)
            (cAlias)->(dbSkip())
        End
        (cAlias)->(dbCloseArea())

        // 6. Response paginada
        oJson['hasNext'] := (Len(aList) >= nTotalPagina)
        oJson['items']   := aList

    Recover

        nStatusRestHTTP := 500

    End Sequence

    // 7. Retorno padronizado
    If nStatusRestHTTP == 200
        oRest:SetStatusCode(200)
        oRest:SetResponse(oJson:toJson())
        oCustomLog:GRAVALOG("CXXX", cIdtoken, 'Consulta OK',, , NIL, "1")
    Else
        Local jResponse := JsonObject():new()
        jResponse["code"]        := nStatusRestHTTP
        jResponse["message"]     := Iif(nStatusRestHTTP == 400, "CNPJ nao localizado", "Erro interno: " + cErrorLog)
        jResponse["transaction"] := cIdtoken
        jResponse["date"]        := FWTimeStamp(2)
        oRest:SetStatusCode(nStatusRestHTTP)
        oRest:SetResponse(jResponse:toJson())
        oCustomLog:GRAVALOG("CXXX", cIdtoken, jResponse["message"], cErrorLog, , NIL, "2")
    Endif

    cFilAnt := cFilBkp
Return .T.
```

### 1.4 Metodo POST — Inclusao (Template Completo)

```tlpp
Method incluir() as logical Class <NomeClasse>

    Local nStatusRestHTTP := 201 as numeric
    Local jBody           := JsonObject():new() as object
    Local jHeader         := JsonObject():new() as object
    Local jResponse       := JsonObject():new() as object
    Local oModel          as object
    Local oCustomLog        := CustomLog():New() as object
    Local cIdtoken        := oCustomLog:IDTOKEN as character
    Local cFilBkp         := cFilAnt as character
    Local ret             as character

    Private cErrorLog     := ""
    Private bLastError    := {|oError| cErrorLog := oError:Description + oError:ErrorStack, Break(oError)}
    ErrorBlock(bLastError)

    jHeader := oRest:GetHeaderRequest()
    ret     := jBody:FromJson(oRest:GetBodyRequest())

    Begin Sequence

        // 1. Validar filial via CNPJ
        cFilSel := U_GetFilByCnpj(jHeader['CNPJ'])
        If Empty(cFilSel)
            nStatusRestHTTP := 400
            jResponse["message"] := "CNPJ nao localizado no Protheus"
            Break
        Endif
        cFilAnt := cFilSel

        // 2. Validar JSON
        if ValType(ret) == "C"
            nStatusRestHTTP := 400
            jResponse["message"] := "JSON invalido: " + ret
            Break
        endif

        // 3. Validar campos obrigatorios
        If Empty(jBody['campo_obrigatorio'])
            nStatusRestHTTP := 400
            jResponse["message"] := "Campo 'campo_obrigatorio' e obrigatorio"
            Break
        Endif

        // 4. Processar via MVC (FWLoadModel)
        oModel := FWLoadModel("MODELID")
        oModel:SetOperation(3)  // 3=Inclusao
        oModel:Activate()

        Local oMaster := oModel:GetModel("MASTER")
        oMaster:SetValue("CAMPO1", Padr(jBody['campo1'], TamSX3("CAMPO1")[1]))
        oMaster:SetValue("CAMPO2", Padr(jBody['campo2'], TamSX3("CAMPO2")[1]))

        If oModel:VldData()
            If oModel:CommitData()
                jResponse["code"]    := 201
                jResponse["message"] := "Registro criado com sucesso"
                jResponse["id"]      := AllTrim(TABELA->CAMPO_ID)
            Else
                nStatusRestHTTP := 400
                jResponse["message"] := "Erro ao gravar dados"
            EndIf
        Else
            nStatusRestHTTP := 400
            Local aErro := oModel:GetErrorMessage()
            jResponse["message"] := FwNoAccent(cValToChar(aErro[06]))
        EndIf

        oModel:DeActivate()

    Recover

        nStatusRestHTTP := 500
        jResponse["message"] := "Erro interno: " + cErrorLog

    End Sequence

    // 5. Response padronizada
    jResponse["transaction"] := cIdtoken
    jResponse["date"]        := FWTimeStamp(2)
    oRest:SetStatusCode(nStatusRestHTTP)
    oRest:SetResponse(jResponse:toJson())

    If nStatusRestHTTP < 300
        oCustomLog:GRAVALOG("CXXX", cIdtoken, jResponse["message"],, jBody:toJson(), NIL, "1")
    Else
        oCustomLog:GRAVALOG("CXXX", cIdtoken, jResponse["message"], cErrorLog, jBody:toJson(), NIL, "2")
    Endif

    cFilAnt := cFilBkp
Return .T.
```

### 1.5 Metodo PUT — Alteracao (Template)

```tlpp
Method alterar() as logical Class <NomeClasse>

    Local nStatusRestHTTP := 200 as numeric
    Local jBody           := JsonObject():new() as object
    Local jHeader         := JsonObject():new() as object
    Local jParams         := JsonObject():new() as object
    Local jResponse       := JsonObject():new() as object
    Local oCustomLog        := CustomLog():New() as object
    Local cIdtoken        := oCustomLog:IDTOKEN as character
    Local cFilBkp         := cFilAnt as character
    Local cId             as character

    Private cErrorLog     := ""
    Private bLastError    := {|oError| cErrorLog := oError:Description + oError:ErrorStack, Break(oError)}
    ErrorBlock(bLastError)

    jHeader := oRest:GetHeaderRequest()
    ret     := jBody:FromJson(oRest:GetBodyRequest())
    jParams := oRest:getPathParamsRequest()
    cId     := jParams['id']

    Begin Sequence

        // 1. Validar filial
        cFilSel := U_GetFilByCnpj(jHeader['CNPJ'])
        If Empty(cFilSel)
            nStatusRestHTTP := 400
            jResponse["message"] := "CNPJ nao localizado"
            Break
        Endif
        cFilAnt := cFilSel

        // 2. Validar JSON e ID
        if ValType(ret) == "C"
            nStatusRestHTTP := 400
            jResponse["message"] := "JSON invalido: " + ret
            Break
        endif

        If Empty(cId)
            nStatusRestHTTP := 400
            jResponse["message"] := "ID e obrigatorio"
            Break
        Endif

        // 3. Localizar registro
        TABELA->(DbSetOrder(1))
        If !TABELA->(MsSeek(xFilial("TABELA") + cId))
            nStatusRestHTTP := 404
            jResponse["message"] := "Registro nao localizado: " + cId
            Break
        Endif

        // 4. Alterar via MVC
        oModel := FWLoadModel("MODELID")
        oModel:SetOperation(4)  // 4=Alteracao
        oModel:Activate()

        Local oMaster := oModel:GetModel("MASTER")
        If !Empty(jBody['campo1'])
            oMaster:SetValue("CAMPO1", Padr(jBody['campo1'], TamSX3("CAMPO1")[1]))
        Endif

        If oModel:VldData() .And. oModel:CommitData()
            jResponse["message"] := "Registro atualizado com sucesso"
        Else
            nStatusRestHTTP := 400
            Local aErro := oModel:GetErrorMessage()
            jResponse["message"] := FwNoAccent(cValToChar(aErro[06]))
        EndIf

        oModel:DeActivate()

    Recover

        nStatusRestHTTP := 500
        jResponse["message"] := "Erro interno: " + cErrorLog

    End Sequence

    jResponse["transaction"] := cIdtoken
    jResponse["date"]        := FWTimeStamp(2)
    oRest:SetStatusCode(nStatusRestHTTP)
    oRest:SetResponse(jResponse:toJson())

    If nStatusRestHTTP < 300
        oCustomLog:GRAVALOG("CXXX", cIdtoken, jResponse["message"],, jBody:toJson(), NIL, "1")
    Else
        oCustomLog:GRAVALOG("CXXX", cIdtoken, jResponse["message"], cErrorLog, jBody:toJson(), NIL, "2")
    Endif

    cFilAnt := cFilBkp
Return .T.
```

### 1.6 Padrao de Response JSON

**GET paginado:**
```json
{
  "hasNext": true,
  "items": [
    {"campo1": "valor1", "campo2": "valor2"},
    {"campo1": "valor3", "campo2": "valor4"}
  ]
}
```

**POST/PUT/DELETE sucesso:**
```json
{
  "code": 201,
  "message": "Registro criado com sucesso",
  "id": "000001",
  "transaction": "uuid-de-rastreio",
  "date": "2024-01-15 10:30:00"
}
```

**Erro:**
```json
{
  "code": 400,
  "message": "Campo 'descricao' e obrigatorio",
  "transaction": "uuid-de-rastreio",
  "date": "2024-01-15 10:30:00"
}
```

### 1.7 Referencia: Estilo WSRestful Classico (Legado)

Nao usar para novos servicos. Referencia apenas para manutencao dos existentes.

**Includes:**
```advpl
#include 'totvs.ch'
#include 'restful.ch'
```

**Declaracao:**
```advpl
WSRESTFUL wsNomeServico DESCRIPTION 'Descricao' FORMAT APPLICATION_JSON
    WSDATA Page      AS INTEGER OPTIONAL
    WSDATA PageSize  AS INTEGER OPTIONAL
    WSDATA id        AS String  OPTIONAL

    WSMETHOD POST metodo; PATH '/v1/recurso'; PRODUCES APPLICATION_JSON
    WSMETHOD GET  metodo; PATH '/v1/recurso'; PRODUCES APPLICATION_JSON
ENDWSRESTFUL
```

**Implementacao:**
```advpl
WSMETHOD POST metodo WSRECEIVE WSSERVICE wsNomeServico
    Local cJsonCont := Self:GetContent()     // body
    Local cFilSel   := U_GetFilByCnpj(Self:GetHeader('CNPJ'))  // auth
    ...
    Self:SetStatus(201)
    Self:SetResponse(FWJsonSerialize(oReturn))
Return lRet

WSMETHOD PUT metodo PATHPARAM id WSRECEIVE WSSERVICE wsNomeServico
    Local cId := self:id       // path param
    ...
Return lRet
```

---

## PARTE 2 — TEMPLATE CLIENTE REST (Consumo de API Externa)

### 2.1 Cliente com FWRest (Padrao do Time)

```tlpp
/*/{Protheus.doc} ChamaAPIExterna
Exemplo de consumo de API externa com FWRest
@type function
@author <autor>
@since <data>
/*/
Static Function ChamaAPIExterna(cEndpoint, cMethod, cBody, cToken)

    Local oRest    := FWRest():New(SuperGetMV("MV_APIURL", .F., "https://api.exemplo.com"))
    Local oJson    := JsonObject():New()
    Local aHeaders := {} as array
    Local nStatus  as numeric
    Local cError   as character
    Local cResult  as character
    Local lRet     := .F. as logical

    // 1. Configurar request
    oRest:setPath(cEndpoint)
    oRest:SetChkStatus(.F.)

    // 2. Headers
    aAdd(aHeaders, "Content-Type: application/json")
    aAdd(aHeaders, "Accept: application/json")
    If !Empty(cToken)
        aAdd(aHeaders, "Authorization: Bearer " + cToken)
    Endif

    // 3. Body (para POST/PUT)
    If !Empty(cBody)
        oRest:SetPostParams(cBody)
    Endif

    // 4. Executar request
    If cMethod == "GET"
        lRet := oRest:Get(aHeaders)
    ElseIf cMethod == "POST"
        lRet := oRest:Post(aHeaders)
    ElseIf cMethod == "PUT"
        lRet := oRest:Put(aHeaders)
    ElseIf cMethod == "DELETE"
        lRet := oRest:Delete(aHeaders)
    Endif

    // 5. Verificar resultado
    If lRet
        nStatus := HTTPGetStatus(@cError)
        If nStatus >= 200 .And. nStatus <= 299
            cResult := oRest:GetResult()
            oJson:FromJson(cResult)
            // Processar oJson...
            lRet := .T.
        Else
            ConOut("HTTP Error " + cValToChar(nStatus) + ": " + cError)
            lRet := .F.
        Endif
    Else
        ConOut("Transport Error: " + oRest:GetLastError())
        lRet := .F.
    Endif

    FreeObj(oRest)
    FreeObj(oJson)

Return lRet
```

### 2.2 Cliente com HTTPQuote (Quando Precisa Ler Headers de Resposta)

```tlpp
Static Function ChamaComHeaders(cFullUrl, cMethod, cBody, aHeaders)

    Local cResponse   as character
    Local cHeaderRet  as character
    Local nStatus     as numeric
    Local cError      as character

    cResponse := HTTPQuote(cFullUrl, Upper(cMethod), "", cBody, 30, aHeaders, @cHeaderRet)
    nStatus   := HTTPGetStatus(@cError)

    If nStatus >= 200 .And. nStatus <= 299
        // Sucesso — cHeaderRet contem headers de resposta como string bruta
        // Parse manual se necessario (ex: extrair Set-Cookie, Location)
    Else
        ConOut("Erro HTTP " + cValToChar(nStatus) + ": " + cError)
    Endif

Return cResponse
```

### 2.3 Padrao de Autenticacao — OAuth2 Client Credentials

```tlpp
Static Function ObtemTokenOAuth2()

    Local cUrl      := SuperGetMV("MV_AUTHURL", .F., "")
    Local cClientId := SuperGetMV("MV_CLID", .F., "")
    Local cSecret   := SuperGetMV("MV_CLSEC", .F., "")
    Local cToken    as character
    Local aHeaders  := {} as array
    Local cBody     as character
    Local cResponse as character
    Local cHeaderRet as character
    Local oJson     := JsonObject():New()

    aAdd(aHeaders, "Content-Type: application/x-www-form-urlencoded")

    cBody := "grant_type=client_credentials"
    cBody += "&client_id=" + cClientId
    cBody += "&client_secret=" + cSecret

    cResponse := HttpPost(cUrl, "", cBody, 30, aHeaders, @cHeaderRet)

    If HTTPGetStatus() >= 200 .And. HTTPGetStatus() <= 299
        oJson:FromJson(cResponse)
        cToken := oJson["access_token"]
    Endif

    FreeObj(oJson)

Return cToken
```

### 2.4 Padrao de Autenticacao — Bearer Token Login

```tlpp
Static Function ObtemTokenLogin()

    Local oRest   := FWRest():New(SuperGetMV("MV_APIURL", .F., ""))
    Local oJson   := JsonObject():New()
    Local oBody   := JsonObject():New()
    Local aHeaders := {} as array
    Local cToken  as character

    oRest:setPath("/api/auth/login")
    oRest:SetChkStatus(.F.)

    aAdd(aHeaders, "Content-Type: application/json")

    oBody["username"] := SuperGetMV("MV_APIUSR", .F., "")
    oBody["password"] := SuperGetMV("MV_APIPWD", .F., "")
    oRest:SetPostParams(oBody:ToJson())

    If oRest:Post(aHeaders)
        If HTTPGetStatus() >= 200 .And. HTTPGetStatus() <= 299
            oJson:FromJson(oRest:GetResult())
            cToken := oJson["access_token"]
        Endif
    Endif

    FreeObj(oRest)
    FreeObj(oJson)
    FreeObj(oBody)

Return cToken
```

### 2.5 Padrao de Retry

```tlpp
Static Function HttpComRetry(oRest, aHeaders, cMethod, nMaxRetry)

    Local lSucesso := .F. as logical
    Local nTentativa := 0 as numeric

    Default nMaxRetry := 3

    While nTentativa < nMaxRetry .And. !lSucesso
        nTentativa++

        If cMethod == "GET"
            lSucesso := oRest:Get(aHeaders)
        ElseIf cMethod == "POST"
            lSucesso := oRest:Post(aHeaders)
        Endif

        If lSucesso
            If HTTPGetStatus() >= 200 .And. HTTPGetStatus() <= 299
                lSucesso := .T.
            ElseIf HTTPGetStatus() >= 500   // Retry apenas em erros de servidor
                lSucesso := .F.
                TSleep(2000 * nTentativa)   // Backoff progressivo
            Else
                Exit  // Erro 4xx nao faz retry
            Endif
        Else
            TSleep(2000 * nTentativa)
        Endif
    EndDo

Return lSucesso
```

### 2.6 Parse de JSON — Padrao do Time

```tlpp
// PADRAO A — JsonObject (preferido para novos codigos)
oJson := JsonObject():New()
cParseErr := oJson:FromJson(cResponse)

If cParseErr == NIL        // NIL = parse OK
    cValue := oJson["chave"]
    aItens := oJson["items"]
Else
    ConOut("Erro parse JSON: " + cParseErr)
Endif
FreeObj(oJson)

// PADRAO B — FWJsonDeserialize (usado em codigo legado)
Local oJson
FWJsonDeserialize(cResponse, @oJson)
cValue := oJson:CHAVE          // dot-notation, MAIUSCULO
FreeObj(oJson)
```

### 2.7 Leitura de Response Headers (FWRest)

```tlpp
// Para acessar headers de resposta com FWRest:
For nI := 1 to Len(oRest:ORESPONSEH:AHEADERFIELDS)
    If Alltrim(oRest:ORESPONSEH:AHEADERFIELDS[nI][1]) == 'Location'
        cLocation := oRest:ORESPONSEH:AHEADERFIELDS[nI][2]
    Endif
Next nI
```

---

## PARTE 3 — REGRAS OBRIGATORIAS

### 3.1 Obrigatorias

1. **Sempre fazer backup e restore de cFilAnt:**
   ```tlpp
   Local cFilBkp := cFilAnt
   // ... codigo ...
   cFilAnt := cFilBkp   // restaura no final
   ```

2. **Sempre usar CustomLog para logging:**
   ```tlpp
   Local oCustomLog := CustomLog():New()
   Local cIdtoken  := oCustomLog:IDTOKEN    // UUID unico
   // Sucesso:
   oCustomLog:GRAVALOG("CXXX", cIdtoken, 'Msg',, jBody:toJson(), NIL, "1")
   // Erro:
   oCustomLog:GRAVALOG("CXXX", cIdtoken, 'Msg', cStack, jBody:toJson(), NIL, "2")
   ```

3. **Sempre validar o parse JSON antes de usar:**
   ```tlpp
   ret := jBody:FromJson(oRest:GetBodyRequest())
   if ValType(ret) == "C"
       // ret contem string de erro — JSON invalido
       Break
   endif
   ```

4. **Sempre usar `FreeObj()` ao final:**
   ```tlpp
   FreeObj(oRest)
   FreeObj(oJson)
   FreeObj(oCustomLog)
   ```

5. **URLs e credenciais via SuperGetMV (nunca hardcoded):**
   ```tlpp
   cUrl   := SuperGetMV("MV_APIURL", .F., "https://default.url")
   cToken := SuperGetMV("MV_TOKEN", .F., "")
   ```

6. **Paginacao padrao: `Page`/`PageSize` com response `hasNext`/`items`**

7. **Autenticacao do servidor REST: CNPJ no header -> `U_GetFilByCnpj()`**

8. **Usar `ErrorBlock` para capturar excecoes inesperadas:**
   ```tlpp
   Private cErrorLog := ""
   Private bLastError := {|oError| cErrorLog := oError:Description + oError:ErrorStack, Break(oError)}
   ErrorBlock(bLastError)
   ```

9. **SEMPRE retornar `.T.` em methods REST anotados (`@Get`/`@Post`/`@Put`/`@Delete`):**
   Em TLPP REST com anotacoes, o `Return` do method e um sinal para o **framework**, nao o HTTP status:
   - `Return .T.` = "eu tratei a requisicao" — framework usa o StatusCode/Response que voce definiu via `oRest:SetStatusCode()`
   - `Return .F.` = "eu falhei" — framework **descarta** seu SetStatusCode e retorna **HTTP 500**

   O HTTP status code e controlado **exclusivamente** por `oRest:SetStatusCode()`. O Return so diz ao framework se o method tratou a requisicao.
   ```tlpp
   // ERRADO — Return .F. causa HTTP 500 mesmo com SetStatusCode(400)
   oRest:SetStatusCode(400)
   oRest:SetResponse(oResponse:ToJson())
   Return .F.   // Framework sobrescreve com 500!

   // CORRETO — Return .T. respeita o SetStatusCode(400)
   oRest:SetStatusCode(400)
   oRest:SetResponse(oResponse:ToJson())
   Return .T.   // Framework devolve 400 conforme definido
   ```

### 3.2 Recomendadas

9. **Usar `TamSX3("CAMPO")[1]` ao setar valores com `Padr()`**

10. **Usar `DecodeUTF8()` para strings recebidas de APIs externas**

11. **Usar `FwNoAccent()` ao retornar mensagens de erro do MVC**

12. **Usar `ChangeQuery()` ao abrir queries SQL:**
    ```tlpp
    MPSysOpenQuery(ChangeQuery(cQuery), cAlias)
    ```

13. **Sempre fechar alias apos uso:**
    ```tlpp
    (cAlias)->(dbCloseArea())
    ```

14. **Para FWRest, sempre chamar `SetChkStatus(.F.)` e verificar status manualmente**

15. **Sempre chamar `HTTPGetStatus(@cError)` apos qualquer chamada HTTP**

---

## PARTE 4 — ANTI-PATTERNS ENCONTRADOS

### 4.1 CRITICO — Return .F. em Method REST TLPP (Causa HTTP 500 Silencioso)

**Problema:**
```tlpp
// ERRADO — Method REST retorna .F. em caso de erro de negocio
Method getPendingApprovals() Class MinhaAPI
    If Empty(cEmail)
        oRest:SetStatusCode(400)
        oResponse['message'] := "Email nao encontrado"
        oRest:SetResponse(oResponse:ToJson())
        Return .F.    // CAUSA HTTP 500! Framework ignora o SetStatusCode(400)
    EndIf
    ...
Return .T.
```

**Sintoma:** API retorna HTTP 500 mesmo tendo chamado `SetStatusCode(400)` corretamente. Logs mostram que o codigo executou ate o ponto de erro, mas o status HTTP final e 500.

**Causa:** Em TLPP REST com anotacoes (`@Get`/`@Post`/`@Put`/`@Delete`), `Return .F.` sinaliza ao framework que o method **falhou no tratamento da requisicao**. O framework entao descarta qualquer `SetStatusCode()` e `SetResponse()` que tenham sido chamados e retorna HTTP 500 automaticamente.

**Correto:**
```tlpp
// CORRETO — Sempre Return .T., status controlado por SetStatusCode()
Method getPendingApprovals() Class MinhaAPI
    If Empty(cEmail)
        oRest:SetStatusCode(400)
        oResponse['message'] := "Email nao encontrado"
        oRest:SetResponse(oResponse:ToJson())
        Return .T.    // Framework respeita o SetStatusCode(400)
    EndIf
    ...
Return .T.
```

**Regra:** Methods REST anotados devem **SEMPRE** retornar `.T.`. O HTTP status code e controlado exclusivamente por `oRest:SetStatusCode()`.

### 4.2 CRITICO — Credenciais Hardcoded

**Problema:**
```tlpp
// ERRADO — credenciais hardcoded no fonte
oBody["Login"] := "user@exemplo.com.br"
oBody["Senha"] := "SenhaAqui123"
```

**Correto:**
```tlpp
oBody["Login"] := SuperGetMV("XX_LOGIN", .F., "")
oBody["Senha"] := SuperGetMV("XX_PASSW", .F., "")
```

### 4.3 CRITICO — HTTP Sem TLS

**Problema:**
```tlpp
// ERRADO
cUrl := "http://www.api.exemplo.com.br:8080/"   // dados em texto plano
```

**Correto:** Sempre usar HTTPS. Se o servico externo nao suporta, documentar o risco.

### 4.4 ALTO — JSON Body via GET

**Problema:**
```tlpp
// ERRADO
HttpGet(cEndpoint, oJsonTkn:ToJson(), nTimeout, aHeader, @cHeaderGet)
// O 2o parametro de HttpGet e query string, nao body
```

**Correto:** Usar POST quando precisa enviar body JSON.

### 4.5 ALTO — Envelope de Response Inconsistente

**Problema:** POST retorna formatos diferentes entre servicos:
```json
// Servico A: {"id": "001", "status": true, "date": "..."}
// Servico B: {"code": 201, "message": "...", "transaction": "..."}
// Servico C: {"success": true, "message": "..."}
```

**Correto:** Usar sempre o envelope padrao:
```json
{"code": 201, "message": "...", "id": "...", "transaction": "uuid", "date": "..."}
```

### 4.6 MEDIO — Status Code Inconsistente

**Problema:** POST retorna 200, 201 ou 202 conforme o servico.

**Correto:**
- `200` = GET sucesso, PUT/DELETE sucesso
- `201` = POST sucesso (recurso criado)
- `400` = Validacao falhou
- `404` = Recurso nao encontrado
- `500` = Erro interno

### 4.7 MEDIO — Validacao Campo-a-Campo Sem Reutilizacao

**Problema:**
```tlpp
// ERRADO — cada metodo repete validacao manual
If Empty(oJson:GetJsonObject('campo1'))
    SetRestFault(cIdtoken, "Campo1 obrigatorio", .T., 400)
    Break
Endif
If Empty(oJson:GetJsonObject('campo2'))
    SetRestFault(cIdtoken, "Campo2 obrigatorio", .T., 400)
    Break
Endif
// ... 20+ campos validados um a um
```

**Sugestao:** Criar funcao helper para validar campos obrigatorios:
```tlpp
Static Function ValidaCampos(jBody, aCamposObrig)
    Local nI as numeric
    For nI := 1 To Len(aCamposObrig)
        If Empty(jBody[aCamposObrig[nI]])
            Return "Campo '" + aCamposObrig[nI] + "' e obrigatorio"
        Endif
    Next nI
Return ""
```

### 4.8 MEDIO — Falta de Retry em Chamadas Externas

**Problema:** 13 de 15 integracoes nao tem retry.

**Correto:** Implementar retry com backoff para APIs externas (ver template 2.5).

### 4.9 BAIXO — Naming Convention Inconsistente nas Rotas

**Problema:**
```
/v1/tabelaPreco        (camelCase)
/api/v1/pedidovenda    (lowercase)
exemplo/resultado-analise  (kebab-case, sem /api/, sem versao)
```

**Correto:** Padronizar em `/api/v1/<recurso>` lowercase.

### 4.10 BAIXO — PageSize Default Inconsistente

**Problema:** Default varia entre 100, 500 e 10000.

**Correto:** Padronizar default em 100 com max configuravel via SuperGetMV.

---

## PARTE 5 — EXEMPLOS DE REFERENCIA

### 5.1 Servidor REST — TLPP Moderno (REFERENCIA)

Melhor exemplo de classe TLPP REST limpa:
- Declaracao com `@GET`/`@PUT` anotacoes
- Metodos private para logica de negocio
- Response padronizada com `success`/`message`
- Validacao de campos obrigatorios
- Sem dependencia de CNPJ (usa usuario logado)

### 5.2 Servidor REST — WSRestful Classico (REFERENCIA)

Exemplo mais completo de WSRestful com:
- 4 metodos (POST, PUT, GET lista, GET por ID)
- WSDATA com paginacao
- PATHPARAM para path params
- BeginSQL com `%Table%` e `%NotDel%`
- `FWLoadModel` para CRUD
- CustomLog para logging
- `U_GetFilByCnpj()` para autenticacao

### 5.3 Cliente HTTP — FWRest com OAuth2 (REFERENCIA)

Exemplo completo de OAuth2 client_credentials:
- `HttpPost` para token request
- `FWRest` para chamadas subsequentes
- Leitura de response headers via `:ORESPONSEH:AHEADERFIELDS`
- Notificacao de erro por email

### 5.4 Cliente HTTP — Session/Cookie Auth (REFERENCIA)

Exemplo avancado com:
- `HTTPQuote` para acesso a headers de resposta
- Regex para extrair cookie
- Cache de sessao em tabela (SZ0)
- Lock distribuido para prevenir login concorrente
- Retry com backoff

### 5.5 Cliente HTTP — Classe Dedicada (REFERENCIA)

Exemplo de wrapper OOP para API:
- Classe `ConsultaAPIWs` encapsula toda integracao
- Metodos dedicados: `BuscaCnpj()`, `GetHeader()`, `Consumo()`
- URL e headers configurados no construtor
- Mapeamento de response para campos Protheus

---

## RESUMO RAPIDO — CHECKLIST

### Novo Servico REST (Servidor):
- [ ] Usar TLPP com anotacoes (`@GET`, `@POST`, etc.)
- [ ] Prefixo `/api/v1/<recurso>` lowercase
- [ ] Include: `Tlpp-Rest.th`, `Protheus.ch`, `tlpp-core.th`
- [ ] Auth: `U_GetFilByCnpj(jHeader['CNPJ'])` no inicio
- [ ] Backup: `cFilBkp := cFilAnt` no inicio, restaurar no final
- [ ] Log: `CustomLog():New()` com `GRAVALOG()` para sucesso ("1") e erro ("2")
- [ ] Erros: `ErrorBlock` + `Begin Sequence`
- [ ] GET paginado: `Page`/`PageSize` query params, response `{hasNext, items}`
- [ ] POST/PUT/DELETE: response `{code, message, id, transaction, date}`
- [ ] Status: 200=GET/PUT, 201=POST, 400=validacao, 404=nao encontrado, 500=interno
- [ ] `FreeObj()` em todos os objetos ao final

### Nova Integracao Externa (Cliente):
- [ ] Usar `FWRest():New()` (preferido) ou `HTTPQuote` (quando precisa headers)
- [ ] `SetChkStatus(.F.)` + `HTTPGetStatus(@cError)` manual
- [ ] URLs e credenciais via `SuperGetMV()` — nunca hardcode
- [ ] Sempre HTTPS
- [ ] `JsonObject():FromJson()` para parse — validar retorno `!= NIL`
- [ ] Retry com backoff para APIs criticas
- [ ] Log da comunicacao (request/response)
- [ ] `FreeObj()` em todos os objetos
- [ ] Cache de token em tabela se token tiver validade longa
