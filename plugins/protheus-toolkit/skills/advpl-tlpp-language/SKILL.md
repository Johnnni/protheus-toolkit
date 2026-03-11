---
name: advpl-tlpp-language
description: >
  Funcoes nativas da linguagem ADVPL/TLPP e xBase.
  Use esta skill SEMPRE que o usuario pedir codigo ADVPL ou TLPP que envolva:
  manipulacao de strings, arrays, conversoes de tipo, funcoes de data/hora,
  funcoes matematicas, manipulacao de arquivos, blocos de codigo,
  ou qualquer funcao nativa da linguagem (nao do framework Protheus).
  Inclui AllTrim, SubStr, AAdd, AScan, Val, Str, IIf, Empty, Date, Type,
  ValType, PadR, StrZero, Round, e todas as demais funcoes da linguagem base.
---

# ADVPL/TLPP — Referencia de Funcoes da Linguagem

Referencia prescritiva das funcoes nativas da linguagem ADVPL/TLPP,
com padroes e boas praticas para desenvolvimento Protheus.
Ordenada por frequencia de uso.

---

## 1. STRINGS — Manipulacao de Texto

### Funcoes de limpeza e padding

| Funcao | Assinatura | Descricao | Chamadas |
|--------|-----------|-----------|----------|
| AllTrim | `AllTrim(cText) => character` | Remove espacos a esquerda e direita | 42.177 |
| RTrim | `RTrim(cText) => character` | Remove espacos a direita | 760 |
| LTrim | `LTrim(cText) => character` | Remove espacos a esquerda | 156 |
| Trim | `Trim(cText) => character` | Alias de RTrim | 611 |
| PadR | `PadR(xExp, nLen, [cFill]) => character` | Preenche com caractere a direita | 3.548 |
| PadL | `PadL(xExp, nLen, [cFill]) => character` | Preenche com caractere a esquerda | 328 |
| PadC | `PadC(xExp, nLen, [cFill]) => character` | Centraliza com preenchimento | 147 |
| Space | `Space(nCount) => character` | String de N espacos | 5.264 |
| Replicate | `Replicate(cStr, nTimes) => character` | Repete string N vezes | 1.021 |

**Padrao recomendado:** Usar `AllTrim` como padrao para limpar campos do banco.
`PadR` e obrigatorio ao montar chaves de busca concatenadas.

```advpl
// Padrao: PadR para montar chave de seek
cChave := xFilial("SA1") + PadR(cCodigo, TamSX3("A1_COD")[1]) + PadR(cLoja, TamSX3("A1_LOJA")[1])
SA1->(MsSeek(cChave))

// Inicializar variavel de campo com tamanho correto
Local cDoc := Space(TamSX3("F1_DOC")[1])
```

### Funcoes de extracao e busca

| Funcao | Assinatura | Descricao | Chamadas |
|--------|-----------|-----------|----------|
| SubStr | `SubStr(cText, nStart, [nLen]) => character` | Extrai parte da string | 18.554 |
| Subs | `Subs(cText, nStart, [nLen]) => character` | Alias abreviado de SubStr | 713 |
| Left | `Left(cText, nLen) => character` | N caracteres da esquerda | 776 |
| Right | `Right(cText, nLen) => character` | N caracteres da direita | 276 |
| Rat | `Rat(cSearch, cText) => numeric` | Posicao da ultima ocorrencia | 370 |

### Funcoes de transformacao

| Funcao | Assinatura | Descricao | Chamadas |
|--------|-----------|-----------|----------|
| Upper | `Upper(cText) => character` | Converte para maiusculas | 3.818 |
| Lower | `Lower(cText) => character` | Converte para minusculas | 288 |
| Capital | `Capital(cText) => character` | Primeira letra maiuscula | 127 |
| StrTran | `StrTran(cStr, cSearch, [cReplace], [nStart], [nCount]) => character` | Substitui substrings | 4.123 |
| Transform | `Transform(xValue, cPicture) => character` | Formata com mascara | 5.622 |
| Chr | `Chr(nCode) => character` | ASCII para caractere | 3.071 |
| Asc | `Asc(cChar) => numeric` | Caractere para ASCII | 206 |
| OemToAnsi | `OemToAnsi(cText) => character` | Converte charset OEM para ANSI | 723 |

**Constantes comuns com Chr:**
```advpl
CRLF := Chr(13) + Chr(10)  // Quebra de linha Windows
cTab := Chr(9)              // Tabulacao
```

---

## 2. CONVERSAO DE TIPOS

### String <-> Numerico

| Funcao | Assinatura | Descricao | Chamadas |
|--------|-----------|-----------|----------|
| Val | `Val(cString) => numeric` | String para numerico | 8.062 |
| Str | `Str(nNum, [nLen], [nDec]) => character` | Numero para string | 4.265 |
| StrZero | `StrZero(nVal, nLen, [nDec]) => character` | Numero para string com zeros a esquerda | 3.624 |
| cValToChar | `cValToChar(xParam) => character` | Qualquer tipo para string | 3.838 |
| AllToChar | `AllToChar(xParam) => character` | Qualquer tipo para string (alternativa) | 211 |

**Padrao recomendado:**
```advpl
// Para exibir/concatenar: cValToChar
ConOut("Total: " + cValToChar(nTotal))

// Para formatar numero com tamanho fixo: Str
cValor := Str(nPreco, 15, 2)

// Para codigos sequenciais: StrZero
cItem := StrZero(nItem, 4)  // "0001", "0002", ...
```

### String <-> Data

| Funcao | Assinatura | Descricao | Chamadas |
|--------|-----------|-----------|----------|
| DToS | `DToS(dDate) => character` | Data para "AAAAMMDD" | 3.537 |
| SToD | `SToD(cDate) => date` | "AAAAMMDD" para data | 1.225 |
| DToC | `DToC(dDate) => character` | Data para formato local "DD/MM/AAAA" | 835 |
| CToD | `CToD(cDate) => date` | Formato local para data | 1.464 |

**Padrao obrigatorio:** Sempre usar `DToS` ao concatenar datas em chaves de busca ou queries SQL:
```advpl
cQuery += " AND E1_VENCTO >= '" + DToS(dDataDe) + "' "
```

### Verificacao de tipo

| Funcao | Assinatura | Descricao | Chamadas |
|--------|-----------|-----------|----------|
| Type | `Type(cExpr) => character` | Tipo de expressao (string com nome) | 8.153 |
| ValType | `ValType(xVal) => character` | Tipo de valor ja avaliado | 3.523 |
| Empty | `Empty(xExp) => logical` | Verifica se vazio/nulo/zero/falso | 40.012 |
| IsNull | `IsNull(xVal) => logical` | Verifica se e NIL | 111 |
| IsAlpha | `IsAlpha(cText) => logical` | Verifica se e alfabetico | 231 |
| IsDigit | `IsDigit(cText) => logical` | Verifica se e numerico | 123 |

**Diferenca critica Type vs ValType:**
```advpl
// Type: recebe STRING com o nome da variavel (avalia se existe)
If Type("cMeuVar") != "U"  // "U" = undefined (nao existe)
    // variavel existe
EndIf

// ValType: recebe o VALOR diretamente (variavel ja deve existir)
If ValType(xParam) == "C"  // "C"=char, "N"=num, "D"=date, "L"=logic, "A"=array, "O"=obj
    // e string
EndIf
```

---

## 3. ARRAYS

| Funcao | Assinatura | Descricao | Chamadas |
|--------|-----------|-----------|----------|
| AAdd | `AAdd(aDest, xExpr) => variant` | Adiciona elemento ao final | 57.630 |
| AScan | `AScan(aArr, xExpr, [nStart], [nCount]) => numeric` | Busca elemento, retorna posicao | 5.378 |
| ATail | `ATail(aArr) => variant` | Retorna ultimo elemento | 5.087 |
| ASize | `ASize(aArr, nNewSize) => NIL` | Redimensiona array | 1.899 |
| AClone | `AClone(aArr) => array` | Cria copia do array | 763 |
| AEval | `AEval(aArr, bBlock, [nStart], [nCount]) => NIL` | Executa bloco para cada elemento | 540 |
| ASort | `ASort(aArr, [nStart], [nCount], [bOrder]) => array` | Ordena array | 387 |
| ADel | `ADel(aArr, nPos) => NIL` | Remove elemento (nao redimensiona) | 88 |
| AFill | `AFill(aArr, xVal, [nStart], [nCount]) => NIL` | Preenche array com valor | 84 |
| Len | `Len(xVal) => numeric` | Tamanho de string ou array | 27.660 |

**Padrao para remover elemento corretamente:**
```advpl
// ADel apenas marca como NIL — precisa redimensionar depois
ADel(aArr, nPos)
ASize(aArr, Len(aArr) - 1)
```

**Padrao AScan com bloco de codigo:**
```advpl
// Buscar em array bidimensional
nPos := AScan(aCampos, {|x| AllTrim(x[1]) == "D1_COD"})
If nPos > 0
    cValor := aCampos[nPos][2]
EndIf
```

---

## 4. DATA E HORA

| Funcao | Assinatura | Descricao | Chamadas |
|--------|-----------|-----------|----------|
| Date | `Date() => date` | Data atual do sistema | 1.177 |
| Year | `Year(dDate) => numeric` | Extrai ano | 523 |
| Month | `Month(dDate) => numeric` | Extrai mes | 487 |
| Day | `Day(dDate) => numeric` | Extrai dia | 408 |
| Time | `Time() => character` | Hora atual "HH:MM:SS" | 774 |
| Seconds | `Seconds() => numeric` | Segundos desde meia-noite | 110 |

---

## 5. MATEMATICA

| Funcao | Assinatura | Descricao | Chamadas |
|--------|-----------|-----------|----------|
| Round | `Round(nVal, nDec) => numeric` | Arredonda | 1.526 |
| NoRound | `NoRound(nVal, nDec) => numeric` | Trunca sem arredondar | 308 |
| Abs | `Abs(nVal) => numeric` | Valor absoluto | 199 |
| Max | `Max(nVal1, nVal2) => numeric` | Maior valor | 497 |
| Min | `Min(nVal1, nVal2) => numeric` | Menor valor | 434 |
| Int | `Int(nVal) => numeric` | Parte inteira | 151 |
| Mod | `Mod(nVal, nDiv) => numeric` | Resto da divisao | 210 |
| Ceiling | `Ceiling(nVal) => numeric` | Arredonda para cima | 103 |

**Atencao com NoRound vs Round:**
```advpl
// NoRound TRUNCA, nao arredonda — usar para calculos fiscais quando exigido
NoRound(10.456, 2)  // => 10.45
Round(10.456, 2)     // => 10.46
```

---

## 6. LOGICA E CONTROLE

| Funcao | Assinatura | Descricao | Chamadas |
|--------|-----------|-----------|----------|
| IIf | `IIf(lCond, xTrue, xFalse) => variant` | Ternario inline | 29.874 |
| ExistBlock | `ExistBlock(cBlock) => logical` | Verifica se bloco de codigo existe | 739 |
| Eval | `Eval(bBlock, [...]) => variant` | Executa bloco de codigo | 432 |
| ErrorBlock | `ErrorBlock([bNewBlock]) => codeblock` | Define/obtem tratamento de erro | 136 |
| PCount | `PCount() => numeric` | Numero de parametros recebidos | 267 |
| Sleep | `Sleep(nMs) => NIL` | Pausa execucao em milissegundos | 145 |
| Coalesce | `Coalesce(x1, x2, ...) => variant` | Retorna primeiro valor nao nulo | 162 |

**Padrao IIf (recomendado):**
```advpl
cTipo := IIf(Len(cCGC) == 11, "F", "J")  // Pessoa Fisica ou Juridica
```

---

## 7. ARQUIVOS

| Funcao | Assinatura | Descricao | Chamadas |
|--------|-----------|-----------|----------|
| File | `File(cPath) => logical` | Verifica se arquivo existe | 767 |
| FCreate | `FCreate(cPath) => numeric` | Cria arquivo, retorna handle | 93 |
| FWrite | `FWrite(nHandle, cData) => numeric` | Escreve em arquivo | 174 |
| FSeek | `FSeek(nHandle, nOffset, [nOrigin]) => numeric` | Posiciona ponteiro | 103 |
| FClose | `FClose(nHandle) => logical` | Fecha arquivo | 128 |
| FErase | `FErase(cPath) => numeric` | Apaga arquivo | 424 |
| FError | `FError() => numeric` | Ultimo codigo de erro | 88 |
| MemoWrite | `MemoWrite(cPath, cContent) => logical` | Grava texto em arquivo | 144 |
| MemoLine | `MemoLine(cText, nWidth, nLine) => character` | Retorna linha de texto memo | 122 |

**Padrao para escrita em arquivo:**
```advpl
nHandle := FCreate(cPath)
If nHandle >= 0
    FWrite(nHandle, cConteudo)
    FClose(nHandle)
Else
    ConOut("Erro ao criar arquivo: " + cValToChar(FError()))
EndIf
```

---

## 8. TOKENIZACAO

| Funcao | Assinatura | Descricao | Chamadas |
|--------|-----------|-----------|----------|
| StrToKArr | `StrToKArr(cStr, cSep) => array` | Quebra string em array pelo separador | 311 |
| StrToKArr2 | `StrToKArr2(cStr, cSep) => array` | Versao 2, trata separadores consecutivos | 221 |

```advpl
// Quebrar lista separada por virgula
aItens := StrToKArr("001,002,003", ",")
// aItens = {"001", "002", "003"}
```

---

## 9. LOG E DIAGNOSTICO

### Funcoes de output e log

| Funcao | Assinatura | Descricao | Uso |
|--------|-----------|-----------|-----|
| ConOut | `ConOut(cMsg) => NIL` | Escreve no console.log do AppServer | Debug temporario |
| FwLogMsg | `FwLogMsg(cSeverity, cTransId, cSource, cFunction, cOper, cCode, cMsg, nP1, nP2, aExtras) => NIL` | Log estruturado com severidade | Log permanente |

**ConOut — debug temporario (remover antes de deploy):**
```advpl
ConOut(">>> DEBUG: cStatus = " + cValToChar(cStatus))
ConOut(">>> DEBUG: nRecno = " + cValToChar(nRecno))
```

**FwLogMsg — log permanente e estruturado:**
```advpl
// Severidades: "INFO", "WARNING", "ERROR"
FwLogMsg("INFO", /*cTransId*/, "U_MEUFUNC", FunName(), "", "01", ;
    "Processamento concluido. Total: " + cValToChar(nTotal), 0, 0, {})

FwLogMsg("ERROR", /*cTransId*/, "U_MEUFUNC", FunName(), "MATA410", "01", ;
    "Erro ao gerar pedido: " + cErroMsg, 0, 0, GetAutoGrLog())
```

Para guia completo de debugging e diagnostico, consulte a skill `advpl-debugging`.

---

## 10. ANTI-PATTERNS — O que NUNCA gerar

| Errado | Correto | Motivo |
|--------|---------|--------|
| `nVar++` | `nVar += 1` ou `nVar := nVar + 1` | Operador `++` NAO existe em ADVPL |
| `True` / `False` | `.T.` / `.F.` | Booleanos ADVPL usam ponto |
| `null` / `None` | `NIL` | Nulo em ADVPL e NIL |
| `aArray.Add(x)` | `AAdd(aArray, x)` | ADVPL usa funcoes, nao metodos de array |
| `Trim(cTexto)` sem contexto | `AllTrim(cTexto)` | AllTrim e o padrao recomendado |
| Concatenar data sem DToS | `DToS(dData)` para chaves | Data deve ser string AAAAMMDD em queries |
| `If Type("x") == "C"` | `If ValType(x) == "C"` | Type recebe string, ValType recebe valor |

---

## 11. NOTACAO HUNGARA (obrigatoria)

| Prefixo | Tipo | Exemplo |
|---------|------|---------|
| `c` | Character | `cNome`, `cCodigo` |
| `n` | Numeric | `nTotal`, `nQtd` |
| `d` | Date | `dDataIni`, `dVencto` |
| `l` | Logical | `lOk`, `lExiste` |
| `a` | Array | `aItens`, `aCampos` |
| `o` | Object | `oModel`, `oJson` |
| `b` | CodeBlock | `bBloco`, `bValid` |
| `x` | Indeterminado | `xParam`, `xRetorno` |

Em TLPP, adicionar tipo apos declaracao:
```tlpp
Local cNome := "" As Character
Local nTotal := 0 As Numeric
Local aItens := {} As Array
```
