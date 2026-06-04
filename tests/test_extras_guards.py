"""Tests for the optional-extras import guards.

These exercise the missing-dependency paths without uninstalling anything: the
real import is intercepted and made to raise ``ModuleNotFoundError``, then we
assert the friendly install hint is surfaced instead of a bare traceback.
"""

import builtins
import sys

import pytest

import duckdb_ext.extension as duckdb_ext
import mcp_server


def _import_blocker(blocked: str):
    """Return an ``__import__`` replacement that fails for one top-level name."""
    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == blocked or name.startswith(blocked + "."):
            raise ModuleNotFoundError(f"No module named '{blocked}'", name=name)
        return real_import(name, globals, locals, fromlist, level)

    return fake_import


class TestMcpGuard:
    def test_is_missing_mcp_matches_package(self):
        assert mcp_server._is_missing_mcp(ModuleNotFoundError(name="mcp"))
        assert mcp_server._is_missing_mcp(ModuleNotFoundError(name="mcp.server"))

    def test_is_missing_mcp_ignores_other_modules(self):
        assert not mcp_server._is_missing_mcp(ModuleNotFoundError(name="numpy"))
        assert not mcp_server._is_missing_mcp(ModuleNotFoundError(name=None))

    def test_main_exits_with_hint_when_mcp_missing(self, monkeypatch, capsys):
        # Force a fresh import of mcp_server.server while mcp is unimportable.
        for mod in list(sys.modules):
            if (
                mod == "mcp"
                or mod.startswith("mcp.")
                or mod.startswith("mcp_server.server")
            ):
                monkeypatch.delitem(sys.modules, mod, raising=False)
        monkeypatch.setattr(builtins, "__import__", _import_blocker("mcp"))

        with pytest.raises(SystemExit) as excinfo:
            mcp_server.main()

        assert excinfo.value.code == 1
        captured = capsys.readouterr()
        assert captured.err.strip() == mcp_server.MCP_MISSING_MESSAGE
        # Single line, no traceback dump.
        assert captured.err.count("\n") == 1


class TestDuckdbGuard:
    def test_require_duckdb_returns_module_when_present(self):
        assert duckdb_ext._require_duckdb() is sys.modules["duckdb"]

    def test_require_duckdb_raises_hint_when_missing(self, monkeypatch):
        monkeypatch.delitem(sys.modules, "duckdb", raising=False)
        monkeypatch.setattr(builtins, "__import__", _import_blocker("duckdb"))

        with pytest.raises(ModuleNotFoundError) as excinfo:
            duckdb_ext._require_duckdb()

        assert str(excinfo.value) == duckdb_ext.DUCKDB_MISSING_MESSAGE

    def test_load_raises_hint_when_missing(self, monkeypatch):
        monkeypatch.delitem(sys.modules, "duckdb", raising=False)
        monkeypatch.setattr(builtins, "__import__", _import_blocker("duckdb"))

        with pytest.raises(ModuleNotFoundError) as excinfo:
            duckdb_ext.load()

        assert str(excinfo.value) == duckdb_ext.DUCKDB_MISSING_MESSAGE
