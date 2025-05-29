"""Logging system configuration for PASCAL NDVI Block project.

Provides functions for configuring the logging system, including log file handling,
rotation, and custom formats compliant with ISO 42001 requirements.
"""

from loguru import logger
import sys
import os
import hashlib
import shutil
from pathlib import Path
from datetime import datetime


def calculate_hash(file_path: Path) -> str:
    """Calculates the SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def backup_log(log_file: Path, backup_dir: Path) -> None:
    """Creates a backup copy of the log file with integrity verification."""
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_file = backup_dir / f"{log_file.stem}_backup{log_file.suffix}"
    shutil.copy2(log_file, backup_file)

    # Crear archivo de verificación con hash
    hash_value = calculate_hash(log_file)
    hash_file = backup_file.with_suffix(".sha256")
    hash_file.write_text(hash_value)


def setup_logging(output_dir: Path) -> None:
    """Configure logging system according to ISO 42001 standards.

    Implements auditable and permanent logging following standardized guidelines.
    Ensures log file integrity and maintains backup copies with verification.

    Args:
        output_dir: Directory path where log files will be stored
    """
    # Crear directorios
    log_dir = output_dir / "logs"
    backup_dir = output_dir / "logs" / "backup"
    log_dir.mkdir(parents=True, exist_ok=True)
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Formato para auditoría ISO 42001
    log_format = (
        "[{time:YYYY-MM-DD HH:mm:ss.SSS}] "
        "{process}.{thread} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "usuario={extra[user]} | "
        "hash={extra[hash]} | "
        "{message}"
    )

    # Archivo de log con fecha y hora exacta
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"pascal_ndvi_{current_datetime}.log"

    # Configurar contexto para auditoría
    logger.configure(
        extra={"user": os.getenv("USERNAME", "unknown"), "hash": "calculating..."}
    )

    # Log a archivo (sin rotación - permanente)
    logger.add(
        log_file,
        format=log_format,
        level="INFO",
        rotation=None,  # Sin rotación - logs permanentes
        enqueue=True,  # Thread-safe
        backtrace=True,  # Más info para debug
        diagnose=True,  # Más info para diagnóstico
    )

    # Log a consola (formato simplificado)
    logger.add(
        sys.stderr,
        format=(
            "<green>{time:HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan> | {message}"
        ),
        level="INFO",
    )

    # Registrar inicio con metadata
    logger.info("🚀 Iniciando P.A.S.C.A.L NDVI Block")
    logger.info(f"📁 Directorio de salida: {output_dir}")
    logger.info(f"📝 Archivo de log: {log_file}")

    # Crear backup inmediatamente
    backup_log(log_file, backup_dir)

    # Registrar también backup al finalizar por si hay cambios
    import atexit

    atexit.register(backup_log, log_file, backup_dir)
