use base64::{engine::general_purpose::STANDARD as BASE64, Engine as _};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::{
    collections::HashMap,
    fs::{self, File, OpenOptions},
    io::{Read, Write},
    path::{Path, PathBuf},
    sync::{Arc, Mutex},
    time::{SystemTime, UNIX_EPOCH},
};
use tauri::{AppHandle, Manager, State};
use whisper_rs::{FullParams, SamplingStrategy, WhisperContext, WhisperContextParameters};

const MIN_MODEL_BYTES: u64 = 10 * 1024 * 1024;
const MAX_MODEL_BYTES: u64 = 4 * 1024 * 1024 * 1024;
const MAX_TRANSCRIBE_SECONDS: usize = 180;
const REQUIRED_SAMPLE_RATE: u32 = 16_000;

#[derive(Clone, Default)]
struct RuntimeState {
    contexts: Arc<Mutex<HashMap<PathBuf, Arc<WhisperContext>>>>,
}

#[derive(Debug, Serialize, Clone)]
#[serde(rename_all = "camelCase")]
struct NativeModel {
    name: String,
    path: String,
    bytes: u64,
    source: String,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
struct NativeStatus {
    available: bool,
    runtime: String,
    whisper_cpp_version: String,
    model_dir: String,
    models: Vec<NativeModel>,
    recommended_threads: usize,
    sample_rate: u32,
    max_segment_seconds: usize,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
struct TranscribeRequest {
    samples: Vec<f32>,
    sample_rate: u32,
    model_file: Option<String>,
    profile: Option<String>,
    language: Option<String>,
    threads: Option<usize>,
    no_context: Option<bool>,
    single_segment: Option<bool>,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
struct TranscriptSegment {
    start_ms: i64,
    end_ms: i64,
    text: String,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
struct TranscribeResponse {
    text: String,
    segments: Vec<TranscriptSegment>,
    model_file: String,
    language: String,
    samples: usize,
    duration_ms: u64,
    processing_ms: u128,
    realtime_factor: f64,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct ImportMeta {
    id: String,
    name: String,
    total_size: u64,
    expected_sha256: Option<String>,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
struct ImportBeginResponse {
    id: String,
    name: String,
    total_size: u64,
}

fn model_dir(app: &AppHandle) -> Result<PathBuf, String> {
    let dir = app
        .path()
        .app_local_data_dir()
        .map_err(|e| format!("App-Datenverzeichnis nicht verfügbar: {e}"))?
        .join("models");
    fs::create_dir_all(&dir).map_err(|e| format!("Modellverzeichnis konnte nicht erstellt werden: {e}"))?;
    Ok(dir)
}

fn import_dir(app: &AppHandle) -> Result<PathBuf, String> {
    let dir = model_dir(app)?.join(".imports");
    fs::create_dir_all(&dir).map_err(|e| format!("Importverzeichnis konnte nicht erstellt werden: {e}"))?;
    Ok(dir)
}

fn safe_file_name(name: &str) -> Result<String, String> {
    let file_name = Path::new(name)
        .file_name()
        .and_then(|x| x.to_str())
        .ok_or_else(|| "Ungültiger Dateiname.".to_string())?;
    if file_name != name || file_name.is_empty() {
        return Err("Der Modellname darf keinen Pfad enthalten.".into());
    }
    let lower = file_name.to_ascii_lowercase();
    if !(lower.ends_with(".bin") || lower.ends_with(".gguf")) {
        return Err("Erwartet wird eine .bin- oder .gguf-Modelldatei.".into());
    }
    Ok(file_name.to_string())
}

fn available_threads() -> usize {
    std::thread::available_parallelism().map(|n| n.get()).unwrap_or(1)
}

fn collect_models(app: &AppHandle) -> Vec<NativeModel> {
    let mut out = Vec::new();
    let mut seen = std::collections::HashSet::new();

    if let Ok(local) = model_dir(app) {
        collect_models_from(&local, "App-Daten", &mut seen, &mut out);
    }
    if let Ok(resource) = app.path().resource_dir() {
        for dir in [resource.join("runtime").join("models"), resource.join("models")] {
            collect_models_from(&dir, "Gebündelt", &mut seen, &mut out);
        }
    }
    out.sort_by(|a, b| a.name.cmp(&b.name));
    out
}

fn collect_models_from(
    dir: &Path,
    source: &str,
    seen: &mut std::collections::HashSet<String>,
    out: &mut Vec<NativeModel>,
) {
    let Ok(read_dir) = fs::read_dir(dir) else { return };
    for entry in read_dir.flatten() {
        let path = entry.path();
        if !path.is_file() {
            continue;
        }
        let Some(name) = path.file_name().and_then(|x| x.to_str()).map(str::to_string) else { continue };
        let lower = name.to_ascii_lowercase();
        if !(lower.ends_with(".bin") || lower.ends_with(".gguf")) || !seen.insert(name.clone()) {
            continue;
        }
        let bytes = entry.metadata().map(|m| m.len()).unwrap_or(0);
        out.push(NativeModel {
            name,
            path: path.to_string_lossy().into_owned(),
            bytes,
            source: source.to_string(),
        });
    }
}

fn profile_fragment(profile: &str) -> &str {
    match profile {
        "schnell" => "tiny",
        "genau" => "small",
        "maximum" => "medium",
        _ => "base",
    }
}

fn resolve_model(app: &AppHandle, request: &TranscribeRequest) -> Result<PathBuf, String> {
    let models = collect_models(app);
    if models.is_empty() {
        return Err(format!(
            "Kein lokales Whisper-Modell gefunden. Lege ein Modell in {} ab oder importiere es in NAQYA.",
            model_dir(app)?.display()
        ));
    }

    if let Some(file) = request.model_file.as_deref() {
        let safe = safe_file_name(file)?;
        if let Some(model) = models.iter().find(|m| m.name == safe) {
            return Ok(PathBuf::from(&model.path));
        }
        return Err(format!("Das Modell '{safe}' wurde nicht gefunden."));
    }

    let fragment = profile_fragment(request.profile.as_deref().unwrap_or("ausgewogen"));
    if let Some(model) = models.iter().find(|m| m.name.to_ascii_lowercase().contains(fragment)) {
        return Ok(PathBuf::from(&model.path));
    }
    Ok(PathBuf::from(&models[0].path))
}

fn context_for(runtime: &RuntimeState, model_path: &Path) -> Result<Arc<WhisperContext>, String> {
    if let Some(existing) = runtime
        .contexts
        .lock()
        .map_err(|_| "Whisper-Kontextspeicher ist gesperrt.".to_string())?
        .get(model_path)
        .cloned()
    {
        return Ok(existing);
    }

    let ctx = WhisperContext::new_with_params(model_path, WhisperContextParameters::default())
        .map_err(|e| format!("Whisper-Modell konnte nicht geladen werden: {e}"))?;
    let ctx = Arc::new(ctx);
    runtime
        .contexts
        .lock()
        .map_err(|_| "Whisper-Kontextspeicher ist gesperrt.".to_string())?
        .insert(model_path.to_path_buf(), ctx.clone());
    Ok(ctx)
}

fn transcribe_inner(
    runtime: RuntimeState,
    model_path: PathBuf,
    request: TranscribeRequest,
) -> Result<TranscribeResponse, String> {
    if request.sample_rate != REQUIRED_SAMPLE_RATE {
        return Err(format!(
            "Whisper erwartet {REQUIRED_SAMPLE_RATE} Hz Mono-PCM, erhalten: {} Hz.",
            request.sample_rate
        ));
    }
    if request.samples.is_empty() {
        return Err("Leeres Audiosignal.".into());
    }
    if request.samples.len() > REQUIRED_SAMPLE_RATE as usize * MAX_TRANSCRIBE_SECONDS {
        return Err(format!("Ein einzelner Transkriptionsblock darf höchstens {MAX_TRANSCRIBE_SECONDS} Sekunden lang sein."));
    }
    if request.samples.iter().any(|x| !x.is_finite()) {
        return Err("Das Audiosignal enthält ungültige Samplewerte.".into());
    }

    let started = std::time::Instant::now();
    let ctx = context_for(&runtime, &model_path)?;
    let mut state = ctx
        .create_state()
        .map_err(|e| format!("Whisper-Zustand konnte nicht erzeugt werden: {e}"))?;

    let max_threads = available_threads().max(1);
    let threads = request.threads.unwrap_or_else(|| max_threads.min(6)).clamp(1, max_threads);
    let language = request.language.clone().unwrap_or_else(|| "de".into());
    let mut params = FullParams::new(SamplingStrategy::Greedy { best_of: 1 });
    params.set_n_threads(threads as i32);
    params.set_translate(false);
    params.set_language(Some(&language));
    params.set_print_special(false);
    params.set_print_progress(false);
    params.set_print_realtime(false);
    params.set_print_timestamps(false);
    params.set_no_context(request.no_context.unwrap_or(true));
    params.set_single_segment(request.single_segment.unwrap_or(false));

    state
        .full(params, &request.samples)
        .map_err(|e| format!("Lokale Transkription fehlgeschlagen: {e}"))?;

    let mut segments = Vec::new();
    let mut text_parts = Vec::new();
    for segment in state.as_iter() {
        let text = segment
            .to_str_lossy()
            .map_err(|e| format!("Transkriptsegment konnte nicht gelesen werden: {e}"))?
            .trim()
            .to_string();
        if text.is_empty() {
            continue;
        }
        text_parts.push(text.clone());
        segments.push(TranscriptSegment {
            start_ms: segment.start_timestamp() * 10,
            end_ms: segment.end_timestamp() * 10,
            text,
        });
    }

    let duration_ms = ((request.samples.len() as f64 / REQUIRED_SAMPLE_RATE as f64) * 1000.0).round() as u64;
    let processing_ms = started.elapsed().as_millis();
    let realtime_factor = if duration_ms > 0 {
        processing_ms as f64 / duration_ms as f64
    } else {
        0.0
    };

    Ok(TranscribeResponse {
        text: text_parts.join(" ").trim().to_string(),
        segments,
        model_file: model_path
            .file_name()
            .and_then(|x| x.to_str())
            .unwrap_or("unbekannt")
            .to_string(),
        language,
        samples: request.samples.len(),
        duration_ms,
        processing_ms,
        realtime_factor,
    })
}

fn hash_file(path: &Path) -> Result<String, String> {
    let mut file = File::open(path).map_err(|e| format!("Datei konnte nicht geprüft werden: {e}"))?;
    let mut hasher = Sha256::new();
    let mut buffer = vec![0_u8; 1024 * 1024];
    loop {
        let n = file.read(&mut buffer).map_err(|e| format!("Datei konnte nicht gelesen werden: {e}"))?;
        if n == 0 {
            break;
        }
        hasher.update(&buffer[..n]);
    }
    Ok(format!("{:x}", hasher.finalize()))
}

fn import_paths(app: &AppHandle, id: &str) -> Result<(PathBuf, PathBuf), String> {
    if id.is_empty() || !id.chars().all(|c| c.is_ascii_alphanumeric() || c == '-') {
        return Err("Ungültige Import-ID.".into());
    }
    let dir = import_dir(app)?;
    Ok((dir.join(format!("{id}.part")), dir.join(format!("{id}.json"))))
}

#[tauri::command]
fn naqya_native_status(app: AppHandle) -> Result<NativeStatus, String> {
    Ok(NativeStatus {
        available: true,
        runtime: "whisper-rs 0.16 / whisper.cpp".into(),
        whisper_cpp_version: whisper_rs::get_whisper_version().to_string(),
        model_dir: model_dir(&app)?.to_string_lossy().into_owned(),
        models: collect_models(&app),
        recommended_threads: available_threads().min(6).max(1),
        sample_rate: REQUIRED_SAMPLE_RATE,
        max_segment_seconds: MAX_TRANSCRIBE_SECONDS,
    })
}

#[tauri::command]
async fn naqya_transcribe_pcm(
    app: AppHandle,
    runtime: State<'_, RuntimeState>,
    request: TranscribeRequest,
) -> Result<TranscribeResponse, String> {
    let model_path = resolve_model(&app, &request)?;
    let runtime = runtime.inner().clone();
    tauri::async_runtime::spawn_blocking(move || transcribe_inner(runtime, model_path, request))
        .await
        .map_err(|e| format!("Whisper-Arbeitsthread wurde beendet: {e}"))?
}

#[tauri::command]
fn naqya_model_import_begin(
    app: AppHandle,
    name: String,
    total_size: u64,
    expected_sha256: Option<String>,
) -> Result<ImportBeginResponse, String> {
    let name = safe_file_name(&name)?;
    if !(MIN_MODEL_BYTES..=MAX_MODEL_BYTES).contains(&total_size) {
        return Err(format!("Unplausible Modellgröße: {total_size} Bytes."));
    }
    let stamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|e| e.to_string())?
        .as_nanos();
    let id = format!("{}-{stamp}", std::process::id());
    let (part_path, meta_path) = import_paths(&app, &id)?;
    File::create(&part_path).map_err(|e| format!("Modellimport konnte nicht gestartet werden: {e}"))?;
    let meta = ImportMeta {
        id: id.clone(),
        name: name.clone(),
        total_size,
        expected_sha256: expected_sha256.map(|x| x.to_ascii_lowercase()),
    };
    fs::write(&meta_path, serde_json::to_vec_pretty(&meta).map_err(|e| e.to_string())?)
        .map_err(|e| format!("Importmetadaten konnten nicht geschrieben werden: {e}"))?;
    Ok(ImportBeginResponse { id, name, total_size })
}

#[tauri::command]
fn naqya_model_import_chunk(app: AppHandle, id: String, chunk_base64: String) -> Result<u64, String> {
    let (part_path, meta_path) = import_paths(&app, &id)?;
    if !meta_path.is_file() || !part_path.is_file() {
        return Err("Modellimport wurde nicht gefunden oder bereits beendet.".into());
    }
    let bytes = BASE64
        .decode(chunk_base64.as_bytes())
        .map_err(|e| format!("Importblock ist beschädigt: {e}"))?;
    if bytes.len() > 2 * 1024 * 1024 {
        return Err("Ein Importblock darf maximal 2 MiB groß sein.".into());
    }
    let mut file = OpenOptions::new()
        .append(true)
        .open(&part_path)
        .map_err(|e| format!("Importdatei konnte nicht fortgesetzt werden: {e}"))?;
    file.write_all(&bytes)
        .map_err(|e| format!("Importblock konnte nicht gespeichert werden: {e}"))?;
    file.flush().map_err(|e| format!("Importblock konnte nicht bestätigt werden: {e}"))?;
    let size = file.metadata().map_err(|e| e.to_string())?.len();
    Ok(size)
}

#[tauri::command]
fn naqya_model_import_finish(app: AppHandle, id: String) -> Result<NativeModel, String> {
    let (part_path, meta_path) = import_paths(&app, &id)?;
    let meta: ImportMeta = serde_json::from_slice(
        &fs::read(&meta_path).map_err(|e| format!("Importmetadaten fehlen: {e}"))?,
    )
    .map_err(|e| format!("Importmetadaten sind beschädigt: {e}"))?;
    let actual_size = fs::metadata(&part_path)
        .map_err(|e| format!("Importdatei fehlt: {e}"))?
        .len();
    if actual_size != meta.total_size {
        return Err(format!("Modellimport unvollständig: {actual_size} von {} Bytes.", meta.total_size));
    }
    let sha256 = hash_file(&part_path)?;
    if let Some(expected) = meta.expected_sha256.as_deref() {
        if !expected.eq_ignore_ascii_case(&sha256) {
            return Err("SHA-256-Prüfsumme des Sprachmodells stimmt nicht.".into());
        }
    }
    let target = model_dir(&app)?.join(&meta.name);
    if target.exists() {
        fs::remove_file(&target).map_err(|e| format!("Vorhandenes Modell konnte nicht ersetzt werden: {e}"))?;
    }
    fs::rename(&part_path, &target).map_err(|e| format!("Modell konnte nicht aktiviert werden: {e}"))?;
    let _ = fs::remove_file(meta_path);
    Ok(NativeModel {
        name: meta.name,
        path: target.to_string_lossy().into_owned(),
        bytes: actual_size,
        source: format!("App-Daten · SHA-256 {}", &sha256[..16]),
    })
}

#[tauri::command]
fn naqya_model_import_abort(app: AppHandle, id: String) -> Result<(), String> {
    let (part_path, meta_path) = import_paths(&app, &id)?;
    let _ = fs::remove_file(part_path);
    let _ = fs::remove_file(meta_path);
    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .manage(RuntimeState::default())
        .invoke_handler(tauri::generate_handler![
            naqya_native_status,
            naqya_transcribe_pcm,
            naqya_model_import_begin,
            naqya_model_import_chunk,
            naqya_model_import_finish,
            naqya_model_import_abort
        ])
        .run(tauri::generate_context!())
        .expect("NAQYA Desktop konnte nicht gestartet werden");
}
