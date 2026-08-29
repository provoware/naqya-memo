import Foundation
import UIKit
import WebKit
import AVFoundation
import UserNotifications

final class NativeBridge: NSObject, WKScriptMessageHandler {
    weak var webView: WKWebView?
    weak var host: UIViewController?
    private var recorder: AVAudioRecorder?
    private var recordingURL: URL?

    init(webView: WKWebView, host: UIViewController) {
        self.webView = webView
        self.host = host
        super.init()
    }

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard message.name == "provoware",
              let body = message.body as? [String: Any],
              let id = body["id"] as? String,
              let action = body["action"] as? String else { return }
        let payload = body["payload"] as? [String: Any] ?? [:]
        guard BridgeContract.isAllowed(action) else { reject(id, "NATIVE_ACTION_BLOCKED"); return }
        switch action {
        case "platformInfo": resolve(id, platformInfo())
        case "shareText": shareText(id, payload)
        case "scheduleReminder": scheduleReminder(id, payload)
        case "cancelReminder": cancelReminder(id, payload)
        case "audioStart": audioStart(id)
        case "audioStop": audioStop(id)
        case "acceptanceResult": acceptanceResult(id, payload)
        default: reject(id, "NATIVE_ACTION_BLOCKED")
        }
    }

    private func platformInfo() -> [String: Any] {
        let mic: String
        switch AVAudioSession.sharedInstance().recordPermission {
        case .granted: mic = "granted"
        case .denied: mic = "denied"
        default: mic = "undetermined"
        }
        return [
            "platform": "ios",
            "native_bridge": true,
            "system_version": UIDevice.current.systemVersion,
            "model": UIDevice.current.model,
            "microphone_permission": mic,
            "runtime_source": "V0.12.2"
        ]
    }

    private func shareText(_ id: String, _ payload: [String: Any]) {
        guard let host else { reject(id, "SHARE_HOST_MISSING"); return }
        let title = payload["title"] as? String ?? "OI - PROVOWARE - IO"
        let text = payload["text"] as? String ?? ""
        let vc = UIActivityViewController(activityItems: [title, text], applicationActivities: nil)
        if let pop = vc.popoverPresentationController {
            pop.sourceView = host.view
            pop.sourceRect = CGRect(x: host.view.bounds.midX, y: host.view.bounds.midY, width: 1, height: 1)
        }
        host.present(vc, animated: true)
        resolve(id, ["opened": true])
    }

    private func scheduleReminder(_ id: String, _ payload: [String: Any]) {
        guard let at = payload["at"] as? String,
              let date = ISO8601DateFormatter().date(from: at) else { reject(id, "INVALID_REMINDER_TIME"); return }
        let center = UNUserNotificationCenter.current()
        center.requestAuthorization(options: [.alert, .sound, .badge]) { granted, error in
            if let error { self.reject(id, "NOTIFICATION_PERMISSION_ERROR: \(error.localizedDescription)"); return }
            guard granted else { self.reject(id, "NOTIFICATION_PERMISSION_DENIED"); return }
            let content = UNMutableNotificationContent()
            content.title = payload["title"] as? String ?? "Erinnerung"
            content.body = payload["body"] as? String ?? ""
            content.sound = .default
            let interval = max(1, date.timeIntervalSinceNow)
            let trigger = UNTimeIntervalNotificationTrigger(timeInterval: interval, repeats: false)
            let entity = payload["id"] as? String ?? UUID().uuidString
            center.add(UNNotificationRequest(identifier: "provoware.\(entity)", content: content, trigger: trigger)) { err in
                if let err { self.reject(id, "REMINDER_SCHEDULE_FAILED: \(err.localizedDescription)") }
                else { self.resolve(id, ["scheduled": true]) }
            }
        }
    }


    private func cancelReminder(_ id: String, _ payload: [String: Any]) {
        let entity = payload["id"] as? String ?? ""
        guard !entity.isEmpty else { resolve(id, ["cancelled": false]); return }
        UNUserNotificationCenter.current().removePendingNotificationRequests(withIdentifiers: ["provoware.\(entity)"])
        resolve(id, ["cancelled": true])
    }

    private func audioStart(_ id: String) {
        let session = AVAudioSession.sharedInstance()
        session.requestRecordPermission { granted in
            guard granted else { self.reject(id, "MICROPHONE_PERMISSION_DENIED"); return }
            DispatchQueue.main.async {
                do {
                    try session.setCategory(.playAndRecord, mode: .default, options: [.defaultToSpeaker, .allowBluetooth])
                    try session.setActive(true)
                    let url = FileManager.default.temporaryDirectory.appendingPathComponent("provoware_voice_\(UUID().uuidString).m4a")
                    let settings: [String: Any] = [
                        AVFormatIDKey: Int(kAudioFormatMPEG4AAC),
                        AVSampleRateKey: 44100.0,
                        AVNumberOfChannelsKey: 1,
                        AVEncoderBitRateKey: 128000
                    ]
                    let r = try AVAudioRecorder(url: url, settings: settings)
                    r.prepareToRecord()
                    guard r.record() else { throw NSError(domain: "Provoware", code: 1, userInfo: [NSLocalizedDescriptionKey: "RECORDING_START_FAILED"]) }
                    self.recorder = r; self.recordingURL = url
                    self.resolve(id, ["started": true])
                } catch { self.reject(id, "AUDIO_START_FAILED: \(error.localizedDescription)") }
            }
        }
    }

    private func audioStop(_ id: String) {
        guard let recorder, let url = recordingURL else { reject(id, "RECORDING_NOT_ACTIVE"); return }
        recorder.stop(); self.recorder = nil; self.recordingURL = nil
        do {
            let data = try Data(contentsOf: url)
            try? FileManager.default.removeItem(at: url)
            guard !data.isEmpty else { reject(id, "RECORDING_EMPTY"); return }
            guard data.count <= 25 * 1024 * 1024 else { reject(id, "RECORDING_TOO_LARGE_FOR_BRIDGE"); return }
            resolve(id, ["base64": data.base64EncodedString(), "mime": "audio/mp4", "name": "sprachmemo.m4a"])
        } catch { reject(id, "AUDIO_READ_FAILED: \(error.localizedDescription)") }
    }


    private func acceptanceResult(_ id: String, _ payload: [String: Any]) {
        let data = try? JSONSerialization.data(withJSONObject: payload, options: [.prettyPrinted])
        let text = data.flatMap { String(data: $0, encoding: .utf8) } ?? "{}"
        NSLog("[ProvowareAcceptance] %@", text.replacingOccurrences(of: "\n", with: " "))
        if let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first {
            try? data?.write(to: docs.appendingPathComponent("acceptance_result.json"), options: .atomic)
        }
        resolve(id, ["logged": true])
    }

    private func resolve(_ id: String, _ payload: Any) { callback(method: "resolve", id: id, value: payload) }
    private func reject(_ id: String, _ message: String) { callback(method: "reject", id: id, value: message) }

    private func callback(method: String, id: String, value: Any) {
        DispatchQueue.main.async {
            guard let webView = self.webView else { return }
            let idJSON = Self.jsonLiteral(id)
            let valueJSON = Self.jsonLiteral(value)
            webView.evaluateJavaScript("window.ProvowareNativeCallbacks && window.ProvowareNativeCallbacks.\(method)(\(idJSON),\(valueJSON));", completionHandler: nil)
        }
    }

    private static func jsonLiteral(_ value: Any) -> String {
        if JSONSerialization.isValidJSONObject(value), let data = try? JSONSerialization.data(withJSONObject: value), let s = String(data: data, encoding: .utf8) { return s }
        if let data = try? JSONSerialization.data(withJSONObject: [value]), let s = String(data: data, encoding: .utf8), s.count >= 2 { return String(s.dropFirst().dropLast()) }
        return "null"
    }

    func close() {
        recorder?.stop(); recorder = nil
        if let recordingURL { try? FileManager.default.removeItem(at: recordingURL) }
        recordingURL = nil
    }
}
