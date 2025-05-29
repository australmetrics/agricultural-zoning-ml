# tests/test_main.py

from typer.testing import CliRunner
from src.main import app

runner = CliRunner()


def test_help_command() -> None:
    """Verifica que el CLI muestra ayuda correctamente."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "clip" in result.output
    assert "indices" in result.output
    assert "auto" in result.output
