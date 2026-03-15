"""Integration tests for claude-tdn MCP server (live HTTP calls).

Run with: pytest --integration
Requires internet access.
"""

import time
import pytest

import tdn_server as srv

pytestmark = pytest.mark.integration


# Reset session between tests to avoid stale connections
@pytest.fixture(autouse=True)
def fresh_session():
    srv._session = None
    srv._dicionario_index = None
    yield
    srv._session = None
    srv._dicionario_index = None


# ---------------------------------------------------------------------------
# tdn_search - live
# ---------------------------------------------------------------------------

class TestTdnSearchLive:

    def test_search_fwrest(self):
        result = srv.tdn_search("FWRest", limit=5)
        assert "FWRest" in result
        assert "[ID:" in result
        assert "Mostrando" in result

    def test_search_msexecauto(self):
        result = srv.tdn_search("MsExecAuto", limit=3)
        assert "[ID:" in result

    def test_search_treport(self):
        result = srv.tdn_search("TReport", limit=3)
        assert "[ID:" in result

    def test_search_nonsense_returns_empty(self):
        result = srv.tdn_search("zxqwkj9999xyzabc", limit=3)
        assert "Nenhum resultado" in result

    def test_search_limit_respected(self):
        result = srv.tdn_search("Protheus", limit=3)
        # Count result lines that have [ID:
        id_lines = [line for line in result.split("\n") if "[ID:" in line]
        assert len(id_lines) <= 3


# ---------------------------------------------------------------------------
# tdn_fetch - live
# ---------------------------------------------------------------------------

class TestTdnFetchLive:

    def test_fetch_known_page_by_id(self):
        # First search to get a valid ID
        search_result = srv.tdn_search("FWRest", limit=1)
        # Extract first ID
        import re
        match = re.search(r"\[ID: (\d+)\]", search_result)
        assert match, f"Could not find page ID in search results: {search_result}"
        page_id = match.group(1)

        time.sleep(1)  # be kind to the API

        result = srv.tdn_fetch(page_id)
        assert "Source:" in result
        assert page_id in result
        # Should have meaningful content (more than just header)
        assert len(result) > 100

    def test_fetch_by_url(self):
        result = srv.tdn_fetch(
            "https://tdn.totvs.com/display/tec/DBSelectArea"
        )
        assert "Source:" in result
        assert "DBSelectArea" in result or "dbselectarea" in result.lower()

    def test_fetch_invalid_id(self):
        result = srv.tdn_fetch("1")
        # Should either error or return minimal content
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# dicionario_fetch - live
# ---------------------------------------------------------------------------

class TestDicionarioFetchLive:

    def test_fetch_sa1(self):
        result = srv.dicionario_fetch("SA1")
        assert "# SA1" in result
        assert "Clientes" in result
        assert "A1_COD" in result
        assert "## Campos" in result
        assert "## Indices" in result

    def test_fetch_sa2(self):
        result = srv.dicionario_fetch("SA2")
        assert "# SA2" in result
        assert "Fornecedores" in result or "Fornecedor" in result

    def test_fetch_sc5(self):
        result = srv.dicionario_fetch("SC5")
        assert "# SC5" in result

    def test_fetch_reserved_name_aux(self):
        result = srv.dicionario_fetch("AUX")
        # AUX is a Windows reserved name, should use _AUX.json
        assert isinstance(result, str)
        # Should either find the table or say not found (not crash)
        assert "AUX" in result or "nao encontrada" in result

    def test_fetch_nonexistent_table(self):
        result = srv.dicionario_fetch("ZZZ")
        assert "nao encontrada" in result

    def test_search_by_name_clientes(self):
        result = srv.dicionario_fetch("Clientes")
        # Should find SA1 directly or list matches
        assert "SA1" in result or "Clientes" in result

    def test_search_by_name_pedidos(self):
        result = srv.dicionario_fetch("Pedidos")
        # Should return multiple matches
        assert "SC5" in result or "Encontradas" in result

    def test_search_nonexistent_name(self):
        result = srv.dicionario_fetch("XyzInexistenteAbc123")
        assert "Nenhuma tabela encontrada" in result


# ---------------------------------------------------------------------------
# Performance / response time
# ---------------------------------------------------------------------------

class TestPerformance:

    def test_search_response_time(self):
        start = time.time()
        srv.tdn_search("FWRest", limit=5)
        elapsed = time.time() - start
        assert elapsed < 15, f"tdn_search took {elapsed:.1f}s (expected < 15s)"

    def test_fetch_response_time(self):
        start = time.time()
        srv.dicionario_fetch("SA1")
        elapsed = time.time() - start
        assert elapsed < 10, f"dicionario_fetch took {elapsed:.1f}s (expected < 10s)"

    def test_dicionario_index_caching(self):
        # First call loads index
        start1 = time.time()
        srv.dicionario_fetch("Clientes")
        elapsed1 = time.time() - start1

        # Second call should use cache
        start2 = time.time()
        srv.dicionario_fetch("Fornecedores")
        elapsed2 = time.time() - start2

        # Cached call should be significantly faster
        assert elapsed2 < elapsed1 or elapsed2 < 2, (
            f"Cache not working: 1st={elapsed1:.1f}s, 2nd={elapsed2:.1f}s"
        )
