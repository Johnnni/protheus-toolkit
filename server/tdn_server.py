"""
claude-tdn MCP Server
Pesquisa e busca documentacao do TOTVS Protheus no TDN.
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


if __name__ == "__main__":
    mcp_server.run()
