"""
claude-tdn MCP Server
Pesquisa e busca documentacao do TOTVS Protheus no TDN.
Busca estrutura de tabelas do dicionario Protheus via GitHub.
"""

import json
import re
import urllib.parse

from mcp.server.fastmcp import FastMCP
from curl_cffi import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

TDN_BASE = "https://tdn.totvs.com"

mcp_server = FastMCP(
    "tdn-docs",
    instructions="Pesquisa e busca documentacao do TOTVS Protheus no TDN (TOTVS Developer Network)"
)

_session = None


def get_session():
    global _session
    if _session is None:
        _session = requests.Session(impersonate="chrome124")
    return _session


@mcp_server.tool()
def tdn_search(query: str, limit: int = 10) -> str:
    """Pesquisa paginas de documentacao do Protheus no TDN (TOTVS Developer Network).

    Usar para encontrar documentacao sobre funcoes ADVPL/TLPP, classes,
    modulos do Protheus, componentes do framework ou qualquer topico TOTVS.

    Args:
        query: Termo de busca (ex: "FWRest", "TReport", "MsExecAuto")
        limit: Maximo de resultados (padrao 10)

    Returns:
        Lista de paginas encontradas com IDs, titulos e URLs.
    """
    s = get_session()
    cql = 'type=page AND title~"' + query + '"'
    encoded = urllib.parse.urlencode({"cql": cql, "limit": limit})
    url = TDN_BASE + "/rest/api/content/search?" + encoded

    r = s.get(url)
    if r.status_code != 200:
        return "Error: HTTP " + str(r.status_code) + " - " + r.text[:200]

    data = json.loads(r.text)
    results = data.get("results", [])

    if not results:
        return "Nenhum resultado encontrado para '" + query + "'"

    output = []
    for i, item in enumerate(results):
        title = item["title"]
        page_id = item["id"]
        webui = item.get("_links", {}).get("webui", "")
        page_url = TDN_BASE + webui if webui else ""
        output.append(str(i + 1) + ". [ID: " + page_id + "] " + title)
        if page_url:
            output.append("   " + page_url)

    total = data.get("totalSize", len(results))
    output.append("")
    output.append("Mostrando " + str(len(results)) + " de " + str(total) + " resultados.")
    output.append("Use tdn_fetch com o ID da pagina para buscar o conteudo completo.")

    return "\n".join(output)


@mcp_server.tool()
def tdn_fetch(source: str) -> str:
    """Busca o conteudo completo de uma pagina de documentacao do TDN em Markdown.

    Args:
        source: ID da pagina (ex: "417696190") ou URL completa do TDN
                (ex: "https://tdn.totvs.com/display/framework/FWRest")

    Returns:
        Conteudo da pagina convertido para formato Markdown.
    """
    s = get_session()
    page_id = None
    title = None

    if source.startswith("http"):
        r = s.get(source)
        if r.status_code != 200:
            return "Error: HTTP " + str(r.status_code) + " fetching URL"
        soup = BeautifulSoup(r.content, "html.parser")
        meta = soup.find("meta", {"name": "ajs-page-id"})
        if not meta:
            return "Error: Could not extract page ID from URL"
        page_id = meta["content"]
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text().replace(" - TOTVS Developers", "").strip()
    else:
        page_id = source.strip()

    src_url = TDN_BASE + "/plugins/viewsource/viewpagesrc.action?pageId=" + page_id
    r = s.get(src_url)
    if r.status_code != 200:
        return "Error: HTTP " + str(r.status_code) + " fetching page content"

    md_content = md(r.text, heading_style="ATX")
    md_content = re.sub(r"\n{3,}", "\n\n", md_content)

    page_link = TDN_BASE + "/pages/viewpage.action?pageId=" + page_id

    if title:
        return "# " + title + "\n\nSource: " + page_link + "\n\n" + md_content

    return "Source: " + page_link + "\n\n" + md_content


# --- Dicionario de Dados Protheus ---

DICIONARIO_BASE = "https://raw.githubusercontent.com/Johnnni/protheus-dicionario/main"
_dicionario_index = None  # cache em memoria

# Nomes reservados do Windows que usam prefixo _ no filename
_RESERVED_NAMES = {"CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "LPT1", "LPT2", "LPT3"}


def _get_dicionario_index():
    """Carrega e cacheia o indice do dicionario."""
    global _dicionario_index
    if _dicionario_index is not None:
        return _dicionario_index

    s = get_session()
    url = DICIONARIO_BASE + "/index.json"
    r = s.get(url)
    if r.status_code != 200:
        return None

    _dicionario_index = json.loads(r.text)
    return _dicionario_index


def _table_filename(code):
    """Retorna o nome do arquivo para uma tabela, tratando nomes reservados do Windows."""
    if code.upper() in _RESERVED_NAMES:
        return "_" + code
    return code


def _format_table(data):
    """Converte JSON da tabela para markdown legivel."""
    lines = []
    lines.append("# " + data["tabela"] + " - " + data["nome"])
    if data.get("nome_eng"):
        lines.append("**Nome EN:** " + data["nome_eng"])
    if data.get("modo"):
        lines.append("**Modo:** " + data["modo"])
    if data.get("arquivo"):
        lines.append("**Arquivo:** " + data["arquivo"])
    lines.append("")

    # Campos
    campos = data.get("campos", [])
    if campos:
        lines.append("## Campos (" + str(len(campos)) + ")")
        lines.append("")
        lines.append("| Campo | Titulo | Tipo | Tam | Dec | Obrig |")
        lines.append("|-------|--------|------|-----|-----|-------|")
        for c in campos:
            obrig = "Sim" if c.get("obrig") else ""
            lines.append("| " + c["campo"] + " | " + c["titulo"] + " | " + c["tipo"] + " | " + str(c["tam"]) + " | " + str(c["dec"]) + " | " + obrig + " |")
        lines.append("")

        # Detalhes com validacao/ini_padrao/combo
        details = [c for c in campos if c.get("validacao") or c.get("ini_padrao") or c.get("combo")]
        if details:
            lines.append("### Detalhes")
            for c in details:
                parts = ["**" + c["campo"] + "**:"]
                if c.get("validacao"):
                    parts.append("Validacao: `" + c["validacao"] + "`")
                if c.get("ini_padrao"):
                    parts.append("Ini Padrao: `" + c["ini_padrao"] + "`")
                if c.get("combo"):
                    parts.append("Combo: `" + c["combo"] + "`")
                lines.append("- " + " | ".join(parts))
            lines.append("")

    # Indices
    indices = data.get("indices", [])
    if indices:
        lines.append("## Indices (" + str(len(indices)) + ")")
        lines.append("")
        lines.append("| Ordem | Chave | Descricao |")
        lines.append("|-------|-------|-----------|")
        for idx in indices:
            lines.append("| " + idx["ordem"] + " | " + idx["chave"] + " | " + idx["descricao"] + " |")
        lines.append("")

    # Gatilhos
    gatilhos = data.get("gatilhos", [])
    if gatilhos:
        lines.append("## Gatilhos (" + str(len(gatilhos)) + ")")
        lines.append("")
        lines.append("| Origem | Tipo | Seq | Regra |")
        lines.append("|--------|------|-----|-------|")
        for g in gatilhos:
            lines.append("| " + g["origem"] + " | " + g["tipo"] + " | " + g["seq"] + " | " + g["regra"] + " |")
        lines.append("")

    # Relacionamentos (resumido)
    rels = data.get("relacionamentos", [])
    if rels:
        lines.append("## Relacionamentos (" + str(len(rels)) + ")")
        lines.append("")
        # Mostrar apenas os primeiros 20 para nao poluir
        show = rels[:20]
        lines.append("| Dominio | Expressao | Identificador |")
        lines.append("|---------|-----------|---------------|")
        for r in show:
            lines.append("| " + r["dominio"] + " | " + r["expressao_dom"] + " | " + r["identificador"] + " |")
        if len(rels) > 20:
            lines.append("| ... | *+" + str(len(rels) - 20) + " relacionamentos* | |")
        lines.append("")

    return "\n".join(lines)


@mcp_server.tool()
def dicionario_fetch(tabela: str) -> str:
    """Busca estrutura completa de uma tabela do dicionario Protheus (campos, indices, gatilhos).

    Args:
        tabela: Codigo da tabela (ex: "SA1") ou termo de busca (ex: "Clientes")

    Returns:
        Estrutura da tabela em markdown com campos, indices, gatilhos e relacionamentos.
    """
    s = get_session()
    input_upper = tabela.strip().upper()

    # Heuristica: se parece codigo de tabela (2-4 chars alfanumericos), fetch direto
    if re.match(r'^[A-Z0-9]{2,4}$', input_upper):
        filename = _table_filename(input_upper)
        # Determinar prefixo (primeiro caractere da tabela)
        prefix = input_upper[0]
        url = DICIONARIO_BASE + "/tabelas/" + prefix + "/" + filename + ".json"

        r = s.get(url)
        if r.status_code == 200:
            data = json.loads(r.text)
            return _format_table(data)
        else:
            return "Tabela '" + tabela + "' nao encontrada no dicionario (HTTP " + str(r.status_code) + ")."

    # Busca por nome: carregar indice e filtrar
    index = _get_dicionario_index()
    if index is None:
        return "Erro ao carregar indice do dicionario."

    search = tabela.strip().lower()
    matches = []
    for entry in index:
        if search in entry["nome"].lower():
            matches.append(entry)

    if not matches:
        return "Nenhuma tabela encontrada para '" + tabela + "'."

    if len(matches) == 1:
        # Fetch direto da unica tabela encontrada
        code = matches[0]["codigo"]
        prefix = matches[0]["prefixo"]
        filename = _table_filename(code)
        url = DICIONARIO_BASE + "/tabelas/" + prefix + "/" + filename + ".json"
        r = s.get(url)
        if r.status_code == 200:
            data = json.loads(r.text)
            return _format_table(data)

    # Multiplos matches: listar
    output = ["Encontradas " + str(len(matches)) + " tabelas para '" + tabela + "':", ""]
    output.append("| Codigo | Nome | Prefixo |")
    output.append("|--------|------|---------|")
    for m in matches[:30]:
        output.append("| " + m["codigo"] + " | " + m["nome"] + " | " + m["prefixo"] + " |")
    if len(matches) > 30:
        output.append("| ... | *+" + str(len(matches) - 30) + " tabelas* | |")
    output.append("")
    output.append("Use `dicionario_fetch` com o codigo da tabela para ver a estrutura completa.")

    return "\n".join(output)


if __name__ == "__main__":
    mcp_server.run()
