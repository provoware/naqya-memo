$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$WorkDir = Join-Path $Root ".sidecar-build-windows"
$SourceDir = Join-Path $WorkDir "whisper.cpp"
$BuildDir = Join-Path $WorkDir "build"
$BinaryDir = Join-Path $Root "src-tauri\binaries"
$Repository = "https://github.com/ggml-org/whisper.cpp"
$UpstreamTag = "v1.9.2"
$UpstreamCommit = "306c88f4d1286aec1bf96e544632897886af5501"
$TargetTriple = "x86_64-pc-windows-msvc"
$Output = Join-Path $BinaryDir "naqya-whisper-$TargetTriple.exe"
$ShaFile = "$Output.sha256"

foreach ($command in @("git", "cmake", "rustc")) {
    if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
        throw "FEHLER: Benötigtes Werkzeug fehlt: $command"
    }
}

$HostLine = (& rustc -vV | Select-String '^host:').Line
if (-not $HostLine) {
    throw "FEHLER: Rust-Zielplattform konnte nicht ermittelt werden."
}
$HostTarget = $HostLine.Split(':', 2)[1].Trim()
if ($HostTarget -ne $TargetTriple) {
    throw "FEHLER: Windows-Sidecar darf nur auf $TargetTriple gebaut werden; erkannt: $HostTarget"
}

if (Test-Path $WorkDir) {
    Remove-Item -Recurse -Force $WorkDir
}
New-Item -ItemType Directory -Force -Path $WorkDir, $BinaryDir | Out-Null

& git clone --filter=blob:none --no-checkout $Repository $SourceDir
if ($LASTEXITCODE -ne 0) { throw "FEHLER: whisper.cpp konnte nicht geklont werden." }

& git -C $SourceDir fetch --depth 1 origin "refs/tags/$UpstreamTag:refs/tags/$UpstreamTag"
if ($LASTEXITCODE -ne 0) { throw "FEHLER: Gepinnter whisper.cpp-Tag konnte nicht geladen werden." }

& git -C $SourceDir checkout --detach $UpstreamCommit
if ($LASTEXITCODE -ne 0) { throw "FEHLER: Gepinnter whisper.cpp-Commit konnte nicht ausgecheckt werden." }

$ActualCommit = (& git -C $SourceDir rev-parse HEAD).Trim().ToLowerInvariant()
if ($ActualCommit -ne $UpstreamCommit) {
    throw "FEHLER: Upstream-Commit stimmt nicht: $ActualCommit != $UpstreamCommit"
}

& cmake -S $SourceDir -B $BuildDir -A x64 `
    -DCMAKE_BUILD_TYPE=Release `
    -DGGML_NATIVE=OFF `
    -DBUILD_SHARED_LIBS=OFF `
    -DWHISPER_BUILD_EXAMPLES=ON
if ($LASTEXITCODE -ne 0) { throw "FEHLER: CMake-Konfiguration fehlgeschlagen." }

& cmake --build $BuildDir --config Release --target whisper-cli --parallel
if ($LASTEXITCODE -ne 0) { throw "FEHLER: whisper-cli-Build fehlgeschlagen." }

$Candidates = @(
    (Join-Path $BuildDir "bin\Release\whisper-cli.exe"),
    (Join-Path $BuildDir "bin\whisper-cli.exe"),
    (Join-Path $BuildDir "examples\cli\Release\whisper-cli.exe")
)
$BuiltBinary = $Candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $BuiltBinary) {
    throw "FEHLER: whisper-cli.exe wurde nach erfolgreichem Build nicht gefunden."
}

Copy-Item -Force $BuiltBinary $Output
$Hash = (Get-FileHash -Algorithm SHA256 $Output).Hash.ToLowerInvariant()
"$Hash  $(Split-Path -Leaf $Output)" | Set-Content -Encoding ascii $ShaFile

& $Output --help *> $null
if ($LASTEXITCODE -ne 0) {
    throw "FEHLER: Gebauter Windows-Sidecar startet nicht erfolgreich."
}

Write-Host "NAQYA whisper.cpp Windows-Sidecar vorbereitet"
Write-Host "Upstream: $UpstreamTag @ $UpstreamCommit"
Write-Host "Ziel: $TargetTriple"
Write-Host "Binary: $Output"
Write-Host "SHA-256: $Hash"
