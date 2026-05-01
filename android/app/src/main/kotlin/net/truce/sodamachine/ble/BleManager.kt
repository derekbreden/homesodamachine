package net.truce.sodamachine.ble

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import kotlinx.coroutines.delay

/**
 * Connection state machine. Mirrors the iOS `ConnectionState` enum in
 * `BLEManager.swift` so the same UI conditions translate one-to-one.
 */
enum class ConnectionState {
    BluetoothOff,
    Searching,
    SearchingLong,    // been searching a while; show hints
    Connecting,
    Connected,
}

/**
 * Stubbed BLE manager that drives ScanView's state transitions without real
 * BLE. Real implementation lands in M3 via Nordic's Android-BLE-Library and
 * replaces this class wholesale; the surface API stays the same so callers
 * don't change.
 *
 * State is held in Compose `mutableStateOf` so observing composables
 * recompose automatically. M3 will likely move this to StateFlow once the
 * real BLE layer needs lifecycle-scoped callbacks; for now Compose state is
 * the simplest thing that works and matches the iOS `@Observable` pattern
 * one-to-one in feel.
 *
 * `hasCompletedOnboarding` and `prefersDemoMode` are in-memory only —
 * iOS persists them via `@AppStorage` (UserDefaults). M3 ports that to
 * DataStore. For now every launch shows onboarding.
 */
class BleManager {
    var connectionState by mutableStateOf(ConnectionState.BluetoothOff)
        private set

    var hasCompletedOnboarding by mutableStateOf(false)
    var prefersDemoMode by mutableStateOf(false)

    var demoMode by mutableStateOf(false)
        private set

    val readyToShow: Boolean
        get() = connectionState == ConnectionState.Connected

    /**
     * Stub of the iOS `activateBluetooth()` flow:
     *   BluetoothOff → Searching → SearchingLong → Connecting → Connected.
     *
     * The real iOS flow advances states based on actual BLE callbacks; this
     * stub uses delays that approximate the real timing so the connection-
     * state UI can be verified end-to-end. Cooperatively cancelable —
     * collecting from a `LaunchedEffect` that leaves composition (e.g. user
     * taps Cancel) cancels the chain partway through.
     */
    suspend fun activateBluetooth() {
        connectionState = ConnectionState.Searching
        delay(2_000)
        if (connectionState != ConnectionState.Searching) return
        connectionState = ConnectionState.SearchingLong
        delay(3_000)
        if (connectionState != ConnectionState.SearchingLong) return
        connectionState = ConnectionState.Connecting
        delay(1_500)
        connectionState = ConnectionState.Connected
    }

    fun enterDemoMode() {
        demoMode = true
        connectionState = ConnectionState.Connected
    }

    fun exitDemoMode() {
        demoMode = false
        connectionState = ConnectionState.BluetoothOff
    }

    fun disconnect() {
        demoMode = false
        connectionState = ConnectionState.BluetoothOff
        hasCompletedOnboarding = false
    }
}
