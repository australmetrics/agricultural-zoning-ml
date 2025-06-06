# tests/test_pipeline.py
from typer.testing import CliRunner
from pascal_zoning.pipeline import app

runner = CliRunner()


def test_help_command() -> None:
    """Verifica que el subcomando 'run' muestra ayuda correctamente."""
    result = runner.invoke(app, ["run", "--help"])
    assert result.exit_code == 0
    assert "--raster" in result.output
    assert "--indices" in result.output
    # --block-path quedó obsoleto y ya no se comprueba
    assert "--output" in result.output
