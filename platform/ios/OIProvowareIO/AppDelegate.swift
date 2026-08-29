import UIKit
import WebKit
import UserNotifications

@main
final class AppDelegate: UIResponder, UIApplicationDelegate, UNUserNotificationCenterDelegate {
    var window: UIWindow?

    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil) -> Bool {
        UNUserNotificationCenter.current().delegate = self
        let window = UIWindow(frame: UIScreen.main.bounds)
        window.rootViewController = MobileViewController()
        window.makeKeyAndVisible()
        self.window = window
        return true
    }

    func userNotificationCenter(_ center: UNUserNotificationCenter, willPresent notification: UNNotification, withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void) {
        NSLog("[ProvowareAcceptance] REMINDER_FIRED:%@", notification.request.identifier)
        completionHandler([.banner, .sound])
    }
}

final class MobileViewController: UIViewController {
    private var webView: WKWebView!
    private var bridge: NativeBridge!

    override func loadView() {
        let config = WKWebViewConfiguration()
        config.websiteDataStore = .default()
        config.defaultWebpagePreferences.allowsContentJavaScript = true
        let controller = WKUserContentController()
        let args = ProcessInfo.processInfo.arguments
        if let i = args.firstIndex(of: "-ProvowareAcceptance"), i + 1 < args.count {
            let mode = args[i + 1]
            if mode == "run" || mode == "verify" {
                controller.addUserScript(WKUserScript(source: "window.__PROVOWARE_ACCEPTANCE_MODE__=\"\(mode)\";", injectionTime: .atDocumentStart, forMainFrameOnly: true))
            }
        }
        config.userContentController = controller
        webView = WKWebView(frame: .zero, configuration: config)
        bridge = NativeBridge(webView: webView, host: self)
        controller.add(bridge, name: "provoware")
        webView.allowsBackForwardNavigationGestures = true
        view = webView
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        guard let root = Bundle.main.resourceURL?.appendingPathComponent("WebAssets"),
              let index = root.appendingPathComponent("index.html") as URL? else { return }
        webView.loadFileURL(index, allowingReadAccessTo: root)
    }

    deinit {
        webView?.configuration.userContentController.removeScriptMessageHandler(forName: "provoware")
        bridge?.close()
    }
}
