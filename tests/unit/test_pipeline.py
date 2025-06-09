from typer.testing import CliRunner
from pascal_zoning.pipeline import app
import click  # <- importa Click para usar unstyle

runner = CliRunner()


def test_help_command() -> None:
    """Verifica que el subcomando 'run' muestra ayuda correctamente."""
    result = runner.invoke(
        app,
        ["run", "--help"],
        color=False,
    )
    assert result.exit_code == 0

    plain = click.unstyle(result.output)  # ← quita TODOS los escapes ANSI
    assert "--raster" in plain
    assert "--indices" in plain
    assert "--output-dir" in plain
