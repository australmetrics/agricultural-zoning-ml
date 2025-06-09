# tests/test_pipeline.py
from typer.testing import CliRunner
from pascal_zoning.pipeline import app

runner = CliRunner()


def test_help_command() -> None:
    """Verifica que el subcomando 'run' muestra ayuda correctamente."""
    result = runner.invoke(
        app,
        ["run", "--help"],
        color=False,  # desactiva Click
        env={
            "NO_COLOR": "1",  # estándar, respeta Rich ≥ 13
            "RICH_NO_COLOR": "1",  # fallback explícito para Rich
        },
    )

    assert result.exit_code == 0
    assert "--raster" in result.output
    assert "--indices" in result.output
    # --block-path quedó obsoleto y ya no se comprueba
    assert "--output-dir" in result.output
