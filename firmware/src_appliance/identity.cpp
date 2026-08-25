#include <Arduino.h>
#include <Preferences.h>
#include <esp_mac.h>

#include "identity.h"

static Preferences prefs;
static char machineName[MACHINE_NAME_MAX + 1] = {0};
static uint8_t unitId[3] = {0};

void identityBegin() {
    uint8_t mac[6] = {0};
    // Straight out of efuse. WiFi.macAddress answers all zeros until the driver
    // is started, and nothing on this board ever starts it.
    esp_read_mac(mac, ESP_MAC_WIFI_STA);
    unitId[0] = mac[3];
    unitId[1] = mac[4];
    unitId[2] = mac[5];

    if (prefs.begin("machine", true)) {
        prefs.getString("name", machineName, sizeof(machineName));
        prefs.end();
    }
}

void machineIdentity(IdentityPayload &out) {
    out.model = MACHINE_APPLIANCE;
    memcpy(out.unit, unitId, sizeof(unitId));
    memset(out.name, 0, sizeof(out.name));
    strncpy(out.name, machineName, MACHINE_NAME_MAX);
}

bool machineSetName(const char *name) {
    strncpy(machineName, name ? name : "", MACHINE_NAME_MAX);
    machineName[MACHINE_NAME_MAX] = 0;
    if (!prefs.begin("machine", false)) return false;
    const bool ok = prefs.putString("name", machineName) > 0 || machineName[0] == 0;
    prefs.end();
    return ok;
}

void identityConsole(const String &line) {
    String rest = line.substring(8);
    rest.trim();
    if (rest.length()) {
        if (!machineSetName(rest.c_str())) { Serial.println("\nIDENTITY:FAIL"); return; }
    }
    Serial.printf("\nIDENTITY model=appliance unit=%02X%02X%02X name=%s\n",
                  unitId[0], unitId[1], unitId[2],
                  machineName[0] ? machineName : "(unset)");
}
