plugins { id("com.android.application"); kotlin("android") }

android {
    namespace = "de.provoware.naqya"
    compileSdk = 35
    defaultConfig {
        applicationId = "de.provoware.naqya"
        minSdk = 26
        targetSdk = 35
        versionCode = 122
        versionName = "0.12.2"
    }
    signingConfigs {
        val ks = System.getenv("PROVOWARE_ANDROID_KEYSTORE")
        val alias = System.getenv("PROVOWARE_ANDROID_KEY_ALIAS")
        val storePass = System.getenv("PROVOWARE_ANDROID_STORE_PASSWORD")
        val keyPass = System.getenv("PROVOWARE_ANDROID_KEY_PASSWORD")
        if (!ks.isNullOrBlank() && !alias.isNullOrBlank() && !storePass.isNullOrBlank() && !keyPass.isNullOrBlank()) {
            create("release") {
                storeFile = file(ks); keyAlias = alias; storePassword = storePass; keyPassword = keyPass
            }
        }
    }
    buildTypes {
        getByName("debug") { isDebuggable = true }
        getByName("release") {
            isMinifyEnabled = false
            isDebuggable = false
            signingConfigs.findByName("release")?.let { signingConfig = it }
        }
    }
    packaging { resources.excludes += setOf("META-INF/*") }
}
