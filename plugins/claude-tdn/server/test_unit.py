"""Unit tests for claude-tdn MCP server (mocked HTTP)."""

import json
import pytest
from unittest.mock import patch, MagicMock

import tdn_server as srv


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_response(status_code=200, text="", content=None):
    r = MagicMock()
    r.status_code = status_code
    r.text = text
    r.content = content or text.encode("utf-8")
    return r


# ---------------------------------------------------------------------------
# tdn_search
# ---------------------------------------------------------------------------

class TestTdnSearch:

    @patch.object(srv, "get_session")
    def test_basic_search(self, mock_gs):
        payload = {
            "results": [
                {
                    "id": "123",
                    "title": "FWRest",
                    "_links": {"webui": "/display/framework/FWRest"},
                },
                {
                    "id": "456",
                    "title": "FWRest - Exemplo",
                    "_links": {"webui": "/display/framework/FWRest+Exemplo"},
                },
            ],
            "totalSize": 2,
        }
        mock_gs.return_value.get.return_value = _mock_response(text=json.dumps(payload))

        result = srv.tdn_search("FWRest")

        assert "[ID: 123] FWRest" in result
        assert "[ID: 456] FWRest - Exemplo" in result
        assert "tdn.totvs.com/display/framework/FWRest" in result
        assert "Mostrando 2 de 2 resultados" in result

    @patch.object(srv, "get_session")
    def test_empty_results(self, mock_gs):
        payload = {"results": [], "totalSize": 0}
        mock_gs.return_value.get.return_value = _mock_response(text=json.dumps(payload))

        result = srv.tdn_search("xyzNaoExiste999")

        assert "Nenhum resultado" in result
        assert "xyzNaoExiste999" in result

    @patch.object(srv, "get_session")
    def test_http_error(self, mock_gs):
        mock_gs.return_value.get.return_value = _mock_response(
            status_code=500, text="Internal Server Error"
        )

        result = srv.tdn_search("FWRest")

        assert "Error" in result
        assert "500" in result

    @patch.object(srv, "get_session")
    def test_limit_parameter(self, mock_gs):
        payload = {"results": [], "totalSize": 0}
        mock_gs.return_value.get.return_value = _mock_response(text=json.dumps(payload))

        srv.tdn_search("FWRest", limit=5)

        called_url = mock_gs.return_value.get.call_args[0][0]
        assert "limit=5" in called_url

    @patch.object(srv, "get_session")
    def test_no_webui_link(self, mock_gs):
        payload = {
            "results": [{"id": "789", "title": "Pagina Sem Link", "_links": {}}],
            "totalSize": 1,
        }
        mock_gs.return_value.get.return_value = _mock_response(text=json.dumps(payload))

        result = srv.tdn_search("teste")

        assert "[ID: 789] Pagina Sem Link" in result
        # Should not have a URL line for this result
        assert "tdn.totvs.com" not in result.split("\n")[1]

    @patch.object(srv, "get_session")
    def test_cql_query_encoding(self, mock_gs):
        payload = {"results": [], "totalSize": 0}
        mock_gs.return_value.get.return_value = _mock_response(text=json.dumps(payload))

        srv.tdn_search("MsExecAuto")

        called_url = mock_gs.return_value.get.call_args[0][0]
        assert "MsExecAuto" in called_url
        assert "type%3Dpage" in called_url or "type=page" in called_url


# ---------------------------------------------------------------------------
# tdn_fetch
# ---------------------------------------------------------------------------

class TestTdnFetch:

    @patch.object(srv, "get_session")
    def test_fetch_by_id(self, mock_gs):
        html_content = "<h1>FWRest</h1><p>Framework REST do Protheus</p>"
        mock_gs.return_value.get.return_value = _mock_response(text=html_content)

        result = srv.tdn_fetch("417696190")

        assert "417696190" in result
        assert "viewpage.action" in result
        # markdownify should convert HTML
        assert "FWRest" in result

    @patch.object(srv, "get_session")
    def test_fetch_by_url(self, mock_gs):
        # First call: fetch the URL page to extract page ID
        url_html = """
        <html>
        <head>
            <title>FWRest - TOTVS Developers</title>
            <meta name="ajs-page-id" content="417696190">
        </head>
        <body></body>
        </html>
        """
        # Second call: fetch viewsource
        src_html = "<h2>Descricao</h2><p>FWRest e o framework REST.</p>"

        mock_session = mock_gs.return_value
        mock_session.get.side_effect = [
            _mock_response(text=url_html, content=url_html.encode("utf-8")),
            _mock_response(text=src_html),
        ]

        result = srv.tdn_fetch("https://tdn.totvs.com/display/framework/FWRest")

        assert "# FWRest" in result
        assert "417696190" in result

    @patch.object(srv, "get_session")
    def test_fetch_url_no_page_id(self, mock_gs):
        url_html = "<html><head></head><body>No meta</body></html>"
        mock_gs.return_value.get.return_value = _mock_response(
            text=url_html, content=url_html.encode("utf-8")
        )

        result = srv.tdn_fetch("https://tdn.totvs.com/display/framework/Nada")

        assert "Error" in result
        assert "page ID" in result

    @patch.object(srv, "get_session")
    def test_fetch_http_error_on_url(self, mock_gs):
        mock_gs.return_value.get.return_value = _mock_response(status_code=404, text="Not Found")

        result = srv.tdn_fetch("https://tdn.totvs.com/display/framework/Nada")

        assert "Error" in result
        assert "404" in result

    @patch.object(srv, "get_session")
    def test_fetch_http_error_on_source(self, mock_gs):
        mock_gs.return_value.get.return_value = _mock_response(status_code=403, text="Forbidden")

        result = srv.tdn_fetch("999999999")

        assert "Error" in result
        assert "403" in result

    @patch.object(srv, "get_session")
    def test_newline_cleanup(self, mock_gs):
        html = "<p>Line1</p>\n\n\n\n\n<p>Line2</p>"
        mock_gs.return_value.get.return_value = _mock_response(text=html)

        result = srv.tdn_fetch("123")

        # Should not have 3+ consecutive newlines
        assert "\n\n\n" not in result


# ---------------------------------------------------------------------------
# _table_filename
# ---------------------------------------------------------------------------

class TestTableFilename:

    def test_normal_table(self):
        assert srv._table_filename("SA1") == "SA1"

    def test_reserved_con(self):
        assert srv._table_filename("CON") == "_CON"

    def test_reserved_prn(self):
        assert srv._table_filename("PRN") == "_PRN"

    def test_reserved_aux(self):
        assert srv._table_filename("AUX") == "_AUX"

    def test_reserved_nul(self):
        assert srv._table_filename("NUL") == "_NUL"

    def test_reserved_com1(self):
        assert srv._table_filename("COM1") == "_COM1"

    def test_reserved_lpt1(self):
        assert srv._table_filename("LPT1") == "_LPT1"

    def test_non_reserved_similar(self):
        assert srv._table_filename("CON1") == "CON1"  # not in reserved list? check
        # COM1 IS reserved, CON1 is NOT
        assert srv._table_filename("CON1") == "CON1"


# ---------------------------------------------------------------------------
# _format_table
# ---------------------------------------------------------------------------

class TestFormatTable:

    def test_minimal_table(self):
        data = {"tabela": "ZZ1", "nome": "Teste", "campos": [], "indices": []}
        result = srv._format_table(data)
        assert "# ZZ1 - Teste" in result

    def test_with_fields(self):
        data = {
            "tabela": "SA1",
            "nome": "Clientes",
            "nome_eng": "Customers",
            "modo": "C",
            "arquivo": "SA1990",
            "campos": [
                {
                    "campo": "A1_COD",
                    "titulo": "Codigo",
                    "tipo": "C",
                    "tam": 6,
                    "dec": 0,
                    "obrig": True,
                    "validacao": "ExistChav('SA1')",
                    "ini_padrao": "",
                    "combo": "",
                },
            ],
            "indices": [
                {"ordem": "1", "chave": "A1_FILIAL+A1_COD+A1_LOJA", "descricao": "Codigo+Loja"},
            ],
        }
        result = srv._format_table(data)

        assert "# SA1 - Clientes" in result
        assert "**Nome EN:** Customers" in result
        assert "**Modo:** C" in result
        assert "A1_COD" in result
        assert "Sim" in result  # obrig=True
        assert "ExistChav" in result
        assert "A1_FILIAL+A1_COD+A1_LOJA" in result

    def test_with_gatilhos(self):
        data = {
            "tabela": "SA1",
            "nome": "Clientes",
            "campos": [],
            "gatilhos": [
                {"origem": "A1_COD", "tipo": "P", "seq": "001", "regra": "POSICIONE('SA1')"},
            ],
        }
        result = srv._format_table(data)
        assert "## Gatilhos (1)" in result
        assert "A1_COD" in result

    def test_with_relationships_truncation(self):
        rels = []
        for i in range(25):
            rels.append({
                "dominio": "SA1",
                "expressao_dom": f"A1_COD{i}",
                "identificador": f"{i:03d}",
                "expressao_ident": "",
            })
        data = {"tabela": "SA1", "nome": "Clientes", "campos": [], "relacionamentos": rels}
        result = srv._format_table(data)

        assert "## Relacionamentos (25)" in result
        assert "+5 relacionamentos" in result  # 25-20 = 5 truncated

    def test_no_optional_sections(self):
        data = {"tabela": "ZZ1", "nome": "Teste"}
        result = srv._format_table(data)
        assert "## Campos" not in result
        assert "## Indices" not in result
        assert "## Gatilhos" not in result
        assert "## Relacionamentos" not in result


# ---------------------------------------------------------------------------
# dicionario_fetch
# ---------------------------------------------------------------------------

class TestDicionarioFetch:

    @patch.object(srv, "get_session")
    def test_fetch_by_code(self, mock_gs):
        table_json = json.dumps({
            "tabela": "SA1",
            "nome": "Clientes",
            "campos": [],
            "indices": [],
        })
        mock_gs.return_value.get.return_value = _mock_response(text=table_json)

        result = srv.dicionario_fetch("SA1")

        assert "# SA1 - Clientes" in result

    @patch.object(srv, "get_session")
    def test_fetch_by_code_lowercase(self, mock_gs):
        table_json = json.dumps({
            "tabela": "SA1",
            "nome": "Clientes",
            "campos": [],
        })
        mock_gs.return_value.get.return_value = _mock_response(text=table_json)

        result = srv.dicionario_fetch("sa1")

        assert "# SA1 - Clientes" in result

    @patch.object(srv, "get_session")
    def test_fetch_by_code_not_found(self, mock_gs):
        mock_gs.return_value.get.return_value = _mock_response(status_code=404, text="Not Found")

        result = srv.dicionario_fetch("ZZZ")

        assert "nao encontrada" in result

    @patch.object(srv, "get_session")
    def test_fetch_reserved_name(self, mock_gs):
        table_json = json.dumps({
            "tabela": "AUX",
            "nome": "Auxiliar",
            "campos": [],
        })
        mock_gs.return_value.get.return_value = _mock_response(text=table_json)

        srv.dicionario_fetch("AUX")

        called_url = mock_gs.return_value.get.call_args[0][0]
        assert "/_AUX.json" in called_url

    @patch.object(srv, "_get_dicionario_index")
    @patch.object(srv, "get_session")
    def test_search_by_name_single_match(self, mock_gs, mock_idx):
        mock_idx.return_value = [
            {"codigo": "SA1", "nome": "Clientes", "prefixo": "S"},
            {"codigo": "SA2", "nome": "Fornecedores", "prefixo": "S"},
        ]
        table_json = json.dumps({
            "tabela": "SA1",
            "nome": "Clientes",
            "campos": [],
        })
        mock_gs.return_value.get.return_value = _mock_response(text=table_json)

        result = srv.dicionario_fetch("Clientes")

        assert "# SA1 - Clientes" in result

    @patch.object(srv, "_get_dicionario_index")
    @patch.object(srv, "get_session")
    def test_search_by_name_multiple_matches(self, mock_gs, mock_idx):
        mock_idx.return_value = [
            {"codigo": "SC5", "nome": "Pedidos de Venda", "prefixo": "S"},
            {"codigo": "SC6", "nome": "Itens Pedidos de Venda", "prefixo": "S"},
            {"codigo": "SC9", "nome": "Pedidos de Compra", "prefixo": "S"},
        ]

        result = srv.dicionario_fetch("Pedidos")

        assert "Encontradas" in result
        assert "SC5" in result
        assert "SC6" in result
        assert "SC9" in result

    @patch.object(srv, "_get_dicionario_index")
    def test_search_by_name_no_match(self, mock_idx):
        mock_idx.return_value = [
            {"codigo": "SA1", "nome": "Clientes", "prefixo": "S"},
        ]

        result = srv.dicionario_fetch("XyzInexistente")

        assert "Nenhuma tabela encontrada" in result

    @patch.object(srv, "_get_dicionario_index")
    def test_search_index_error(self, mock_idx):
        mock_idx.return_value = None

        result = srv.dicionario_fetch("Clientes")

        assert "Erro ao carregar indice" in result


# ---------------------------------------------------------------------------
# _get_dicionario_index (cache behavior)
# ---------------------------------------------------------------------------

class TestDicionarioIndex:

    def setup_method(self):
        srv._dicionario_index = None  # reset cache

    def teardown_method(self):
        srv._dicionario_index = None  # cleanup

    @patch.object(srv, "get_session")
    def test_loads_and_caches(self, mock_gs):
        index_data = [{"codigo": "SA1", "nome": "Clientes", "prefixo": "S"}]
        mock_gs.return_value.get.return_value = _mock_response(text=json.dumps(index_data))

        result1 = srv._get_dicionario_index()
        result2 = srv._get_dicionario_index()

        assert result1 == index_data
        assert result2 == index_data
        # Should only fetch once (cached)
        assert mock_gs.return_value.get.call_count == 1

    @patch.object(srv, "get_session")
    def test_returns_none_on_error(self, mock_gs):
        mock_gs.return_value.get.return_value = _mock_response(status_code=500, text="Error")

        result = srv._get_dicionario_index()

        assert result is None


# ---------------------------------------------------------------------------
# get_session
# ---------------------------------------------------------------------------

class TestGetSession:

    def setup_method(self):
        srv._session = None

    def teardown_method(self):
        srv._session = None

    def test_creates_session(self):
        session = srv.get_session()
        assert session is not None

    def test_returns_same_session(self):
        s1 = srv.get_session()
        s2 = srv.get_session()
        assert s1 is s2
