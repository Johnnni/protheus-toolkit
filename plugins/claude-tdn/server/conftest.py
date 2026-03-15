"""Pytest configuration for claude-tdn MCP server tests."""


def pytest_addoption(parser):
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="Run integration tests (requires internet)",
    )


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--integration"):
        import pytest
        skip = pytest.mark.skip(reason="Use --integration to run")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip)
