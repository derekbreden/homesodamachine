plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.compose)
}

android {
    namespace = "net.truce.sodamachine"
    compileSdk = 36

    defaultConfig {
        applicationId = "net.truce.sodamachine"
        minSdk = 26
        targetSdk = 36
        versionCode = 1
        versionName = "1.0.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro",
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    // No explicit `kotlinOptions { jvmTarget = "17" }` here — that DSL came
    // from the standalone `kotlin-android` plugin, which AGP 9.0+ replaces
    // with built-in Kotlin support. The built-in Kotlin reads the JVM target
    // from `compileOptions` above, so JVM 17 propagates to Kotlin compilation
    // automatically. If this needs to diverge later, configure it via a
    // top-level `kotlin { compilerOptions { jvmTarget.set(...) } }` block.

    buildFeatures {
        compose = true
    }

    sourceSets["main"].java.srcDirs("src/main/kotlin")

    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

dependencies {
    implementation(libs.androidx.core.splashscreen)
    implementation(libs.androidx.activity.compose)

    implementation(platform(libs.compose.bom))
    implementation(libs.compose.ui)
    implementation(libs.compose.ui.graphics)
    implementation(libs.compose.foundation)
    implementation(libs.compose.material3)
    implementation(libs.compose.ui.tooling.preview)

    debugImplementation(libs.compose.ui.tooling)
}
