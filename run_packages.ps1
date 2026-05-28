$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

if (Get-Command python -ErrorAction SilentlyContinue) {
    python -m packages @args
    exit $LASTEXITCODE
}

if (Get-Command python3 -ErrorAction SilentlyContinue) {
    python3 -m packages @args
    exit $LASTEXITCODE
}

if (Get-Command py -ErrorAction SilentlyContinue) {
    py -3 -m packages @args
    exit $LASTEXITCODE
}

throw "Neither python, python3, nor py was found in PATH."
