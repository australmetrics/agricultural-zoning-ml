"""
Logging estructurado ISO-42001 para Agri-Zoning.
"""

from loguru import logger
import sys                    # ← Importar sys directamente
from pathlib import Path
from datetime import datetime

def setup_logging(output_dir: Path) -> None:
    log_dir = Path(output_dir) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    fmt_console = (
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan> | {message}"
    )
    fmt_file = (
        "[{time:YYYY-MM-DD HH:mm:ss.SSS}] "
        "{process}.{thread} | {level: <8} | "
        "{name}:{function}:{line} | {message}"
    )

    current = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = log_dir / f"agri_zoning_{current}.log"

    logger.remove()  # Borra handlers por defecto
    logger.add(file_path, format=fmt_file, level="INFO", enqueue=True)
    logger.add(sys.stderr, format=fmt_console, level="INFO")  # ← Usar sys.stderr

    logger.info("Logging inicializado")


