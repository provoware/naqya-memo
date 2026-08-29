package de.provoware.naqya

import android.Manifest
import android.app.Activity
import android.app.AlarmManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.media.MediaRecorder
import android.os.Build
import android.util.Base64
import android.util.Log
import android.webkit.JavascriptInterface
import android.webkit.WebView
import org.json.JSONObject
import java.io.File
import java.time.Instant

class NativeBridge(private val activity: Activity, private val webView: WebView) {
    private val audioPermissionCode = 7211
    private val notificationPermissionCode = 7212
    private var pendingAudioRequestId: String? = null
    private var pendingReminderRequestId: String? = null
    private var pendingReminderPayload: JSONObject? = null
    private var recorder: MediaRecorder? = null
    private var recordingFile: File? = null

    @JavascriptInterface
    fun postMessage(message: String) {
        val obj = try { JSONObject(message) } catch (e: Exception) { return }
        val id = obj.optString("id")
        val action = obj.optString("action")
        val payload = obj.optJSONObject("payload") ?: JSONObject()
        activity.runOnUiThread {
            try {
                if (!BridgeContract.isAllowed(action)) throw IllegalArgumentException("NATIVE_ACTION_BLOCKED")
                when (action) {
                    "platformInfo" -> resolve(id, platformInfo())
                    "shareText" -> { shareText(payload); resolve(id, JSONObject().put("opened", true)) }
                    "scheduleReminder" -> scheduleReminderWithPermission(id, payload)
                    "cancelReminder" -> { cancelReminder(payload); resolve(id, JSONObject().put("cancelled", true)) }
                    "audioStart" -> audioStart(id)
                    "audioStop" -> resolve(id, audioStop())
                    "acceptanceResult" -> { Log.i("ProvowareAcceptance", payload.toString()); resolve(id, JSONObject().put("logged", true)) }
                }
            } catch (e: Exception) { reject(id, e.message ?: e.javaClass.simpleName) }
        }
    }

    private fun platformInfo(): JSONObject = JSONObject()
        .put("platform", "android")
        .put("native_bridge", true)
        .put("sdk_int", Build.VERSION.SDK_INT)
        .put("model", Build.MODEL)
        .put("manufacturer", Build.MANUFACTURER)
        .put("record_audio_permission", activity.checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED)
        .put("notification_permission", Build.VERSION.SDK_INT < 33 || activity.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED)
        .put("runtime_source", "V0.12.2")

    private fun shareText(payload: JSONObject) {
        val intent = Intent(Intent.ACTION_SEND).apply {
            type = "text/plain"
            putExtra(Intent.EXTRA_SUBJECT, payload.optString("title", "OI - PROVOWARE - IO"))
            putExtra(Intent.EXTRA_TEXT, payload.optString("text", ""))
        }
        activity.startActivity(Intent.createChooser(intent, "Teilen"))
    }


    private fun scheduleReminderWithPermission(requestId: String, payload: JSONObject) {
        if (Build.VERSION.SDK_INT >= 33 && activity.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            pendingReminderRequestId = requestId
            pendingReminderPayload = JSONObject(payload.toString())
            activity.requestPermissions(arrayOf(Manifest.permission.POST_NOTIFICATIONS), notificationPermissionCode)
            return
        }
        scheduleReminder(payload)
        resolve(requestId, JSONObject().put("scheduled", true))
    }

    private fun scheduleReminder(payload: JSONObject) {
        val at = payload.optString("at")
        val millis = try { Instant.parse(at).toEpochMilli() } catch (e: Exception) { throw IllegalArgumentException("INVALID_REMINDER_TIME") }
        val intent = Intent(activity, ReminderReceiver::class.java).apply {
            putExtra("title", payload.optString("title", "Erinnerung"))
            putExtra("body", payload.optString("body", ""))
            putExtra("entity_id", payload.optString("id", ""))
        }
        val requestCode = payload.optString("id", at).hashCode()
        val pi = PendingIntent.getBroadcast(activity, requestCode, intent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
        val alarm = activity.getSystemService(Context.ALARM_SERVICE) as AlarmManager
        alarm.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, millis, pi)
    }


    private fun cancelReminder(payload: JSONObject) {
        val entity = payload.optString("id", "")
        if (entity.isBlank()) return
        val intent = Intent(activity, ReminderReceiver::class.java)
        val pi = PendingIntent.getBroadcast(activity, entity.hashCode(), intent, PendingIntent.FLAG_NO_CREATE or PendingIntent.FLAG_IMMUTABLE)
        if (pi != null) {
            val alarm = activity.getSystemService(Context.ALARM_SERVICE) as AlarmManager
            alarm.cancel(pi); pi.cancel()
        }
    }

    private fun audioStart(requestId: String) {
        if (activity.checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            pendingAudioRequestId = requestId
            activity.requestPermissions(arrayOf(Manifest.permission.RECORD_AUDIO), audioPermissionCode)
            return
        }
        startRecorder()
        resolve(requestId, JSONObject().put("started", true))
    }

    private fun startRecorder() {
        if (recorder != null) throw IllegalStateException("RECORDING_ALREADY_ACTIVE")
        val file = File.createTempFile("provoware_voice_", ".m4a", activity.cacheDir)
        val r = if (Build.VERSION.SDK_INT >= 31) MediaRecorder(activity) else @Suppress("DEPRECATION") MediaRecorder()
        r.setAudioSource(MediaRecorder.AudioSource.MIC)
        r.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
        r.setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
        r.setAudioSamplingRate(44100)
        r.setAudioEncodingBitRate(128000)
        r.setOutputFile(file.absolutePath)
        r.prepare(); r.start()
        recorder = r; recordingFile = file
    }

    private fun audioStop(): JSONObject {
        val r = recorder ?: throw IllegalStateException("RECORDING_NOT_ACTIVE")
        val file = recordingFile ?: throw IllegalStateException("RECORDING_FILE_MISSING")
        try { r.stop() } finally { r.reset(); r.release(); recorder = null }
        if (!file.isFile || file.length() == 0L) throw IllegalStateException("RECORDING_EMPTY")
        if (file.length() > 25L * 1024L * 1024L) { file.delete(); recordingFile = null; throw IllegalStateException("RECORDING_TOO_LARGE_FOR_BRIDGE") }
        val encoded = Base64.encodeToString(file.readBytes(), Base64.NO_WRAP)
        file.delete(); recordingFile = null
        return JSONObject().put("base64", encoded).put("mime", "audio/mp4").put("name", "sprachmemo.m4a")
    }

    fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        if (requestCode == audioPermissionCode) {
            val id = pendingAudioRequestId ?: return
            pendingAudioRequestId = null
            if (grantResults.firstOrNull() == PackageManager.PERMISSION_GRANTED) {
                try { startRecorder(); resolve(id, JSONObject().put("started", true)) }
                catch (e: Exception) { reject(id, e.message ?: "AUDIO_START_FAILED") }
            } else reject(id, "MICROPHONE_PERMISSION_DENIED")
            return
        }
        if (requestCode == notificationPermissionCode) {
            val id = pendingReminderRequestId ?: return
            val payload = pendingReminderPayload
            pendingReminderRequestId = null; pendingReminderPayload = null
            if (grantResults.firstOrNull() == PackageManager.PERMISSION_GRANTED && payload != null) {
                try { scheduleReminder(payload); resolve(id, JSONObject().put("scheduled", true)) }
                catch (e: Exception) { reject(id, e.message ?: "REMINDER_SCHEDULE_FAILED") }
            } else reject(id, "NOTIFICATION_PERMISSION_DENIED")
        }
    }

    private fun resolve(id: String, payload: JSONObject) = callback("resolve", id, payload.toString())
    private fun reject(id: String, message: String) = callback("reject", id, JSONObject.quote(message))
    private fun callback(method: String, id: String, jsArg: String) {
        val js = "window.ProvowareNativeCallbacks && window.ProvowareNativeCallbacks.$method(${JSONObject.quote(id)},$jsArg);"
        webView.post { webView.evaluateJavascript(js, null) }
    }

    fun close() {
        try { recorder?.stop() } catch (_: Exception) {}
        try { recorder?.release() } catch (_: Exception) {}
        recorder = null; recordingFile?.delete(); recordingFile = null
    }
}
