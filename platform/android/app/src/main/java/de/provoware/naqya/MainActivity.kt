package de.provoware.naqya

import android.app.Activity
import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.content.pm.ApplicationInfo
import android.net.Uri
import android.os.Bundle
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebView
import android.webkit.WebViewClient

class MainActivity : Activity() {
    private lateinit var webView: WebView
    private lateinit var bridge: NativeBridge
    private var fileChooserCallback: ValueCallback<Array<Uri>>? = null
    private val fileChooserCode = 7102

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        webView = WebView(this)
        bridge = NativeBridge(this, webView)
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            databaseEnabled = true
            allowFileAccess = true
            allowContentAccess = true
            mediaPlaybackRequiresUserGesture = false
            userAgentString = userAgentString + " OIProvowareMobile/0.12.2 Android"
        }
        webView.webViewClient = WebViewClient()
        webView.webChromeClient = object : WebChromeClient() {
            override fun onShowFileChooser(
                webView: WebView?,
                filePathCallback: ValueCallback<Array<Uri>>?,
                fileChooserParams: FileChooserParams?
            ): Boolean {
                fileChooserCallback?.onReceiveValue(null)
                fileChooserCallback = filePathCallback
                val intent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
                    addCategory(Intent.CATEGORY_OPENABLE)
                    type = "*/*"
                    putExtra(Intent.EXTRA_MIME_TYPES, arrayOf(
                        "application/pdf", "text/plain", "text/markdown",
                        "audio/wav", "audio/mpeg", "audio/ogg", "audio/mp4",
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    ))
                }
                startActivityForResult(intent, fileChooserCode)
                return true
            }
        }
        webView.addJavascriptInterface(bridge, "ProvowareAndroid")
        setContentView(webView)
        val debuggable = (applicationInfo.flags and ApplicationInfo.FLAG_DEBUGGABLE) != 0
        val acceptance = if (debuggable) intent?.getStringExtra("provoware_acceptance") else null
        val suffix = if (acceptance == "run" || acceptance == "verify") "?acceptance=$acceptance" else ""
        webView.loadUrl("file:///android_asset/www/index.html$suffix")
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == fileChooserCode) {
            val result = if (resultCode == RESULT_OK && data?.data != null) arrayOf(data.data!!) else null
            fileChooserCallback?.onReceiveValue(result)
            fileChooserCallback = null
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        bridge.onRequestPermissionsResult(requestCode, permissions, grantResults)
    }

    @Deprecated("Back navigation compatibility")
    override fun onBackPressed() {
        if (webView.canGoBack()) webView.goBack() else super.onBackPressed()
    }

    override fun onDestroy() {
        bridge.close()
        webView.removeJavascriptInterface("ProvowareAndroid")
        webView.destroy()
        super.onDestroy()
    }
}
