# Colores para los mensajes
$colors = @{
    Success = "Green"
    Error = "Red"
    Info = "Cyan"
}

function Write-Step {
    param (
        [string]$Message
    )
    Write-Host "`n=== $Message ===" -ForegroundColor $colors.Info
}

$ErrorActionPreference = "Continue"
$success = $true

# Quality Check
Write-Step "Verificando formato de código"
try {
    flake8 src/ tests/ --count --max-line-length=100 --statistics
    black --check src/ tests/
} catch {
    $success = $false
    Write-Host "❌ Error en verificación de formato" -ForegroundColor $colors.Error
}

Write-Step "Verificando tipos"
try {
    mypy src/ tests/
} catch {
    $success = $false
    Write-Host "❌ Error en verificación de tipos" -ForegroundColor $colors.Error
}

Write-Step "Ejecutando tests con cobertura"
try {
    pytest tests/ --cov=pascal_ndvi_block --cov-report=xml --cov-report=term-missing:skip-covered
} catch {
    $success = $false
    Write-Host "❌ Error en tests" -ForegroundColor $colors.Error
}

Write-Step "Verificando documentación"
try {
    pydocstyle src/
} catch {
    $success = $false
    Write-Host "❌ Error en documentación" -ForegroundColor $colors.Error
}

Write-Step "Verificando seguridad"
try {
    bandit -r src/ -ll
} catch {
    $success = $false
    Write-Host "❌ Error en verificación de seguridad" -ForegroundColor $colors.Error
}

Write-Step "Verificando dependencias"
try {
    safety check
} catch {
    $success = $false
    Write-Host "❌ Error en verificación de dependencias" -ForegroundColor $colors.Error
}

# Compliance Check
Write-Step "Verificando cumplimiento ISO 42001"
$requiredFiles = @(
    "src/logging_config.py",
    "docs/compliance/iso42001_compliance.md",
    "README.md",
    "CHANGELOG.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md"
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        $success = $false
        Write-Host "❌ Falta archivo requerido: $file" -ForegroundColor $colors.Error
    }
}

# Resultado Final
Write-Host "`n=== Resultado Final ===" -ForegroundColor $colors.Info
if ($success) {
    Write-Host "✅ Verificación exitosa - ISO 42001 Compliance Check" -ForegroundColor $colors.Success
    exit 0
} else {
    Write-Host "❌ Verificación fallida - ISO 42001 Compliance Check" -ForegroundColor $colors.Error
    exit 1
}
