use base64::{engine::general_purpose::STANDARD, Engine};
use serde::{Deserialize, Serialize};
use std::{
    fs,
    path::PathBuf,
    process::Command,
    time::{SystemTime, UNIX_EPOCH},
};

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct Capabilities {
    available: bool,
    platform: String,
    whisper: bool,
    whisper_cli: Option<String>,
    logical_cpus: usize,
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

fn whisper_cli_path() -> Option<PathBuf> {
    if let Ok(path) = std::env::var("NAQYA_WHISPER_CLI") {
        let p = PathBuf::from(path);
        if p.is_file() {
            return Some(p);
        }
    }
    for candidate in ["whisper-cli", "main"] {
        if let Ok(output) = Command::new(candidate).arg("--help").output() {
            if output.status.success() {
                return Some(PathBuf::from(candidate));
            }
        }
    }
    None
}

#[tauri::command]
fn naqya_capabilities() -> Capabilities {
    let cli = whisper_cli_path();
    Capabilities {
        available: true,
        platform: std::env::consts::OS.to_string(),
        whisper: cli.is_some(),
        whisper_cli: cli.map(|p| p.to_string_lossy().to_string()),
        logical_cpus: num_cpus::get(),
    }
}

#[tauri::command]
fn naqya_transcribe(request: TranscribeRequest) -> Result<TranscribeResult, String> {
    let started = std::time::Instant::now();
    let cli = whisper_cli_path().ok_or(
        "whisper.cpp CLI wurde nicht gefunden. NAQYA_WHISPER_CLI setzen oder whisper-cli installieren.",
    )?;
    let model = PathBuf::from(&request.model_path);
    if !model.is_file() {
        return Err("Sprachmodell wurde nicht gefunden.".into());
    }
    let bytes = STANDARD
        .decode(request.audio_base64.as_bytes())
        .map_err(|_| "Audiodaten sind kein gültiges Base64.")?;
    if bytes.len() > 512 * 1024 * 1024 {
        return Err("Audiodatei ist für eine Einzeltranskription zu groß.".into());
    }
    let stamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|e| e.to_string())?
        .as_millis();
    let mut wav = std::env::temp_dir();
    wav.push(format!("naqya-stt-{stamp}.wav"));
    fs::write(&wav, bytes)
        .map_err(|e| format!("Temporäre Audiodatei konnte nicht geschrieben werden: {e}"))?;
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
        .arg("-otxt")
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
            naqya_transcribe
        ])
        .run(tauri::generate_context!())
        .expect("NAQYA Desktop konnte nicht gestartet werden");
}
