use base64::{engine::general_purpose::STANDARD, Engine};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::{
    fs::{self, OpenOptions},
    io::{Read, Write},
    path::{Path, PathBuf},
    process::Command,
    sync::atomic::{AtomicU64, Ordering},
    time::{SystemTime, UNIX_EPOCH},
};
use tauri::Manager;

const MAX_AUDIO_BYTES: usize = 512 * 1024 * 1024;
static STT_TEMP_SEQUENCE: AtomicU64 = AtomicU64::new(0);

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct Capabilities {
    available: bool,
    platform: String,
    whisper: bool,
    whisper_cli: Option<String>,
    logical_cpus: usize,
    model_store: Option<String>,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct TranscribeRequest {
    audio_base64: String,
    model_path: String,
    language: Option<String>,
    threads: Option<usize>,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct TranscribeResult {
    text: String,
    provider: String,
    elapsed_ms: u128,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct ModelBeginRequest {
    name: String,
    sha256: Option<String>,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct ModelBeginResult {
    token: String,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct ModelAppendRequest {
    token: String,
    chunk_base64: String,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct ModelFinishRequest {
    token: String,
    name: String,
    sha256: Option<String>,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct ModelAbortRequest {
    token: String,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct ModelMaterializeResult {
    path: String,
    sha256: String,
    bytes: u64,
}

fn whisper_cli_path() -> Option<PathBuf> {
    if let Ok(path) = std::env::var("NAQYA_WHISPER_CLI") {
        let p = PathBuf::from(path);
        if p.is_file() {
            return fs::canonicalize(&p).ok().or(Some(p));
        }
    }
    if let Ok(output) = Command::new("whisper-cli").arg("--help").output() {
        if output.status.success() {
            return Some(PathBuf::from("whisper-cli"));
        }
    }
    None
}

fn model_root(app: &tauri::AppHandle) -> Result<PathBuf, String> {
    let root = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("Lokaler NAQYA-Datenpfad ist nicht verfügbar: {e}"))?
        .join("models");
    fs::create_dir_all(root.join(".incoming"))
        .map_err(|e| format!("Modellverzeichnis konnte nicht angelegt werden: {e}"))?;
    Ok(root)
}

fn stt_temp_root(app: &tauri::AppHandle) -> Result<PathBuf, String> {
    let root = app
        .path()
        .app_cache_dir()
        .map_err(|e| format!("Lokaler NAQYA-Cachepfad ist nicht verfügbar: {e}"))?
        .join("stt-temp");
    fs::create_dir_all(&root)
        .map_err(|e| format!("Temporärer STT-Pfad konnte nicht angelegt werden: {e}"))?;
    Ok(root)
}

fn write_private_temp_wav(app: &tauri::AppHandle, bytes: &[u8]) -> Result<PathBuf, String> {
    let root = stt_temp_root(app)?;
    let stamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|e| e.to_string())?
        .as_millis();
    for _ in 0..32 {
        let seq = STT_TEMP_SEQUENCE.fetch_add(1, Ordering::Relaxed);
        let path = root.join(format!("naqya-stt-{stamp}-{}-{seq}.wav", std::process::id()));
        match OpenOptions::new().write(true).create_new(true).open(&path) {
            Ok(mut file) => {
                file.write_all(bytes)
                    .map_err(|e| format!("Temporäre Audiodatei konnte nicht geschrieben werden: {e}"))?;
                file.sync_all()
                    .map_err(|e| format!("Temporäre Audiodatei konnte nicht finalisiert werden: {e}"))?;
                return Ok(path);
            }
            Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => continue,
            Err(error) => {
                return Err(format!(
                    "Temporäre Audiodatei konnte nicht exklusiv angelegt werden: {error}"
                ));
            }
        }
    }
    Err("Temporäre Audiodatei konnte nach mehreren Versuchen nicht sicher angelegt werden.".into())
}

fn safe_model_name(name: &str) -> Result<String, String> {
    let lower = name.to_lowercase();
    if !(lower.ends_with(".bin") || lower.ends_with(".gguf")) {
        return Err("Nur .bin- oder .gguf-Sprachmodelle sind erlaubt.".into());
    }
    let base = Path::new(name)
        .file_name()
        .and_then(|v| v.to_str())
        .ok_or("Ungültiger Modellname.")?;
    let safe: String = base
        .chars()
        .map(|c| {
            if c.is_ascii_alphanumeric() || matches!(c, '.' | '-' | '_') {
                c
            } else {
                '_'
            }
        })
        .collect();
    if safe.len() < 5 {
        return Err("Ungültiger Modellname.".into());
    }
    Ok(safe)
}

fn validate_token(token: &str) -> Result<(), String> {
    if token.len() < 8
        || token.len() > 96
        || !token.chars().all(|c| c.is_ascii_alphanumeric() || c == '-')
    {
        return Err("Ungültige Modell-Transferkennung.".into());
    }
    Ok(())
}

fn hash_file(path: &Path) -> Result<(String, u64), String> {
    let mut file =
        fs::File::open(path).map_err(|e| format!("Modell konnte nicht gelesen werden: {e}"))?;
    let mut hasher = Sha256::new();
    let mut buffer = vec![0_u8; 1024 * 1024];
    let mut bytes = 0_u64;
    loop {
        let read = file
            .read(&mut buffer)
            .map_err(|e| format!("Modellprüfung fehlgeschlagen: {e}"))?;
        if read == 0 {
            break;
        }
        hasher.update(&buffer[..read]);
        bytes += read as u64;
    }
    Ok((format!("{:x}", hasher.finalize()), bytes))
}

fn trusted_model_path(app: &tauri::AppHandle, requested: &str) -> Result<PathBuf, String> {
    let root = fs::canonicalize(model_root(app)?)
        .map_err(|e| format!("NAQYA-Modellpfad konnte nicht geprüft werden: {e}"))?;
    let model = fs::canonicalize(requested)
        .map_err(|e| format!("Sprachmodell wurde nicht gefunden: {e}"))?;
    if !model.starts_with(&root) || !model.is_file() {
        return Err("Das Sprachmodell liegt nicht im geschützten NAQYA-Modellpfad.".into());
    }
    Ok(model)
}

#[tauri::command]
fn naqya_capabilities(app: tauri::AppHandle) -> Capabilities {
    let cli = whisper_cli_path();
    let root = model_root(&app).ok();
    Capabilities {
        available: true,
        platform: std::env::consts::OS.to_string(),
        whisper: cli.is_some(),
        whisper_cli: cli.map(|p| p.to_string_lossy().to_string()),
        logical_cpus: num_cpus::get(),
        model_store: root.map(|p| p.to_string_lossy().to_string()),
    }
}

#[tauri::command]
fn naqya_model_begin(
    app: tauri::AppHandle,
    request: ModelBeginRequest,
) -> Result<ModelBeginResult, String> {
    safe_model_name(&request.name)?;
    if let Some(hash) = &request.sha256 {
        if hash.len() != 64 || !hash.chars().all(|c| c.is_ascii_hexdigit()) {
            return Err("Ungültige SHA-256-Prüfsumme.".into());
        }
    }
    let root = model_root(&app)?;
    let stamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|e| e.to_string())?
        .as_millis();
    let token = format!("{stamp}-{}", std::process::id());
    let part = root.join(".incoming").join(format!("{token}.part"));
    fs::File::create(part)
        .map_err(|e| format!("Modelltransfer konnte nicht gestartet werden: {e}"))?;
    Ok(ModelBeginResult { token })
}

#[tauri::command]
fn naqya_model_append(app: tauri::AppHandle, request: ModelAppendRequest) -> Result<(), String> {
    validate_token(&request.token)?;
    let root = model_root(&app)?;
    let part = root
        .join(".incoming")
        .join(format!("{}.part", request.token));
    if !part.is_file() {
        return Err("Modelltransfer wurde nicht gefunden oder bereits beendet.".into());
    }
    let chunk = STANDARD
        .decode(request.chunk_base64.as_bytes())
        .map_err(|_| "Modellsegment ist kein gültiges Base64.".to_string())?;
    if chunk.len() > 8 * 1024 * 1024 {
        return Err("Modellsegment ist zu groß.".into());
    }
    OpenOptions::new()
        .append(true)
        .open(part)
        .and_then(|mut f| f.write_all(&chunk))
        .map_err(|e| format!("Modellsegment konnte nicht gespeichert werden: {e}"))
}

#[tauri::command]
fn naqya_model_finish(
    app: tauri::AppHandle,
    request: ModelFinishRequest,
) -> Result<ModelMaterializeResult, String> {
    validate_token(&request.token)?;
    let safe_name = safe_model_name(&request.name)?;
    let root = model_root(&app)?;
    let part = root
        .join(".incoming")
        .join(format!("{}.part", request.token));
    if !part.is_file() {
        return Err("Unvollständiger Modelltransfer wurde nicht gefunden.".into());
    }
    let (actual, bytes) = hash_file(&part)?;
    if bytes < 10 * 1024 * 1024 {
        let _ = fs::remove_file(&part);
        return Err("Die Modelldatei ist ungewöhnlich klein und wurde verworfen.".into());
    }
    if let Some(expected) = request.sha256.as_ref() {
        if !actual.eq_ignore_ascii_case(expected) {
            let _ = fs::remove_file(&part);
            return Err("SHA-256-Prüfung des Sprachmodells ist fehlgeschlagen.".into());
        }
    }
    let final_path = root.join(format!("{}-{safe_name}", &actual[..16]));
    if final_path.is_file() {
        let (existing_hash, existing_bytes) = hash_file(&final_path)?;
        if existing_hash == actual {
            let _ = fs::remove_file(&part);
            return Ok(ModelMaterializeResult {
                path: final_path.to_string_lossy().to_string(),
                sha256: actual,
                bytes: existing_bytes,
            });
        }
        fs::remove_file(&final_path)
            .map_err(|e| format!("Altes Modell konnte nicht ersetzt werden: {e}"))?;
    }
    fs::rename(&part, &final_path)
        .map_err(|e| format!("Sprachmodell konnte nicht atomar aktiviert werden: {e}"))?;
    Ok(ModelMaterializeResult {
        path: final_path.to_string_lossy().to_string(),
        sha256: actual,
        bytes,
    })
}

#[tauri::command]
fn naqya_model_abort(app: tauri::AppHandle, request: ModelAbortRequest) -> Result<(), String> {
    validate_token(&request.token)?;
    let path = model_root(&app)?
        .join(".incoming")
        .join(format!("{}.part", request.token));
    if path.exists() {
        fs::remove_file(path)
            .map_err(|e| format!("Modelltransfer konnte nicht bereinigt werden: {e}"))?;
    }
    Ok(())
}

#[tauri::command]
fn naqya_transcribe(
    app: tauri::AppHandle,
    request: TranscribeRequest,
) -> Result<TranscribeResult, String> {
    let started = std::time::Instant::now();
    let cli = whisper_cli_path().ok_or(
        "whisper.cpp CLI wurde nicht gefunden. NAQYA_WHISPER_CLI setzen oder whisper-cli installieren.",
    )?;
    let model = trusted_model_path(&app, &request.model_path)?;
    let bytes = STANDARD
        .decode(request.audio_base64.as_bytes())
        .map_err(|_| "Audiodaten sind kein gültiges Base64.")?;
    if bytes.len() > MAX_AUDIO_BYTES {
        return Err("Audiodatei ist für eine Einzeltranskription zu groß.".into());
    }
    if bytes.len() < 44 || &bytes[0..4] != b"RIFF" || &bytes[8..12] != b"WAVE" {
        return Err("Native Transkription erwartet normalisierte WAV-Audiodaten.".into());
    }
    let wav = write_private_temp_wav(&app, &bytes)?;
    let threads = request
        .threads
        .unwrap_or_else(|| num_cpus::get().clamp(1, 8));
    let language = request.language.unwrap_or_else(|| "de".into());
    let output = Command::new(&cli)
        .arg("-m")
        .arg(&model)
        .arg("-f")
        .arg(&wav)
        .arg("-l")
        .arg(language)
        .arg("-t")
        .arg(threads.to_string())
        .arg("--no-timestamps")
        .output();
    let _ = fs::remove_file(&wav);
    let output = output.map_err(|e| format!("whisper.cpp konnte nicht gestartet werden: {e}"))?;
    if !output.status.success() {
        return Err(format!(
            "whisper.cpp Fehler: {}",
            String::from_utf8_lossy(&output.stderr).trim()
        ));
    }
    let text = String::from_utf8_lossy(&output.stdout).trim().to_string();
    Ok(TranscribeResult {
        text,
        provider: "whisper.cpp-native".into(),
        elapsed_ms: started.elapsed().as_millis(),
    })
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            naqya_capabilities,
            naqya_model_begin,
            naqya_model_append,
            naqya_model_finish,
            naqya_model_abort,
            naqya_transcribe
        ])
        .run(tauri::generate_context!())
        .expect("NAQYA Desktop konnte nicht gestartet werden");
}
