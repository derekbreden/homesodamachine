package net.truce.sodamachine

import androidx.compose.runtime.Composable
import net.truce.sodamachine.ui.scan.ScanView
import net.truce.sodamachine.ui.theme.SodaMachineTheme

@Composable
fun App() {
    SodaMachineTheme {
        ScanView()
    }
}
