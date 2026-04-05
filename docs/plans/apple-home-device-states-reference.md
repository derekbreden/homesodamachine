# Apple Home / HomeKit / Matter — Complete Device States Reference

## Status: Reference document for ESP32-C6 Matter planning

This documents every state, attribute, notification, and UI element that Apple Home
displays for each supported device type. Sourced from Apple developer documentation,
the HomeKit Accessory Protocol (HAP) specification, HomeKit bridge references, and
community testing.

---

## Table of Contents

1. [Cross-cutting characteristics (shared by many device types)](#cross-cutting-characteristics)
2. [Lock Mechanism](#lock-mechanism)
3. [Contact Sensor](#contact-sensor)
4. [Motion Sensor](#motion-sensor)
5. [Occupancy Sensor](#occupancy-sensor)
6. [Temperature Sensor](#temperature-sensor)
7. [Humidity Sensor](#humidity-sensor)
8. [Light Sensor](#light-sensor)
9. [Switch](#switch)
10. [Outlet](#outlet)
11. [Lightbulb](#lightbulb)
12. [Thermostat](#thermostat)
13. [Heater/Cooler](#heatercooler)
14. [Window Covering / Blinds / Shades](#window-covering)
15. [Fan (v2)](#fan-v2)
16. [Garage Door Opener](#garage-door-opener)
17. [Valve](#valve)
18. [Faucet](#faucet)
19. [Irrigation System](#irrigation-system)
20. [Air Quality Sensor](#air-quality-sensor)
21. [Air Purifier](#air-purifier)
22. [Smoke Sensor](#smoke-sensor)
23. [Carbon Monoxide Sensor](#carbon-monoxide-sensor)
24. [Carbon Dioxide Sensor](#carbon-dioxide-sensor)
25. [Leak Sensor](#leak-sensor)
26. [Security System](#security-system)
27. [Doorbell](#doorbell)
28. [Stateless Programmable Switch](#stateless-programmable-switch)
29. [Humidifier / Dehumidifier](#humidifier-dehumidifier)
30. [Filter Maintenance](#filter-maintenance)
31. [Battery Service](#battery-service)
32. [Apple Home UI behaviors and limitations](#apple-home-ui-behaviors)
33. [Soda Dispenser Mapping Analysis](#soda-dispenser-mapping)

---

## Cross-cutting Characteristics

These optional characteristics can be added to most sensor and accessory services.
They affect what Apple Home displays in accessory detail views and notifications.

| Characteristic | Values | Apple Home Display |
|---|---|---|
| **StatusActive** | 0=inactive, 1=active | NOT prominently shown. Only visible in accessory settings. |
| **StatusFault** | 0=no fault, 1=fault | NOT shown on main tile. Only visible in accessory settings. Third-party apps (Eve, Controller) show a "!" badge. Apple Home does not. |
| **StatusTampered** | 0=not tampered, 1=tampered | Same as StatusFault — hidden in settings, not on tile. |
| **StatusLowBattery** | 0=normal, 1=low | Shown as battery glyph highlight in detail view. Can trigger notification. |
| **BatteryLevel** | 0-100% | Shown in accessory detail view as percentage with glyph. Requires BatteryService with Power Source cluster (Matter). |
| **ChargingState** | 0=not charging, 1=charging, 2=not chargeable | Shown in battery detail section. |
| **Name** | String | Accessory name shown on tile and detail. |
| **FirmwareVersion** | String | Shown in accessory info section (scroll to bottom of detail). |
| **Model** | String | Shown in accessory info section. |
| **SerialNumber** | String | Shown in accessory info section. |
| **Manufacturer** | String | Shown in accessory info section. |

### Activity History (iOS 17+)

Apple Home records up to 30 days of activity for security-related accessories:
- Door locks, garage doors, contact sensors, motion sensors, smoke detectors
- Shows accessory name, action, date, time
- Requires Apple TV or HomePod as home hub with tvOS 17+
- End-to-end encrypted, view-only, auto-deleted after 30 days

### Connectivity States

Every accessory can show these connection-level states on its tile:
- **Normal** — shows current state (e.g., "Locked", "72°F")
- **Not Responding** — shown when hub cannot reach accessory
- **Updating** — transient state during communication
- **No Response** — persistent connectivity failure

---

## Lock Mechanism

**Service:** LockMechanism
**Required characteristics:** LockCurrentState, LockTargetState

### States displayed on tile

| LockCurrentState | Value | Apple Home tile text |
|---|---|---|
| Unsecured | 0 | **Unlocked** |
| Secured | 1 | **Locked** |
| Jammed | 2 | **Jammed** |
| Unknown | 3 | **Unknown** |

LockTargetState (0=unsecured, 1=secured) — used for control, not display.

### Notifications

- Lock was locked
- Lock was unlocked
- Lock jammed (critical-level notification on some implementations)
- Both lock/unlock states always trigger notifications (cannot choose just one)

### Activity History

Yes — full 30-day log of lock/unlock events with timestamps.

### Detail view

- Lock/Unlock toggle control
- Status text
- Notification settings (time-based, presence-based)

---

## Contact Sensor

**Service:** ContactSensor
**Required:** ContactSensorState
**Optional:** StatusActive, StatusFault, StatusTampered, StatusLowBattery

### States displayed on tile

| ContactSensorState | Value | Apple Home tile text |
|---|---|---|
| Contact detected | 0 | **Closed** (or context-specific: "Home", "Not Open") |
| Contact not detected | 1 | **Open** |

### Notifications

- "[Name] was opened"
- "[Name] was closed"
- Both states always generate notifications (cannot select only one)
- Time-based and presence-based filtering available

### Activity History

Yes — 30-day log of open/close events.

### Detail view

- Current open/closed state
- Notification settings

---

## Motion Sensor

**Service:** MotionSensor
**Required:** MotionDetected (bool)
**Optional:** StatusActive, StatusFault, StatusTampered, StatusLowBattery

### States displayed on tile

| MotionDetected | Apple Home tile text |
|---|---|
| false | **No Motion** (or clear state) |
| true | **Motion Detected** |

### Notifications

- "Motion Detected" at [Name]
- Time-based filtering (e.g., only at night)
- Presence-based filtering (only when nobody home)

### Activity History

Yes — 30-day log.

### Notes

- No duration attribute — motion is boolean, device controls how long it stays "detected"
- No "last triggered" timestamp exposed in UI (only in Activity History)

---

## Occupancy Sensor

**Service:** OccupancySensor
**Required:** OccupancyDetected (0=not occupied, 1=occupied)
**Optional:** StatusActive, StatusFault, StatusTampered, StatusLowBattery

### States displayed on tile

| OccupancyDetected | Value | Apple Home tile text |
|---|---|---|
| Not occupied | 0 | **Not Detected** |
| Occupied | 1 | **Detected** |

### Notifications

Similar to motion sensor — occupancy detected/cleared.

---

## Temperature Sensor

**Service:** TemperatureSensor
**Required:** CurrentTemperature (-100 to 500 C)
**Optional:** StatusActive, StatusFault, StatusTampered, StatusLowBattery

### Display

- Tile shows current temperature value (e.g., "72°F" or "22°C")
- Respects TemperatureDisplayUnits if set
- No min/max/threshold display in native Apple Home
- Can be used as automation trigger ("When temperature rises above X")

### Notifications

- No native notifications for threshold crossing
- Can use automations to trigger other actions at specific temperatures

---

## Humidity Sensor

**Service:** HumiditySensor
**Required:** CurrentRelativeHumidity (0-100%)
**Optional:** StatusActive, StatusFault, StatusTampered, StatusLowBattery

### Display

- Tile shows current humidity percentage (e.g., "45%")
- No threshold alerts natively
- Can be used as automation trigger

---

## Light Sensor

**Service:** LightSensor
**Required:** CurrentAmbientLightLevel (0.0001-100000 lux)
**Optional:** StatusActive, StatusFault, StatusTampered, StatusLowBattery

### Display

- Tile shows current light level in lux
- Primarily useful as automation trigger
- No alert/notification capabilities

---

## Switch

**Service:** Switch
**Required:** On (bool)
**Optional:** (none beyond Name)

### States displayed on tile

| On | Apple Home tile text |
|---|---|
| false | **Off** |
| true | **On** |

### Detail view

- Simple on/off toggle
- No power consumption, no "in use" state
- No notifications available for standard switches

---

## Outlet

**Service:** Outlet
**Required:** On (bool), OutletInUse (bool)
**Optional:** (none standard; vendor characteristics for power monitoring ignored by Apple Home)

### States displayed on tile

| On | OutletInUse | Apple Home tile text |
|---|---|---|
| false | false | **Off** |
| false | true | **Off** (InUse may show as subtext) |
| true | false | **On** |
| true | true | **On** (with "In Use" indicator) |

### Power monitoring

- Apple Home IGNORES power consumption vendor characteristics (watts, kWh, voltage, current)
- These values only visible in third-party apps (Eve, Controller for HomeKit)
- No energy dashboard in native Apple Home

### Notifications

- Not available for standard outlets/switches

---

## Lightbulb

**Service:** Lightbulb
**Required:** On (bool)
**Optional:** Brightness (0-100%), Hue (0-360°), Saturation (0-100%), ColorTemperature (140-500 mireds)

### States displayed on tile

- **Off** / **On**
- If brightness supported: shows brightness percentage
- Tile color changes to reflect current light color

### Detail view

- On/Off toggle
- Brightness slider (if supported)
- Color picker wheel (if Hue/Saturation supported)
- Color temperature slider (if ColorTemperature supported): warm to cool white
- Adaptive Lighting toggle (if supported): auto-adjusts color temp throughout day
- Preset color/temperature favorites

### No fault/error states

- No built-in "bulb burned out" or fault indication
- StatusFault could be added but Apple Home won't show it on tile

---

## Thermostat

**Service:** Thermostat
**Required:** CurrentHeatingCoolingState, TargetHeatingCoolingState, CurrentTemperature, TargetTemperature, TemperatureDisplayUnits
**Optional:** HeatingThresholdTemperature, CoolingThresholdTemperature, CurrentRelativeHumidity, TargetRelativeHumidity

### Current state (read-only, what system is actually doing)

| CurrentHeatingCoolingState | Value | Display |
|---|---|---|
| Off | 0 | **Off** / **Idle** |
| Heat | 1 | **Heating** |
| Cool | 2 | **Cooling** |

### Target state (controllable)

| TargetHeatingCoolingState | Value | Display |
|---|---|---|
| Off | 0 | **Off** |
| Heat | 1 | **Heat** |
| Cool | 2 | **Cool** |
| Auto | 3 | **Auto** |

### Detail view

- Current temperature (large display)
- Target temperature control (dial or slider)
- Mode selector (Off/Heat/Cool/Auto)
- Heating/Cooling threshold temperatures (in Auto mode)
- Current humidity (if characteristic present)
- Target humidity (if characteristic present)
- Temperature display units (C/F)

### Notifications

- No native thermostat notifications in Apple Home

---

## Heater/Cooler

**Service:** HeaterCooler
**Required:** Active, CurrentHeaterCoolerState, TargetHeaterCoolerState, CurrentTemperature
**Optional:** LockPhysicalControls, RotationSpeed, SwingMode, HeatingThresholdTemperature, CoolingThresholdTemperature, TemperatureDisplayUnits

### Current state

| CurrentHeaterCoolerState | Value | Display |
|---|---|---|
| Inactive | 0 | **Inactive** |
| Idle | 1 | **Idle** |
| Heating | 2 | **Heating** |
| Cooling | 3 | **Cooling** |

### Target state

| TargetHeaterCoolerState | Value |
|---|---|
| Auto | 0 |
| Heat | 1 |
| Cool | 2 |

---

## Window Covering

**Service:** WindowCovering
**Required:** CurrentPosition (0-100%), TargetPosition (0-100%), PositionState
**Optional:** CurrentHorizontalTiltAngle (-90 to 90°), CurrentVerticalTiltAngle (-90 to 90°), TargetHorizontalTiltAngle, TargetVerticalTiltAngle, HoldPosition, ObstructionDetected

### States displayed on tile

- Shows position as percentage (e.g., "50%")
- **Closed** (0%), **Open** (100%), or percentage
- When moving: Apple Home derives state from position difference:
  - CurrentPosition > TargetPosition: **Closing**
  - CurrentPosition < TargetPosition: **Opening**
  - CurrentPosition == TargetPosition: shows percentage

### Detail view

- Position slider (0-100%)
- Tilt angle control (if tilt characteristics present)
- Favorite positions (via scenes)

### Notifications

- Can notify on open/close state changes

---

## Fan (v2)

**Service:** Fanv2
**Required:** Active (0=inactive, 1=active)
**Optional:** CurrentFanState, TargetFanState, RotationSpeed (0-100%), RotationDirection (0=CW, 1=CCW), SwingMode (0=disabled, 1=enabled), LockPhysicalControls

### Current fan state

| CurrentFanState | Value | Display |
|---|---|---|
| Inactive | 0 | **Off** |
| Idle | 1 | **Idle** |
| Blowing Air | 2 | **On** |

### Detail view

- Speed slider (0-100%, often in 25% steps: off/low/medium/high/max)
- Setting speed to 0 turns fan off; any nonzero turns it on
- No separate power button shown — speed slider IS the control
- Rotation direction control (if supported)
- Swing/oscillation toggle (limited Apple Home support)

---

## Garage Door Opener

**Service:** GarageDoorOpener
**Required:** CurrentDoorState, TargetDoorState, ObstructionDetected
**Optional:** LockCurrentState, LockTargetState

### States displayed on tile

| CurrentDoorState | Value | Apple Home tile text |
|---|---|---|
| Open | 0 | **Open** |
| Closed | 1 | **Closed** |
| Opening | 2 | **Opening** |
| Closing | 3 | **Closing** |
| Stopped | 4 | **Stopped** |

ObstructionDetected (bool): When true, shows **Obstructed** on tile.

### Notifications

- Door opened
- Door closed
- Obstruction detected
- Both open/close always notify (cannot select only one)
- Critical notification category for some implementations

### Activity History

Yes — 30-day log of open/close events.

---

## Valve

**Service:** Valve
**Required:** Active (0/1), InUse (0/1), ValveType
**Optional:** SetDuration (0-3600s), RemainingDuration (0-3600s), IsConfigured, StatusFault, ServiceLabelIndex

### Valve types and icons

| ValveType | Value | Apple Home icon |
|---|---|---|
| Generic | 0 | Generic valve icon |
| Irrigation/Sprinkler | 1 | Sprinkler icon |
| Shower Head | 2 | Shower icon |
| Water Faucet | 3 | Faucet icon |

### States displayed on tile (Active + InUse matrix)

| Active | InUse | Apple Home tile text |
|---|---|---|
| 0 | 0 | **Off** |
| 0 | 1 | **Stopping** |
| 1 | 0 | **Starting** (or **Waiting**) |
| 1 | 1 | **Running** |

### Duration features

- **SetDuration**: User-configurable default run time shown in Home app. Home app allows user to set this value before activating valve.
- **RemainingDuration**: Apple Home auto-decrements a countdown timer display. Timer is display-only — the accessory must control actual shutoff. Apple designed it this way because if Home lost connectivity, the accessory still shuts off the valve.

### Detail view

- On/Off control
- Duration setting (before activation)
- Countdown timer (during operation)
- InUse status indicator

### Limitations

- Valves CANNOT be added to Apple Home scenes or automations
- Scheduling must be done via manufacturer's app or the accessory's own timer
- This is a significant limitation for creative use

---

## Faucet

**Service:** Faucet
**Required:** Active (0/1)
**Optional:** StatusFault

### Display

- Parent service for linked Valve services
- Shows as faucet icon
- Active/Inactive control

---

## Irrigation System

**Service:** IrrigationSystem
**Required:** Active (0/1), ProgramMode, InUse (0/1)
**Optional:** StatusFault, RemainingDuration

### Program mode

| ProgramMode | Value | Display |
|---|---|---|
| No program scheduled | 0 | No schedule indicator |
| Program scheduled | 1 | Schedule active indicator |
| Manual mode | 2 | Manual indicator |

### Display

- Parent service with linked Valve child services
- Each zone appears as a separate valve tile
- Home app shows system state but CANNOT create schedules
- Individual valve control is possible from Home app
- RemainingDuration shown per-zone

---

## Air Quality Sensor

**Service:** AirQualitySensor
**Required:** AirQuality (enum)
**Optional:** StatusActive, StatusFault, StatusLowBattery, StatusTampered, OzoneDensity (0-1000 ppb), NitrogenDioxideDensity (0-1000 ppb), SulphurDioxideDensity (0-1000 ppb), PM2.5Density (0-1000 ug/m3), PM10Density (0-1000 ug/m3), VOCDensity, CarbonDioxideLevel (0-10000 ppm), CarbonMonoxideLevel (0-100 ppm)

### Air quality levels

| AirQuality | Value | Apple Home display |
|---|---|---|
| Unknown | 0 | **Unknown** |
| Excellent | 1 | **Excellent** |
| Good | 2 | **Good** |
| Fair | 3 | **Fair** |
| Inferior | 4 | **Inferior** |
| Poor | 5 | **Poor** |

### Detail view

- Overall air quality rating (Excellent/Good/Fair/Inferior/Poor)
- Individual readings (PM2.5, PM10, CO2, VOC) shown as numeric values in detail
- Combined PM values also shown as the aggregate air quality rating

### Matter support

- Air quality sensors supported in Apple Home via Matter (iOS 18.4+)

---

## Air Purifier

**Service:** AirPurifier
**Required:** Active, CurrentAirPurifierState, TargetAirPurifierState
**Optional:** LockPhysicalControls, RotationSpeed, SwingMode

### States

| CurrentAirPurifierState | Value | Display |
|---|---|---|
| Inactive | 0 | **Inactive** |
| Idle | 1 | **Idle** |
| Purifying Air | 2 | **Purifying** |

| TargetAirPurifierState | Value |
|---|---|
| Manual | 0 |
| Auto | 1 |

### Detail view

- Active/Inactive toggle
- Speed control (if RotationSpeed present)
- Auto/Manual mode selector
- Linked FilterMaintenance service shows filter status

---

## Smoke Sensor

**Service:** SmokeSensor
**Required:** SmokeDetected (0=not detected, 1=detected)
**Optional:** StatusActive, StatusFault, StatusTampered, StatusLowBattery

### States displayed on tile

| SmokeDetected | Value | Display |
|---|---|---|
| Not detected | 0 | **Normal** / **Clear** |
| Detected | 1 | **Smoke Detected** |

### Notifications

- **CRITICAL NOTIFICATION** — bypasses Do Not Disturb, Focus modes, silent mode
- Notification includes type of danger (smoke) and location
- HomePod Sound Recognition can also detect smoke alarm sounds and send critical alerts

### Matter support

- Smoke detectors supported via Matter as of iOS 18.4

---

## Carbon Monoxide Sensor

**Service:** CarbonMonoxideSensor
**Required:** CarbonMonoxideDetected (0=normal, 1=abnormal)
**Optional:** StatusActive, StatusFault, StatusLowBattery, StatusTampered, CarbonMonoxideLevel (0-100 ppm), CarbonMonoxidePeakLevel (0-100 ppm)

### States

| CarbonMonoxideDetected | Value | Display |
|---|---|---|
| Levels normal | 0 | **Normal** |
| Levels abnormal | 1 | **CO Detected** |

### Notifications

- **CRITICAL NOTIFICATION** — bypasses Do Not Disturb
- Same critical alert behavior as smoke sensors

### Matter support

- CO detectors supported via Matter as of iOS 18.4

---

## Carbon Dioxide Sensor

**Service:** CarbonDioxideSensor
**Required:** CarbonDioxideDetected (0=normal, 1=abnormal)
**Optional:** StatusActive, StatusFault, StatusLowBattery, StatusTampered, CarbonDioxideLevel (0-10000 ppm), CarbonDioxidePeakLevel (0-10000 ppm)

### States

| CarbonDioxideDetected | Value | Display |
|---|---|---|
| Levels normal | 0 | **Normal** |
| Levels abnormal | 1 | **Abnormal** |

---

## Leak Sensor

**Service:** LeakSensor
**Required:** LeakDetected (0=not detected, 1=detected)
**Optional:** StatusActive, StatusFault, StatusTampered, StatusLowBattery

### States displayed on tile

| LeakDetected | Value | Display |
|---|---|---|
| Not detected | 0 | **No Leak** / **Normal** |
| Detected | 1 | **Leak Detected** |

### Notifications

- **CRITICAL NOTIFICATION** — bypasses Do Not Disturb, Focus modes, silent mode
- Breaks through all notification suppression
- Instant alert to iPhone and Apple Watch

### Matter support

- Water leak sensors supported via Matter as of iOS 18.4

---

## Security System

**Service:** SecuritySystem
**Required:** SecuritySystemCurrentState, SecuritySystemTargetState
**Optional:** StatusFault, StatusTampered, SecuritySystemAlarmType

### Current state

| SecuritySystemCurrentState | Value | Display |
|---|---|---|
| Stay Armed | 0 | **Home** |
| Away Armed | 1 | **Away** |
| Night Armed | 2 | **Night** |
| Disarmed | 3 | **Off** |
| Alarm Triggered | 4 | **Alarm Triggered** |

### Target state

| SecuritySystemTargetState | Value | Control label |
|---|---|---|
| Stay Arm | 0 | **Home** |
| Away Arm | 1 | **Away** |
| Night Arm | 2 | **Night** |
| Disarm | 3 | **Off** |

### Alarm type

| SecuritySystemAlarmType | Value |
|---|---|
| No alarm | 0 |
| Alarm | 1 |

### Notifications

- Notifies on arm/disarm state changes
- Alarm triggered state should send critical notification (implementation varies)

---

## Doorbell

**Service:** Doorbell (experimental in some implementations)
**Required:** ProgrammableSwitchEvent
**Optional:** Volume, Brightness

### Events

| ProgrammableSwitchEvent | Value | Action |
|---|---|---|
| Single Press | 0 | Doorbell ring |
| Double Press | 1 | (if supported) |
| Long Press | 2 | (if supported) |

### Notifications

- Push notification with optional camera snapshot
- Rich notification on iPhone/Apple Watch

---

## Stateless Programmable Switch

**Service:** StatelessProgrammableSwitch
**Required:** ProgrammableSwitchEvent

### Events

| ProgrammableSwitchEvent | Value | Apple Home action |
|---|---|---|
| Single Press | 0 | Trigger assigned scene |
| Double Press | 1 | Trigger assigned scene |
| Long Press | 2 | Trigger assigned scene |

### Behavior

- No visible on/off state — it is stateless
- Each press type can be assigned to trigger a different HomeKit scene
- Configuration done in accessory settings, not automations screen
- Up to 3 actions per physical button
- Can have multiple buttons via ServiceLabelIndex

---

## Humidifier / Dehumidifier

**Service:** HumidifierDehumidifier
**Required:** Active, CurrentHumidifierDehumidifierState, TargetHumidifierDehumidifierState, CurrentRelativeHumidity
**Optional:** LockPhysicalControls, RotationSpeed, RelativeHumidityHumidifierThreshold, RelativeHumidityDehumidifierThreshold, SwingMode, WaterLevel (0-100%)

### Current state

| CurrentHumidifierDehumidifierState | Value | Display |
|---|---|---|
| Inactive | 0 | **Inactive** |
| Idle | 1 | **Idle** |
| Humidifying | 2 | **Humidifying** |
| Dehumidifying | 3 | **Dehumidifying** |

### Target state

| TargetHumidifierDehumidifierState | Value |
|---|---|
| Humidifier or Dehumidifier (auto) | 0 |
| Humidifier | 1 |
| Dehumidifier | 2 |

### Water level

- WaterLevel (0-100%) is shown in detail view when supported
- Displayed as percentage in accessory detail

---

## Filter Maintenance

**Service:** FilterMaintenance
**Required:** FilterChangeIndication (0=OK, 1=change needed)
**Optional:** FilterLifeLevel (0-100%), ResetFilterIndication

### Display

- Usually linked to Air Purifier service
- FilterChangeIndication: binary indicator (filter OK vs needs change)
- FilterLifeLevel: percentage of filter life remaining
- Apple Home support for filter notifications is limited — more visible in third-party apps

---

## Battery Service

**Service:** BatteryService
**Required:** BatteryLevel (0-100%), ChargingState, StatusLowBattery

### Display

- Battery percentage with glyph icon
- Glyph highlights when low
- Charging state indicator
- Detail view shows charge status and trends
- Third-party app HomeBatteries provides enhanced battery tracking

### Charging states

| ChargingState | Value |
|---|---|
| Not Charging | 0 |
| Charging | 1 |
| Not Chargeable | 2 |

---

## Apple Home UI Behaviors

### What Apple Home DOES prominently display on tiles

- Primary state (locked/unlocked, open/closed, on/off, temperature values)
- "Not Responding" connectivity issues
- Running/Off for valves (Active + InUse matrix)
- Countdown timers for valve RemainingDuration
- Percentages for window coverings, brightness, fan speed
- Critical alerts for smoke/CO/leak (bypass DND)

### What Apple Home does NOT display on tiles (only in settings/detail)

- StatusFault (no "!" badge — third-party apps do show this)
- StatusTampered (hidden in settings)
- StatusActive (hidden in settings)
- Power consumption / energy monitoring (ignored entirely, needs Eve app)
- Custom vendor characteristics (Apple Home ignores all non-standard chars)

### What Apple Home CANNOT do with valves

- Cannot add valves to scenes
- Cannot add valves to automations
- Cannot create schedules for irrigation systems
- Timer/duration is display-only (accessory controls actual shutoff)

### Notifications summary by device type

| Device Type | Notifications | Critical (bypass DND) |
|---|---|---|
| Lock | Lock/Unlock, Jammed | No (varies) |
| Contact Sensor | Open/Closed | No |
| Motion Sensor | Motion Detected | No |
| Garage Door | Open/Closed, Obstructed | No (varies) |
| Smoke Sensor | Smoke Detected | **YES** |
| CO Sensor | CO Detected | **YES** |
| Leak Sensor | Leak Detected | **YES** |
| Security System | Armed/Disarmed, Alarm | Varies |
| Doorbell | Ring | No |
| Camera | Motion, Person, Vehicle, Animal, Package | No |

### Matter device types confirmed working in Apple Home (as of iOS 18.4+)

- Lights (on/off, dimmable, color, color temperature)
- Switches
- Outlets / plug-in units
- Locks
- Thermostats
- Window coverings / blinds / shades
- Fans
- Sensors: temperature, humidity, ambient light, motion, contact
- Smoke detectors (iOS 18.4)
- CO detectors (iOS 18.4)
- Water leak sensors (iOS 18.4)
- Bridges
- Air conditioners / heater-coolers
- Robot vacuums (iOS 18.4)

---

## Soda Dispenser Mapping

The soda machine has these states to represent:
1. **Currently dispensing** (flow active)
2. **Low on flavoring** (supply level)
3. **Which flavor selected** (1 or 2)
4. **Usage stats** (ounces dispensed)

### Analysis of each HomeKit/Matter device type for creative mapping

#### Option A: Valve (ValveType=3 "Water Faucet") -- BEST FIT for "dispensing" state

Pros:
- Active + InUse matrix maps perfectly to dispensing states:
  - Active=0, InUse=0 → "Off" (idle, not dispensing)
  - Active=1, InUse=0 → "Starting" (flow starting)
  - Active=1, InUse=1 → "Running" (actively dispensing)
  - Active=0, InUse=1 → "Stopping" (flow ending)
- RemainingDuration shows countdown timer (could show estimated pour time)
- SetDuration allows user to set pour amount/time
- StatusFault can indicate system errors
- Faucet icon is conceptually close to "dispensing liquid"

Cons:
- **Valves CANNOT be in scenes or automations** — huge limitation
- Cannot trigger "Hey Siri, pour me a drink" via automation
- No power consumption for tracking usage
- No concept of "which flavor" in a single valve

#### Option B: Irrigation System with 2 Valve zones — BEST FIT for "which flavor"

Pros:
- Two linked Valve services = Flavor 1 and Flavor 2
- Each valve shows Active/InUse independently
- ProgramMode could indicate: manual (user-selected) vs scheduled
- RemainingDuration per valve
- Conceptually: "zone 1 = flavor 1, zone 2 = flavor 2"

Cons:
- Same valve limitations (no scenes/automations)
- Sprinkler icon (ValveType=1) is less appropriate, but can use generic (0)
- ProgramMode values don't map cleanly to flavor selection

#### Option C: Contact Sensor — for "low on flavoring" alert

Pros:
- Binary state maps to: "Supply OK" (closed/0) vs "Low Flavoring" (open/1)
- Generates notification: "[Flavor 1] was opened" = "Flavor 1 is running low"
- Can be named "Flavor 1 Supply" and "Flavor 2 Supply"
- Participates in automations (trigger actions when supply goes low)
- Activity History tracks when supply went low

Cons:
- "Open/Closed" text is somewhat confusing for supply level
- No percentage level — just binary

#### Option D: Leak Sensor — for "low on flavoring" CRITICAL alert

Pros:
- **CRITICAL notification that bypasses Do Not Disturb**
- "Leak Detected" at "Flavor 1 Supply" = attention-grabbing low-supply alert
- Appropriate urgency level for "you're about to run out of flavoring"

Cons:
- "Leak Detected" text is misleading
- Might cause alarm/panic
- Probably too aggressive for a supply-level indicator

#### Option E: Switch or Outlet — for "which flavor selected"

Pros:
- Simple on/off maps to flavor toggle
- "Hey Siri, turn on flavor 2" / "turn off flavor 2"
- Can be added to scenes and automations
- Outlet's OutletInUse could indicate "currently dispensing"

Cons:
- On/Off for flavor selection requires 2 switches (one per flavor)
- Or 1 switch where on=flavor1, off=flavor2 (confusing)
- No dispensing state feedback beyond OutletInUse

#### Option F: Temperature Sensor — for usage stats (creative hack)

Pros:
- CurrentTemperature accepts -100 to 500, could represent ounces dispensed
- Shows as a number on tile (e.g., "24°F" = 24 ounces today)
- Can trigger automations at thresholds

Cons:
- Shows "°F" or "°C" suffix — misleading
- Not semantically correct
- Users would need to mentally map temperature to ounces

#### Option G: Humidity Sensor — for supply level percentage

Pros:
- 0-100% maps to supply level percentage
- Shows percentage on tile (e.g., "65%" = 65% flavoring remaining)
- Can trigger automations at thresholds

Cons:
- "Humidity" label is misleading
- No notification capability for low level

#### Option H: Light Sensor — for usage tracking

Pros:
- 0.0001-100000 lux range could represent pour count or ounces
- Numeric display on tile

Cons:
- Shows "lux" unit — misleading
- Poor semantic fit

### Recommended composite device mapping

For maximum Apple Home visibility with honest-ish mappings:

**1. Irrigation System (parent) + 2 Valve children**
- Zone 1 = "Flavor 1" (valve with Active/InUse for dispensing state)
- Zone 2 = "Flavor 2" (valve with Active/InUse for dispensing state)
- Active valve shows "Running" when dispensing
- RemainingDuration shows pour countdown
- ProgramMode indicates manual vs air-switch-selected

**2. Two Contact Sensors for supply levels**
- "Flavor 1 Supply" — Closed=OK, Open=Low
- "Flavor 2 Supply" — Closed=OK, Open=Low
- Notifications: "Flavor 1 Supply was opened" = time to refill
- Participates in automations

**3. Switch for flavor toggle (if voice control desired)**
- "Soda Flavor" — On=Flavor 1, Off=Flavor 2
- "Hey Siri, turn on the soda flavor" switches to flavor 1
- Can be part of scenes

**4. Battery Service for supply level percentage (on each valve)**
- BatteryLevel 0-100% for syrup supply level
- StatusLowBattery triggers when below threshold
- Low battery notification = "low supply" alert
- Apple Home shows battery percentage and low indicator

**Alternative for stats: vendor-specific Matter clusters**
- Custom clusters won't appear in Apple Home UI
- Would need mobile app (BLE) to display usage stats properly
- Apple Home is not designed for dashboards/counters

### Key takeaway

Apple Home is designed for state display (on/off, open/closed, temperature) and
event notifications (motion detected, leak detected, lock jammed). It is NOT designed
for counters, dashboards, or rich data display. Usage stats will need the mobile
app. The device type mapping should focus on what matters in Apple Home: current
dispensing state, flavor selection voice control, and supply-level alerts.
