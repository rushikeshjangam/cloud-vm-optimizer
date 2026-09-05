param(
    [int]$Port = 8501
)

$ErrorActionPreference = "Stop"
$RepositoryRoot = Split-Path -Parent $PSScriptRoot
$PythonPath = Join-Path $RepositoryRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $PythonPath)) {
    throw "Python environment not found. Follow README.md once to create .venv and install the project."
}

& $PythonPath -m streamlit run (Join-Path $RepositoryRoot "streamlit_app.py") `
    --server.address 0.0.0.0 --server.port $Port

