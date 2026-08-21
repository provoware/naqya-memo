$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Port = 8765
$Server = $null

function Fail([string]$Message) {
    Write-Host "`n[NAQYA] FEHLER: $Message" -ForegroundColor Red
    exit 1
}

try {
    if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
        Fail 'Rust/Cargo fehlt. Siehe docs/NATIVE_DESKTOP.md.'
    }

    $Python = $null
    if (Get-Command py -ErrorAction SilentlyContinue) { $Python = 'py' }
    elseif (Get-Command python -ErrorAction SilentlyContinue) { $Python = 'python' }
    elseif (Get-Command python3 -ErrorAction SilentlyContinue) { $Python = 'python3' }
    if (-not $Python) { Fail 'Python 3 fehlt.' }

    if (-not (Test-Path (Join-Path $Root 'src-tauri\Cargo.toml'))) {
        Fail 'src-tauri\Cargo.toml fehlt.'
    }

    $Listener = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Loopback, $Port)
    try { $Listener.Start() }
    catch { Fail "Port $Port ist bereits belegt." }
    finally { try { $Listener.Stop() } catch {} }

    Write-Host '[NAQYA] Starte lokalen Offline-Frontendserver ...'
    $Args = if ($Python -eq 'py') {
        @('-3', '-m', 'http.server', $Port, '--bind', '127.0.0.1')
    } else {
        @('-m', 'http.server', $Port, '--bind', '127.0.0.1')
    }
    $Server = Start-Process -FilePath $Python -ArgumentList $Args -WorkingDirectory $Root -PassThru -WindowStyle Hidden
    Start-Sleep -Milliseconds 600
    if ($Server.HasExited) { Fail 'Frontendserver konnte nicht gestartet werden.' }

    Write-Host '[NAQYA] Starte Tauri + lokale whisper.cpp-Runtime ...'
    Push-Location $Root
    try {
        & cargo run --manifest-path (Join-Path $Root 'src-tauri\Cargo.toml')
        if ($LASTEXITCODE -ne 0) { Fail "Cargo wurde mit Code $LASTEXITCODE beendet." }
    }
    finally { Pop-Location }
}
finally {
    if ($Server -and -not $Server.HasExited) {
        Stop-Process -Id $Server.Id -Force -ErrorAction SilentlyContinue
    }
}
