package net.truce.sodamachine

import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import net.truce.sodamachine.ble.BleManager
import net.truce.sodamachine.ui.scan.ScanView
import net.truce.sodamachine.ui.theme.SodaMachineTheme

@Composable
fun App() {
    // Hoist BleManager to App scope so it survives recomposition of ScanView's
    // sub-composables. M3 will replace this with a real lifecycle-scoped BLE
    // service and likely route through a ViewModel, but for now a simple
    // remember-at-root mirrors the iOS @State on SodaMachineApp.
    val ble = remember { BleManager() }
    SodaMachineTheme {
        ScanView(ble = ble)
    }
}
