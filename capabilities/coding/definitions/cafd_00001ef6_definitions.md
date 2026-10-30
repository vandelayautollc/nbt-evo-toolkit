# NBT EVO coding definitions — CAFD 00001EF6 (v006.048.013)

Human-readable description of every coding parameter in CAFD `00001EF6`: what each coordinate `(datagroup, byte, mask)` is, its settable values, the factory default, and an honest confidence rating. These are our own descriptions reconstructed from firmware tokens, enum tables, and traces (see [../04-definitions.md](../04-definitions.md)); they are not BMW data. Car-specific state has been removed.

**1481 parameters.** Confidence: `high` = corroborated; `med` = reasoned from one good source; `low` = genuinely reserved/undocumented (not a guess).

**210 are `source: firmware-trace`:** name, description and value labels written from the firmware itself (the code that reads the value, the unit's own value table, the files it loads). Where a firmware trace exists it is preferred over every other source.

## Datagroup 0x3000 (419 parameters)

### `3000/0/00000001b` — Undocumented field (SL01)  ·  _low_

Opaque SL-family feature bit with no descriptive suffix. BMW ships this name verbatim with no further documentation; purpose not determined from available sources.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `SL01`· source: firmware-token

### `3000/0/00000010b` — Spanish/ES market variant flag (SL02_ES)  ·  _med_

SL-family flag with suffix 'ES', indicating a Spanish or ES-market variant feature. Active when FA option 807 (Japanese version) is set — suggesting this flag enables certain ES-variant features even on Japan-spec vehicles. Token suffix 'ES' is the authoritative market designator from the firmware descriptor.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 807 Japanese version· token `SL02_ES`· source: firmware-token

### `3000/0/00000100b` — Cover Flow album browser (entertainment)  ·  _high_

Enables the Cover Flow album-art browsing mode in the entertainment system. Active when Professional navigation (609) is not fitted and the car is not the China country-control variant (8LH).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `01`· gate: NOT 609 Professional navigation system / 8LH Country control 04142· token `ENT_COVERFLOW`· source: firmware-token

### `3000/0/00001000b` — Cover Flow via USB  ·  _high_

Enables Cover Flow album-art browsing specifically for media played from a USB device. Companion bit to ENT_COVERFLOW; same FA gate (excludes 609 Professional nav and 8LH).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `01`· gate: NOT 609 Professional navigation system / 8LH Country control 04142· token `ENT_COVERFLOW_USB`· source: firmware-token

### `3000/0/00010000b` — Undocumented feature flag (SL05)  ·  _low_

Opaque SL-family bit with no descriptive suffix and only NICHT_AKTIV (not active) as its documented state. Purpose not determined from available sources.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SL05`· source: firmware-token

### `3000/0/00100000b` — Speed lock: owner's manual, part 1  ·  _med_

Locks part of the Integrated Owner's Manual while the car is moving; it is the first of three such locks. Rules on driver distraction vary by country.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: always (no FA gate)· token `SL06_IBA_1`· source: firmware-trace

### `3000/0/01000000b` — Speed lock: owner's manual, part 2  ·  _med_

Locks part of the Integrated Owner's Manual while the car is moving; it is the second of three such locks. Enabled at the factory for the Japanese, Australian, Canadian and Chinese versions (S807, S810, S838 or S8AA). Rules on driver distraction vary by country.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 807 Japanese version / 810 Australian version / 838 Canadian version / 8AA Chinese version / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93)· token `SL07_IBA_2`· source: firmware-trace

### `3000/0/10000000b` — Manual number entry (SL08_NUMMEREINGABE)  ·  _med_

Enables manual number/digit entry input mode in the HMI, typically for entering phone numbers or codes via the iDrive controller. Active for Japanese market (807).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 807 Japanese version· token `SL08_NUMMEREINGABE`· source: firmware-token

### `3000/1/00000001b` — Undocumented reserved bit (byte 1, bit 0)  ·  _low_

Purpose not determined from available sources. The firmware acknowledges this bit position (bare magic word in sysetshellevo) but ships no name string and no consumer reads it in the OMAP image.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

_Not in syset_fielddict; no name pointer; Neighbors: SL10/SL11/SL12/SL13/SL14/SL15/SL16_ADD_CEDEVICE._

default `00`· gate: FA-gated (depends on vehicle options)· source: firmware-trace

### `3000/1/00000010b` — Undocumented feature flag (SL10)  ·  _low_

Opaque SL-family bit, Purpose not determined from available sources.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SL10`· source: firmware-token

### `3000/1/00000100b` — Undocumented feature flag (SL11)  ·  _low_

Opaque SL-family bit, Purpose not determined from available sources.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SL11`· source: firmware-token

### `3000/1/00001000b` — Undocumented feature flag (SL12)  ·  _low_

Opaque SL-family bit, Purpose not determined from available sources.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SL12`· source: firmware-token

### `3000/1/00010000b` — Undocumented feature flag (SL13)  ·  _low_

Opaque SL-family bit, Purpose not determined from available sources.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SL13`· source: firmware-token

### `3000/1/00100000b` — Undocumented feature flag (SL14)  ·  _low_

Opaque SL-family bit, Purpose not determined from available sources.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SL14`· source: firmware-token

### `3000/1/01000000b` — Undocumented feature flag (SL15)  ·  _low_

Opaque SL-family bit, Purpose not determined from available sources.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SL15`· source: firmware-token

### `3000/1/10000000b` — Allow adding CE devices (SL16_ADD_CEDEVICE)  ·  _med_

SL-family flag enabling the option to add consumer-electronics (CE) devices such as additional Bluetooth or media accessories. Active for Japan, Australia, Canada, China markets, and certain vehicle type-key groups.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 807 Japanese version / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93)· token `SL16_ADD_CEDEVICE`· source: firmware-token

### `3000/2/00000111b` — Standstill rule for video  ·  _med_

Sets what counts as stopped before video can play on the central display: parking brake set, transmission in Park, both, or either. Rules on driver distraction vary by country.

| value | meaning |
|---|---|
| `0` | None |
| `1` | Parking brake set |
| `2` | Transmission in Park |
| `3` | Parking brake and Park |
| `4` | Parking brake or Park |

default `00`· gate: FA-gated (depends on vehicle options)· token `VIDEO_SPEEDLOCK_CONDITION`· source: firmware-token

### `3000/2/00001000b` — OPP (opportunistic) transfer (SL20_OPP_TRANSFER)  ·  _med_

SL-family flag enabling OPP (Object Push Profile / opportunistic Bluetooth) file transfer. Active for Japanese market (807) only.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | On/active (inferred) |

default `00`· gate: 807 Japanese version· token `SL20_OPP_TRANSFER`· source: firmware-token

### `3000/2/00010000b` — Speed lock: owner's manual, part 3  ·  _med_

Locks part of the Integrated Owner's Manual while the car is moving; it is the third of three such locks. Enabled at the factory for the Japanese, Australian, Canadian and Chinese versions (S807, S810, S838 or S8AA). Rules on driver distraction vary by country.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 807 Japanese version / 810 Australian version / 838 Canadian version / 8AA Chinese version / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93)· token `SL21_IBA_3`· source: firmware-trace

### `3000/2/00100000b` — Service history display  ·  _low_

Shows the service history on the central display: a list of the maintenance work carried out and recorded for the car.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: always (no FA gate)· token `SERVICE_HISTORY`· source: firmware-token

### `3000/2/01000000b` — Integrated Owner's Manual  ·  _high_

Turns on the Integrated Owner's Manual, the owner's handbook built into iDrive, including the context help that opens the matching page from other menus and messages.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: always (no FA gate)· token `IBA`· source: firmware-trace

### `3000/2/10000000b` — Auxiliary head-unit media connection (CDMM AUX)  ·  _med_

Enables an auxiliary media connection (AUX-in) routed through the CDMM (CD/Media Module). When active, an external audio source can be connected to the head unit.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: always (no FA gate)· token `CDMM_AUX_HU`· source: firmware-token

### `3000/3/11111111b` — Media metadata generation  ·  _low_

Setting for generating track details (metadata) in the media player.

| value | meaning |
|---|---|
| `0` | Disabled |

default `0000`· gate: FA-gated (depends on vehicle options)· token `ENT_GEN_META_DATA`· source: firmware-token

### `3000/5/00000001b` — Compass display  ·  _high_

Enables a compass bearing display in the instrument cluster or head-unit status bar.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `COMPASS`· source: firmware-token

### `3000/5/00000010b` — Head-unit optical drive cover enabled  ·  _med_

Enables the drive slot/cover UI for the head-unit's built-in optical drive. Active by default; disabled for the 8LH China country-control variant (which lacks the drive).

| value | meaning |
|---|---|
| `0` | Off (no drive/cover shown) |
| `1` | On (drive cover shown) |

default `01`· gate: NOT 8LH Country control 04142· token `ENT_HU_DRIVE_COVER`· source: firmware-token

### `3000/5/00000100b` — Video only with parking brake set  ·  _med_

Allows video on the central display only while the parking brake is set. Enabled at the factory for the Australian version (S810), the Great Britain and Ireland version (S812) and the Canadian version (S838). Rules on driver distraction vary by country.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 810 Australian version / 812 Great Britain/Ireland version / 838 Canadian version / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93)· token `VIDEO_HANDBRAKE`· source: firmware-token

### `3000/5/00001000b` — Wind speed display (drive information)  ·  _med_

Enables the wind speed readout in the head-unit drive information / efficiency display. Variant 1 = one display layout, Variant 2 = alternate layout.

| value | meaning |
|---|---|
| `0` | Variant 1 |
| `1` | Variant 2 |

default `00`· gate: always (no FA gate)· token `ENT_HU_DRIVE_WIND_SPEED`· source: firmware-token

### `3000/5/00010000b` — Video lock: central display  ·  _med_

Locks video playback on the central display up front. Enabled at the factory for some markets (S8LH). Rules on driver distraction vary by country.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 8LH Country control 04142· token `VIDEO_FRONT_LOCKED`· source: firmware-token

### `3000/5/11100000b` — Rear-seat entertainment extended options  ·  _med_

3-bit field selecting extended RSE (Rear-Seat Entertainment) option variants for special equipment configurations.

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_RSE_EXT_OPTIONS`· source: firmware-token

### `3000/6/00000001b` — Text-to-speech (TTS / TTS Nuance) app enable  ·  _high_

SWT 'application coded' enable bit that gates whether the text-to-speech (TTS and TTS Nuance) speech synthesis component is active. Firmware-traced: queried in FUN_002f58c4 switch cases 5 (TTS) and 0xD (TTS Nuance). Requires Business nav (606) or Professional nav (609) or MFL (249).

| value | meaning |
|---|---|
| `0` | TTS disabled |
| `1` | TTS enabled |

_Token SWT_APP_TTS; decoded by FUN_00334984; switch cases 5 and 0xD in FUN_002f58c4._

default `00`· gate: 606 Navigation system Business / 609 Professional navigation system / 249 Multifunction for steering wheel / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `SWT_APP_TTS`· source: firmware-trace

### `3000/6/00000010b` — CD/DVD changer installed  ·  _high_

Declares that an external CD/DVD changer (6-disc, SA 696) is physically connected to the head unit. Enables changer-related UI and media source switching.

| value | meaning |
|---|---|
| `0` | Not installed |
| `1` | Installed |

default `00`· gate: 696 DVD changer for 6 DVDs· token `ENT_CHANGER_INSTALLED`· source: firmware-token

### `3000/6/00000100b` — CD/DVD changer cover UI  ·  _med_

Enables the UI element (cover/slot graphic) for an external CD/DVD changer. allowing the changer interface to be shown even if no changer is connected.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `ENT_CHANGER_COVER`· source: firmware-token

### `3000/6/00001000b` — Personal Radio (Online Entertainment)  ·  _med_

Shows Personal Radio in the media menu, a streaming radio feature of BMW Online Entertainment. Using it needs the Online Entertainment service and a data connection.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_PERSONALRADIO`· source: firmware-trace

### `3000/6/00010000b` — Multichannel audio (surround sound)  ·  _med_

Enables multichannel/surround audio processing in the entertainment system.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_MULTICHANNEL`· source: firmware-token

### `3000/6/00100000b` — OE login / service-level access  ·  _med_

Enables OE (Original Equipment) login or service-level coding access for authorised dealers/tools. Controls whether the service login entry point is shown in the HMI.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `OE_LOGIN_SL`· source: firmware-token

### `3000/6/01000000b` — Video playback  ·  _med_

Turns on video playback in the media menu. Video while driving follows the head unit's speed-lock rules, and rules on driver distraction vary by country.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: NOT 609 Professional navigation system / 8LH Country control 04142· token `ENT_VIDEO`· source: firmware-token

### `3000/6/10000000b` — Miracast screen mirroring  ·  _high_

Enables Wi-Fi Miracast wireless screen mirroring from a compatible Android device to the head-unit display.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_MIRACAST`· source: firmware-token

### `3000/7/11111111b` — DVD region code  ·  _high_

Sets the DVD region code for the built-in optical drive. Determines which geographic region's DVDs can be played.

| value | meaning |
|---|---|
| `0` | All regions (region-free) |
| `1` | Region 1 (USA, Canada) |
| `2` | Region 2 (Europe, Japan, Middle East) |
| `3` | Region 3 (Southeast Asia) |
| `4` | Region 4 (Latin America, Australia) |
| `5` | Region 5 (Russia, Africa, India) |
| `6` | Region 6 (China) |

default `00`· token `ENT_VIDEO_DVD_AREA_CODE`· source: firmware-token

### `3000/8/11111111b` — Blu-ray region code  ·  _high_

Sets the Blu-ray region code for the head-unit's optical drive. Determines which geographic region's Blu-ray discs can be played.

| value | meaning |
|---|---|
| `0` | All regions (region-free) |
| `1` | Region A (Americas, Japan, Southeast Asia) |
| `2` | Region B (Europe, Africa, Middle East, Australia) |
| `3` | Region C (China, Russia, India) |

default `00`· token `ENT_VIDEO_BLUERAYD_AREA_CODE`· source: firmware-token

### `3000/9/00000001b` — WLAN/DLNA media server cover art  ·  _med_

Enables album cover art display when streaming audio from a WLAN DLNA media server (DMP = Digital Media Player).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_MC_WLAN_STREAM_DMP_COVERART`· source: firmware-token

### `3000/9/00000010b` — WLAN/DLNA video streaming  ·  _med_

Enables video playback from a WLAN DLNA media server (DMP) on the head-unit display.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | On/active (inferred) |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_MC_WLAN_STREAM_DMP_VIDEO`· source: firmware-token

### `3000/9/00000100b` — Bluetooth/iPod cover art (BTAS/iAP)  ·  _med_

Enables album cover art display for music played via Bluetooth Audio Streaming (BTAS) or Apple iAP (iPod Accessory Protocol).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `ENT_BTAS_IAP_COVERART`· source: firmware-token

### `3000/9/00001000b` — TV electronic programme guide (EPG) presentation  ·  _med_

Sets the scope/mode of the TV Electronic Programme Guide display. Standard mode vs. Advanced/extended mode.

| value | meaning |
|---|---|
| `0` | Standard |
| `1` | Advanced |

default `00`· gate: FA-gated (depends on vehicle options)· token `CDMM_TV_EPG_PRES_SCOPE`· source: firmware-token

### `3000/9/00010000b` — Cover Flow for Professional navigation  ·  _high_

Enables the Cover Flow album-art browser specifically for vehicles with Professional navigation (609). Companion to ENT_COVERFLOW, active when 609 is fitted.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `01`· gate: 609 Professional navigation system· token `ENT_COVERFLOW_ES`· source: firmware-token

### `3000/9/00100000b` — Cover Flow vertical scroll  ·  _med_

Enables vertical scrolling mode for the Cover Flow album browser (as opposed to horizontal/coverflow swipe). Active by default.

| value | meaning |
|---|---|
| `0` | Off (horizontal only) |
| `1` | On (vertical scroll enabled) |

default `01`· token `ENT_COVERFLOW_VERTICAL`· source: firmware-token

### `3000/9/11000000b` — RSE optical drive type  ·  _med_

Specifies the optical drive type fitted in the rear-seat entertainment (RSE) system.

| value | meaning |
|---|---|
| `1` | DVD drive |
| `2` | Blu-ray drive |

default `01`· gate: FA-gated (depends on vehicle options)· token `ENT_RSE_DRIVE`· source: firmware-token

### `3000/10/00000011b` — Head-unit optical drive type  ·  _high_

Specifies the type of optical drive fitted in the head unit itself.

| value | meaning |
|---|---|
| `1` | CD drive |
| `2` | DVD drive |
| `3` | Blu-ray drive |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_HU_DRIVE`· source: firmware-token

### `3000/10/00000100b` — Video HMI mode  ·  _med_

Controls the HMI presentation mode for the video player: either the standard DVD-style on-screen interface or a track/title list view.

| value | meaning |
|---|---|
| `0` | DVD on-screen menu style |
| `1` | Title list view |

default `00`· gate: always (no FA gate)· token `ENT_VIDEO_HMI`· source: firmware-token

### `3000/10/00001000b` — Online Entertainment  ·  _med_

Turns on Online Entertainment, BMW's in-car music streaming service, in the media menu. Using it needs an active service and a data connection.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `OE_ENABLED`· source: firmware-trace

### `3000/10/00010000b` — OE rear-seat entertainment features enabled  ·  _med_

Enable flag for OE (dealer) rear-seat entertainment feature extensions.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `OE_RSE_ENABLED`· source: firmware-token

### `3000/10/00100000b` — Instantaneous fuel consumption display  ·  _high_

Enables the real-time (instantaneous) fuel consumption readout in the vehicle information / efficiency display on the head unit.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· token `MOMENTANVERBRAUCHSANZEIGE`· source: firmware-token

### `3000/10/11000000b` — Speed lock: connected app text lists  ·  _high_

Sets how many lines a long text list in a connected app (one whose screens come from a phone or an online service) can show on the central display while the car is moving, for apps that don't set their own limit. Rules on driver distraction vary by country.

| value | meaning |
|---|---|
| `1` | Up to 9 lines while moving |
| `2` | Up to 3 lines while moving |

default `01`· token `RHMI_LIST_SPEEDLOCK_LEVEL`· source: firmware-trace

### `3000/11/00000001b` — Charging power reduction (HU)  ·  _med_

Enables head-unit-managed reduction of battery charging power, typically for plug-in hybrid/EV charge management.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `CHARGING_POWER_REDUCTION_HU`· source: firmware-token

### `3000/11/00000110b` — Speech-to-text speller input level  ·  _med_

Configures which speech-to-text (STT) speller input confidence levels are made available to the user. Higher = more input options; Hoch+Mittel+Gering = high+medium+low confidence inputs.

| value | meaning |
|---|---|
| `1` | High only |
| `2` | High and medium |
| `3` | High, medium, and low |

default `00`· gate: FA-gated (depends on vehicle options)· token `STT_SPELLER_INPUT`· source: firmware-token

### `3000/11/00011000b` — AdBlue range display  ·  _high_

Shows the AdBlue (diesel exhaust fluid) status in “Vehicle status” on diesel models with selective catalytic reduction (SCR) and sets the highest remaining range it shows as a number. Above that limit it shows the limit with a “>” sign. With miles as the display unit, the limits are 6,000 and 4,500 mi.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Up to 10000 km |
| `2` | Up to 7000 km |
| `3` | No limit |

default `00`· token `SCR_ANZEIGE`· source: firmware-trace

### `3000/11/00100000b` — Automatic unlock after journey end  ·  _high_

Enables automatic unlocking of the vehicle doors when the ignition is turned off and the journey ends.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENTRIEGELN_NACH_FAHRTENDE`· source: firmware-token

### `3000/11/01000000b` — Goodbye screen: hide non-transmission-capable info  ·  _med_

When enabled, the goodbye/farewell screen suppresses information that cannot be transmitted (Nichtsendefaehigkeit) — i.e. content that requires connectivity not available at shutdown.

| value | meaning |
|---|---|
| `0` | Off (show all goodbye info) |
| `1` | On (suppress non-transmittable info) |

default `00`· gate: FA-gated (depends on vehicle options)· token `HMI_GOODBYE_NICHTSENDEFAEHIGKEIT`· source: firmware-token

### `3000/11/10000000b` — AC fast charging  ·  _med_

Enables AC fast charging capability declaration in the HMI (for plug-in hybrid/EV).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `AC_LADEN_SCHNELL`· source: firmware-token

### `3000/12/00000001b` — Weekly departure timer  ·  _high_

Enables the weekly repeating departure timer for pre-conditioning (climate/charge).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `WEEKLY_TIMER`· source: firmware-token

### `3000/12/00000010b` — Climate departure timer  ·  _high_

Enables the one-shot or weekly departure timer for pre-conditioning the vehicle climate before driving.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `CLIMATE_DEPARTURE`· source: firmware-token

### `3000/12/00000100b` — DAC2 configuration  ·  _low_

Configuration setting for the DAC vehicle function in the head unit's car menus. Best left unchanged.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `DAC2_KONFIGURATION`· source: firmware-trace

### `3000/12/00001000b` — NFC Bluetooth pairing speed-lock  ·  _med_

When enabled, NFC-triggered Bluetooth device pairing is restricted to when the vehicle is stationary (speed-locked).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `NFC_BT_PAIRING_SPEEDLOCK`· source: firmware-token

### `3000/12/00010000b` — NFC beam speed-lock  ·  _med_

When enabled, NFC beam (data transfer via NFC tap) is restricted to when the vehicle is stationary.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active (NFC beam locked at speed) |

default `00`· gate: FA-gated (depends on vehicle options)· token `NFC_BEAM_SPEEDLOCK`· source: firmware-token

### `3000/12/00100000b` — Fader front/rear balance setting  ·  _high_

Enables the front/rear audio fader adjustment in the sound settings menu.

| value | meaning |
|---|---|
| `0` | Off (fader not shown) |
| `1` | On (fader control available) |

default `00`· gate: always (no FA gate)· token `FADER_EINSTELLUNG`· source: firmware-token

### `3000/12/11000000b` — Gracenote album info features  ·  _med_

Chooses which Gracenote album information features the media options offer: the album information screen, which shows Gracenote details for an album, and the online lookup that updates those details from the Gracenote service. The online lookup is reached from the album information screen.

| value | meaning |
|---|---|
| `0` | None |
| `1` | Online lookup |
| `2` | Album info screen |
| `3` | Album info and online lookup |

Bits (set = on): bit 0 Online lookup; bit 1 Album info screen

default `00`· token `ENT_GRACENOTE_ACCESS`· source: firmware-trace

### `3000/13/00000001b` — Media Centre active  ·  _high_

Enables the Media Centre (internal hard-disk music library / ripped CD storage) feature. Requires Professional navigation (609).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 609 Professional navigation system· token `ENT_MC_ACTIV`· source: firmware-token

### `3000/13/00000010b` — Media Centre album art cover display  ·  _med_

Enables album cover art display in the Media Centre (internal HDD library) browser. Active when Professional navigation (609) is NOT fitted.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: NOT 609 Professional navigation system / 8LH Country control 04142· token `ENT_MC_COVER`· source: firmware-token

### `3000/13/00000100b` — Media Centre video support  ·  _med_

Enables video file storage and playback from the Media Centre internal hard drive.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_MC_VIDEO_SUPPORT`· source: firmware-token

### `3000/13/00001000b` — Media Centre playlist import  ·  _med_

Enables importing of playlists (e.g. M3U files from USB) into the Media Centre internal library.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_MC_PLAYLIST_IMPORT`· source: firmware-token

### `3000/13/00010000b` — Media Centre Asia character input  ·  _med_

Enables Asian character set input (CJK) for Media Centre music search.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_MC_ASIA_INPUT`· source: firmware-token

### `3000/13/00100000b` — Media Centre auto-rip (CD to HDD)  ·  _high_

Enables automatic ripping of inserted audio CDs to the Media Centre internal hard drive.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_MC_AUTO_RIP_IMPORT`· source: firmware-token

### `3000/13/01000000b` — Media Centre auto backup/restore  ·  _med_

Enables automatic backup and restore of the Media Centre (HDD music library) to/from an external source.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_MC_AUTO_BACKUPRESTORE`· source: firmware-token

### `3000/13/10000000b` — Media Centre WLAN/DLNA streaming  ·  _med_

Enables streaming audio from a WLAN DLNA media server (DMP) directly into the Media Centre.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_MC_WLAN_STREAM_DMP`· source: firmware-token

### `3000/14/00000001b` — Web server for online services  ·  _med_

Turns on the head unit's built-in web server, which BMW's online services use to show their content on the central display. Enabled at the factory with BMW Live (S6AL) or TeleServices (S6AE).

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 6AL BMW live / 6AE TeleServices· token `IPCE_WEBSERVER`· source: firmware-trace

### `3000/14/00000010b` — Media Centre: allow deleting music search index  ·  _med_

Enables the user option to delete the music search/metadata index in the Media Centre.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `ENT_MC_DELETE_MUSICSEARCH`· source: firmware-token

### `3000/14/00000100b` — Media Centre song bookmarks  ·  _med_

Enables the ability to bookmark individual songs/tracks in the Media Centre library.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_MC_SONG_BOOKMARKS`· source: firmware-token

### `3000/14/00001000b` — Media Centre time-shift recording  ·  _med_

Enables time-shift recording (pause/rewind live media) in the Media Centre.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_MC_TIMESHIFT_REC`· source: firmware-token

### `3000/14/00010000b` — Music collection: driver profile link  ·  _low_

Setting that links the music collection with the driver profiles, the personal settings the head unit keeps for each key. Best left unchanged.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_MC_PIA`· source: firmware-trace

### `3000/14/00100000b` — Media Centre album art scale/fit  ·  _med_

Enables scaled/fitted display of album cover art in the Media Centre (filling the display rather than displaying at native size).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_MC_COVER_SCALE`· source: firmware-token

### `3000/14/01000000b` — Gracenote database installed  ·  _high_

Declares that the Gracenote music recognition database is installed on the head unit (on internal storage).

| value | meaning |
|---|---|
| `0` | Not installed |
| `1` | Installed |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_GRACENOTE_INSTALLED`· source: firmware-token

### `3000/14/10000000b` — Gesture control  ·  _high_

Turns on gesture control for cars with the gesture camera: hand movements in front of the central display can change the volume, accept or reject calls and more.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `GESTURE_CAMERA`· source: firmware-trace

### `3000/15/00000001b` — X-View 3D camera view  ·  _med_

Enables the X-View (360-degree / 3D surround camera view) feature on the head-unit display.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `X_VIEW`· source: firmware-token

### `3000/15/00000010b` — Gracenote database via USB  ·  _high_

Enables loading/updating the Gracenote music database from a USB drive.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_GRACENOTE_USB`· source: firmware-token

### `3000/15/00000100b` — Gracenote music lookup (MLT / over-the-air)  ·  _med_

Enables Gracenote MLT (Music Label Tagging / online music recognition lookup) for identifying and tagging music.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: always (no FA gate)· token `ENT_GRACENOTE_MLT`· source: firmware-token

### `3000/15/00001000b` — Gracenote music service  ·  _high_

Enables the Gracenote music metadata service (artist/album/track tag lookup) in the entertainment system.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `ENT_GRACENOTE_SERVICE`· source: firmware-token

### `3000/15/00010000b` — Ogg audio playback  ·  _med_

Lets the head unit play Ogg audio files, such as Ogg Vorbis music, from connected media.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_CODEC_OGG`· source: firmware-token

### `3000/15/00100000b` — Xvid video playback  ·  _med_

Lets the head unit play video files encoded with Xvid, a common MPEG-4 video format.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_CODEC_XVID`· source: firmware-token

### `3000/15/01000000b` — Video CD playback  ·  _med_

Lets the head unit play Video CDs (VCD), an older disc format for movies and music videos.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_CODEC_VCD`· source: firmware-token

### `3000/15/10000000b` — MLS/MI language switching mode  ·  _med_

Enables or configures the MLS (Multi-Language Support) / MI (Market Interface) language and interface mode switch.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `01`· gate: always (no FA gate)· token `SWITCH_MLS_MI`· source: firmware-token

### `3000/16/00000001b` — Navigation in cluster: AR presentation  ·  _low_

Setting for how the navigation map is presented in the instrument cluster (AR presentation). Best left unchanged.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `KOMBI_AR_PRES`· source: firmware-trace

### `3000/16/00000010b` — Satellite radio module generation (SDARS)  ·  _med_

Specifies the generation of the SDARS (Satellite Digital Audio Radio Service, e.g. SiriusXM) module.

| value | meaning |
|---|---|
| `0` | Generation 4/5 |
| `1` | X65 module |

default `01`· gate: FA-gated (depends on vehicle options)· token `SDARS_MODUL`· source: firmware-token

### `3000/16/00000100b` — HDMI/MHL AUX video input  ·  _high_

Enables an HDMI or MHL (Mobile High-Definition Link) auxiliary video input port connection to the head unit.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `HDMI_MHL_AUX_IN`· source: firmware-token

### `3000/16/00001000b` — Distance unit setting in vehicle info  ·  _med_

Enables the distance unit (km/miles) selector in the vehicle information / settings display.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `SETTINGS_INFO_DISPLAY_DISTANCE`· source: firmware-token

### `3000/16/00010000b` — High-capacity oil quantity (3L) display  ·  _med_

Enables display logic for vehicles with a high-capacity engine oil reservoir (e.g. 3-litre / large engine oil quantities).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `OIL_QUANTITY_HIGH`· source: firmware-token

### `3000/16/00100000b` — Date display in vehicle info  ·  _med_

Enables the current date readout in the vehicle information / settings display.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: always (no FA gate)· token `SETTINGS_INFO_DISPLAY_DATE`· source: firmware-token

### `3000/16/01000000b` — NFC status display  ·  _med_

Enables display of the NFC (Near-Field Communication) module status in the settings/connectivity menu.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `NFC_STATUS`· source: firmware-token

### `3000/16/10000000b` — iDrive controller (ZBE) new hard-key layout  ·  _high_

Enables the newer iDrive controller (ZBE) hard-key button layout. Required when a newer ZBE controller with a revised button arrangement is fitted (e.g. with touch surface or revised media buttons). Active when TV function (601), Business nav (606), or Professional nav (609) is fitted.

| value | meaning |
|---|---|
| `0` | Old hard-key layout |
| `1` | New hard-key layout |

default `00`· gate: 601 TV Function / 606 Navigation system Business / 609 Professional navigation system· token `ZBE_HARDKEY_LAYOUT_NEW`· source: firmware-token

### `3000/17/00000001b` — Steering wheel buttons: MINI skip variant  ·  _med_

Enables the MINI-variant skip/seek button mapping for the MFL (Multi-Function steering wheel / Lenkrad) buttons. not MINI).

| value | meaning |
|---|---|
| `0` | Off (standard skip) |
| `1` | On (MINI skip variant) |

default `00`· gate: FA-gated (depends on vehicle options)· token `MFL_SKIP_MINI`· source: firmware-token

### `3000/17/00000010b` — Speaker lighting  ·  _med_

Shows the setting for the illuminated speaker covers installed with some high-end sound systems, such as Bang & Olufsen.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `LAUTSPRECHERBELEUCHTUNG`· source: firmware-trace

### `3000/17/00000100b` — Navigation: EV import  ·  _low_

Setting for the navigation system's electric-vehicle data, used in its energy consumption calculations. Best left unchanged.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: always (no FA gate)· token `EV_IMPORT`· source: firmware-trace

### `3000/17/00001000b` — Front armrest control panel  ·  _high_

Enables the front centre armrest control panel (touch/button controls in the armrest).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `ARMREST_FRONT_CONTROL`· source: firmware-token

### `3000/17/00110000b` — Entertainment list index mode  ·  _med_

Selects how the entertainment list browser indexes and displays entries: no index, read-only mode, or read/write mode.

| value | meaning |
|---|---|
| `0` | No index |
| `1` | Reading data (read-only index) |
| `2` | Writing data (read/write index) |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_INDEX_LIST`· source: firmware-token

### `3000/17/01000000b` — Light carpet  ·  _med_

Shows the light carpet setting in the exterior lighting menu. The light carpet lights up the ground beside the doors when you unlock the car or open a door.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `LIGHT_CARPET`· source: firmware-trace

### `3000/17/10000000b` — Door handle lighting  ·  _med_

Offers the door handle lighting setting in the exterior lighting menu, for cars with illuminated door handles.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `DOOR_HANDLE_LIGHTS`· source: firmware-trace

### `3000/18/00000011b` — Ambient light colour switch ensemble  ·  _med_

Selects the variant of the ambient light colour-switch button/ensemble in the interior. Controls whether the ambient lighting colour controls are in the default layout, colour switch, or colour switch with panoramic roof.

| value | meaning |
|---|---|
| `1` | Default |
| `2` | Colour switch |
| `3` | Colour switch with panoramic roof |

default `01`· gate: always (no FA gate)· token `BENENNUNG_COLOUR_SWITCH_ENSEMBLE`· source: firmware-token

### `3000/18/00000100b` — Ambient light deactivation: follow interior lighting  ·  _med_

Controls whether the ambient lighting (Ambilight) deactivation option is in default mode or coupled to the interior lighting. When set to Interior lighting (1), the ambilight turns off and on together with the interior room lighting.

| value | meaning |
|---|---|
| `0` | Default (ambient light behavior not coupled to interior lighting) |
| `1` | Interior lighting (ambient light follows interior lighting on/off) |

default `00`· gate: always (no FA gate)· token `BENENNUNG_DEAKTIVIERUNGSMOEGLICHKEIT_AMBILIGHT`· source: firmware-token

### `3000/18/00001000b` — Captain's chair seating  ·  _high_

Declares that the vehicle has captain's chair rear seating (individual rear bucket seats rather than a bench). Adjusts applicable HMI seat control menus.

| value | meaning |
|---|---|
| `0` | Off (bench/standard rear seating) |
| `1` | On (captain's chairs fitted) |

default `00`· gate: FA-gated (depends on vehicle options)· token `CAPTAINCHAIR`· source: firmware-token

### `3000/18/00010000b` — Seat multi-function controls  ·  _med_

Enables the seat multi-function control menu (e.g. massage, memory, ventilation combined control).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `SEAT_MULTIFUNCTION`· source: firmware-token

### `3000/18/00100000b` — Comfort exit seat adjustment  ·  _med_

Enables the comfort exit feature — when a door is opened, the seat slides back to ease exit. Shows a checkbox in the HMI settings.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `HMI_CHECKBOX_COMFORT_EXIT`· source: firmware-token

### `3000/18/01000000b` — Seat auto-climate  ·  _high_

Enables automatic seat climate control (heated/ventilated seat that adjusts automatically based on cabin conditions).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `SEAT_AUTO_CLIMATE`· source: firmware-token

### `3000/18/10000000b` — Rear seat ventilation  ·  _high_

Enables rear seat ventilation control in the HMI.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `SEAT_VENTILATION_REAR`· source: firmware-token

### `3000/19/00000001b` — Fragrance ioniser  ·  _high_

Enables the interior fragrance/ioniser system control in the HMI (e.g. BMW ambient air fragrance diffuser).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `DUFT_IONISATOR`· source: firmware-token

### `3000/19/00000110b` — Automatic time synchronisation source  ·  _high_

Selects whether the head-unit clock is synchronised automatically, and from which source (offline/not active, online ConnectedDrive, or GPS navigation).

| value | meaning |
|---|---|
| `0` | Not active (manual time) |
| `1` | Online (ConnectedDrive sync) |
| `2` | Navigation (GPS sync) |

default `00`· gate: FA-gated (depends on vehicle options)· token `SETTINGS_TIME_AUTOMATIC`· source: firmware-token

### `3000/19/00001000b` — Automatic window close in rain  ·  _high_

Enables the feature that automatically closes windows/convertible roof when rain is detected.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `REGEN_SCHLIESSEN`· source: firmware-token

### `3000/19/00010000b` — Always open HMI (bypass speed-lock)  ·  _med_

Forces the HMI to remain open/accessible at all times regardless of speed-lock rules.

| value | meaning |
|---|---|
| `0` | Off (speed-lock applies normally) |
| `1` | On (HMI always open) |

default `00`· gate: FA-gated (depends on vehicle options)· token `ALWAYS_OPEN_HMI`· source: firmware-token

### `3000/19/00100000b` — MINI colour switch setting  ·  _med_

Enables the MINI-variant interior colour selector setting in the HMI. not MINI).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `SETTINGS_COLOUR_SWITCH_MINI`· source: firmware-token

### `3000/19/01000000b` — Smartphone apps: XL layout  ·  _med_

Tells connected smartphone apps that they can use the XL (large-format) layout, so supported apps fill more of the central display.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `A4A_XL`· source: firmware-trace

### `3000/19/10000000b` — Smartphone apps: map content  ·  _med_

Tells connected smartphone apps that the head unit can show their map content, so supported apps can offer maps on the central display. Takes effect only when “Central display type” (`3001/57/11111111b`) is the wide display or the display with cover flap.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: NOT 606 Navigation system Business / 609 Professional navigation system / 6NR Apps / 6VB Infotainment control / 6AE TeleServices· token `A4A_KML`· source: firmware-trace

### `3000/20/00000001b` — Smartphone apps: profiles (PIA)  ·  _low_

Tells connected smartphone apps whether the head unit offers PIA, its personal profile feature, so supported apps can use it. Enabled at the factory with Apps (S6NR) or TeleServices (S6AE). Best left unchanged.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 6NR Apps / 6AE TeleServices· token `A4A_PIA`· source: firmware-trace

### `3000/20/00011110b` — Maximum navigation range display  ·  _med_

4-bit numeric field selecting the maximum displayed range value in the EV / hybrid range indicator. encoded as a step index, not a direct km value.

default `03`· gate: FA-gated (depends on vehicle options)· token `RANGE_MAX`· source: firmware-token

### `3000/20/11100000b` — USB ports installed  ·  _med_

Tells the head unit which USB ports the car has and whether a snap-in adapter (phone cradle) is connected, so the matching media sources appear. Check only what the car has.

| value | meaning |
|---|---|
| `0` | None |
| `1` | USB port 1 |
| `2` | Snap-in adapter |
| `3` | USB port 1 and snap-in adapter |
| `4` | USB port 2 |
| `5` | USB ports 1 and 2 |
| `6` | USB port 2 and snap-in adapter |
| `7` | USB 1, USB 2 and snap-in adapter |

Bits (set = on): bit 0 USB port 1; bit 1 Snap-in adapter; bit 2 USB port 2

default `00`· token `CDMM_USB_PORTS`· source: firmware-trace

### `3000/21/00000001b` — HMI generation version  ·  _high_

Selects the iDrive HMI generation: ID4++ (iDrive 4 enhanced, older NBT Evo interface) or ID5 (iDrive 5 style, newer interface with tile/widget home screen).

| value | meaning |
|---|---|
| `0` | iDrive 4++ (ID4++) |
| `1` | iDrive 5 (ID5) |

default `00`· token `HMI_VERSION`· source: firmware-token

### `3000/21/00000010b` — Japanese music search reading (kana/romaji)  ·  _high_

Enables the Japanese phonetic reading (kana or romaji) input mode for music search in the entertainment system. Active for Japanese market (807).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 807 Japanese version· token `ENT_JAPAN_SEARCH_READING`· source: firmware-token

### `3000/21/00000100b` — Japanese speller input variant  ·  _high_

Selects the Japanese speller keyboard variant (with or without phonetic mapping for kana input). Active for Japanese market (807).

| value | meaning |
|---|---|
| `0` | Speller without phonetic mapping |
| `1` | Speller with phonetic mapping |

default `00`· gate: 807 Japanese version· token `ENT_JAPAN_SPELLER_VARIANT`· source: firmware-token

### `3000/21/00001000b` — Taiwan music search reading (zhuyin/pinyin)  ·  _high_

Enables the Taiwan phonetic reading input mode for music search. Active for Taiwan country-control (8LT) variant.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 8LT Country control 04825 · token `ENT_TAIWAN_SEARCH_READING`· source: firmware-token

### `3000/21/00010000b` — Taiwan speller input variant  ·  _high_

Selects the Taiwan speller keyboard variant (with or without phonetic mapping for zhuyin/bopomofo input). Active for Taiwan country-control (8LT) variant.

| value | meaning |
|---|---|
| `0` | Speller without phonetic mapping |
| `1` | Speller with phonetic mapping |

default `00`· gate: 8LT Country control 04825 · token `ENT_TAIWAN_SPELLER_VARIANT`· source: firmware-token

### `3000/21/01100000b` — Bowers & Wilkins high-end audio system menu  ·  _high_

Selects the B&W (Bowers & Wilkins) high-end audio system's light staging / 'Surround Sound Experience' presentation mode shown in the HMI. Controls whether a menu is shown and what level of ambient light staging accompanies the audio.

| value | meaning |
|---|---|
| `0` | No menu shown |
| `1` | Menu shown, no light staging |
| `2` | Menu shown, light staging only |
| `3` | Menu shown, full staging (light + surround) |

default `00`· gate: always (no FA gate)· token `HIGH_END_AUDIO_B_UND_W`· source: firmware-token

### `3000/21/10000000b` — John Cooper Works HMI theme  ·  _high_

Enables the John Cooper Works (JCW) branded HMI theme/graphics for MINI JCW models. not MINI JCW).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `JOHN_COOPER_WORKS_HMI`· source: firmware-token

### `3000/22/00000001b` — eDrive popup suppression  ·  _med_

Suppresses the eDrive mode popup/notification that appears when switching electric drive modes (for plug-in hybrid/EV).

| value | meaning |
|---|---|
| `0` | Off (popup shown normally) |
| `1` | On (popup suppressed) |

default `00`· gate: FA-gated (depends on vehicle options)· token `EDRIVE_POPUP_DEACTIVATE`· source: firmware-token

### `3000/22/00000010b` — eDrive mode toggle available  ·  _med_

Enables the eDrive (electric drive) mode toggle button/option in the driving experience controls.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `EDRIVE_TOGGLE_AVAILABLE`· source: firmware-token

### `3000/22/00000100b` — iDrive usage statistics  ·  _med_

Records statistics on how the iDrive menus and controls are used.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

_Not a user setting: Usage statistics only: HmiMain3D's AbkStatistic manager (CHmiAbkStatisticManager/Counter/Timer/FileIO) counts key, speech, gesture and menu events into a statistics file; no screen in the HMI shows them. No driver-visible effect._

default `00`· gate: always (no FA gate)· token `MMI_STATISTIK`· source: firmware-trace

### `3000/22/00001000b` — Logic 7 audio system branding icon  ·  _high_

Shows the Logic 7 surround-sound system branding symbol/icon in the audio settings menu.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `LOGIC7_SYMBOL`· source: firmware-token

### `3000/22/00010000b` — ConnectedDrive services  ·  _high_

Enables the BMW ConnectedDrive online services menu and framework.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `CONNECTED_DRIVE`· source: firmware-token

### `3000/22/00100000b` — Hybrid vehicle mode  ·  _high_

Declares the vehicle as a hybrid (plug-in or full hybrid), enabling hybrid-specific HMI elements such as eDrive displays and charge indicators.

| value | meaning |
|---|---|
| `0` | Off (conventional drivetrain) |
| `1` | On (hybrid) |

default `00`· gate: FA-gated (depends on vehicle options)· token `HYBRID`· source: firmware-token

### `3000/22/01000000b` — Headlight settings menu  ·  _med_

Shows the headlight settings in the exterior lighting menu, such as daytime running lights and the setting for driving on the other side of the road.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `HEADLIGHT_SETTING`· source: firmware-trace

### `3000/22/10000000b` — Apple enhancements (BMW Apps / CarPlay prep)  ·  _med_

Enables Apple-specific enhancements in the HMI, primarily the BMW Apps (A4A/PIA) Apple integration layer. Required together with 6NR Apps SA for Siri/Apple app features. Active when 6NR Apps is fitted.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 6NR Apps· token `APPLE_ENHANCEMENTS`· source: firmware-token

### `3000/23/00000001b` — Speech feedback audio channel  ·  _med_

Enables a dedicated audio feedback channel for speech recognition (voice commands are acknowledged via a separate audio path rather than interrupting the main audio). Active when 6NR Apps is fitted.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: 6NR Apps· token `SPEECH_FEEDBACK_CHANNEL`· source: firmware-token

### `3000/23/00000010b` — Tourist light change with engine on  ·  _med_

Lets you change the headlight setting for driving on the other side of the road (tourist function) while the engine is running. When disabled, it can be changed only with the engine off.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `IGNORE_ENGINE_RUN_TOURIST`· source: firmware-trace

### `3000/23/00000100b` — Service history: who can access/edit  ·  _med_

Controls who has access to view or modify the service history records. Default = dealer/BMW access; value 1 = owner/driver access also allowed.

| value | meaning |
|---|---|
| `0` | Default (BMW/dealer access) |
| `1` | Extended access (owner/driver) |

default `00`· gate: always (no FA gate)· token `SERVICE_HISTORY_WHO`· source: firmware-token

### `3000/23/00001000b` — WCA (wireless charging area) display  ·  _med_

Enables the WCA (Wireless Charging Area) status and settings in the HMI connectivity menu.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `WCA`· source: firmware-token

### `3000/23/00010000b` — Armrest all-zone control  ·  _med_

Enables HMI control of an electric armrest covering all zones. When active, an armrest adjustment menu is shown.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ARMREST_ALL_CONTROL`· source: firmware-token

### `3000/23/01100000b` — RSE media serving mode  ·  _med_

Configures what the rear-seat entertainment (RSE) system can do when browsing media: basic playback only, skipping tracks, or full library browsing.

| value | meaning |
|---|---|
| `1` | Basic (playback only) |
| `2` | Skipping (track skip allowed) |
| `3` | Browsing (full library browsing) |

default `00`· gate: FA-gated (depends on vehicle options)· token `RSE_SERVING_SETTINGS`· source: firmware-token

### `3000/23/10000000b` — Speed-dependent volume (SLD) available  ·  _med_

Enables speed-dependent volume (Geschwindigkeitsabhaengige Lautstaerkeanpassung / SLD) function in the audio settings.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: NOT 544 Cruise control with braking function / 710 M leather steering wheel / 249 Multifunction for steering wheel· token `SLD`· source: firmware-token

### `3000/24/00000001b` — Doors/Key menu: tailgate options  ·  _med_

Shows the tailgate options in the “Doors/Key” menu, which set how the tailgate unlocks with the remote key.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: NOT 322 Comfort Access / 812 Great Britain/Ireland version· token `KEY_CONF_TAILGATE`· source: firmware-trace

### `3000/24/00000010b` — Doors/Key menu: Comfort Access  ·  _med_

Shows the Comfort Access options in the “Doors/Key” settings, for cars that unlock and lock when you touch the door handle with the key nearby.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `KEY_CONF_COMFORT`· source: firmware-trace

### `3000/24/00000100b` — Doors/Key menu: Comfort Access tailgate  ·  _low_

Shows the tailgate options that belong to Comfort Access in the “Doors/Key” menu, for cars whose tailgate can be opened with the key nearby.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `KEY_CONF_COMFORT_TAILGATE`· source: firmware-trace

### `3000/24/00001000b` — Doors/Key menu: comfort cooling  ·  _low_

Shows a cooling option among the Comfort Access settings in the “Doors/Key” menu.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `KEY_CONF_COMFORT_COOLING`· source: firmware-trace

### `3000/24/00110000b` — Doors/Key menu: second rear opening  ·  _low_

Shows the options for a second, smaller rear opening, such as a rear window that opens on its own, in the “Doors/Key” menu.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `KEY_CONF_TAILGATE_SMALL`· source: firmware-trace

### `3000/24/11000000b` — Special vehicle type  ·  _med_

Identifies special/authority vehicle designation. Used for vehicles fitted with special authority markings.

| value | meaning |
|---|---|
| `1` | Security vehicle |
| `2` | Authority vehicle (marked) |
| `3` | Authority vehicle (unmarked) |

default `00`· gate: FA-gated (depends on vehicle options)· token `SPECIAL_VEHICLE`· source: firmware-token

### `3000/25/00001111b` — Doors/Key menu: tailgate name  ·  _med_

Chooses what the “Doors/Key” menu calls the car's rear opening: rear window, tailgate, front gate or split doors. Match it to the car's body style.

| value | meaning |
|---|---|
| `0` | None |
| `1` | Rear window |
| `2` | Tailgate |
| `3` | Front gate |
| `4` | Split doors |

default `00`· gate: FA-gated (depends on vehicle options)· token `KEY_CONF_TAILGATE_NAME`· source: firmware-trace

### `3000/25/00110000b` — Off-road gauge (Offroadmeter)  ·  _med_

Enables the off-road gauges/display in the instrument cluster or HMI for off-road capable vehicles.

| value | meaning |
|---|---|
| `2` | Partially active |

default `00`· gate: FA-gated (depends on vehicle options)· token `OFFROADMETER`· source: firmware-token

### `3000/25/01000000b` — Car wash button  ·  _med_

Shows a car wash button in the parking and camera menu, which switches the camera system into its car wash mode.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `MACRO_CARWASH`· source: firmware-trace

### `3000/25/10000000b` — Air quality popup notification  ·  _med_

Enables a popup notification for the air quality sensor reading. Active on Chinese-market variants (8AA) and certain vehicle body-type groups.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 8AA Chinese version / vehicle type-key attribute group (FP category 1; 71 type tokens, e.g. 1A10,1A11,1A12,1A31) / vehicle type-key attribute group (FP category 1; 65 type tokens, e.g. 11CK,11DE,12CK,12DE) / vehicle type-key attribute group (FP category 1; 55 type tokens, e.g. 11CL,12CL,1K51,1K52) / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `AIRQUALITY_POPUP`· source: firmware-token

### `3000/26/00000011b` — Doors/Key menu: second opening name  ·  _med_

Chooses what the “Doors/Key” menu calls the second, smaller rear opening: rear window, tailgate or front gate.

| value | meaning |
|---|---|
| `0` | None |
| `1` | Rear window |
| `2` | Tailgate |
| `3` | Front gate |

default `00`· gate: FA-gated (depends on vehicle options)· token `KEY_CONF_TAILGATE_SMALL_NAME`· source: firmware-trace

### `3000/26/00000100b` — Doors/Key menu: unlock options  ·  _med_

Shows the unlock options in the “Doors/Key” menu, where you choose whether the remote key first unlocks only the driver's door or all doors.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· token `KEY_CONF_UNLOCK_VEHICLE`· source: firmware-trace

### `3000/26/00001000b` — Doors/Key menu: home lights  ·  _low_

Shows a home lights option among the Comfort Access settings in the “Doors/Key” menu.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `KEY_CONF_COMFORT_HOMELIGHT`· source: firmware-trace

### `3000/26/00110000b` — 3D view graphic slope interpolation  ·  _med_

Sets the interpolation curve for the slope (pitch) axis in the 3D vehicle graphic (X-View). LINEAR=direct proportional, TRAJECTORY variants use non-linear curves.

| value | meaning |
|---|---|
| `0` | Linear |
| `1` | Trajectory 1 |
| `2` | Trajectory 2 |
| `3` | Trajectory 3 |

default `00`· gate: always (no FA gate)· token `X_VIEW_GRAPHIC_SLOP`· source: firmware-token

### `3000/26/11000000b` — 3D view graphic roll interpolation  ·  _med_

Sets the interpolation curve for the roll axis in the 3D vehicle graphic (X-View).

| value | meaning |
|---|---|
| `0` | Linear |
| `1` | Trajectory 1 |
| `2` | Trajectory 2 |
| `3` | Trajectory 3 |

default `00`· gate: always (no FA gate)· token `X_VIEW_GRAPHIC_ROLL`· source: firmware-token

### `3000/27/00000001b` — Front seat ventilation  ·  _high_

Enables front seat ventilation control in the HMI settings menu.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SEAT_VENTILATION_FRONT`· source: firmware-token

### `3000/27/00000010b` — Rear seat heating  ·  _med_

Enables rear seat heating control in the HMI.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SEAT_HEATING_REAR`· source: firmware-token

### `3000/27/00000100b` — Front seat heating  ·  _med_

Enables front seat heating control in the HMI.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SEAT_HEATING_FRONT`· source: firmware-token

### `3000/27/00001000b` — Seat training / posture program  ·  _med_

Enables an automatic seat position training/exercise program that periodically adjusts the seat for ergonomics.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SEAT_TRAINING`· source: firmware-token

### `3000/27/00010000b` — Front seat lumbar support  ·  _med_

Enables lumbar support (Lordose) adjustment in the front seat settings menu.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SEAT_FRONT_LORDOSE`· source: firmware-token

### `3000/27/00100000b` — Front seat massage  ·  _high_

Enables the front seat massage function in the HMI.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SEAT_FRONT_MASSAGE`· source: firmware-token

### `3000/27/01000000b` — Rear seat massage  ·  _med_

Enables the rear seat massage function in the HMI.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SEAT_REAR_MASSAGE`· source: firmware-token

### `3000/27/10000000b` — Rear seat multifunction controls  ·  _med_

Enables the rear seat multifunction control panel (e.g. recliner, legrest, individual climate) in the HMI.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SEAT_REAR_MULTIFUNCTION`· source: firmware-token

### `3000/28/00000001b` — Deactivatable seat-belt alert (SBA)  ·  _med_

Allows the seat-belt reminder alert (SBA) to be turned off by the driver in settings.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `DEAKTIVIERBARKEIT_SBA`· source: firmware-token

### `3000/28/00000010b` — Deactivatable parking brake alert (PBA)  ·  _med_

Allows the parking brake alert (PBA) to be deactivated by the user through settings.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `DEAKTIVIERBARKEIT_PBA`· source: firmware-token

### `3000/28/00000100b` — Automatic climate recirculation (AUC)  ·  _high_

Specifies whether automatic air recirculation (AUC = Automatische Umluftsteuerung) is fitted, which closes the fresh air intake when poor outside air quality is detected.

| value | meaning |
|---|---|
| `0` | AUC not fitted |
| `1` | AUC fitted |

default `00`· gate: always (no FA gate)· token `CLIMATE_AUTORECIRCULATION`· source: firmware-token

### `3000/28/00001000b` — Indirect ventilation (diffuse air mode)  ·  _high_

Indicates whether indirect/diffuse ventilation (deflecting air from vents) is available in the climate system.

| value | meaning |
|---|---|
| `0` | Indirect ventilation not available |
| `1` | Indirect ventilation available |

default `00`· gate: always (no FA gate)· token `CLIMATE_INDIRECTVENTILATION`· source: firmware-token

### `3000/28/01110000b` — HVAC steering/operation mode (STRA menu)  ·  _med_

Sets how the HVAC system is operated in the iDrive HMI: display-only (sense/touch or rotary), full MMI control, or MMI control in 1-zone mode.

| value | meaning |
|---|---|
| `1` | Display only (sense/touch panel) |
| `2` | Display only (rotary/scroll controller) |
| `3` | Control via MMI |
| `4` | Control via MMI (1-zone) |

default `00`· gate: FA-gated (depends on vehicle options)· token `HVAC_STRA_MENUE`· source: firmware-token

### `3000/28/10000000b` — LCI (facelift) variant  ·  _med_

Flags this vehicle as an LCI (Life Cycle Impulse / facelift) model. Enables LCI-specific menus and display elements.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: vehicle type-key attribute group (FP category 1; 71 type tokens, e.g. 1A10,1A11,1A12,1A31) / vehicle type-key attribute group (FP category 1; 61 type tokens, e.g. 1D11,1D12,1D31,1D32)· token `LCI`· source: firmware-token

### `3000/29/00000011b` — Gesture control: two-finger gesture  ·  _med_

Turns on the two-finger gesture, whose action you choose in the gesture settings (such as opening the main menu or muting audio), in the standard version or the version for China.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Standard version |
| `2` | China version |

default `00`· gate: FA-gated (depends on vehicle options)· token `GESTURE_CAMERA_TWO_GESTURE`· source: firmware-trace

### `3000/29/00011100b` — HMI ID version / iDrive generation  ·  _high_

Selects the iDrive HMI interface generation/version loaded for this vehicle. Determines the overall HMI look and feature set.

| value | meaning |
|---|---|
| `0` | ID4++ |
| `1` | ID5 |
| `2` | ID5++ |
| `3` | ID6 Light |
| `4` | ID6 |

default `00`· token `HMI_ID_VERSION`· source: firmware-token

### `3000/29/11100000b` — Tire settings in tire pressure menu  ·  _med_

Adds a tire settings screen to the tire pressure menu, where you select the tires installed and how heavily the car is loaded, so the monitor checks against the right pressures. The extended version adds tire identification.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Tire and load selection |
| `2` | With tire identification |

default `00`· gate: FA-gated (depends on vehicle options)· token `ERFS`· source: firmware-trace

### `3000/30/00000111b` — Speed lock: car standstill condition  ·  _high_

Defines what vehicle condition is required to unlock speed-restricted functions (handbrake, gearbox in P, or a combination).

| value | meaning |
|---|---|
| `0` | None (no standstill condition) |
| `1` | Handbrake applied |
| `2` | Gearbox in P |
| `3` | Handbrake AND gearbox in P |
| `4` | Handbrake OR gearbox in P |

default `00`· gate: FA-gated (depends on vehicle options)· token `SPEEDLOCK_CAR_STANDSTILL`· source: firmware-token

### `3000/30/00001000b` — Miracast display in settings  ·  _med_

Shows the Miracast wireless display option in the entertainment settings menu.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_MIRACAST_DISPLAY_SETTINGS`· source: firmware-token

### `3000/30/00010000b` — USB display in settings  ·  _med_

Shows the USB display/mirroring option in the entertainment settings menu.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: always (no FA gate)· token `ENT_USB_DISPLAY_SETTINGS`· source: firmware-token

### `3000/30/00100000b` — HDMI display in settings  ·  _med_

Shows the HDMI input option in the entertainment settings menu.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_HDMI_DISPLAY_SETTINGS`· source: firmware-token

### `3000/30/01000000b` — Remote 360-degree camera  ·  _med_

Enables remote/external 360-degree surround-view camera functionality.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `REMOTE360`· source: firmware-token

### `3000/30/10000000b` — Multifunction steering wheel (MFL)  ·  _med_

Enables HMI integration of multifunction steering wheel (MFL = Multifunktionslenkrad) buttons.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 249 Multifunction for steering wheel / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `MFL`· source: firmware-token

### `3000/31/00000111b` — Speed lock: speller/keyboard input restriction  ·  _high_

Controls how text/address input via the speller or touchpad is locked while the vehicle is moving.

| value | meaning |
|---|---|
| `0` | None locked (no restriction) |
| `1` | Touch screen locked |
| `2` | Touch screen and touchpad locked |
| `3` | All input locked |

default `00`· gate: 807 Japanese version / 8LH Country control 04142· token `SPEEDLOCK_SPELLER_INPUT`· source: firmware-token

### `3000/31/00111000b` — Speed lock: destination text display length  ·  _high_

Sets how much of a destination/address text string is shown while the vehicle is in motion.

| value | meaning |
|---|---|
| `0` | Full text |
| `1` | One page (truncated) |
| `3` | No text |

default `00`· gate: 838 Canadian version / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93)· token `SPEEDLOCK_TEXT_LENGTH`· source: firmware-token

### `3000/31/01000000b` — Speed lock: video playback restriction  ·  _med_

Enables restriction of video (moving picture) playback while driving.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SPEEDLOCK_MOVING_PICTURES`· source: firmware-token

### `3000/31/10000000b` — Speed lock: additional picture display restriction  ·  _high_

Restricts access to picture/image viewing while the vehicle is moving.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SPEEDLOCK_PICTURE_ADD`· source: firmware-token

### `3000/32/00000001b` — Speed lock: interactive map (additional) restriction  ·  _med_

Restricts use of additional interactive map features while driving.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SPEEDLOCK_INTERACTIVE_MAP_ADD`· source: firmware-token

### `3000/32/00000010b` — Speed lock: interactive map (main) restriction  ·  _med_

Restricts main interactive map use while the vehicle is in motion.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SPEEDLOCK_INTERACTIVE_MAP_MAIN`· source: firmware-token

### `3000/32/00000100b` — Speed lock: owner's manual from Check Control  ·  _med_

Blocks opening the Integrated Owner's Manual from a Check Control message while the car is moving. Enabled at the factory for some markets, such as the Japanese, Australian, Canadian and Chinese versions (S807, S810, S838, S8AA or S8LH). Rules on driver distraction vary by country.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 807 Japanese version / 810 Australian version / 838 Canadian version / 8AA Chinese version / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / 8LH Country control 04142· token `SPEEDLOCK_IBA_ACCESS_CCM`· source: firmware-trace

### `3000/32/00001000b` — Speed lock: owner's manual short form  ·  _low_

Blocks the short form of the Integrated Owner's Manual while the car is moving. Enabled at the factory for some markets, such as the Japanese, Australian, Canadian and Chinese versions (S807, S810, S838, S8AA or S8LH). Rules on driver distraction vary by country.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 807 Japanese version / 810 Australian version / 838 Canadian version / 8AA Chinese version / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / 8LH Country control 04142· token `SPEEDLOCK_IBA_SHORT`· source: firmware-trace

### `3000/32/00010000b` — Speed lock: owner's manual index  ·  _med_

Blocks the index of the Integrated Owner's Manual while the car is moving. Rules on driver distraction vary by country.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `SPEEDLOCK_IBA_INDEX`· source: firmware-trace

### `3000/32/11100000b` — Automatic seat climate: front  ·  _med_

Chooses which seat climate functions the head unit offers in automatic mode for the front seats. A checked item is offered; check only what the front seats have.

| value | meaning |
|---|---|
| `0` | None |
| `1` | Heating |
| `2` | Cooling |
| `3` | Heating and cooling |

Bits (set = on): bit 0 Heating; bit 1 Cooling

default `00`· gate: FA-gated (depends on vehicle options)· token `AKT_AUTO_SITZE_FRONT`· source: firmware-trace

### `3000/33/00000111b` — Automatic seat climate: rear  ·  _med_

Chooses which seat climate functions the head unit offers in automatic mode for the rear seats. A checked item is offered; check only what the rear seats have.

| value | meaning |
|---|---|
| `0` | None |
| `1` | Heating |
| `2` | Cooling |
| `3` | Heating and cooling |

Bits (set = on): bit 0 Heating; bit 1 Cooling

default `00`· gate: FA-gated (depends on vehicle options)· token `AKT_AUTO_SITZE_FOND`· source: firmware-trace

### `3000/33/00001000b` — Active automatic steering wheel heating  ·  _med_

Enables automatic steering wheel heating control via the HMI.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `AKT_AUTO_LENKRADHEIZUNG`· source: firmware-token

### `3000/33/00010000b` — Gesture control on by default  ·  _med_

Sets whether gesture control starts out switched on or off, for example on a new car or after the gesture settings are reset.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `01`· gate: FA-gated (depends on vehicle options)· token `GESTURE_CAMERA_DEFAULT_STATE`· source: firmware-trace

### `3000/33/00100000b` — Setup wizard on first boot  ·  _med_

Enables an initial setup wizard that runs the first time the vehicle is started or after a factory reset, guiding the driver through key settings.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: always (no FA gate)· token `SETUP_WIZARD`· source: firmware-token

### `3000/33/01000000b` — M model on 35up platform  ·  _low_

Tells the head unit the car is a BMW M model built on the 35up vehicle architecture, so it offers the M-specific menus for those cars. Enable it only on such a car.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `M_VEHICLE_35UP`· source: firmware-trace

### `3000/33/10000000b` — M-specific menu  ·  _med_

Enables the M-specific settings and drive menu in the iDrive HMI (M Drive / M Setup menus).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `M_MENUE`· source: firmware-token

### `3000/34/00000001b` — M xDrive settings  ·  _med_

Shows the M xDrive settings on M models with M xDrive, where the driver picks the all-wheel-drive mode, such as 4WD or 4WD Sport.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `M_ALLRAD`· source: firmware-trace

### `3000/34/00000010b` — M launch/staging animation (Inszenierung)  ·  _med_

Enables the M-specific startup/launch staging animation or choreography in the HMI.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `M_INSZENIERUNG`· source: firmware-token

### `3000/34/00000100b` — M shift lights  ·  _med_

Enables the M shift lights feature (RPM-based shift indicator lights) shown in the instrument cluster or HMI.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `M_SHIFTLIGHTS`· source: firmware-token

### `3000/34/00001000b` — Battery charge control available  ·  _med_

Indicates whether the user-adjustable battery charge control (setting the target state-of-charge) is available on this vehicle.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `BATTERY_CONTROL_AVAILABILITY`· source: firmware-token

### `3000/34/11110000b` — Battery charge target: step size  ·  _med_

Sets the increment step size (in percent) for the user-selectable battery charge target SOC (state of charge).

default `01`· gate: always (no FA gate)· token `BATTERY_CONTROL_SOC_TARGET_STEP`· source: firmware-token

### `3000/35/00001111b` — Battery charge target: maximum SOC  ·  _med_

Sets the maximum selectable target state of charge (SOC) percentage for battery charge control.

default `02`· gate: always (no FA gate)· token `BATTERY_CONTROL_SOC_TARGET_MAX`· source: firmware-token

### `3000/35/11110000b` — Battery charge target: minimum SOC  ·  _med_

Sets the minimum selectable target state of charge (SOC) percentage for battery charge control.

default `05`· gate: FA-gated (depends on vehicle options)· token `BATTERY_CONTROL_SOC_TARGET_MIN`· source: firmware-token

### `3000/36/00000001b` — 5-flash one-touch lane-change indicator  ·  _high_

Enables the convenience 5-flash turn signal function: a single tap of the indicator stalk produces 5 flashes for lane changes.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· source: firmware-token

### `3000/36/00000010b` — Miracast: multiple simultaneous streams  ·  _med_

Enables support for multiple simultaneous Miracast wireless display streams (e.g. front and rear screens independently).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_MIRACAST_MULTIPLE_STREAMS`· source: firmware-token

### `3000/36/00000100b` — Charging preferences: ESL  ·  _low_

Setting used by the charging preferences of plug-in hybrid and electric models. Best left unchanged.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `ESL`· source: firmware-trace

### `3000/36/00001000b` — Office (connected apps) menus active  ·  _med_

Enables the BMW Connected Drive 'Office' menu group (messages, calendar, tasks, notes) in the iDrive HMI.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: NOT 8LH Country control 04142 / 6NS Comfort telephony with expanded smartphone connection / 6NW Telephony with wireless charging· token `OFFICE_MENUS_ACTIVE`· source: firmware-token

### `3000/36/00010000b` — Battery charge control: configurable home/residential mode  ·  _med_

Enables a user-configurable home/residential charging energy mode (Wohnen = home usage scenario). Firmware enum only names value 0 as NICHT_AKTIV (not active).

| value | meaning |
|---|---|
| `0` | Not active |

default `00`· gate: FA-gated (depends on vehicle options)· token `BATTERY_CONTROL_CONFIGURABLE_WOHNEN`· source: firmware-token

### `3000/36/00100000b` — High oil capacity (3+ litre sump)  ·  _high_

Flags that the engine has a large oil sump capacity (>=3 litres above standard), affecting oil condition display intervals.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: FA-gated (depends on vehicle options)· token `OIL_QUANTITY_HIGH_3L`· source: firmware-token

### `3000/36/01000000b` — NFC hotspot pairing  ·  _med_

Enables NFC tap-to-pair for the vehicle Wi-Fi hotspot, allowing a phone to join the hotspot by touching an NFC sensor.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `NFC_HOTSPOT_PAIRING`· source: firmware-token

### `3000/36/10000000b` — Automatic exterior mirror folding setting  ·  _med_

Shows the automatic exterior mirror folding option in the vehicle settings menu.

| value | meaning |
|---|---|
| `1` | Active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SETTINGS_AUTOMATIC_EXT_MIRROR_FOLDING`· source: firmware-token

### `3000/37/00000111b` — Ambient fragrance: climate menu button type  ·  _high_

Configures whether and which type of button is shown in the climate menu for the ambient fragrance (Beduefter) system.

| value | meaning |
|---|---|
| `0` | No button |
| `1` | Fragrance button |
| `2` | Climate menu button |

default `00`· gate: always (no FA gate)· token `TASTE_BEDUFTER_KLIMAMENUE`· source: firmware-token

### `3000/37/00011000b` — Fragrance cartridge holder orientation  ·  _med_

Sets the physical orientation of the fragrance cartridge holder in the vehicle (vertical or horizontal install).

| value | meaning |
|---|---|
| `1` | Vertical |
| `2` | Horizontal |

default `00`· gate: FA-gated (depends on vehicle options)· token `ORIENTATION_FRAGRANCE_CARTRIDGE_HOLDER`· source: firmware-token

### `3000/37/01100000b` — AdBlue filler position  ·  _high_

Specifies where the AdBlue (diesel exhaust fluid) filler cap is located on the vehicle.

| value | meaning |
|---|---|
| `0` | Next to fuel tank |
| `1` | In engine compartment |

default `00`· gate: FA-gated (depends on vehicle options)· token `POSITION_ADBLUE_TANK`· source: firmware-token

### `3000/37/10000000b` — Indirect ventilation: 2-zone climate  ·  _med_

Enables indirect ventilation control for a 2-zone (driver + passenger) climate system.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `CLIMATE_INDIRECTVENTILATION_2ZONES`· source: firmware-token

### `3000/38/00000001b` — Gesture control: voice dialogs  ·  _med_

Lets gesture control act on voice control dialogs, for example a swipe gesture while a voice dialog is open. Works only when “Gesture control” (`3000/14/10000000b`) is enabled.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `01`· gate: FA-gated (depends on vehicle options)· token `GESTURE_CAMERA_ENABLE_SPEECH_CTRL`· source: firmware-trace

### `3000/38/00000110b` — Wireless charging pad position  ·  _high_

Specifies the physical location of the wireless charging area (WCA = Wireless Charging Area) in the vehicle.

| value | meaning |
|---|---|
| `0` | Centre stack (dashboard) |
| `1` | Centre console (between seats) |

default `00`· gate: always (no FA gate)· token `WCA_POSITION`· source: firmware-token

### `3000/38/00001000b` — Bluetooth audio cover art browsing  ·  _med_

Enables album cover art display and browsing when using Bluetooth audio (BT Audio Source / BTAS).

| value | meaning |
|---|---|
| `1` | Active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_BTAS_BROWSING_COVER`· source: firmware-token

### `3000/38/00010000b` — eDrive startup mode  ·  _low_

Shows a setting that lets the driver choose which eDrive mode a plug-in hybrid starts in.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `EV_CONF_STARTUP_MODE`· source: firmware-trace

### `3000/38/00100000b` — Speed lock: see all (unrestricted view)  ·  _med_

When active, allows all menu items to be visible while driving (not hidden by speed lock), though interaction may still be restricted.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93)· token `SPEEDLOCK_SEE_ALL`· source: firmware-token

### `3000/38/01000000b` — External HU drive (entertainment)  ·  _med_

Enables an external storage drive connected directly to the head unit for entertainment (media storage/playback).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_HU_EXT_DRIVE`· source: firmware-token

### `3000/38/10000000b` — M xDrive 2WD mode  ·  _med_

Enables the 2WD (rear-wheel drive only) mode selector for M vehicles with xDrive.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `M_ALLRAD_2WD`· source: firmware-token

### `3000/39/00000001b` — PMA cursor orientation (longitudinal/lateral)  ·  _med_

Sets the axis orientation of the Park Distance Control (PMA = Parkmanoeuvrerassistent) cursor on the HMI display.

| value | meaning |
|---|---|
| `0` | Longitudinal (front-to-rear) |
| `1` | Lateral (side-to-side) |

default `00`· token `CURSORPOSITION_PMA_AUSRICHTUNG`· source: firmware-token

### `3000/39/00000010b` — Key memory: vehicle level change  ·  _high_

Enables or disables the vehicle suspension level change option in the key memory configuration.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: always (no FA gate)· token `KEY_CONF_LEVEL_CHANGE_VEHICLE`· source: firmware-token

### `3000/39/00001100b` — External HU drive type (entertainment)  ·  _med_

Specifies what kind of external drive is available for entertainment content connected to the head unit.

| value | meaning |
|---|---|
| `1` | CD/DVD (CDDA) |
| `2` | CD/DVD + data disc |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENT_DRIVE_HU_EXT_AVAILABLE`· source: firmware-token

### `3000/39/00010000b` — Soccer Mum / easy-access seat  ·  _med_

Enables the 'Soccer Mum' easy-entry/exit seat feature for the rear seats, simplifying rear passenger egress (seat slides back).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SEAT_SOCCER_MUM`· source: firmware-token

### `3000/39/00100000b` — Bus network generation (ALEV4)  ·  _high_

Identifies the vehicle bus architecture generation. Determines whether this is an NBT Evo BN2015 or BN2018 network generation.

| value | meaning |
|---|---|
| `0` | BN2015 NBT Evo |
| `1` | BN2018 NBT Evo |

default `00`· gate: always (no FA gate)· token `ALEV4_STATUS_SELECTION`· source: firmware-token

### `3000/39/01000000b` — Eco load in tire settings  ·  _med_

Adds an Eco option to the load choices on the tire settings screen of the tire pressure menu, so the tire pressure monitor (RDC) can be set for that load condition.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `ERFS_ECO_BELADUNG`· source: firmware-trace

### `3000/39/10000000b` — CarPlay/projection fullscreen mode  ·  _high_

Enables fullscreen display mode for CarPlay or other phone projection sources, expanding them to fill the entire display instead of a windowed view.

| value | meaning |
|---|---|
| `0` | Off/inactive (windowed) |
| `1` | On/active (fullscreen) |

default `00`· gate: FA-gated (depends on vehicle options)· token `CARPLAY_FULLSCREEN`· source: firmware-token

### `3000/40/00000001b` — Rolls-Royce off-road mode available  ·  _med_

Flags availability of the RR (Rolls-Royce) off-road terrain mode. Not applicable to standard BMW variants.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `RR_OFFROAD_AVL`· source: firmware-token

### `3000/40/00000010b` — Comfort key: door lock/unlock  ·  _med_

Enables the comfort key (CKT) door lock/unlock function (auto-lock on walk away, unlock on approach).

| value | meaning |
|---|---|
| `1` | Active |

default `00`· gate: FA-gated (depends on vehicle options)· token `CKT_DOOR_LOCK_UNLOCK`· source: firmware-token

### `3000/40/00001100b` — Key memory: tailgate rear window deactivate  ·  _med_

Configures whether the tailgate rear window deactivation can be saved to key memory.

default `00`· gate: FA-gated (depends on vehicle options)· token `KEY_CONF_TAILGATE_REAR_WINDOW_DEACTIVATE`· source: firmware-token

### `3000/40/00010000b` — Seat headrest height adjustment available  ·  _med_

Indicates that the front seat headrests are electrically adjustable in height, enabling the relevant menu in seat settings.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SETTINGS_SEATS_HEADREST_ADJUSTABLE_IN_HEIGHT`· source: firmware-token

### `3000/40/00100000b` — Low-voltage recuperation system  ·  _med_

Enables the low-voltage recuperation/energy recovery system (e.g. belt starter-generator in mild-hybrid variants).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `LOW_VOLTAGE_RECUP_SYSTEM`· source: firmware-token

### `3000/40/11000000b` — Panoramic roof / sunroof motor config (SMO)  ·  _med_

Configures the powered roof motor operation mode: open only, open and close, or close only.

| value | meaning |
|---|---|
| `1` | Open only |
| `2` | Open and close |
| `3` | Close only |

default `00`· gate: FA-gated (depends on vehicle options)· token `SMO_CONFIG`· source: firmware-token

### `3000/41/11111111b` — SCR display variant (AdBlue indicator style)  ·  _med_

Selects the display style/variant for the SCR (Selective Catalytic Reduction / AdBlue) system status indicator in the HMI.

| value | meaning |
|---|---|
| `1` | Variant 1 |
| `2` | Variant 2 |
| `3` | Variant 3 |
| `4` | Variant 4 |
| `5` | Variant 5 |
| `6` | Variant 6 |
| `7` | Variant 7 |

default `00`· token `SCR_ANZEIGE_NEU`· source: firmware-token

### `3000/42/00000001b` — RSE: no remote control  ·  _med_

Disables the physical remote control for the rear-seat entertainment (RSE) system.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `RSE_NO_REMOTECONTROL`· source: firmware-token

### `3000/42/00000110b` — RSL illuminated front grille  ·  _med_

Enables and configures the illuminated front grille feature (RSL = Rolls-Royce Spirit of Ecstasy Illuminated). Not applicable to standard BMW.

default `00`· gate: FA-gated (depends on vehicle options)· token `RSL_ILLUMINATED_FRONTGRILL`· source: firmware-token

### `3000/42/00011000b` — Extended ambient light ensembles  ·  _med_

Enables extended/additional ambient lighting ensembles (predefined colour scenes) in the ambient light settings.

default `00`· gate: FA-gated (depends on vehicle options)· token `ERWEITERTE_LICHTENSEMBLES`· source: firmware-token

### `3000/42/01100000b` — PMA long-press operation mode  ·  _med_

Sets whether the Park Distance Control display acknowledgement (PMALQ) requires a long press/hold to dismiss.

| value | meaning |
|---|---|
| `0` | Without long-press (tap to dismiss) |
| `1` | With long-press (hold to dismiss) |

default `00`· gate: always (no FA gate)· token `PMALQ_BEDIENUNG`· source: firmware-token

### `3000/42/10000000b` — Rolls-Royce off-road preview additional info  ·  _med_

Enables additional informational content in the RR off-road mode preview screen. Not applicable to standard BMW.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `RR_OFFROAD_PREVIEW_ADD_INFO`· source: firmware-token

### `3000/43/00000111b` — iDrive controller (ZBE) hard key layout  ·  _high_

Selects the hard key layout variant of the iDrive rotary controller (ZBE = Zentrales Bediengeraet).

| value | meaning |
|---|---|
| `0` | Standard |
| `7` | Projected mode (China) |

default `00`· gate: FA-gated (depends on vehicle options)· token `ZBE_HARDKEY_LAYOUT_VARIANT`· source: firmware-token

### `3000/43/11111000b` — Reserved (unused 5-bit field)  ·  _low_

Purpose not determined from available sources. This 5-bit field shares byte 43 with ZBE_HARDKEY_LAYOUT_VARIANT but has no name, no descriptor record, and no consumer in the firmware.

_Resolved as RESERVED_3000_43_bits7,6,5,4,3 in resolved_unnamed.json._

source: firmware-trace

### `3000/44/11111111b` — Reserved block (bytes 44-56)  ·  _low_

Unnamed 13-byte reserved block in the HMI coding page. No descriptor record, no consumer in the OMAP firmware image. Purpose undetermined.

_Resolved as RESERVED_3000_BYTES_44_56 in resolved_unnamed.json._

source: firmware-trace

### `3000/57/00000111b` — Remote Control Parking button  ·  _med_

Tells the head unit which generation of Remote Control Parking the car has. Only generation 1 adds the “Remote controlled parking” button to the control bar of the parking view. Set it to match the car's parking equipment.

| value | meaning |
|---|---|
| `0` | None |
| `1` | Generation 1 |
| `2` | Generation 2 |

default `00`· gate: FA-gated (depends on vehicle options)· token `MACRO_RCP_EINPARKEN`· source: firmware-trace

### `3000/57/00001000b` — Junction views (Guiding Plus)  ·  _med_

Shows enlarged views of complex intersections and highway exits during route guidance, so you can see the way through before you reach them.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: NOT 609 Professional navigation system / 802 Korean version / 807 Japanese version / 8AA Chinese version / 8LH Country control 04142 / 8LT Country control 04825 · token `GUIDING_PLUS`· source: firmware-trace

### `3000/57/00110000b` — High-end audio menu / staging level  ·  _high_

Controls the depth of the high-end audio (e.g. Bang & Olufsen / HiFi) settings menu shown in the HMI, from no menu to full staging with light animation.

| value | meaning |
|---|---|
| `0` | No menu |
| `1` | No staging animation |
| `2` | Light staging only |
| `3` | Full staging (animation + visuals) |

default `00`· gate: always (no FA gate)· token `HIGH_END_AUDIO_MENUE`· source: firmware-token

### `3000/57/01000000b` — Office: SMS/text messaging menu  ·  _med_

Enables the SMS/text messaging option in the BMW Connected Drive Office menu.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: always (no FA gate)· token `OFFICE_MENUS_SMS_EIN_AUS`· source: firmware-token

### `3000/57/10000000b` — Office: email menu  ·  _med_

Enables the email option in the BMW Connected Drive Office menu.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: always (no FA gate)· token `OFFICE_MENUS_EMAIL_EIN_AUS`· source: firmware-token

### `3000/58/00000001b` — Office: calendar menu  ·  _high_

Enables the calendar option in the BMW Connected Drive Office menu. Requires Professional Navigation (609).

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: 609 Professional navigation system· token `OFFICE_MENUS_CALENDAR_EIN_AUS`· source: firmware-token

### `3000/58/00000010b` — Office: tasks menu  ·  _med_

Enables the task management option in the BMW Connected Drive Office menu. Requires Professional Navigation (609).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 609 Professional navigation system· token `OFFICE_MENUS_TASK_EIN_AUS`· source: firmware-token

### `3000/58/00000100b` — Office: notes menu  ·  _med_

Enables the notes/memo pad option in the BMW Connected Drive Office menu.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: always (no FA gate)· token `OFFICE_MENUS_NOTES_EIN_AUS`· source: firmware-token

### `3000/58/00001000b` — Seat memory popup on key change  ·  _med_

Shows a popup prompt offering to load a seat memory position when a different key is detected.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: always (no FA gate)· token `SEAT_SEAT_MEMORY_POPUP`· source: firmware-token

### `3000/58/00010000b` — Seat limit popup  ·  _med_

Enables a popup notification when seat movement has reached a configured limit (e.g. child safety zone).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SEAT_LIMIT_POPUP`· source: firmware-token

### `3000/58/00100000b` — Seat memory popup  ·  _med_

Enables a popup to appear offering seat memory recall when entering the vehicle.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: always (no FA gate)· token `SEAT_MEMORY_POPUP`· source: firmware-token

### `3000/58/01000000b` — HVAC remote engine start  ·  _med_

Enables remote engine start with climate pre-conditioning from the BMW Connected Drive app or key fob.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `HVAC_REMOTE_ENGINE_START`· source: firmware-token

### `3000/58/10000000b` — Water injection system  ·  _med_

Enables HMI support for the BMW M water injection system (water/methanol injection for charge cooling on M performance engines).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `WATER_INJECTION`· source: firmware-token

### `3000/59/00000001b` — Charging plug lock (EV)  ·  _med_

Enables the charging plug/cable lock control in the HMI for electric and plug-in hybrid vehicles.

| value | meaning |
|---|---|
| `1` | Active |

default `00`· gate: FA-gated (depends on vehicle options)· token `CHARGING_PLUG_LOCK`· source: firmware-token

### `3000/59/11111110b` — Reserved (bits 7-1 of byte 59)  ·  _low_

Purpose not determined from available sources. Unnamed reserved bits sharing byte 59 with CHARGING_PLUG_LOCK.

_Resolved as RESERVED_3000_59_bits7,6,5,4,3,2,1 in resolved_unnamed.json._

source: firmware-trace

### `3000/60/11111111b` — Reserved block (bytes 60-91)  ·  _low_

Unnamed 32-byte reserved block in the HMI coding page. No descriptor record, no consumer in the OMAP firmware image. Purpose undetermined.

_Resolved as RESERVED_3000_BYTES_60_91 in resolved_unnamed.json._

source: firmware-trace

### `3000/92/00000001b` — PIM supported features popup  ·  _med_

Enables a popup informing the user which Personal Information Management (PIM) features are available via Connected Drive.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `PIM_SUPPORTED_FEATURES_POPUP`· source: firmware-token

### `3000/92/00000010b` — Tourist light / right-hand drive market  ·  _high_

Sets the default traffic-side for the tourist/driving-on-right headlamp assistant. Relevant for UK/Japan/Australia markets.

| value | meaning |
|---|---|
| `0` | Right-hand traffic (standard) |
| `1` | Left-hand traffic (UK/Japan/AU) |

default `00`· gate: 807 Japanese version / vehicle type-key attribute group (FP category 7; 103 type tokens, e.g. 12CK,12CL,12DE,1A12) / 8LH Country control 04142· token `TOURISTLIGHT_RIGHTHANDDRIVE`· source: firmware-token

### `3000/92/00000100b` — Text abbreviation / truncation  ·  _med_

Enables automatic abbreviation/truncation of long text strings in the HMI where space is limited.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `01`· gate: always (no FA gate)· token `TEXTKUERZUNG`· source: firmware-token

### `3000/92/00011000b` — Daytime light behavior  ·  _med_

Sets the daytime running lights to always off, always on or the standard behavior. The always-off and always-on values also change the daytime running lights entry in the exterior lighting menu.

| value | meaning |
|---|---|
| `0` | Always off |
| `1` | Always on |
| `2` | Standard |

default `00`· token `DAYDRIVING_LIGHT`· source: firmware-trace

### `3000/92/00100000b` — Welcome light  ·  _med_

Enables the welcome/coming-home light function that illuminates exterior lights when the vehicle is unlocked.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: always (no FA gate)· token `WELCOME_LIGHT`· source: firmware-token

### `3000/92/01000000b` — Traffic mode  ·  _med_

Enables a special driving mode optimised for heavy traffic conditions.

| value | meaning |
|---|---|
| `1` | Active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TRAFFIC_MODE`· source: firmware-token

### `3000/92/10000000b` — Automatic traffic mode  ·  _med_

Enables automatic activation of traffic mode based on detected traffic conditions.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TRAFFIC_MODE_AUTO`· source: firmware-token

### `3000/93/00001111b` — App voice commands: global limit  ·  _med_

Limits how many global voice commands connected apps can register with the car's voice control. Best left unchanged.

| value | meaning |
|---|---|
| `0` | None |
| `1` | 5 commands |
| `2` | 20 commands |
| `3` | 40 commands |
| `4` | 60 commands |
| `5` | 80 commands |
| `6` | 100 commands |
| `7` | 150 commands |
| `8` | 200 commands |
| `9` | 300 commands |
| `10` | 400 commands |
| `11` | 500 commands |
| `12` | 750 commands |
| `13` | 1000 commands |

default `00`· gate: FA-gated (depends on vehicle options)· token `MAXGLOBALREMOTECOMMANDS`· source: firmware-trace

### `3000/93/11110000b` — App voice commands: local limit  ·  _low_

Limits how many local voice commands connected apps can register with the car's voice control. Best left unchanged.

| value | meaning |
|---|---|
| `0` | None |
| `1` | 2 commands |
| `2` | 4 commands |
| `3` | 6 commands |
| `4` | 8 commands |
| `5` | 10 commands |
| `6` | 15 commands |
| `7` | 20 commands |
| `8` | 30 commands |
| `9` | 50 commands |
| `10` | 100 commands |
| `11` | 200 commands |

default `00`· gate: FA-gated (depends on vehicle options)· token `MAXLOCALREMOTECOMMANDS`· source: firmware-trace

### `3000/94/11111111b` — Reserved (byte 94)  ·  _low_

Purpose not determined from available sources. Unnamed single-byte reserved field between remote command limits and A4A production date.

_Resolved as RESERVED_3000_BYTE_94 in resolved_unnamed.json._

source: firmware-trace

### `3000/95/00001111b` — Smartphone apps: production date (month)  ·  _med_

Production month the head unit reports to connected smartphone apps, together with the year setting.

| value | meaning |
|---|---|
| `1` | January |
| `2` | February |
| `3` | March |
| `4` | April |
| `5` | May |
| `6` | June |
| `7` | July |
| `8` | August |
| `9` | September |
| `10` | October |
| `11` | November |
| `12` | December |

_Not a user setting: Production-date stamp: read only by CHmiVariantServer::getProductionMonth (libhmicoding 0x477a4, features 306-317 -> 1..12), which the A4A capability init in HmiMain3D sends to phone apps as 'vehicle.productiondate' ('%02d.%02d'). Nothing in the car shows it._

default `01`· gate: FA-gated (depends on vehicle options)· token `A4A_PROD_MONTH`· source: firmware-trace

### `3000/95/11110000b` — Smartphone apps: production date (year)  ·  _med_

Production year the head unit reports to connected smartphone apps, together with the month setting.

| value | meaning |
|---|---|
| `2` | 2012 |
| `3` | 2013 |
| `4` | 2014 |
| `5` | 2015 |
| `6` | 2016 |
| `7` | 2017 |
| `8` | 2018 |
| `9` | 2019 |

_Not a user setting: Production-date stamp: read only by CHmiVariantServer::getProductionYear (libhmicoding 0x47648), sent to phone apps as 'vehicle.productiondate'. Nothing in the car shows it._

default `02`· token `A4A_PROD_YEAR`· source: firmware-trace

### `3000/96/00000111b` — Rear seat entertainment (RSE) type  ·  _high_

Specifies the type of rear-seat entertainment system fitted: none, mid-level, or high-end.

| value | meaning |
|---|---|
| `0` | No RSE |
| `1` | RSE Mid |
| `2` | RSE High |

default `00`· gate: always (no FA gate)· token `RSE`· source: firmware-token

### `3000/96/00111000b` — RSE wireless system (Kleer)  ·  _high_

Specifies the Kleer wireless audio/headphone system configuration for RSE.

| value | meaning |
|---|---|
| `0` | None |
| `1` | Headphones only |
| `2` | Remote control only |
| `3` | Headphones and remote control |

default `00`· gate: FA-gated (depends on vehicle options)· token `RSE_KLEER`· source: firmware-token

### `3000/96/01000000b` — Video system: PAL format  ·  _med_

Enables PAL video format support for the rear screen video system (SVS = Seat Video System).

| value | meaning |
|---|---|
| `0` | Off/inactive (NTSC default) |
| `1` | On/active (PAL) |

default `00`· gate: always (no FA gate)· token `SVS_PAL`· source: firmware-token

### `3000/96/10000000b` — Voice control (SVS/iDrive speech)  ·  _med_

Enables the iDrive voice control system. Active when navigation (606/609) or multifunction steering wheel (249) is fitted.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 606 Navigation system Business / 609 Professional navigation system / 249 Multifunction for steering wheel / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `SVS_VOICE`· source: firmware-token

### `3000/97/00000111b` — RSE Bluetooth type  ·  _high_

Specifies the Bluetooth keyboard/trackball type for the RSE system.

| value | meaning |
|---|---|
| `0` | None |
| `1` | Keyboard with trackball |

default `00`· gate: always (no FA gate)· token `RSE_BLUETOOTH`· source: firmware-token

### `3000/97/00001000b` — Reduced functionality while driving  ·  _med_

Enables a mode where some HMI features are reduced or simplified while the vehicle is in motion.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `REDUZIERT_BEI_FAHRT`· source: firmware-token

### `3000/97/00010000b` — ISpeech voice recognition app (SWT)  ·  _high_

Software token (SWT) enable bit for the ISpeech or ISpeech-Nuance voice recognition application. When inactive, the ISpeech component is treated as not coded and is disabled.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

_Token SWT_APP_ISPEECH recovered from cur_desc RE analysis. Decoded by FUN_00334a8c; queried in switch cases 0 (ISpeech) and 0xc (ISpeech Nuance) in FUN_002f58c4. The syset_enum_values dict maps this coord to token 'SVS' which is an extraction artifact; the firmware-traced RE name SWT_APP_ISPEECH is correct._

default `00`· gate: 606 Navigation system Business / 609 Professional navigation system / 249 Multifunction for steering wheel / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `SWT_APP_ISPEECH`· source: firmware-trace

### `3000/97/00100000b` — External music management  ·  _med_

Enables external/third-party music management on the head unit. When active, allows the HMI to expose extended music library management controls beyond the built-in player.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `EXT_MUSIC_MANAGEMENT`· source: firmware-token

### `3000/97/01000000b` — One-shot destination input  ·  _med_

Enables single-step destination entry mode in navigation, allowing the user to enter a destination without stepping through address fields individually.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `ONE_SHOT_DEST_INPUT`· source: firmware-token

### `3000/97/10000000b` — TV tuner auto-store channels  ·  _med_

Enables automatic channel storage (auto-store) for the CDMM television tuner module. When active, the TV tuner automatically scans and stores available channels.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `CDMM_TV_AUTOSTORE`· source: firmware-token

### `3000/98/00001111b` — TV tuner variant  ·  _med_

Selects which television tuner variant (TVM) is installed. Controls which tuner hardware the CDMM module communicates with.

| value | meaning |
|---|---|
| `0` | No TV tuner |
| `1` | TV tuner fitted |

default `00`· token `TVM_VARIANTEN`· source: firmware-token

### `3000/98/00010000b` — TV tuner BML (basic menu list)  ·  _med_

Enables the Basic Menu List for the television tuner, providing a simplified channel list UI for the CDMM TV module.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `CDMM_TV_BML`· source: firmware-token

### `3000/98/00100000b` — TV tuner teletext  ·  _med_

Enables the teletext feature for the CDMM television tuner, allowing the display of broadcast text pages.

| value | meaning |
|---|---|
| `0` | Not active |

default `00`· gate: FA-gated (depends on vehicle options)· token `CDMM_TV_TELETEXT`· source: firmware-token

### `3000/98/01000000b` — Speed-lock unlock menu (Japan)  ·  _med_

Enables the speed-lock unlock menu, which is a Japanese-market feature allowing the operator to access a menu to suppress speed-dependent function restrictions.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 807 Japanese version· token `SPEEDLOCK_FREISCHALTMENU`· source: firmware-token

### `3000/98/10000000b` — USB MSD Composer support  ·  _med_

Enables CDMM support for USB Mass Storage Device (MSD) with the Composer metadata library. When active, the USB port can browse music via the Composer-generated database.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 6NH Hands-free system with USB interface / 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `CDMM_USB_COMPOSER_MSD`· source: firmware-token

### `3000/99/00000001b` — TV tuner subtitles  ·  _med_

Enables subtitle display for the CDMM television tuner, allowing broadcast subtitle tracks to be shown on screen.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `CDMM_TV_SUBTITLES`· source: firmware-token

### `3000/99/00000010b` — TV tuner pay-TV browser list  ·  _med_

Enables the pay-TV / conditional-access channel browser list in the CDMM television tuner menu.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `CDMM_TV_PAY_BROWSER_LIST`· source: firmware-token

### `3000/99/00000100b` — TV tuner channel following  ·  _med_

Enables automatic channel-following in the CDMM TV tuner: when the current channel becomes unavailable, the tuner automatically switches to the best available alternative.

| value | meaning |
|---|---|
| `1` | Active |

default `00`· gate: FA-gated (depends on vehicle options)· token `CDMM_TV_FOLLOWING`· source: firmware-token

### `3000/99/00001000b` — TV tuner preset list  ·  _med_

Enables the preset/favourite channel list in the CDMM television tuner, showing stored channels in the channel browser.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: FA-gated (depends on vehicle options)· token `CDMM_TV_PRESETLIST`· source: firmware-token

### `3000/99/00010000b` — TV tuner audio track selection  ·  _med_

Enables the audio track selection feature for the CDMM television tuner, allowing the user to choose from multiple broadcast audio tracks (e.g. language, commentary).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `CDMM_TV_AUDIOTRACK`· source: firmware-token

### `3000/99/00100000b` — TV tuner EPG (electronic programme guide)  ·  _med_

Enables the Electronic Programme Guide in the CDMM television tuner, showing broadcast schedules and programme information on-screen.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `CDMM_TV_EPG`· source: firmware-token

### `3000/99/01000000b` — M digital speedometer units  ·  _med_

Controls the measurement units for the M-mode digital speedometer display (Einheit=unit). Determines whether the digital tacho reads in km/h or mph.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `M_DIGITAL_TACHO_EINH`· source: firmware-token

### `3000/99/10000000b` — M Drive setups: one or two  ·  _med_

Sets whether the M Drive menu offers two stored setups (M Drive 1 and M Drive 2) or a single one. Match it to the car's M Drive buttons.

| value | meaning |
|---|---|
| `0` | Two setups |
| `1` | One setup |

default `00`· token `MDRIVE_CONFIG`· source: firmware-trace

### `3000/100/00000001b` — M digital speedometer  ·  _med_

Enables the M-mode digital speedometer display in the head unit HMI, showing a large digital speed readout during sporty driving.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `M_DIGITAL_TACHO`· source: firmware-token

### `3000/100/00000010b` — M Drive menu  ·  _med_

Shows the M Drive menu, where the driver stores a preferred mix of engine, chassis, steering and stability control settings to call up with the M Drive button.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: vehicle type-key attribute group (FP category 13; 7 type tokens, e.g. 1J31,1J32,1J33,2T73) / vehicle type-key attribute group (FP category 25; 27 type tokens, e.g. 11CK,11CL,11DE,12CK) / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31) / vehicle type-key attribute group (FP category 25; 3 type tokens, e.g. 1J31,1J32,1J33)· token `MDRIVE`· source: firmware-trace

### `3000/100/00000100b` — NFC access (digital key)  ·  _med_

Shows the NFC access settings in the “Doors/Key” menu, where phones or cards set up as keys for the car are managed.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `NFC_SMART_ACCESS`· source: firmware-trace

### `3000/100/00001000b` — DSC Off menu  ·  _high_

Enables the DSC (Dynamic Stability Control) Off option in the driving mode/settings menu, allowing the driver to fully disable DSC. When not active, the DSC Off option is hidden.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: vehicle type-key attribute group (FP category 13; 7 type tokens, e.g. 1J31,1J32,1J33,2T73) / SIXT Deactivation of DSC menu / vehicle type-key attribute group (FP category 25; 27 type tokens, e.g. 11CK,11CL,11DE,12CK) / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31) / vehicle type-key attribute group (FP category 25; 3 type tokens, e.g. 1J31,1J32,1J33)· token `DSC_OFF`· source: firmware-token

### `3000/100/00010000b` — DSC settings menu  ·  _med_

Enables the DSC (Dynamic Stability Control) settings sub-menu in the HMI, providing access to DSC mode selection and related options.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `DSC_MENUE`· source: firmware-token

### `3000/100/00100000b` — EDC suspension menu (CIC)  ·  _med_

Enables the Electronic Damper Control (EDC) menu in the HMI for vehicles with adaptive suspension. Provides the user-facing damper mode selector.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 2VF Adaptive M running gear· token `EDC_CIC`· source: firmware-token

### `3000/100/01000000b` — Comfort access (window/sunroof opening)  ·  _med_

Enables the comfort opening feature, which allows windows and/or the sunroof to be opened by holding the unlock button on the key fob. Not available on Canadian-spec cars.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: NOT 838 Canadian version / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / vehicle type-key attribute group (FP category 1; 61 type tokens, e.g. 1D11,1D12,1D31,1D32) / vehicle type-key attribute group (FP category 1; 65 type tokens, e.g. 11CK,11DE,12CK,12DE) / vehicle type-key attribute group (FP category 1; 55 type tokens, e.g. 11CL,12CL,1K51,1K52) / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `COMFORT_OPENING`· source: firmware-token

### `3000/100/10000000b` — Oil level menu  ·  _high_

Shows the electronic oil level check in the vehicle status menu, so you can measure and read the engine oil level on the central display.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· token `OELSTANDSMENUE`· source: firmware-trace

### `3000/101/00000001b` — Oil level sensor (OENS) support  ·  _med_

Enables support for the oil level sensor (OENS = Ölstand-Echtzeitmessung, real-time oil level measurement), required for the oil level readout to function.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `OELSTAND_OENS`· source: firmware-token

### `3000/101/00000010b` — TV tuner conditional-access (CAS) menu  ·  _med_

Enables the Conditional Access System (CAS) menu for the CDMM television tuner, providing access to pay-TV smart-card/subscription management.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: FA-gated (depends on vehicle options)· token `CDMM_TV_CAS_MENUE`· source: firmware-token

### `3000/101/00000100b` — Analog AUX input  ·  _med_

Enables the analog AUX audio input source in the CDMM media manager, making the AUX IN socket selectable as an audio source in the media menu.

| value | meaning |
|---|---|
| `0` | Not active |

default `00`· gate: always (no FA gate)· token `CDMM_ANALOG_AUX`· source: firmware-token

### `3000/101/00001000b` — Auxiliary consumers display (EV)  ·  _med_

Shows the auxiliary consumers screen for electrified models, which lists how much power comfort features such as climate control are drawing.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `EV_AUXILIARY_CONSUMERS`· source: firmware-trace

### `3000/101/00010000b` — Handwriting recognition input  ·  _med_

Enables handwriting/gesture recognition as an input method on the iDrive touchpad, allowing the user to draw letters to enter destinations or search terms.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· token `HMI_HANDWRITING_RECOGNITION`· source: firmware-token

### `3000/101/00100000b` — Inductive car charging  ·  _med_

Turns on support for inductive (wireless) charging of the car's battery, for cars with the system installed. Adds a button in the parking menu, charging station settings and a positioning guide that helps you stop over the charging pad.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `INDUCTIVECHARGING`· source: firmware-trace

### `3000/101/01000000b` — RSE driver distraction relevant  ·  _med_

Marks the rear-seat entertainment (RSE) system as driver-distraction-relevant, enabling speed-dependent content restrictions on the RSE screens when viewed from the front.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `RSE_DRIVER_DISTRACTION_RELEVANT`· source: firmware-token

### `3000/101/10000000b` — Acoustic touch feedback  ·  _med_

Enables acoustic (audible click) feedback when the touchscreen or touchpad is tapped, providing haptic-style audio confirmation of touch inputs.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `ACOUSTIC_TOUCH_FEEDBACK`· source: firmware-token

### `3000/102/00011111b` — Seat belt reminder menu type  ·  _med_

Selects the type of seat belt reminder notification available to the driver/passenger. Controls whether the reminder shows a simple OK button or a deeper settings menu link.

| value | meaning |
|---|---|
| `1` | OK button only (V1) |
| `16` | Settings menu link (V2) |

default `00`· gate: always (no FA gate)· token `SEATBELTREMINDER_MENU_AVAILABLE`· source: firmware-token

### `3000/102/00100000b` — Seat belt reminder middle seat  ·  _med_

Enables seat belt reminder monitoring and notification for the rear middle seat position, in addition to the standard outer seat positions.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `SEATBELTREMINDER_MIDDLE_SEAT`· source: firmware-token

### `3000/102/11000000b` — Reserved (byte 102 bits 7,6)  ·  _low_

Purpose not determined from available sources. Unnamed reserved bits sharing byte 102 with SEATBELTREMINDER_MENU_AVAILABLE and SEATBELTREMINDER_MIDDLE_SEAT. No consumer found in NBTCarHU.c; likely consumed by HMI process on Jacinto node.

source: inferred

### `3000/103/00000111b` — Reserved (byte 103 bits 2,1,0)  ·  _low_

Purpose not determined from available sources. Unnamed reserved bits sharing byte 103 with CARSHARING and HYBRID_EFFICIENCY_GRAPHIC. No consumer found in NBTCarHU.c.

source: inferred

### `3000/103/00001000b` — Car sharing mode  ·  _med_

Enables car-sharing mode in the HMI, which adapts the system for flexible multi-driver use (e.g. anonymising personalisation, enabling guest profiles). Active when car-sharing preparation (5GC) is coded.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: NOT ECSM Deletion of Car Sharing Module / 5GC Preparation of Flexible Car Use· token `CARSHARING`· source: firmware-token

### `3000/103/00010000b` — Hybrid efficiency graphic  ·  _med_

Enables the hybrid-specific energy flow / efficiency graphic display in the HMI, showing battery charge state, regeneration, and power flow for hybrid models.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `HYBRID_EFFICIENCY_GRAPHIC`· source: firmware-token

### `3000/103/11100000b` — Reserved (byte 103 bits 7,6,5)  ·  _low_

Purpose not determined from available sources. Unnamed reserved bits sharing byte 103 with CARSHARING and HYBRID_EFFICIENCY_GRAPHIC. No consumer found in NBTCarHU.c.

source: inferred

### `3000/104/00001111b` — RSE seat longitudinal position threshold (driver)  ·  _med_

Sets the driver-seat forward/rearward position threshold for RSE screen visibility restriction. When the driver seat is forward of this position, RSE screens may be restricted to prevent distraction.

default `00`· gate: FA-gated (depends on vehicle options)· token `RSE_SEAT_LONGITUDINAL_POSITION_DR_THRESHOLD`· source: firmware-token

### `3000/104/11110000b` — RSE seat longitudinal position threshold (passenger)  ·  _med_

Sets the passenger-seat forward/rearward position threshold for RSE screen restriction. When the passenger seat is within this position range, RSE screen access rules apply.

| value | meaning |
|---|---|
| `0` | Not active |

default `00`· gate: FA-gated (depends on vehicle options)· token `RSE_SEAT_LONGITUDINAL_POSITION_PS_THRESHOLD`· source: firmware-token

### `3000/105/00001111b` — RSE seat backrest tilt threshold (passenger)  ·  _med_

Sets the passenger seat backrest recline angle threshold for RSE screen visibility. When the backrest is reclined beyond this angle, RSE restrictions may change.

default `00`· gate: FA-gated (depends on vehicle options)· token `RSE_SEAT_BACKREST_TILT_PS_THRESHOLD`· source: firmware-token

### `3000/105/00010000b` — Rolls-Royce RSE KISI activation  ·  _med_

Enables the RSE KISI (Kino Sitz Infotainment = cinema seat infotainment) feature for Rolls-Royce vehicles with rear-seat entertainment systems.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `RR_RSE_KISI_ACTIVATION`· source: firmware-token

### `3000/105/00100000b` — Automatic clock change (DST/GPS sync)  ·  _med_

Enables automatic clock adjustment for daylight saving time transitions and/or GPS time synchronisation. When active, the clock updates automatically without user intervention.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 606 Navigation system Business / 609 Professional navigation system / 802 Korean version / 807 Japanese version / 8AA Chinese version / 8LH Country control 04142 / 8LT Country control 04825  / 6NL Connecting Bluetooth and USB devices including BMW assist / 6AE TeleServices· token `CLOCK_CHANGE_AUTOMATIC`· source: firmware-token

### `3000/105/11000000b` — Reserved (byte 105 bits 7,6)  ·  _low_

Purpose not determined from available sources. Unnamed reserved bits sharing byte 105 with RSE thresholds, RR_RSE_KISI_ACTIVATION, and CLOCK_CHANGE_AUTOMATIC. No consumer found in NBTCarHU.c.

source: inferred

### `3000/106/00000111b` — Reserved (byte 106 bits 2,1,0)  ·  _low_

Purpose not determined from available sources. Firmware acknowledges this bit position (bare magic word in sysetshellevo) but ships no name. No consumer found in NBTCarHU.c.

source: inferred

### `3000/106/00001000b` — Spirit of Ecstasy settings (Rolls-Royce)  ·  _med_

Enables settings related to the Spirit of Ecstasy retractable bonnet mascot on Rolls-Royce vehicles, providing HMI controls for the feature.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `SETTINGS_SPIRITOFECSTASY`· source: firmware-token

### `3000/106/00010000b` — ZBE Touch interactive map  ·  _med_

Enables touch-based interactive map control via the ZBE (iDrive controller) touchpad, allowing the user to pan and zoom the navigation map by swiping on the iDrive dial surface.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 609 Professional navigation system· token `ZBE_TOUCH_INTERACTIVE_MAP`· source: firmware-token

### `3000/106/00100000b` — ZBE Touch speller input  ·  _med_

Enables the touchpad gesture speller on the ZBE iDrive controller, allowing the user to draw letters on the dial surface for text entry.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 609 Professional navigation system· token `ZBE_TOUCH_SPELLER`· source: firmware-token

### `3000/106/01000000b` — ZBE Touch browser swipe  ·  _med_

Enables touch-based list browsing via the ZBE iDrive controller touchpad, allowing the user to swipe through menus and lists by sliding a finger on the dial.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 609 Professional navigation system· token `ZBE_TOUCH_BROWSER`· source: firmware-token

### `3000/106/10000000b` — Interior light bar  ·  _med_

Shows the setting for the interior light bar (Lichtschwert, light sword) in the interior lighting menu, for cars with one installed.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `LICHTSCHWERT`· source: firmware-trace

### `3000/107/00000011b` — Reserved (byte 107 bits 1,0)  ·  _low_

Purpose not determined from available sources. Firmware acknowledges this bit position (bare magic word in sysetshellevo) but ships no name. No consumer found in NBTCarHU.c.

source: inferred

### `3000/107/00000100b` — Individual ambient lighting colour  ·  _med_

Enables the individual colour selection for interior ambient lighting, allowing the driver to choose from a custom colour palette rather than a preset colour set.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `INDIVIDUAL_AMBIENTELICHT`· source: firmware-token

### `3000/107/00001000b` — Ambient lighting permanent display (FES)  ·  _med_

Enables a permanent-on ambient lighting display mode for FES (Fahrerlebnisschalter / driving experience switch) variants, keeping the ambient light visible at all times regardless of other settings.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `AMBIENTELICHT_PERMANENTANZEIGE_FES`· source: firmware-token

### `3000/107/01110000b` — Remote HMI access level  ·  _med_

Sets the access level for Remote HMI (remote head-unit display/control, e.g. BMW Connected app mirroring or ConnectedDrive remote services).

| value | meaning |
|---|---|
| `2` | Restricted |

default `00`· gate: 6NR Apps / 6AE TeleServices· token `REMOTE_HMI`· source: firmware-token

### `3000/107/10000000b` — A4A (Apps for Auto) enabled  ·  _med_

Master enable bit for the Apps for Auto (A4A) smartphone integration framework. When active, the HMI exposes the A4A app infrastructure for connected smartphone apps.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 6NR Apps / 6AE TeleServices· token `A4A`· source: firmware-token

### `3000/108/00000001b` — A4A remote apps enabled  ·  _med_

Enables remote app execution within the A4A framework, allowing approved smartphone apps to run on or through the head unit via the connected phone.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 6NR Apps / 6AE TeleServices· token `A4A_REMOTE_APPS`· source: firmware-token

### `3000/108/00000010b` — Terminal UI  ·  _med_

Enables the Terminal UI feature, a screen-mirroring / remote-display interface allowing an external device to render its UI on the iDrive screen.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `TERMINAL_UI`· source: firmware-token

### `3000/108/00001100b` — Ambient lighting deactivation option (brand)  ·  _med_

Selects the brand-specific option for whether ambient lighting can be deactivated by the user, and which brand's implementation to use (BMW or MINI style).

| value | meaning |
|---|---|
| `1` | BMW-style deactivation |
| `2` | MINI-style deactivation |

default `00`· gate: FA-gated (depends on vehicle options)· token `DEAKTIVIERUNGSMOEGLICHKEIT_AMBILIGHT`· source: firmware-token

### `3000/108/00110000b` — Terminal UI port  ·  _med_

Selects which physical port(s) the Terminal UI remote-display feature operates over (SIA, KUZU, or both interfaces).

| value | meaning |
|---|---|
| `1` | SIA |
| `2` | KUZU |
| `3` | SIA and KUZU |

default `00`· gate: FA-gated (depends on vehicle options)· token `TERMINAL_UI_PORT`· source: firmware-token

### `3000/108/01000000b` — Simple AUX input 1  ·  _med_

Enables the first simplified AUX audio input channel in the CDMM media manager, typically used for a basic analog audio line input without full metadata support.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· token `CDMM_AUX_SIMPLE_1`· source: firmware-token

### `3000/108/10000000b` — Simple AUX input 2  ·  _med_

Enables the second simplified AUX audio input channel in the CDMM media manager.

| value | meaning |
|---|---|
| `0` | Not active |

default `00`· token `CDMM_AUX_SIMPLE_2`· source: firmware-token

### `3000/109/00000001b` — Speed lock: tuner/radio functions  ·  _med_

Controls whether tuner/radio functions (e.g. station search, frequency input) are locked above a certain speed. When active, these HMI interactions are blocked while driving.

| value | meaning |
|---|---|
| `0` | Not active (no lock) |
| `1` | Active (speed lock applied) |

default `00`· gate: always (no FA gate)· token `SPEEDLOCK_HMI_TUNER`· source: firmware-token

### `3000/109/00000010b` — RSE display brightness control  ·  _med_

Enables the brightness adjustment control for rear-seat entertainment (RSE) screens in the HMI, allowing the driver or passengers to change RSE screen brightness.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `RSE_BRIGHTNESS`· source: firmware-token

### `3000/109/00000100b` — Ambient/UI colour switch (model line)  ·  _med_

Enables the model-line-specific colour theme switch for the HMI and ambient lighting. When active, the system uses the colour scheme associated with the vehicle's line (Sport, Urban, Modern, Luxury).

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |
| `2` | SL09 |

default `00`· gate: vehicle type-key attribute group (FP category 12; 86 type tokens, e.g. 11CK,11CL,12CK,12CL) / 337 M Sports package / vehicle type-key attribute group (FP category 12; 79 type tokens, e.g. 11DE,12DE,1A31,1A32) / vehicle type-key attribute group (FP category 13; 28 type tokens, e.g. 1B71,1B72,1B91,1H91) / 7AC Sport Line / 7AD Urban Line / 7S1 Modern Line / 7S2 Luxury Line / numeric value-attribute 0321 (FP category 255) / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31) / 7B3 M Sport Edition / 7B1 Sport Line Edition· token `COLOUR_SWITCH`· source: firmware-token

### `3000/109/00001000b` — Ambient lighting brightness control  ·  _med_

Enables the ambient lighting brightness adjustment option in the HMI settings, allowing the driver to dim or brighten interior ambient light strips.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 563 Lights package / vehicle type-key attribute group (FP category 12; 86 type tokens, e.g. 11CK,11CL,12CK,12CL) / 337 M Sports package / vehicle type-key attribute group (FP category 12; 79 type tokens, e.g. 11DE,12DE,1A31,1A32) / vehicle type-key attribute group (FP category 13; 28 type tokens, e.g. 1B71,1B72,1B91,1H91) / 7AC Sport Line / 7AD Urban Line / 7S1 Modern Line / 7S2 Luxury Line / numeric value-attribute 0321 (FP category 255) / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31) / 7B3 M Sport Edition / 7B1 Sport Line Edition· token `HELLIGKEIT_AMBILIGHT`· source: firmware-token

### `3000/109/01110000b` — Colour switch line assignment  ·  _med_

Sets which vehicle design line's colour theme is applied. Determines the colour accent used in the iDrive UI and ambient lighting for Sport, Urban, Modern, or Luxury Line variants.

| value | meaning |
|---|---|
| `1` | Sport Line |
| `2` | Urban Line |
| `3` | Modern Line |
| `4` | Luxury Line |

default `00`· gate: 7S2 Luxury Line· token `COLOUR_SWITCH_LINES`· source: firmware-token

### `3000/109/10000000b` — High beam assistant (city lights)  ·  _med_

Enables the High Beam Assistant (automatic main beam control) feature in the HMI, providing the on/off setting and status display for the automatic high-beam system.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `HIGH_BEAM_ASSISTANT`· source: firmware-token

### `3000/110/00000001b` — Audible lock confirmation  ·  _med_

Offers a setting for a sound that confirms the car has locked when you lock it with the remote key. Enabled at the factory with the alarm system (S302) and set per market and model.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 302 Alarm system / 838 Canadian version / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93)· token `ACOUSTICAL_LOCK_CONFIRM`· source: firmware-token

### `3000/110/00000010b` — Torque distribution menu (xDrive/4WD)  ·  _med_

Enables the torque moment distribution menu in the HMI, showing the current xDrive torque split between front and rear axles.

| value | meaning |
|---|---|
| `1` | Active |

default `00`· gate: FA-gated (depends on vehicle options)· token `MOMENTDISTRIBUTION_MENU`· source: firmware-token

### `3000/110/00000100b` — NANP phone number format  ·  _med_

Enables North American Numbering Plan (NANP) phone number formatting in the HMI contact and call display, using the 10-digit +1 (NXX-NXX-XXXX) format.

| value | meaning |
|---|---|
| `0` | Off (international format) |
| `1` | On (NANP format) |

default `00`· gate: 838 Canadian version / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93)· token `NANP_FORMAT`· source: firmware-token

### `3000/110/00001000b` — Software version info request enabled  ·  _med_

Enables the ability to request and display software version information from within the HMI diagnostic/about screens.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `ENABLE_SW_INFO_REQUEST`· source: firmware-token

### `3000/110/00010000b` — Hill descent control (HDC) menu  ·  _med_

Enables the Hill Descent Control (HDC) menu entry in the HMI driving aids settings, allowing the driver to activate and configure the hill descent speed assist.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: vehicle type-key attribute group (FP category 128; 192 type tokens, e.g. 11CK,11CL,11DE,12CK)· token `HDC`· source: firmware-token

### `3000/110/00100000b` — Panoramic sunroof menu  ·  _med_

Enables the panoramic sunroof control entry in the HMI comfort/settings menu, providing shade and opening controls for the panoramic roof.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `PANORAMADACH`· source: firmware-token

### `3000/110/01000000b` — Arabic/Asian date format  ·  _med_

Enables the Arabic or Asian date display format variant in the HMI clock and calendar displays, using the appropriate regional format instead of the Western day/month/year convention.

| value | meaning |
|---|---|
| `0` | Off (Western format) |
| `1` | On (Arabic/Asian format) |

default `01`· gate: always (no FA gate)· token `DATUMSFORMAT_AR_ASIA`· source: firmware-token

### `3000/110/10000000b` — A4A app SWT enable  ·  _high_

SWT (Software Token / software-coded) enable bit for the A4A (Apps for Auto / smartphone projection) application. Decoded by the firmware switch for A4A app presence; a separate gate from the coding-only A4A bit at byte 107.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

_Token SWT_APP_A4A; traced in firmware FUN_002f58c4 switch case 6 (A4A); read from byte 0x6e mask 0x80. See cur_desc for full trace._

default `00`· gate: 6NR Apps· token `SWT_APP_A4A`· source: firmware-trace

### `3000/111/00000111b` — USB profile directory name  ·  _high_

Selects the brand-specific subdirectory name used by the Portation Master when importing/exporting user profiles to/from a USB drive. The directory name corresponds to the vehicle brand.

| value | meaning |
|---|---|
| `0` | BMW |
| `1` | BMW i |
| `2` | MINI |
| `3` | Rolls-Royce |
| `5` | J29 (special variant) |

_Token fUSB_DATA_DIRECTORY_NAME (displayed as USB_DATA_DIRECTORY_NAME in enum dict); firmware-traced via CPortationMaster getCodingProduktlinie at FUN_002c04a4; trace strings confirm field name and values. Default/valid=6 per firmware trace but enum names 0/1/2/3/5; value 6 not in enum may be the 'BMW Evo' default._

default `00`· gate: always (no FA gate)· token `fUSB_DATA_DIRECTORY_NAME`· source: firmware-trace

### `3000/111/00001000b` — Reserved (byte 111 bit 3)  ·  _low_

Purpose not determined from available sources. Unnamed reserved bit sharing byte 111 with USB_DATA_DIRECTORY_NAME, RR_RSE_NEW_CONCEPT_INFOTAINMENT, and HMI_MAIN_MENU_VERSION. No consumer found in NBTCarHU.c.

source: inferred

### `3000/111/00110000b` — Rolls-Royce RSE new infotainment concept  ·  _med_

Selects the RSE (Rear-Seat Entertainment) infotainment system concept type for Rolls-Royce vehicles, enabling a new-generation RSE display architecture.

| value | meaning |
|---|---|
| `0` | Inactive |

default `00`· gate: FA-gated (depends on vehicle options)· token `RR_RSE_NEW_CONCEPT_INFOTAINMENT`· source: firmware-token

### `3000/111/11000000b` — HMI main menu version/layout  ·  _med_

Selects the main menu layout version for the iDrive HMI. Different values select alternative home-screen arrangements.

| value | meaning |
|---|---|
| `0` | Standard |

default `00`· gate: FA-gated (depends on vehicle options)· token `HMI_MAIN_MENU_VERSION`· source: firmware-token

### `3000/112/00001111b` — Reserved (byte 112 bits 3,2,1,0)  ·  _low_

Purpose not determined from available sources. Unnamed reserved bits sharing byte 112 with A4A_LEGAL_DISCLAIMER. No consumer found in NBTCarHU.c.

source: inferred

### `3000/112/00010000b` — A4A legal disclaimer  ·  _med_

Enables the legal disclaimer screen that is displayed when the A4A (Apps for Auto / smartphone projection) session starts. Required for certain markets (Japan) and when TeleServices are active.

| value | meaning |
|---|---|
| `0` | Off (no disclaimer) |
| `1` | On (show disclaimer) |

default `00`· gate: 807 Japanese version / 6NR Apps / 6AE TeleServices· token `A4A_LEGAL_DISCLAIMER`· source: firmware-token

### `3000/112/11100000b` — Reserved (byte 112 bits 7,6,5)  ·  _low_

Purpose not determined from available sources. Unnamed reserved bits sharing byte 112 with A4A_LEGAL_DISCLAIMER. No consumer found in NBTCarHU.c.

source: inferred

### `3000/113/00000001b` — Voice message dictation  ·  _med_

Enables the voice dictation feature for composing messages (e.g. SMS, email) using the voice control system, transcribing spoken words into text.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `MESSAGE_DICTATION`· source: firmware-token

### `3000/113/00001110b` — Maximum voice dictation duration  ·  _med_

Sets the maximum duration in seconds allowed for a single voice dictation recording session. Higher values allow longer spoken messages.

| value | meaning |
|---|---|
| `1` | 5 seconds |
| `2` | 10 seconds |
| `3` | 15 seconds |
| `4` | 20 seconds |
| `6` | 30 seconds |

default `01`· gate: FA-gated (depends on vehicle options)· token `MAX_DICTATION_TIME_SEC`· source: firmware-token

### `3000/113/00010000b` — Terminal UI link (screen mirroring link)  ·  _med_

Enables the Terminal UI link function, establishing the connection between the Terminal UI remote display client and the iDrive screen rendering pipeline.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `TERMINAL_UI_LINK`· source: firmware-token

### `3000/113/11100000b` — Reserved (byte 113 bits 7,6,5)  ·  _low_

Purpose not determined from available sources. Unnamed reserved bits sharing byte 113 with MESSAGE_DICTATION, MAX_DICTATION_TIME_SEC, and TERMINAL_UI_LINK. No consumer found in NBTCarHU.c.

source: inferred

### `3000/114/11111111b` — Reserved (bytes 114–126)  ·  _low_

Purpose not determined from available sources. Unnamed 13-byte block following the MESSAGE_DICTATION / TERMINAL_UI_LINK fields. No consumer found in NBTCarHU.c; likely consumed by the HMI/GUI process on the Jacinto node.

source: inferred

### `3000/127/00111111b` — Reserved (byte 127 bits 5–0)  ·  _low_

Purpose not determined from available sources. Unnamed 6-bit field sharing byte 127 with ECO_SLOPE_ON_OFF and ECO_CURVE_ON_OFF. No consumer found in NBTCarHU.c.

source: inferred

### `3000/127/01000000b` — ECO Pro slope guidance on/off  ·  _med_

Enables the ECO Pro slope/gradient driving guidance feature, which adjusts acceleration and deceleration coaching on hills to maximise fuel economy.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `01`· gate: always (no FA gate)· token `ECO_SLOPE_ON_OFF`· source: firmware-token

### `3000/127/10000000b` — ECO Pro curve guidance on/off  ·  _med_

Enables the ECO Pro curve/cornering guidance feature, providing coaching to lift off the accelerator before bends to save fuel.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `01`· gate: always (no FA gate)· token `ECO_CURVE_ON_OFF`· source: firmware-token

### `3000/128/00000001b` — ECO Pro transmission guidance on/off  ·  _med_

Enables the ECO Pro transmission (gearshift) coaching guidance, advising the driver when to upshift for optimal fuel economy.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `01`· gate: always (no FA gate)· token `ECO_TRANS_ON_OFF`· source: firmware-token

### `3000/128/00000010b` — ECO Pro auxiliary consumers guidance on/off  ·  _med_

Enables ECO Pro coaching for auxiliary electrical consumers (climate, seat heating, etc.), advising the driver to reduce consumption to improve efficiency.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `01`· gate: FA-gated (depends on vehicle options)· token `ECO_AUX_ON_OFF`· source: firmware-token

### `3000/128/00011100b` — ECO PRO route: ferry consumption factor  ·  _med_

Sets the factor that the navigation's ECO PRO (energy-saving) route calculation applies to ferry sections when it estimates a route's fuel or energy use, from 0 to 4 times.

| value | meaning |
|---|---|
| `0` | Factor 0 |
| `1` | Factor 0.25 |
| `2` | Factor 0.5 |
| `3` | Factor 0.75 |
| `4` | Factor 1 |
| `5` | Factor 2 |
| `6` | Factor 4 |

default `00`· gate: always (no FA gate)· token `ECO_FERRY_CONS`· source: firmware-trace

### `3000/128/00100000b` — ECO Pro tips new layout  ·  _med_

Enables the new-generation ECO Pro tips/coaching screen layout, replacing the legacy layout with an updated visual design.

| value | meaning |
|---|---|
| `0` | Off (legacy layout) |
| `1` | On (new layout) |

default `00`· gate: FA-gated (depends on vehicle options)· token `ECO_TIPS_LAYOUT_NEW`· source: firmware-token

### `3000/128/01000000b` — ECO Pro one-pedal drive tips  ·  _med_

Enables ECO Pro coaching tips specific to one-pedal driving technique (lift-off coasting/regeneration), relevant for hybrid and EV models.

| value | meaning |
|---|---|
| `0` | Not active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ECO_TIPPS_ONEPADDLEDRIVE`· source: firmware-token

### `3000/128/10000000b` — Reserved (byte 128 bit 7)  ·  _low_

Purpose not determined from available sources. Unnamed reserved bit sharing byte 128 with ECO_TRANS_ON_OFF, ECO_AUX_ON_OFF, ECO_FERRY_CONS, ECO_TIPS_LAYOUT_NEW, and ECO_TIPPS_ONEPADDLEDRIVE. No consumer found in NBTCarHU.c.

source: inferred

### `3000/129/00111111b` — Reserved (byte 129 bits 5–0)  ·  _low_

Purpose not determined from available sources. Unnamed 6-bit field sharing byte 129 with DOOR_LOCK_AFTER_DRIVING_AWAY and A4A_VOICE_APP_SUPPORT. No consumer found in NBTCarHU.c.

source: inferred

### `3000/129/01000000b` — Auto door lock when driving away  ·  _med_

Enables automatic door locking when the vehicle reaches a set speed after pulling away, without requiring the driver to manually lock the doors.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `DOOR_LOCK_AFTER_DRIVING_AWAY`· source: firmware-token

### `3000/129/10000000b` — A4A voice app support  ·  _med_

Enables voice command integration for A4A (Apps for Auto) smartphone apps, allowing connected apps to be controlled via the vehicle's voice recognition system.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `A4A_VOICE_APP_SUPPORT`· source: firmware-token

### `3000/130/00111111b` — Reserved (byte 130 bits 5–0)  ·  _low_

Purpose not determined from available sources. Unnamed 6-bit field sharing byte 130 with DEPARTURE_TIME_CLIMATE and COVER_FLOW. No consumer found in NBTCarHU.c.

source: inferred

### `3000/130/01000000b` — Departure time climate pre-conditioning  ·  _med_

Enables the departure time pre-conditioning feature, allowing the user to schedule the climate control to reach the desired temperature before entering the vehicle.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `DEPARTURE_TIME_CLIMATE`· source: firmware-token

### `3000/130/10000000b` — Cover Flow album browser  ·  _med_

Enables the Cover Flow album artwork browser in the audio/media player, displaying album art in a horizontally-scrollable 3D carousel view.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 609 Professional navigation system· token `COVER_FLOW`· source: firmware-token

### `3000/131/11111111b` — Reserved (bytes 131–132)  ·  _low_

Purpose not determined from available sources. Unnamed 2-byte block following DEPARTURE_TIME_CLIMATE and COVER_FLOW. No consumer found in NBTCarHU.c.

source: inferred

### `3000/133/00000011b` — Reserved (byte 133 bits 1,0)  ·  _low_

Purpose not determined from available sources. Unnamed 2-bit field sharing byte 133 with HMI_BRAND, M_VEHICLE, and M_DRIVE_SYSTEMS. No consumer found in NBTCarHU.c.

source: inferred

### `3000/133/00111100b` — Brand theme  ·  _med_

Sets which brand's look the head unit uses, including logos, colors and menu styling. Set it to match the car's brand.

| value | meaning |
|---|---|
| `0` | BMW |
| `1` | BMW i |
| `2` | MINI |
| `3` | Rolls-Royce |
| `4` | BMW M |
| `5` | Toyota Supra |

default `00`· gate: always (no FA gate)· token `HMI_BRAND`· source: firmware-trace

### `3000/133/01000000b` — M model  ·  _med_

Tells the head unit the car is a BMW M model, so it offers M-specific menus and graphics. Enable it only on an M model.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `M_VEHICLE`· source: firmware-token

### `3000/133/10000000b` — M Drive systems enable  ·  _med_

Enables the full M Drive Systems integration, activating M-specific powertrain and chassis control displays and settings menus (M differential, M suspension modes, etc.).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `M_DRIVE_SYSTEMS`· source: firmware-token

### `3000/134/00000111b` — Reserved (byte 134 bits 2,1,0)  ·  _low_

Purpose not determined from available sources. Unnamed 3-bit field sharing byte 134 with TRACTION_DEMAND_CONTROL, BARGEIN, GOOGLE_LOCAL_VOICE_SEARCH, and EWS. No consumer found in NBTCarHU.c.

source: inferred

### `3000/134/00001000b` — Traction demand control menu  ·  _med_

Enables the traction demand control menu in the HMI, which may allow selection of traction/all-wheel-drive demand mode settings for compatible drivetrains.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `TRACTION_DEMAND_CONTROL`· source: firmware-token

### `3000/134/00010000b` — Voice control barge-in  ·  _med_

Enables the voice control barge-in feature, allowing the driver to start speaking a voice command without pressing a button, even while audio is playing. Requires navigation and steering wheel buttons.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 606 Navigation system Business / 609 Professional navigation system / 249 Multifunction for steering wheel / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `BARGEIN`· source: firmware-token

### `3000/134/00100000b` — Reserved (byte 134 bit 5)  ·  _low_

Purpose not determined from available sources. Unnamed bit sharing byte 134 with TRACTION_DEMAND_CONTROL, BARGEIN, GOOGLE_LOCAL_VOICE_SEARCH, and EWS. No consumer found in NBTCarHU.c.

source: inferred

### `3000/134/01000000b` — Google local voice search  ·  _med_

Enables Google-powered local voice search integration, allowing the user to search for points of interest and information using Google voice recognition.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `GOOGLE_LOCAL_VOICE_SEARCH`· source: firmware-token

### `3000/134/10000000b` — Emergency warning broadcasts  ·  _med_

Shows emergency warning messages that broadcasters send over digital radio or TV as a pop-up on the central display, in markets where such warnings are broadcast.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `EWS`· source: firmware-trace

### `3000/135/00000001b` — A4A speech-to-text speller input  ·  _med_

Enables speech-to-text (STT) input for the A4A speller, allowing the user to dictate text into A4A connected app text fields using the vehicle's microphone.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `01`· gate: NOT 6NR Apps / 6VB Infotainment control / 6AE TeleServices· token `A4A_STT_SPELLER_INPUT`· source: firmware-token

### `3000/135/00000010b` — A4A status bar notifications  ·  _med_

Enables notification display from A4A connected smartphone apps in the iDrive status bar, showing app alerts and incoming notifications.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `01`· token `A4A_STATUS_BAR_NOTIFICATION`· source: firmware-token

### `3000/135/00000100b` — A4A calendar widget  ·  _med_

Enables the calendar/agenda widget for A4A connected apps, displaying upcoming appointments from the connected smartphone's calendar on the iDrive home screen.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `01`· token `A4A_CALENDER_WIDGET`· source: firmware-token

### `3000/135/11111000b` — Reserved (byte 135 bits 7–3)  ·  _low_

Purpose not determined from available sources. Unnamed 5-bit field sharing byte 135 with A4A_STT_SPELLER_INPUT, A4A_STATUS_BAR_NOTIFICATION, and A4A_CALENDER_WIDGET. No consumer found in NBTCarHU.c.

source: inferred

### `3000/136/00000111b` — Ambient/UI colour ensemble (Rolls-Royce)  ·  _med_

Selects the ambient lighting and UI colour ensemble for Rolls-Royce vehicles, corresponding to the vehicle's interior colour scheme option.

| value | meaning |
|---|---|
| `0` | Not active |

default `00`· gate: FA-gated (depends on vehicle options)· token `COLOUR_SWITCH_ENSEMBLE`· source: firmware-token

### `3000/136/00111000b` — Standstill rule for Office messages  ·  _med_

Sets the standstill condition the head unit checks before it lifts the driving lock on Office messages: none, the parking brake set, the transmission in Park, both or either one. Rules on driver distraction vary by country.

| value | meaning |
|---|---|
| `0` | None |
| `1` | Parking brake set |
| `2` | Transmission in Park |
| `3` | Parking brake and Park |
| `4` | Parking brake or Park |

default `00`· gate: FA-gated (depends on vehicle options)· token `OFFICE_MESSAGES_SPEEDLOCK_CONDITION`· source: firmware-token

### `3000/136/11000000b` — Reserved (byte 136 bits 7,6)  ·  _low_

Purpose not determined from available sources. Unnamed 2-bit field sharing byte 136 with COLOUR_SWITCH_ENSEMBLE and OFFICE_MESSAGES_SPEEDLOCK_CONDITION. No consumer found in NBTCarHU.c.

source: inferred

### `3000/137/00000011b` — Reserved (byte 137 bits 1,0)  ·  _low_

Purpose not determined from available sources. Unnamed 2-bit field sharing byte 137 with MYINFO_DRIVING_TEXT_LENGTH and AKD_DRIVING_TEXT_LENGTH. No consumer found in NBTCarHU.c.

source: inferred

### `3000/137/00011100b` — Text while driving: My Info messages  ·  _med_

Limits how much of a My Info message the head unit shows while the car is moving: no details, the first page or the whole text. Set per market at the factory, as rules on driver distraction vary by country.

| value | meaning |
|---|---|
| `0` | No details |
| `1` | First page only |
| `7` | Full text |

default `00`· gate: 807 Japanese version / 810 Australian version / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / 8LH Country control 04142 / 8LT Country control 04825 · token `MYINFO_DRIVING_TEXT_LENGTH`· source: firmware-token

### `3000/137/11100000b` — Text while driving: AKD messages  ·  _med_

Limits how much of an AKD message the head unit shows while the car is moving: no details, the first page or the whole text. Set per market at the factory, as rules on driver distraction vary by country.

| value | meaning |
|---|---|
| `0` | No details |
| `1` | First page only |
| `7` | Full text |

default `00`· gate: 807 Japanese version / 810 Australian version / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / 8LH Country control 04142 / 8LT Country control 04825 · token `AKD_DRIVING_TEXT_LENGTH`· source: firmware-token

### `3000/138/00000111b` — Text while driving: BMW Info messages  ·  _med_

Limits how much of a BMW Info message (a message BMW sends to the car) the head unit shows while the car is moving: no details, the first page or the whole text. Set per market at the factory, as rules on driver distraction vary by country.

| value | meaning |
|---|---|
| `0` | No details |
| `1` | First page only |
| `7` | Full text |

default `00`· gate: 807 Japanese version / 810 Australian version / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / 8LH Country control 04142 / 8LT Country control 04825 · token `BMWINFO_DRIVING_TEXT_LENGTH`· source: firmware-token

### `3000/138/00111000b` — Standstill rule for Services messages  ·  _med_

Sets the standstill condition the head unit checks before it lifts the driving lock on messages in the Services area: none, the parking brake set, the transmission in Park, both or either one. Rules on driver distraction vary by country.

| value | meaning |
|---|---|
| `0` | None |
| `1` | Parking brake set |
| `2` | Transmission in Park |
| `3` | Parking brake and Park |
| `4` | Parking brake or Park |

default `00`· gate: FA-gated (depends on vehicle options)· token `SERVICES_MESSAGES_SPEEDLOCK_CONDITION`· source: firmware-token

### `3000/138/11000000b` — Reserved (byte 138 bits 7,6)  ·  _low_

Purpose not determined from available sources. Unnamed 2-bit field sharing byte 138 with BMWINFO_DRIVING_TEXT_LENGTH and SERVICES_MESSAGES_SPEEDLOCK_CONDITION. No consumer found in NBTCarHU.c.

source: inferred

### `3000/139/11111111b` — Wireless charging zoom threshold 1  ·  _med_

First map zoom level threshold for the wireless charging tray camera overlay. When the navigation map reaches this zoom level, the inductive charging position indicator behaviour changes.

default `00`· gate: always (no FA gate)· token `INDUCTIVECHARGING_ZOOM_THRESHOLD_1`· source: firmware-token

### `3000/140/11111111b` — Wireless charging zoom threshold 2  ·  _med_

Second map zoom level threshold for the wireless charging tray camera overlay.

default `00`· gate: always (no FA gate)· token `INDUCTIVECHARGING_ZOOM_THRESHOLD_2`· source: firmware-token

### `3000/141/11111111b` — Wireless charging zoom threshold 3  ·  _med_

Third map zoom level threshold for the wireless charging tray camera overlay.

default `00`· gate: always (no FA gate)· token `INDUCTIVECHARGING_ZOOM_THRESHOLD_3`· source: firmware-token

### `3000/142/11111111b` — Wireless charging tray X position (CPM)  ·  _med_

Sets the X-axis position of the wireless charging tray indicator overlay on the camera/map view, in centimetres relative to the charging position marker (CPM).

default `07FF`· gate: always (no FA gate)· token `INDUCTIVECHARGING_POSXCPM`· source: firmware-token

### `3000/144/11111111b` — Wireless charging tray Y position (CPM)  ·  _med_

Sets the Y-axis position of the wireless charging tray indicator overlay on the camera/map view, in centimetres relative to the charging position marker.

default `07FF`· gate: always (no FA gate)· token `INDUCTIVECHARGING_POSYCPM`· source: firmware-token

### `3000/146/00011111b` — Speed lock: lower speed threshold  ·  _high_

Sets the speed the car must slow to before the speed locks on the central display are lifted again; at 0 km/h they stay on until the car stops. Keep it below “Speed lock: upper speed threshold” (`3000/147/00111111b`). Rules on driver distraction vary by country.

Number: raw 0–31 × 1 + 0 km/h; typical 0, 3, 5

default `03`· token `SPEEDLOCK_SPEEDVALUE_MIN`· source: firmware-trace

### `3000/146/11100000b` — Reserved (byte 146 bits 7,6,5)  ·  _low_

Purpose not determined from available sources. Unnamed 3-bit field sharing byte 146 with SPEEDLOCK_SPEEDVALUE_MIN. No consumer found in NBTCarHU.c.

source: inferred

### `3000/147/00111111b` — Speed lock: upper speed threshold  ·  _high_

Sets the speed above which the speed locks on the central display take effect. They are lifted again once the car slows to “Speed lock: lower speed threshold” (`3000/146/00011111b`). If this value isn't above the lower threshold, the head unit uses the lower threshold plus 1 km/h. Rules on driver distraction vary by country.

Number: raw 0–63 × 1 + 0 km/h; typical 5, 8, 10

default `05`· token `SPEEDLOCK_SPEEDVALUE_MAX`· source: firmware-trace

### `3000/147/01000000b` — Air ioniser  ·  _med_

Enables the interior air ioniser function in the HMI, providing the control menu for the cabin air ionisation system.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `IONISATOR`· source: firmware-token

### `3000/147/10000000b` — Reserved (byte 147 bit 7)  ·  _low_

Purpose not determined from available sources. Unnamed reserved bit sharing byte 147 with SPEEDLOCK_SPEEDVALUE_MAX and IONISATOR. No consumer found in NBTCarHU.c.

source: inferred

### `3000/148/11111111b` — Wireless charging zoom threshold 4  ·  _med_

Fourth map zoom level threshold for the wireless charging tray camera overlay.

default `00`· gate: always (no FA gate)· token `INDUCTIVECHARGING_ZOOM_THRESHOLD_4`· source: firmware-token

### `3000/149/11111111b` — Wireless charging zoom threshold 5  ·  _med_

Fifth map zoom level threshold for the wireless charging tray camera overlay.

default `00`· gate: always (no FA gate)· token `INDUCTIVECHARGING_ZOOM_THRESHOLD_5`· source: firmware-token

## Datagroup 0x3001 (140 parameters)

### `3001/0/00000001b` — FBM: Entertainment shortcut  ·  _med_

Controls whether the Entertainment shortcut appears in the favorites/function-bar menu (FBM = Favoritenband-Menü). When active, a direct-access button for the audio/entertainment source is shown.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: always (no FA gate)· token `FBM_ENT`· source: firmware-token

### `3001/0/00000010b` — FBM: Telephone shortcut  ·  _med_

Controls whether the Phone shortcut appears in the favorites/function-bar menu.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: always (no FA gate)· token `FBM_TEL`· source: firmware-token

### `3001/0/00000100b` — FBM: Navigation shortcut  ·  _med_

Controls whether the Navigation shortcut appears in the favorites/function-bar menu.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: always (no FA gate)· token `FBM_NAVI`· source: firmware-token

### `3001/0/00001000b` — FBM: BMW Apps (IBA) shortcut  ·  _med_

Controls whether the BMW Apps (IBA = Integrierte BMW Applikationen) shortcut appears in the favorites bar menu.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: always (no FA gate)· token `FBM_IBA`· source: firmware-token

### `3001/0/00010000b` — FBM: Menu jumps enabled  ·  _med_

Enables direct menu-jump shortcuts in the favorites bar, allowing single-press navigation to sub-menus.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: always (no FA gate)· token `FBM_MENUJUMPS`· source: firmware-token

### `3001/0/00100000b` — FBM: Other shortcuts enabled  ·  _med_

Enables the "Other" catch-all shortcut slot in the favorites/function-bar menu.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: always (no FA gate)· token `FBM_OTHER`· source: firmware-token

### `3001/0/01000000b` — FBM: Short info bar visible  ·  _med_

Controls display of a condensed information bar (short-info overlay) within the favorites menu context.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: always (no FA gate)· token `FBM_SHORT_INFO`· source: firmware-token

### `3001/0/10000000b` — FBM: Detailed info view enabled  ·  _med_

Enables the expanded/detailed-information view in the favorites menu context.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: always (no FA gate)· token `FBM_DETAILED_INFO`· source: firmware-token

### `3001/1/00000001b` — FBM: Default menu layout active  ·  _med_

Sets the default menu layout mode for the favorites/function-bar; when set, the out-of-box default layout is used.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: always (no FA gate)· token `FBM_DEFAULT`· source: firmware-token

### `3001/1/00001110b` — FBM: Button layout selection  ·  _med_

Selects the number of buttons displayed in the function bar/favorites menu. Determines whether 8-button or 6-button layout is used.

| value | meaning |
|---|---|
| `1` | 8-button layout |
| `5` | 6-button layout |

default `00`· gate: always (no FA gate)· token `FBM_SELECTION`· source: firmware-token

### `3001/1/00010000b` — Tyre pressure monitor (RDC) fitted  ·  _med_

Indicates that a direct tyre-pressure monitoring system (RDC = Reifendruckkontrolle) is installed. Enables the RDC display in the HU. FA-gated by 2VB.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 2VB Tire Pressure Monitor· token `RDC`· source: firmware-token

### `3001/1/00100000b` — Tyre pressure safety mode  ·  _med_

Enables a safety-mode variant of the RDC display (e.g. mandatory pressure warnings).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `RDC_SAFETY`· source: firmware-token

### `3001/1/01000000b` — Run-flat indicator (RPA) fitted  ·  _med_

Enables the run-flat / flat-tyre indicator (RPA = Reifenpannenanzeige) in the HU menu. Appears when no RDC sensor ring is installed but a wheel deflation sensor is.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· token `RPA`· source: firmware-token

### `3001/1/10000000b` — Independent air-conditioning mode available  ·  _med_

Enables the independent auxiliary air-conditioning mode (Standklima) in the climate control menus. FA-gated by 534 (automatic climate control).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 534 Automatic climate control· token `HVAC_INDEPENDENT_AIR`· source: firmware-token

### `3001/2/00000001b` — Rear climate control activation  ·  _med_

Activates the rear-seat (fond) climate control zone functionality.

| value | meaning |
|---|---|
| `0` | Inactive/Off |
| `1` | Active/On |

default `00`· gate: FA-gated (depends on vehicle options)· token `HVAC_FOND_ACTIVATION`· source: firmware-token

### `3001/2/00000010b` — Independent auxiliary heater available  ·  _med_

Enables the Zuheizer/Standheizung independent heater mode in climate menus.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `HVAC_INDEPENDENT_HEATING`· source: firmware-token

### `3001/2/00000100b` — Climate efficiency display (MSA)  ·  _med_

Enables efficiency/eco readout related to the MSA (Mehrfachsteuergerät Aussentemperatur / multi-stage aircon) in the climate view.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `HVAC_MSA_EFFICIENCY`· source: firmware-token

### `3001/2/00001000b` — Remote climate pre-conditioning  ·  _med_

Enables remote pre-conditioning of the climate system via BMW ConnectedDrive / Assist services.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· token `ASSIST_REMOTE_HVAC`· source: firmware-token

### `3001/2/01110000b` — Cross-traffic alert flash rate  ·  _high_

Sets how fast the cross-traffic alert markers pulse in the parking view on the central display while traffic approaches from the side.

| value | meaning |
|---|---|
| `0` | Pulses every 0.6 s |
| `1` | Pulses every 0.33 s |

default `00`· gate: always (no FA gate)· token `CTA_FREQUENZ`· source: firmware-trace

### `3001/2/10000000b` — Speed limit information display  ·  _med_

Enables speed limit sign recognition and display in the instrument cluster / HU (requires camera-based KAFAS or map data, FA-gated by 8TH).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 8TH Speed limit info· token `SPEEDLIMIT_INFO`· source: firmware-token

### `3001/3/00000001b` — Rear monitor activation method  ·  _med_

Sets how the rear-seat RSE monitor is activated: via a momentary button (TASTER) or latching switch (SCHALTER).

| value | meaning |
|---|---|
| `0` | Button (momentary) |
| `1` | Switch (latching) |

default `00`· gate: FA-gated (depends on vehicle options)· token `AKTIVIERUNG_FONDMONITOR`· source: firmware-token

### `3001/3/00000010b` — PDC flank protection (side sensors)  ·  _med_

Enables lateral/flank obstacle detection via PDC side sensors (PMA). FA-gated by 5DP (ParkMaster).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 5DP PMA· token `PDC_FLANKENSCHUTZ`· source: firmware-token

### `3001/3/00000100b` — USB port fitted  ·  _med_

Indicates that USB connectivity is available in this vehicle. Enables USB source selection and charging in the HU. Multiple FA options trigger this.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 606 Navigation system Business / 609 Professional navigation system / 6NH Hands-free system with USB interface / 6NR Apps / 6NS Comfort telephony with expanded smartphone connection / 6AE TeleServices / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `USB_AVAILABLE`· source: firmware-token

### `3001/3/00001000b` — PDC system fitted  ·  _med_

Master macro flag indicating that a Park Distance Control system (PDC) is installed. Enables PDC display, graphics and audio. FA-gated by 508/5DP/507.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 508 Park distance control (PDC) / 5DP PMA / 507 Park Distance Control (PDC), rear· token `MACRO_PDC`· source: firmware-token

### `3001/3/00110000b` — PDC front sensor count  ·  _med_

Specifies the number of PDC ultrasonic sensors fitted at the front of the vehicle. KEIN_SENSOR = no front sensors.

| value | meaning |
|---|---|
| `0` | No sensor |

default `00`· gate: 508 Park distance control (PDC)· token `PDC_SENSOR_VORN`· source: firmware-token

### `3001/3/01000000b` — Settings info display available  ·  _med_

Enables an information/settings display sub-page within the HU settings menu.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· token `SETTINGS_INFO_DISPLAY`· source: firmware-token

### `3001/3/10000000b` — Powered tailgate opening angle setting  ·  _med_

Enables adjustment of the maximum opening angle for an electrically-powered tailgate/boot lid.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `BACKDOOR_OPENINGANGLE`· source: firmware-token

### `3001/4/11111111b` — Camera module video connection  ·  _high_

Tells the head unit how the camera module's video (rear view, top view and side view cameras) is wired: which video input it arrives on, directly or through an external video switch, and whether the rear-seat screens get it too. For cars with the rear-view camera (S3AG). Set it to match the car's wiring; a mismatch can keep the camera picture from reaching the screen.

| value | meaning |
|---|---|
| `1` | Analog input 1, rear screens too |
| `5` | Via video switch, input 1 |
| `11` | Analog input 1, no rear screens |
| `25` | Ethernet video |
| `255` | None |

default `FF`· gate: 3AG Rear view camera / 609 Professional navigation system· token `CAM_ECU`· source: firmware-trace

### `3001/5/11111111b` — Night vision video connection  ·  _high_

Tells the head unit how the night vision camera's video is wired: which video input it arrives on and whether the rear-seat screens get it too. Set it to match the car's wiring; a mismatch can keep the night vision picture from reaching the screen.

| value | meaning |
|---|---|
| `1` | Analog input 1, rear screens too |
| `2` | Analog input 2, rear screens too |
| `11` | Analog input 1, no rear screens |
| `12` | Analog input 2, no rear screens |
| `25` | Ethernet video |
| `255` | None |

default `FF`· gate: FA-gated (depends on vehicle options)· token `NVC`· source: firmware-trace

### `3001/6/11111111b` — MMC unit video connection  ·  _high_

Tells the head unit how the MMC unit's video is wired: which of the head unit's analog video inputs it uses, directly or through an external video switch. Set it to match the car's equipment; a mismatch can keep its picture from reaching the screens.

| value | meaning |
|---|---|
| `1` | Analog input 1 |
| `3` | Analog input 3 |
| `7` | Via video switch, input 3 |
| `255` | None |

default `FF`· gate: FA-gated (depends on vehicle options)· token `MMC`· source: firmware-trace

### `3001/7/11111111b` — TV tuner video connection  ·  _high_

Tells the head unit how the TV tuner's video is wired: which of the head unit's analog video inputs it uses, directly or through an external video switch. Set it to match the car's equipment; a mismatch can keep the TV picture from reaching the screens.

| value | meaning |
|---|---|
| `1` | Analog input 1 |
| `4` | Analog input 4 |
| `10` | Via video switch, input 4 |
| `255` | None |

default `FF`· gate: FA-gated (depends on vehicle options)· token `TV`· source: firmware-trace

### `3001/8/11111111b` — Windshield camera (KAFAS) video connection  ·  _med_

Tells the head unit how video from the camera-based driver assistance unit (KAFAS) behind the windshield is wired into the car's video network. Best left unchanged.

| value | meaning |
|---|---|
| `41` | Value 41 |
| `255` | None |

default `FF`· gate: always (no FA gate)· token `KAFAS`· source: firmware-trace

### `3001/9/11111111b` — Head unit video playback  ·  _med_

Sets how video from the head unit's own sources (disc, hard drive, USB, browser, Wi-Fi, Bluetooth and DMB TV) and its first AUX video input is routed to the screens. With “None”, the head unit has no video route for them. Best left unchanged.

| value | meaning |
|---|---|
| `21` | Internal video input |
| `255` | None |

default `FF`· gate: always (no FA gate)· token `HU_INTERNAL_VIDEO_PLAYBACK`· source: firmware-trace

### `3001/10/11111111b` — Rear-seat video playback  ·  _med_

Sets how video from the rear-seat entertainment system's own sources (its disc drive and USB port) is routed to the screens. With “None”, the head unit has no video route for them. Best left unchanged.

| value | meaning |
|---|---|
| `21` | Internal video input |
| `255` | None |

default `FF`· gate: FA-gated (depends on vehicle options)· token `RSE_INTERNAL_VIDEO_PLAYBACK`· source: firmware-trace

### `3001/11/11111111b` — AUX input 2 (rear-seat entertainment)  ·  _high_

Tells the head unit how the second auxiliary (AUX) video input of the rear-seat entertainment system is wired, so its picture can be switched to the rear screens. It reaches the rear screens only, not the central display. With “None”, it has no video route.

| value | meaning |
|---|---|
| `23` | Rear-seat unit input 4 |
| `255` | None |

default `FF`· gate: FA-gated (depends on vehicle options)· token `AUX2_IN_RSE`· source: firmware-trace

### `3001/12/11111111b` — AUX input 3 (rear-seat entertainment)  ·  _high_

Tells the head unit how the third auxiliary (AUX) video input of the rear-seat entertainment system is wired, so its picture can be switched to the rear screens. It reaches the rear screens only, not the central display. With “None”, it has no video route.

| value | meaning |
|---|---|
| `24` | Rear-seat unit input 8 |
| `255` | None |

default `FF`· gate: FA-gated (depends on vehicle options)· token `AUX3_IN_RSE`· source: firmware-trace

### `3001/13/00001111b` — CAN gateway routing table selection  ·  _med_

Selects which CAN gateway routing table is loaded for inter-bus message forwarding. Determines which signals are bridged between CAN buses.

| value | meaning |
|---|---|
| `0` | Table 0 |
| `1` | Table 1 |
| `2` | Table 2 |
| `3` | Table 3 |
| `4` | Table 4 |
| `5` | Table 5 |
| `6` | Table 6 |
| `7` | Table 7 |
| `8` | Table 8 |
| `9` | Table 9 |
| `10` | Table 10 |

default `00`· gate: FA-gated (depends on vehicle options)· token `GATEWAYTABLE`· source: firmware-token

### `3001/13/01110000b` — Parking Assistant: park-in version  ·  _high_

Tells the head unit which generation of the Parking Assistant, which steers the car into a parking space, is installed, so the parking screens match it. For cars with the Parking Assistant (S5DP). The two second-generation values differ in whether the parking settings offer the Parking Assistant sound, a signal when a space is found; generation 3 always offers it.

| value | meaning |
|---|---|
| `0` | None |
| `1` | Generation 1 |
| `2` | Generation 2, no sound setting |
| `3` | Generation 2, with sound setting |
| `4` | Generation 3 |

default `00`· gate: 5DP PMA· token `MACRO_PMA_EINPARKEN`· source: firmware-trace

### `3001/13/10000000b` — ParkMaster parking-out mode  ·  _med_

Enables ParkMaster (PMA) active parking-out assistance.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `MACRO_PMA_AUSPARKEN`· source: firmware-token

### `3001/14/00000001b` — PDC module generation  ·  _high_

Tells the head unit which generation of Park Distance Control (PDC) module the car has. With generation 1, the distance display is laid out from the sensor counts in “PDC sensors, front” (`3001/3/00110000b`) and “PDC sensors, rear” (`3001/18/00000110b`); generation 2 does not use the counts. Set it to match the car's hardware.

| value | meaning |
|---|---|
| `0` | Generation 1 |
| `1` | Generation 2 |

default `00`· gate: always (no FA gate)· token `PDC_GENERATION`· source: firmware-trace

### `3001/14/00000010b` — iCam2 structural deformation detection  ·  _med_

Enables the iCam2 camera structural-deformation detection feature (checks camera mounting integrity). NICHT_AKTIV = not active.

| value | meaning |
|---|---|
| `0` | Inactive/Off |

default `00`· gate: FA-gated (depends on vehicle options)· token `ICAM2_STRUKTURVERFORMUNG`· source: firmware-token

### `3001/14/00000100b` — Rear climate control default state  ·  _med_

Sets the default on/off state for rear-seat climate control zones at vehicle start-up.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `HVAC_FOND_DEFAULT`· source: firmware-token

### `3001/14/00001000b` — Ambient scent/fragrance system (ZBF Duft)  ·  _med_

Enables the ambient fragrance system control via the climate control HMI (ZBF = Zusatz-Belüftungsfunktion).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `HVAC_ZBF_DUFT`· source: firmware-token

### `3001/14/00010000b` — Key config: tailgate unlock guard  ·  _med_

Prevents unintentional remote-key unlocking of the tailgate/boot lid. Controls whether a guard mode is active.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `KEY_CONF_TAILGATE_UNLOCKGUARD`· source: firmware-token

### `3001/14/11100000b` — Tyre load / seating configuration  ·  _med_

Specifies the vehicle seating/load configuration for RDC calibration purposes (e.g. 5-seat vs 7-seat, affects pressure thresholds per axle). 3-bit numeric field; raw values 0-7 observed, no symbolic enum names in firmware.

default `00`· gate: FA-gated (depends on vehicle options)· token `RDC_BELADUNG_DESIGN`· source: firmware-token

### `3001/15/11111111b` — Top-view camera display width  ·  _med_

Sets the top-view/surround-view camera display panel width in pixels. Used to select between narrow (400px), standard (440px), and wide (520px) display variants.

| value | meaning |
|---|---|
| `50` | Value 400 |
| `60` | Value 440 |
| `80` | Value 520 |

default `3C`· gate: FA-gated (depends on vehicle options)· token `TVC_WIDTH`· source: firmware-token

### `3001/16/00000001b` — Macro: Night Vision Camera fitted  ·  _med_

Master macro flag indicating Night Vision Camera (NVC) is installed. Enables NVC source in HU.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `MACRO_NV_C`· source: firmware-token

### `3001/16/00000010b` — Macro: TV tuner fitted  ·  _med_

Master macro flag indicating TV tuner is installed. Enables TV source in HU.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `MACRO_TV_C`· source: firmware-token

### `3001/16/00000100b` — Macro: Rear-view camera fitted  ·  _med_

Master macro flag indicating rear-view camera is installed. Enables camera display and PDC overlay. FA-gated by 3AG.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 3AG Rear view camera· token `MACRO_RV_C`· source: firmware-token

### `3001/16/00001000b` — Macro: Side-view camera fitted  ·  _med_

Master macro flag indicating a side-view (surround) camera is installed.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `MACRO_SV_C`· source: firmware-token

### `3001/16/00010000b` — Macro: Camera system active  ·  _med_

Master flag enabling the combined camera system (top-view/surround) functions.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `MACRO_K_C`· source: firmware-token

### `3001/16/00100000b` — Sequential M Gearbox (SMG/DCT) fitted  ·  _med_

Indicates a Sequential Manual Gearbox (SMG) or M Double Clutch Transmission (DCT) is installed. Enables DCT/Drivelogic HMI features. FA-gated by 2MK.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 2MK M Double Clutch Transmission with Drivelogic· token `SMG`· source: firmware-token

### `3001/16/01000000b` — ACC speed limit sign recognition (SGN)  ·  _med_

Enables speed-limit sign-recognition integration with Active Cruise Control (ACC + camera-based sign reading).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ACC_SGN`· source: firmware-token

### `3001/16/10000000b` — Active Cruise Control (ACC) fitted  ·  _med_

Master flag indicating Active Cruise Control (ACC) is installed, enabling ACC HMI, set-speed display, and related settings. FA-gated by 5DF or type-key.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 5DF Active cruise control with Stop&Go function / vehicle type-key attribute group (FP category 1; 71 type tokens, e.g. 1A10,1A11,1A12,1A31) / vehicle type-key attribute group (FP category 1; 61 type tokens, e.g. 1D11,1D12,1D31,1D32)· token `ACC_CIC`· source: firmware-token

### `3001/17/00000001b` — Dynamic Cruise Control (DCC) fitted  ·  _med_

Enables the Dynamic Cruise Control (DCC / Tempomat with braking function) HMI. NICHT_AKTIV = not currently in use despite being FA-gated active.

| value | meaning |
|---|---|
| `0` | Inactive/Off |

default `00`· gate: 544 Cruise control with braking function / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `DCC`· source: firmware-token

### `3001/17/00000010b` — Standard cruise control (FGR) fitted  ·  _med_

Enables basic speed-limiter/cruise-control (FGR = Fahrgeschwindigkeitsregler) HMI.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `FGR`· source: firmware-token

### `3001/17/00001100b` — CTA pedestrian alert fitted  ·  _med_

Selects the CTA (Close-range Transit Alarm) acoustic pedestrian-warning variant fitted: rear, or both front and rear.

| value | meaning |
|---|---|
| `1` | Rear only |
| `2` | Front and rear |

default `00`· gate: FA-gated (depends on vehicle options)· token `CTA`· source: firmware-token

### `3001/17/00010000b` — PDC distance display version  ·  _med_

Selects the PDC graphical distance-bar display version: ALT = legacy/old layout, NEU = current layout.

| value | meaning |
|---|---|
| `0` | Old (legacy) |
| `1` | New |

default `00`· gate: always (no FA gate)· token `PDC_ABSTAENDE_VERSION`· source: firmware-token

### `3001/17/00100000b` — PDC graphic orientation  ·  _med_

Sets whether the PDC distance graphic is shown in vertical or horizontal orientation on screen.

| value | meaning |
|---|---|
| `0` | Vertical |
| `1` | Horizontal |

default `00`· gate: FA-gated (depends on vehicle options)· token `PDC_DIRECTION`· source: firmware-token

### `3001/17/01000000b` — Seat heating distribution: front  ·  _med_

Configures which front seats have seat heating control elements displayed in the climate HMI.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `HVAC_SEATHEAT_DISTR_FRONT`· source: firmware-token

### `3001/17/10000000b` — Seat heating distribution: rear  ·  _med_

Configures which rear/fond seats have seat heating control elements displayed in the climate HMI.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `HVAC_SEATHEAT_DISTR_FOND`· source: firmware-token

### `3001/18/00000001b` — Climate one-timer activation  ·  _med_

Enables the single-timer climate pre-conditioning activation (one scheduled start time). NICHT_AKTIV = not fitted.

| value | meaning |
|---|---|
| `0` | Inactive/Off |
| `1` | Active/On |

default `00`· gate: FA-gated (depends on vehicle options)· token `CLIMATE_ACT_ONE_TIMER`· source: firmware-token

### `3001/18/00000110b` — PDC rear sensor count  ·  _med_

Specifies the number of PDC ultrasonic sensors fitted at the rear of the vehicle. KEIN_SENSOR = no sensors.

| value | meaning |
|---|---|
| `0` | No sensor |

default `00`· gate: 508 Park distance control (PDC) / 507 Park Distance Control (PDC), rear· token `PDC_SENSOR_HINTEN`· source: firmware-token

### `3001/18/00001000b` — Video watchdog: side-view camera  ·  _med_

Enables the video-signal watchdog monitoring for the side-view camera feed. When active, loss of signal triggers an alert/fallback.

| value | meaning |
|---|---|
| `0` | Inactive/Off |
| `1` | Active/On |

default `00`· gate: always (no FA gate)· token `VIDEO_WATCHDOG_SIDEVIEW`· source: firmware-token

### `3001/18/00010000b` — Video watchdog: rear-view camera  ·  _med_

Enables the video-signal watchdog monitoring for the rear-view camera feed.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: always (no FA gate)· token `VIDEO_WATCHDOG_REARVIEW`· source: firmware-token

### `3001/18/00100000b` — Video watchdog: top-view camera  ·  _med_

Enables the video-signal watchdog for the top/surround-view camera feed.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `VIDEO_WATCHDOG_TOPVIEW`· source: firmware-token

### `3001/18/01000000b` — Video watchdog: night vision camera  ·  _med_

Enables the video-signal watchdog for the night-vision camera feed.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `VIDEO_WATCHDOG_NIGHTVISION`· source: firmware-token

### `3001/18/10000000b` — Video watchdog: KAFAS front camera  ·  _med_

Enables the video-signal watchdog for the KAFAS stereo front-camera feed.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `VIDEO_WATCHDOG_KAFAS`· source: firmware-token

### `3001/19/11111111b` — Early video legal disclaimer state  ·  _med_

Controls whether a legal disclaimer is shown during the early-video (EarlyVideoApp / KAFAS camera) display before the main HMI is ready. INITWERT = initial unset state.

| value | meaning |
|---|---|
| `0` | Initial value (not set) |

default `00`· token `EARLY_VIDEO_LEGALDISCL`· source: firmware-token

### `3001/20/00000011b` — USB hub  ·  _med_

Tells the head unit whether a USB hub is connected and to which of its USB ports. “USB charging current limit” (`3001/20/00011100b`) applies to that port. Set at the factory to match Telephony with wireless charging (S6NW).

| value | meaning |
|---|---|
| `0` | None |
| `1` | On USB port 1 |
| `2` | On USB port 2 |

default `00`· gate: 6NW Telephony with wireless charging· token `USB_HUB_AVAIL`· source: firmware-trace

### `3001/20/00011100b` — USB charging current limit  ·  _high_

Sets the most current the USB port with the hub (see “USB hub” (`3001/20/00000011b`)) supplies for charging a connected device. The 1500 mA choice supplies 1000 mA. With no hub, or with the port default, port 1 supplies 1000 mA and port 2 supplies 500 mA.

| value | meaning |
|---|---|
| `0` | 1000 mA |
| `1` | Limited to 1000 mA |
| `2` | 2100 mA |
| `3` | Port default |

default `03`· gate: FA-gated (depends on vehicle options)· token `USB_MAX_CHARGING_CURRENT`· source: firmware-trace

### `3001/20/01100000b` — Parking priority mode  ·  _med_

Selects parking-function HMI priority/routing for specific market variants (Korea, India, type-key groups). 2-bit numeric field; no symbolic enum names in firmware.

default `00`· gate: 802 Korean version / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / 8LA India version· token `PARK_PRIO`· source: firmware-token

### `3001/20/10000000b` — RESERVED_3001_20_bit7  ·  _low_

Unnamed/reserved coding bit7 (0x80) in the EXBOX page; shares EXBOX byte 20 with named feature bit(s): ['0x3:USB_HUB_AVAIL', '0x1c:USB_MAX_CHARGING_CURRENT', '0x60:PARK_PRIO'] (these together fill the byte to 0xFF, i.e. this is the unallocated remainder of that byte). Not present in the sysetshellevo descriptor table (no name and, for most, no magic), absent from syset_fielddict, and no consumer reads this (byte,mask) in the OMAP image. Most likely a spare/reserved bit reserved by the CAFD layout but not implemented in firmware. FA-gate: ''. Purpose undetermined.

source: firmware

### `3001/21/11111111b` — Car size: reference point to rear  ·  _high_

Declares the car's length from its reference point to the rear end.

| value | meaning |
|---|---|
| `15` | 4019 mm |
| `16` | 4141 mm |

_Not a user setting: Multi-byte (2-byte big-endian mm) with no reader found, so no number setting: EarlyVideoApp and EarlyICam2App have no accessor for EXBOX bytes 21-28; the token appears only in the syset tools (sysetshellevo/sysetadjread/sysetpageproxy tables), libhmicoding's generated va table and getter stub (never imported) and the Jacinto symbol table; HmiMain3D movw hits on the va ids 3253-3273 are generic id-registration runs and trace line numbers, not reads; the HMI 3D car takes its size from widget/variantregistry.pbvar._

default `103B`· gate: always (no FA gate)· token `VEH_DIM_CAR_NET_TO_REAR_X1`· source: firmware-trace

### `3001/23/11111111b` — Car size: width without mirrors  ·  _high_

Declares the car's greatest body width, not counting the side mirrors.

| value | meaning |
|---|---|
| `7` | 1900 mm |

_Not a user setting: Multi-byte (2-byte big-endian mm) with no reader found, so no number setting: EarlyVideoApp and EarlyICam2App have no accessor for EXBOX bytes 21-28; the token appears only in the syset tools (sysetshellevo/sysetadjread/sysetpageproxy tables), libhmicoding's generated va table and getter stub (never imported) and the Jacinto symbol table; HmiMain3D movw hits on the va ids 3253-3273 are generic id-registration runs and trace line numbers, not reads; the HMI 3D car takes its size from widget/variantregistry.pbvar._

default `076E`· gate: always (no FA gate)· token `VEH_DIM_MAX_WIDTH_WITHOUT_WINGMIRROR_W103`· source: firmware-trace

### `3001/25/11111111b` — Car size: reference point to front  ·  _high_

Declares the car's length from its reference point to the front end.

| value | meaning |
|---|---|
| `3` | 934 mm |

_Not a user setting: Multi-byte (2-byte big-endian mm) with no reader found, so no number setting: EarlyVideoApp and EarlyICam2App have no accessor for EXBOX bytes 21-28; the token appears only in the syset tools (sysetshellevo/sysetadjread/sysetpageproxy tables), libhmicoding's generated va table and getter stub (never imported) and the Jacinto symbol table; HmiMain3D movw hits on the va ids 3253-3273 are generic id-registration runs and trace line numbers, not reads; the HMI 3D car takes its size from widget/variantregistry.pbvar._

default `03AF`· gate: always (no FA gate)· token `VEH_DIM_CAR_NET_TO_FRONT_X2`· source: firmware-trace

### `3001/27/11111111b` — Car size: reference point to rear axle  ·  _high_

Declares the distance from the car's reference point to the rear axle.

| value | meaning |
|---|---|
| `11` | 3042 mm |
| `12` | 3147 mm |

_Not a user setting: Multi-byte (2-byte big-endian mm) with no reader found, so no number setting: EarlyVideoApp and EarlyICam2App have no accessor for EXBOX bytes 21-28; the token appears only in the syset tools (sysetshellevo/sysetadjread/sysetpageproxy tables), libhmicoding's generated va table and getter stub (never imported) and the Jacinto symbol table; HmiMain3D movw hits on the va ids 3253-3273 are generic id-registration runs and trace line numbers, not reads; the HMI 3D car takes its size from widget/variantregistry.pbvar._

default `0BBF`· gate: always (no FA gate)· token `VEH_DIM_CAR_NET_TO_REAR_AXIS_X3`· source: firmware-trace

### `3001/29/11111111b` — AUX input 1 (head unit)  ·  _med_

Video connection for the head unit's first auxiliary (AUX) video input, with the same two choices as “Head unit video playback” (`3001/9/11111111b`): the head unit's internal video input, or none. The picture from this input is routed as set in “Head unit video playback” (`3001/9/11111111b`). Best left unchanged.

| value | meaning |
|---|---|
| `21` | Internal video input |
| `255` | None |

default `FF`· gate: NOT 6AE TeleServices / 6CP Smartphone Integration· token `AUX1_IN_HU`· source: firmware-trace

### `3001/30/11111111b` — RESERVED_3001_BYTES_30_51  ·  _low_

Unnamed multi-byte value/reserved block (bytes 30-51, 22 bytes) in the EXBOX coding page. No descriptor record exists for this value field in dg3001's area/type, it is absent from syset_fielddict, and no consumer reads it in the OMAP image (NBTCarHU only reads dg3004 PortationMaster fields; dg3001 consumers live on the Jacinto/HMI node not present in this image). follows named field(s) ['AUX1_IN_HU']. Default='empty'. Purpose undetermined.

source: firmware

### `3001/52/11111111b` — Camera legal disclaimer  ·  _med_

Sets whether a legal notice appears with the parking camera views and how long it stays: for a short time or permanently. Disclaimer rules vary by country.

| value | meaning |
|---|---|
| `0` | Disabled |
| `6` | Shown, closes after a delay |
| `255` | Always shown |

default `06`· gate: FA-gated (depends on vehicle options)· token `MACRO_CAM_LEGALDISCLAIMER`· source: firmware-token

### `3001/53/11111111b` — Night vision legal disclaimer  ·  _med_

Sets whether a legal notice appears with the night vision camera image and how long it stays: for a short time or permanently. Disclaimer rules vary by country.

| value | meaning |
|---|---|
| `0` | Disabled |
| `6` | Shown, closes after a delay |
| `255` | Always shown |

default `06`· gate: FA-gated (depends on vehicle options)· token `MACRO_NIVICAM_LDISCLAIMER`· source: firmware-token

### `3001/54/00000001b` — Trailer tow hitch  ·  _med_

Enables the head unit's trailer-related functions. Enable it only when the car has a trailer tow hitch (S235).

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 235 Trailer tow hitch with removable ball head· token `MACRO_TRAILER_COUPLING`· source: firmware-token

### `3001/54/00000110b` — Air lamination: driver side  ·  _med_

Configures driver-side air lamination (directed airflow zones) for the climate system.

| value | meaning |
|---|---|
| `1` | Low airflow |
| `2` | High airflow |

default `00`· gate: FA-gated (depends on vehicle options)· token `HVAC_AIRLAMINATION_DRV`· source: firmware-token

### `3001/54/00011000b` — Air lamination: front passenger side  ·  _med_

Configures front-passenger-side air lamination (directed airflow zones). 2-bit numeric field; no symbolic enum names in firmware.

default `00`· gate: FA-gated (depends on vehicle options)· token `HVAC_AIRLAMINATION_CODRV`· source: firmware-token

### `3001/54/00100000b` — Climate automatic intensity control  ·  _med_

Enables automatic blower/intensity control within the HVAC automatic mode.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `HVAC_AUTOMATIC_INTENSITY`· source: firmware-token

### `3001/54/01000000b` — Climate popup: air distribution  ·  _med_

Enables the air-distribution control popup/overlay in the climate HMI.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `HVAC_POPUP_AIRDISTR`· source: firmware-token

### `3001/54/10000000b` — Convertible (Cabrio) climate mode  ·  _med_

Activates convertible-specific climate-control logic (adapted airflow when roof is open).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `HVAC_CABRIO`· source: firmware-token

### `3001/55/00000001b` — Climate popup: AUTO mode toggle  ·  _med_

Enables a popup/soft button for toggling the automatic climate mode from within the climate HMI.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `HVAC_POPUP_AUTO_TOGGLE`· source: firmware-token

### `3001/55/00000010b` — Front seat ventilation available  ·  _med_

Enables front seat ventilation control in the climate HMI.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `HVAC_SEATVENTILATION_FRONT`· source: firmware-token

### `3001/55/00000100b` — Climate popup: seat climate controls  ·  _med_

Enables the seat heating/ventilation popup panel in the climate HMI.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `HVAC_POPUP_SEATCLIMATE`· source: firmware-token

### `3001/55/00111000b` — RESERVED_3001_55_bits5,4,3  ·  _low_

Unnamed/reserved coding bits5,4,3 (0x38) in the EXBOX page; shares EXBOX byte 55 with named feature bit(s): ['0x1:HVAC_POPUP_AUTO_TOGGLE', '0x2:HVAC_SEATVENTILATION_FRONT', '0x4:HVAC_POPUP_SEATCLIMATE', '0x40:HEADUP_DISPLAY']. Not present in the sysetshellevo descriptor table (no name and, for most, no magic), absent from syset_fielddict, and no consumer reads this (byte,mask) in the OMAP image. Most likely a spare/reserved bit reserved by the CAFD layout but not implemented in firmware. FA-gate: ''. Purpose undetermined.

source: firmware

### `3001/55/01000000b` — Head-up display (HUD) fitted  ·  _med_

Enables head-up display settings and configuration menus in the HU.

| value | meaning |
|---|---|
| `0` | Inactive/Off |
| `1` | Active/On |

default `00`· gate: FA-gated (depends on vehicle options)· token `HEADUP_DISPLAY`· source: firmware-token

### `3001/55/10000000b` — RESERVED_3001_55_bit7  ·  _low_

Coding bit position the firmware ACKNOWLEDGES (a bare magic word 0x4281bc00 exists in the sysetshellevo name-less magic array @~0x0d33xx, decoding to byte 55/mask 0x80/dg3001) but ships NO name string and no descriptor record, and no consumer reads it in the OMAP image. Sits among named EXBOX fields in the same byte: ['0x1:HVAC_POPUP_AUTO_TOGGLE', '0x2:HVAC_SEATVENTILATION_FRONT', '0x4:HVAC_POPUP_SEATCLIMATE', '0x40:HEADUP_DISPLAY'].

source: firmware

### `3001/56/00000111b` — RESERVED_3001_56_bits2,1,0  ·  _low_

Unnamed/reserved coding bits2,1,0 (0x7) in the EXBOX page; shares EXBOX byte 56 with named feature bit(s): ['0x8:AUDIO_REMOTE_CONTROL', '0x10:DOORLOCKING_SEATMEMORY', '0x60:SCHNEEKETTENERKENNUNG', '0x80:DWA'] (these together fill the byte to 0xFF, i.e. this is the unallocated remainder of that byte). Not present in the sysetshellevo descriptor table (no name and, for most, no magic), absent from syset_fielddict, and no consumer reads this (byte,mask) in the OMAP image. Most likely a spare/reserved bit reserved by the CAFD layout but not implemented in firmware. FA-gate: ''. Purpose undetermined.

source: firmware

### `3001/56/00001000b` — External audio remote control  ·  _med_

Enables support for an external audio remote control device connected to the HU.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `AUDIO_REMOTE_CONTROL`· source: firmware-token

### `3001/56/00010000b` — Seat memory on door lock/unlock  ·  _med_

Enables automatic seat position recall or adjustment linked to door lock/unlock events. FA-gated by 459 (electric seats with memory).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 459 Seat adjustment, electrical, with memory· token `DOORLOCKING_SEATMEMORY`· source: firmware-token

### `3001/56/01100000b` — Snow chain detection  ·  _med_

Enables snow chain detection logic in the vehicle dynamics system; affects HU warning display.

| value | meaning |
|---|---|
| `2` | Active with popup |

default `00`· gate: FA-gated (depends on vehicle options)· token `SCHNEEKETTENERKENNUNG`· source: firmware-token

### `3001/56/10000000b` — Alarm system (DWA) fitted  ·  _med_

Indicates that the anti-theft alarm system (DWA = Diebstahl-Warn-Anlage) is installed. FA-gated by 302.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 302 Alarm system· token `DWA`· source: firmware-token

### `3001/57/11111111b` — Display type variant  ·  _med_

Identifies the physical display type installed: narrow/standard, wide, flap (motorised) or narrow flap. Affects display initialisation and aspect-ratio handling.

| value | meaning |
|---|---|
| `1` | Narrow display |
| `2` | Wide display |
| `3` | Flap display |
| `4` | Narrow flap display |

default `01`· gate: 609 Professional navigation system / 6VB Infotainment control· token `DISPLAY_VARIANTE`· source: firmware-token

### `3001/58/11111111b` — Legal disclaimer display  ·  _med_

Sets whether a legal notice is shown on the central display and how long it stays: for a short time or permanently. “Camera legal disclaimer” (`3001/52/11111111b`) and “Night vision legal disclaimer” (`3001/53/11111111b`) cover those notices. Disclaimer rules vary by country.

| value | meaning |
|---|---|
| `0` | Disabled |
| `10` | Shown, closes after a delay |
| `255` | Always shown |

default `00`· token `LEGAL_DISCLAIMER_TIME`· source: firmware-token

### `3001/59/11111111b` — RESERVED_3001_BYTES_59_60  ·  _low_

Unnamed multi-byte value/reserved block (bytes 59-60, 2 bytes) in the EXBOX coding page. No descriptor record exists for this value field in dg3001's area/type, it is absent from syset_fielddict, and no consumer reads it in the OMAP image (NBTCarHU only reads dg3004 PortationMaster fields; dg3001 consumers live on the Jacinto/HMI node not present in this image). follows named field(s) ['LEGAL_DISCLAIMER_TIME']. Default='empty'. Purpose undetermined.

source: firmware

### `3001/61/00001111b` — Camera system type  ·  _med_

Selects the type of camera system installed: none, top-view service camera, iCam standard rear-view, iCam high-end, iCam2 standard, or iCam2 high-end.

| value | meaning |
|---|---|
| `0` | None |
| `1` | Top-view/surround-view camera service |
| `2` | iCam rear-view camera (standard) |
| `3` | iCam rear-view camera (high-end) |
| `4` | iCam2 rear-view camera (standard) |
| `5` | iCam2 rear-view camera (high-end) |

default `00`· gate: FA-gated (depends on vehicle options)· token `CAMERA_SYSTEM`· source: firmware-token

### `3001/61/11110000b` — RESERVED_3001_61_bits7,6,5,4  ·  _low_

Unnamed/reserved coding bits7,6,5,4 (0xf0) in the EXBOX page; shares EXBOX byte 61 with named feature bit(s): ['0xf:CAMERA_SYSTEM'] (these together fill the byte to 0xFF, i.e. this is the unallocated remainder of that byte). Not present in the sysetshellevo descriptor table (no name and, for most, no magic), absent from syset_fielddict, and no consumer reads this (byte,mask) in the OMAP image. Most likely a spare/reserved bit reserved by the CAFD layout but not implemented in firmware. FA-gate: ''. Purpose undetermined.

source: firmware

### `3001/62/00000001b` — RESERVED_3001_62_bit0  ·  _low_

Unnamed/reserved coding bit0 (0x1) in the EXBOX page; shares EXBOX byte 62 with named feature bit(s): ['0x6:STARTUP_TYPE', '0x78:STARTUP_EMBLEM', '0x80:PDC_3D'] (these together fill the byte to 0xFF, i.e. this is the unallocated remainder of that byte). Not present in the sysetshellevo descriptor table (no name and, for most, no magic), absent from syset_fielddict, and no consumer reads this (byte,mask) in the OMAP image. Most likely a spare/reserved bit reserved by the CAFD layout but not implemented in firmware. FA-gate: ''. Purpose undetermined.

source: firmware

### `3001/62/00000110b` — Boot screen type  ·  _med_

Selects the style of boot/startup screen: black screen, static splash image, animation, or power-welcome animation.

| value | meaning |
|---|---|
| `0` | Black screen |
| `1` | Splash image |
| `2` | Animation |
| `3` | Power-welcome animation |

default `00`· gate: always (no FA gate)· token `STARTUP_TYPE`· source: firmware-token

### `3001/62/01111000b` — Startup emblem  ·  _high_

Picks the brand emblem the central display shows at startup, as a still image, animation or welcome sequence (see “Startup screen” (`3001/62/00000110b`)). A value that lists screen sizes has artwork only for those; on other screens the ConnectedDrive emblem shows instead. As a still image on the wider screens, some emblems show only their background, without the logo.

| value | meaning |
|---|---|
| `0` | ConnectedDrive |
| `1` | M logo |
| `2` | ALPINA |
| `3` | BMW i |
| `4` | MINI chrome logo, 800×480, 1280×480 |
| `5` | Rolls-Royce Spirit of Ecstasy, 1440×540 |
| `6` | ConnectedDrive glow, 1280×480, 1440×540 |
| `7` | John Cooper Works, 1280×480 |
| `8` | MINI flat logo |
| `9` | M logo glow, 1280×480, 1440×540 |
| `10` | No artwork, shows ConnectedDrive |
| `11` | GP logo, 800×480, 1280×480 |
| `12` | No artwork, shows ConnectedDrive |
| `13` | No artwork, shows ConnectedDrive |
| `14` | No artwork, shows ConnectedDrive |
| `15` | No artwork, shows ConnectedDrive |

default `00`· token `STARTUP_EMBLEM`· source: firmware-trace

### `3001/62/10000000b` — PDC 3D graphics mode  ·  _med_

Enables the 3D visualisation mode for the park-distance control display instead of the flat 2D bar graphic.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `PDC_3D`· source: firmware-token

### `3001/63/11111111b` — Digital Multimedia Broadcasting (DMB) variant  ·  _med_

Identifies the DMB (Korean/Asian digital TV) tuner ECU variant. 0xFF = not fitted. FA-gated by 601 (TV) or 802 (Korea).

| value | meaning |
|---|---|
| `21` | Value 21 |

default `FF`· gate: 601 TV Function / 802 Korean version· token `DMB`· source: firmware-token

### `3001/64/00000001b` — RESERVED_3001_64_bit0  ·  _low_

Coding bit position the firmware ACKNOWLEDGES (a bare magic word 0x42820008 exists in the sysetshellevo name-less magic array @~0x0d33xx, decoding to byte 64/mask 0x1/dg3001) but ships NO name string and no descriptor record, and no consumer reads it in the OMAP image. Sits among named EXBOX fields in the same byte: ['0x2:ACTIVE_PDC_FLANKENBREMSUNG', '0x4:ACTIVE_PDC_DEFAULT_ON', '0x8:EIN_AUSTIEGSHILFE_FA_SITZ', '0x10:ACTIVE_PDC', '0x20:TSM', '0x40:ICAM_PBA', '0x80:ICAM_SBA'].

source: firmware

### `3001/64/00000010b` — Active PDC: flank braking  ·  _med_

Enables automatic flank/side braking intervention by the Active PDC system to avoid lateral collisions.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ACTIVE_PDC_FLANKENBREMSUNG`· source: firmware-token

### `3001/64/00000100b` — Active PDC: default on  ·  _med_

Sets Active PDC to be automatically enabled by default at vehicle start (instead of requiring manual activation).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ACTIVE_PDC_DEFAULT_ON`· source: firmware-token

### `3001/64/00001000b` — Exit-assist: driver seat  ·  _med_

Enables the automatic seat exit-assist function for the driver seat (seat moves back on door open / key out).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `EIN_AUSTIEGSHILFE_FA_SITZ`· source: firmware-token

### `3001/64/00010000b` — Active PDC fitted  ·  _med_

Master flag for Active PDC (automated braking assistance during parking). Enables Active PDC HMI and system activation.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ACTIVE_PDC`· source: firmware-token

### `3001/64/00100000b` — Trailer Stability Management (TSM)  ·  _med_

Enables Trailer Stability Management in the HU menus (caravanning/towing stability control).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TSM`· source: firmware-token

### `3001/64/01000000b` — iCam: Panoramic Back-view Assist (PBA)  ·  _med_

Enables panoramic back-view assist functionality using the iCam rear camera system.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ICAM_PBA`· source: firmware-token

### `3001/64/10000000b` — iCam: Side-view Back-view Assist (SBA)  ·  _med_

Enables side-view back-view assist functionality using the iCam system.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ICAM_SBA`· source: firmware-token

### `3001/65/00000001b` — iCam2 camera selector  ·  _med_

Enables the camera source selector for iCam2 multi-camera configurations.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ICAM2_CAMERA_SELECTOR`· source: firmware-token

### `3001/65/00000010b` — iCam2 brightness/contrast adjustment  ·  _med_

Enables user-adjustable brightness and contrast settings for the iCam2 camera display.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ICAM2_HELLIGKEIT_KONTRAST`· source: firmware-token

### `3001/65/00000100b` — RESERVED_3001_65_bit2  ·  _low_

Unnamed/reserved coding bit2 (0x4) in the EXBOX page; shares EXBOX byte 65 with named feature bit(s): ['0x1:ICAM2_CAMERA_SELECTOR', '0x2:ICAM2_HELLIGKEIT_KONTRAST', '0x18:COMMUNICATION_PARKMASTER', '0x20:VSG_HMI_MENUE', '0x40:AUTO_PDC', '0x80:RDC_FORTSCHRITTSANZEIGE'] (these together fill the byte to 0xFF, i.e. this is the unallocated remainder of that byte). Not present in the sysetshellevo descriptor table (no name and, for most, no magic), absent from syset_fielddict, and no consumer reads this (byte,mask) in the OMAP image. Most likely a spare/reserved bit reserved by the CAFD layout but not implemented in firmware. FA-gate: ''. Purpose undetermined.

source: firmware

### `3001/65/00011000b` — Parking module interface  ·  _med_

Tells the head unit which generation of parking module the car has, so the parking view on the central display opens and closes when that module asks. With “None”, the head unit does not respond to a parking module. Set it to match the car's parking hardware.

| value | meaning |
|---|---|
| `0` | None |
| `1` | Generation 1 |
| `2` | Generation 2 |

default `00`· token `COMMUNICATION_PARKMASTER`· source: firmware-trace

### `3001/65/00100000b` — Speed governor (VSG) HMI menu  ·  _med_

Enables the vehicle speed governor (VSG) settings menu in the HU.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `VSG_HMI_MENUE`· source: firmware-token

### `3001/65/01000000b` — PDC automatic activation  ·  _med_

Enables automatic activation of PDC when reverse gear is engaged or at slow speed. NICHT_AKTIV = manual activation only. FA-gated by 5DP.

| value | meaning |
|---|---|
| `0` | Inactive/Off |

default `00`· gate: 5DP PMA· token `AUTO_PDC`· source: firmware-token

### `3001/65/10000000b` — RDC reset progress indicator  ·  _med_

Enables a progress bar / status indicator during the tyre-pressure monitor reset procedure. FA-gated by 2VB.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 2VB Tire Pressure Monitor· token `RDC_FORTSCHRITTSANZEIGE`· source: firmware-token

### `3001/66/00000011b` — Tyre monitoring type selection (RDC/RPA)  ·  _med_

Selects the active tyre monitoring technology: direct pressure sensor (RDC), flat-tyre indicator (RPA), or none.

| value | meaning |
|---|---|
| `1` | Flat-tyre indicator (RPA) |

default `00`· gate: FA-gated (depends on vehicle options)· token `REIFENUEBERWACHUNG_RDC_RPA`· source: firmware-token

### `3001/66/00001100b` — Tire pressure display values  ·  _high_

Sets what the tire pressure display shows for each tire: the pressure, or the pressure and the tire temperature.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Pressure |
| `2` | Pressure and temperature |

default `00`· gate: NOT 2VB Tire Pressure Monitor / vehicle type-key attribute group (FP category 13; 28 type tokens, e.g. 1B71,1B72,1B91,1H91) / numeric value-attribute 0321 (FP category 255) / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `RDC_DRUCK_TEMP`· source: firmware-token

### `3001/66/00010000b` — Transmission sport mode checkbox (SPA)  ·  _med_

Enables a sport/steptronic mode toggle checkbox in the driving settings HMI. Shown on non-automatic/non-sport-transmission variants.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: NOT 205 Steptronic transmission / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / 2TB Steptronic sport transmission / 2MK M Double Clutch Transmission with Drivelogic· token `SPA_CHECKBOX`· source: firmware-token

### `3001/66/00100000b` — Rearview camera regulatory compliance mode  ·  _med_

Enables a regulatory/compliance mode for the rear-view camera display (e.g. mandatory display rules in certain markets).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `REARVIEW_REGULATION`· source: firmware-token

### `3001/66/01000000b` — PDC display version 2  ·  _med_

Selects the V2 (second generation) graphical layout for the PDC distance display.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· token `PDC_DARSTELLUNG_V2`· source: firmware-token

### `3001/66/10000000b` — HVAC zone synchronisation (ZBF Sync)  ·  _med_

Enables synchronisation of climate zones (driver = passenger) for the Zuheizer/ZBF system.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `HVAC_ZBF_SYNC`· source: firmware-token

### `3001/67/00000001b` — HVAC: Automatic air recirculation (AUC)  ·  _med_

Enables automatic recirculation control in the Zuheizer/ZBF auxiliary climate system.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `HVAC_ZBF_AUC`· source: firmware-token

### `3001/67/00000110b` — HVAC ZBF activation: front seat side  ·  _med_

Configures which front seat activates the ZBF (Zusatz-Belüftungsfunktion) auxiliary climate: driver side, passenger side, or both.

| value | meaning |
|---|---|
| `1` | Driver side |
| `2` | Front passenger side |
| `3` | Both front seats |

default `00`· gate: FA-gated (depends on vehicle options)· token `HVAC_ZBF_ACTIVATION_FRT`· source: firmware-token

### `3001/67/00001000b` — HVAC ZBF activation: 2-door activation  ·  _med_

Enables ZBF auxiliary climate activation via the 2nd door (2TIR). Relevant for vehicles where rear-door opening triggers climate.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `HVAC_ZBF_ACTIVATION_2TIR`· source: firmware-token

### `3001/67/00010000b` — HVAC ZBF: 3-door / 3rd row  ·  _med_

Enables ZBF auxiliary climate function for a 3rd row or 3rd door zone.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `HVAC_ZBF_3TIR`· source: firmware-token

### `3001/67/00100000b` — HVAC ZBF: 2-door default state  ·  _med_

Sets the default activation state for the 2-door ZBF auxiliary climate zone.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `HVAC_ZBF_DEFAULT_2TIR`· source: firmware-token

### `3001/67/01000000b` — Electric tailgate (SMO) fitted  ·  _med_

Indicates that an electrically-powered tailgate/boot lid (SMO = Schließmechanismus Öffnung) is installed. NICHT_AKTIV = no electric tailgate.

| value | meaning |
|---|---|
| `0` | Inactive/Off |

default `00`· gate: FA-gated (depends on vehicle options)· token `BACKDOOR_SMO_INSTALLED`· source: firmware-token

### `3001/67/10000000b` — RESERVED_3001_67_bit7  ·  _low_

Unnamed/reserved coding bit7 (0x80) in the EXBOX page; shares EXBOX byte 67 with named feature bit(s): ['0x1:HVAC_ZBF_AUC', '0x6:HVAC_ZBF_ACTIVATION_FRT', '0x8:HVAC_ZBF_ACTIVATION_2TIR', '0x10:HVAC_ZBF_3TIR', '0x20:HVAC_ZBF_DEFAULT_2TIR', '0x40:BACKDOOR_SMO_INSTALLED'] (these together fill the byte to 0xFF, i.e. this is the unallocated remainder of that byte). Not present in the sysetshellevo descriptor table (no name and, for most, no magic), absent from syset_fielddict, and no consumer reads this (byte,mask) in the OMAP image. Most likely a spare/reserved bit reserved by the CAFD layout but not implemented in firmware. FA-gate: ''. Purpose undetermined.

source: firmware

### `3001/68/00000011b` — Tailgate lid configuration  ·  _med_

Configures which tailgate lid(s) are present and adjustable: upper lid only, or both upper and lower (split tailgate).

| value | meaning |
|---|---|
| `1` | Upper lid only |
| `2` | Both lids |

default `00`· gate: FA-gated (depends on vehicle options)· token `BACKDOOR_SETTING_LIDS`· source: firmware-token

### `3001/68/00011100b` — Tailgate opening angle step count  ·  _med_

Sets the number of programmable opening-angle stop positions for the electrically-powered tailgate. 3-bit numeric field; observed raw values 0, 1, 2 — no symbolic enum names in firmware.

default `00`· gate: FA-gated (depends on vehicle options)· token `BACKDOOR_OPENINGANGLE_STEPS`· source: firmware-token

### `3001/68/11100000b` — RESERVED_3001_68_bits7,6,5  ·  _low_

Unnamed/reserved coding bits7,6,5 (0xe0) in the EXBOX page; shares EXBOX byte 68 with named feature bit(s): ['0x3:BACKDOOR_SETTING_LIDS', '0x1c:BACKDOOR_OPENINGANGLE_STEPS'] (these together fill the byte to 0xFF, i.e. this is the unallocated remainder of that byte). Not present in the sysetshellevo descriptor table (no name and, for most, no magic), absent from syset_fielddict, and no consumer reads this (byte,mask) in the OMAP image. Most likely a spare/reserved bit reserved by the CAFD layout but not implemented in firmware. FA-gate: ''. Purpose undetermined.

source: firmware

### `3001/69/11111111b` — RESERVED_3001_BYTES_69_149  ·  _low_

Unnamed multi-byte value/reserved block (bytes 69-149, 81 bytes) in the EXBOX coding page. No descriptor record exists for this value field in dg3001's area/type, it is absent from syset_fielddict, and no consumer reads it in the OMAP image (NBTCarHU only reads dg3004 PortationMaster fields; dg3001 consumers live on the Jacinto/HMI node not present in this image). follows named field(s) ['BACKDOOR_SETTING_LIDS', 'BACKDOOR_OPENINGANGLE_STEPS']. Default='empty'. Purpose undetermined.

source: firmware

## Datagroup 0x3002 (94 parameters)

### `3002/0/00001111b` — Radio country/region  ·  _high_

Selects the radio regulatory region for the tuner. Determines frequency ranges, channel spacing, and reception standards applicable to the market.

| value | meaning |
|---|---|
| `0` | ECE (Europe/Rest-of-world) |
| `1` | US (North America) |
| `2` | Japan |
| `3` | Australia |

default `00`· token `RADIO_COUNTRY`· source: firmware-token

### `3002/0/00010000b` — FM de-emphasis  ·  _med_

Configures the FM tuner de-emphasis time constant. 50 µs is standard for Europe/Australia; 75 µs is used in the US/Japan. Affects high-frequency reproduction of FM audio.

| value | meaning |
|---|---|
| `0` | 50 µs (ECE/default) |
| `1` | 75 µs (US/Japan) |

default `00`· token `FM_DEEMPHASIS`· source: firmware-token

### `3002/0/00100000b` — AF (Alternative Frequency) function  ·  _high_

Enables or disables RDS Alternative Frequency following, allowing the tuner to switch to a stronger transmitter carrying the same programme.

| value | meaning |
|---|---|
| `0` | Off (AF_AUS) |
| `1` | On (AF_EIN) |

default `00`· token `AF_FUNKTION`· source: firmware-token

### `3002/0/01000000b` — Audio timing delay IMG  ·  _low_

Internal timing delay for the audio system. Best left unchanged.

| value | meaning |
|---|---|
| `0` | Standard |

_Not a user setting: No reader: a byte-accessor scan of every syset client (813 OMAP ELFs, Jacinto IFS/EFS binaries incl. AudioProcess, HUJacintoStage1, TunerApp, CDabMain) finds no accessor for AUDIO_TUNER_TRAFFIC byte 0 mask 0x40; AudioProcess, the chime player, reads only bytes 1-2 of the chime timing._

default `00`· token `TIME_LAG_IMG`· source: firmware-trace

### `3002/0/10000000b` — Audio timing delay IDG  ·  _low_

Internal timing delay for the audio system. Best left unchanged.

| value | meaning |
|---|---|
| `0` | Standard |

_Not a user setting: No reader: a byte-accessor scan of every syset client (813 OMAP ELFs, Jacinto IFS/EFS binaries incl. AudioProcess, HUJacintoStage1, TunerApp, CDabMain) finds no accessor for AUDIO_TUNER_TRAFFIC byte 0 mask 0x80; AudioProcess, the chime player, reads only bytes 1-2 of the chime timing._

default `00`· token `TIME_LAG_IDG`· source: firmware-trace

### `3002/1/11111111b` — Minimum gap between equal-priority chimes  ·  _high_

Sets how long the head unit waits after playing a chime before it plays another chime of the same priority; one that comes sooner isn't played. Best left unchanged.

| value | meaning |
|---|---|
| `6` | 1500 ms |

Number: raw 0–255 × 20 + 0 ms; typical 100, 500, 1000, 2000

default `05`· token `TIME_DIST_SAME_PRIO`· source: firmware-trace

### `3002/2/11111111b` — Chime timeout  ·  _med_

Longest time a continuous chime keeps sounding without a new request from the module that asked for it. Best left unchanged.

| value | meaning |
|---|---|
| `250` | Standard |

_Not a user setting: Chime watchdog timing: AudioProcess CPJingleDevCtrl FUN_00288c50 reads byte 2 x 20 ms (BMW 250 = 5000 ms, also the built-in default) and the jingle processors restart this timer on every 'on' request of a continuous chime (and the reverse-gear chime), stopping it when no request follows. Only matters when a module's 'off' request is lost: protocol timing, hidden (decision 2)._

default `FA`· token `TIME_OUT_GONG`· source: firmware-trace

### `3002/3/11111111b` — Switch-on volume limit  ·  _high_

When the audio system switches on, a volume left above this level is lowered to it, so it doesn't start too loud. The level is a step on the head unit's volume scale.

| value | meaning |
|---|---|
| `26` | Same as 25 |

Number: raw 0–79 × 1 + 0; typical 10, 20, 30, 40

default `19`· token `VOL_MAX_ON`· source: firmware-trace

### `3002/4/11111111b` — Rear-seat switch-on volume limit  ·  _high_

When the rear-seat entertainment switches on, a rear volume left above this level is lowered to it, so it doesn't start too loud. The level is a step on the rear volume scale. Only relevant with rear-seat entertainment.

| value | meaning |
|---|---|
| `51` | Same as 50 |

Number: raw 0–79 × 1 + 0; typical 10, 20, 30, 40

default `32`· gate: FA-gated (depends on vehicle options)· token `RSE_MAX_VOLUME_ON`· source: firmware-trace

### `3002/5/11111111b` — Rear-seat volume limits  ·  _med_

Sets two limits for the rear-seat entertainment volume: the top of its volume scale and the lower maximum used in the child ear-protection mode. Best left unchanged.

| value | meaning |
|---|---|
| `54` | Alternative value |
| `60` | Standard |

_Not a user setting: Two packed quantities, not one number: AudioProcess FUN_002ab210 reads bytes 5-6 whole ('getMaxVolumeStepRse codMaxVolumeStepRse = 0x%4X') and FUN_002ab2a0 splits them, high byte = rear volume steps, low byte = child ear-protection limit ('writeVolumeStepsMaxRse %d and in Child Ear Protection %d'); a whole-field number would mean neither._

default `364F`· gate: FA-gated (depends on vehicle options)· token `RSE_MAX_VOLUME_STEP`· source: firmware-trace

### `3002/7/00000001b` — RDS function enable  ·  _high_

Enables or disables Radio Data System (RDS) reception and display (station name, programme type, AF, TP/TA announcements).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `01`· token `RDS_FUNCTION`· source: firmware-token

### `3002/7/00000010b` — SiriusXM album cover art display  ·  _high_

Enables display of album cover art from the SiriusXM (SDARS) satellite radio stream on the head-unit screen.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· token `SDARS_ALBUM_COVER`· source: firmware-token

### `3002/7/00000100b` — RSE headphone 180-degree audio rotation  ·  _med_

Rotates headphone audio channels 180 degrees for RSE rear-seat headphones (e.g. when headphones are worn inverted or mounted differently). Inactive on cars without RSE.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `RSE_180_DEGREES_EARPHONE`· source: firmware-token

### `3002/7/00001000b` — SiriusXM Smart Favourites  ·  _high_

Enables the SiriusXM Smart Favourites feature, which allows the tuner to automatically track and buffer multiple favourite satellite channels simultaneously for instant channel switching.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· token `SDARS_SMART_FAVORITES`· source: firmware-token

### `3002/7/00010000b` — Disable audio/entertainment menu button  ·  _high_

When active, disables the dedicated audio/entertainment hard button in the iDrive menu. Typically applied on vehicles with integrated TV or professional navigation where audio is accessed differently.

| value | meaning |
|---|---|
| `0` | Not active (button shown) |
| `1` | Active (button hidden) |

default `00`· gate: NOT 601 TV Function / 609 Professional navigation system· token `BIN_DISABLE_AUDIO_BUTTON`· source: firmware-token

### `3002/7/00100000b` — RDS character set  ·  _high_

Selects the character encoding used to decode RDS text. Default uses the standard Latin character set; the Chinese variant enables Chinese character decoding for Chinese-market vehicles.

| value | meaning |
|---|---|
| `0` | Default (Latin/standard) |
| `1` | Chinese |

default `00`· gate: 8AA Chinese version / 8LH Country control 04142· token `RDS_CHARACTER_SET`· source: firmware-token

### `3002/7/01000000b` — SiriusXM favourite alert popup  ·  _high_

Enables an on-screen popup notification when a previously favourited SiriusXM artist or song begins playing on any channel.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 655 Satellite Tuner· token `SDARS_FAVORITE_ALERT_POPUP`· source: firmware-token

### `3002/7/10000000b` — Partition wall (limousine divider)  ·  _high_

Indicates presence of a dividing partition wall between front and rear compartments (long-wheelbase limousine variants). Affects audio routing and RSE behaviour.

| value | meaning |
|---|---|
| `0` | Not active (no partition) |
| `1` | Active (partition fitted) |

default `00`· gate: FA-gated (depends on vehicle options)· token `PARTITION_WALL`· source: firmware-token

### `3002/8/11111111b` — Audio timing delay IMG, long  ·  _low_

Internal long timing delay for the audio system. Best left unchanged.

| value | meaning |
|---|---|
| `0` | Standard |

_Not a user setting: No reader: a byte-accessor scan of every syset client (813 OMAP ELFs, Jacinto IFS/EFS binaries incl. AudioProcess, HUJacintoStage1, TunerApp, CDabMain) finds no accessor for AUDIO_TUNER_TRAFFIC byte 8; AudioProcess, the chime player, reads only bytes 1-2 of the chime timing. (byte-8/9 accessors exist only for other groups: their getter defaults, e.g. 4 in NBTMediaMainApp/NbtEvoJacintoDiagHUHighApp, don't match this field's 0+1)_

default `00`· token `TIME_LAG_IMG_LONG`· source: firmware-trace

### `3002/9/11111111b` — Audio timing delay IDG, long  ·  _low_

Internal long timing delay for the audio system. Best left unchanged.

| value | meaning |
|---|---|
| `0` | Initial value |

_Not a user setting: No reader: a byte-accessor scan of every syset client (813 OMAP ELFs, Jacinto IFS/EFS binaries incl. AudioProcess, HUJacintoStage1, TunerApp, CDabMain) finds no accessor for AUDIO_TUNER_TRAFFIC byte 9; AudioProcess, the chime player, reads only bytes 1-2 of the chime timing. (byte-8/9 accessors exist only for other groups: their getter defaults, e.g. 4 in NBTMediaMainApp/NbtEvoJacintoDiagHUHighApp, don't match this field's 0+1)_

default `00`· token `TIME_LAG_IDG_LONG`· source: firmware-trace

### `3002/10/11111111b` — RSE internal video playback configuration  ·  _high_

Multi-byte configuration block (bytes 10–19) for RSE internal video playback parameters. Includes sub-fields EXTERNAL_MOST (byte10 bit2), IOC_TRACE_ON_OFF (byte11), GWTABLE_IDX (byte13 low nibble), and CAN_SELECTIVE_WAKEUP (byte19 bit3).

source: firmware-token

### `3002/20/11111111b` — Audio mixer level updates  ·  _med_

Internal setting for how the audio mixer updates its levels when sources change. Only the standard setting is offered. Best left unchanged.

| value | meaning |
|---|---|
| `2` | Standard |

_Not a user setting: Only copied through: AudioProcess FUN_002ab0f0 ('getUpdateMixerLevel value = %d') reads byte 20 and FUN_002ab188/FUN_002b0b64 hand it unchanged to the amplifier-control interface at startup ('UpdateMixerLevelDifference in CAF while startup'; 200 if unreadable). No arithmetic in the head unit and no driver-visible effect established._

default `02`· token `UPDATE_MIXER_LEVEL`· source: firmware-trace

### `3002/21/00000011b` — Audio system variant  ·  _med_

Selects the audio system hardware variant profile used by the head unit for internal audio processing and routing. Typically set by production to match the installed amplifier/speaker configuration.

| value | meaning |
|---|---|
| `0` | Variant 1 |
| `1` | Variant 2 |
| `2` | Variant 3 |
| `3` | Variant 4 |

default `00`· gate: always (no FA gate)· token `AUDIO_SYSTEM_VAR`· source: firmware-token

### `3002/21/00000100b` — Frequency display (US radio)  ·  _med_

Enables the alternate frequency display format used in US radio markets (e.g. displaying FM frequencies in different step increments). Active only with US radio control option 645.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 645 Radio control US· token `ANZEIGE_FREQ`· source: firmware-token

### `3002/21/00011000b` — SiriusXM antenna diagnostics  ·  _med_

Configures satellite tuner antenna diagnostics mode. ANTDIAG enables active antenna diagnostics; KEIN_ANTDIAG disables them.

| value | meaning |
|---|---|
| `2` | ANTDIAG (antenna diagnostics enabled) |
| `3` | KEIN_ANTDIAG (no antenna diagnostics) |

default `00`· gate: 655 Satellite Tuner· token `RADIO_SDARS`· source: firmware-token

### `3002/21/00100000b` — Reverse gear gong  ·  _high_

Enables or disables the audible chime played when reverse gear is engaged.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· token `REVERSE_GONG`· source: firmware-token

### `3002/21/01000000b` — Store equalizer data  ·  _med_

Enables persistent storage of user equalizer settings to non-volatile memory. When disabled, EQ settings are not retained across ignition cycles.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `STORE_EQ_DATA`· source: firmware-token

### `3002/21/10000000b` — Emergency Warning System — Korea (EWS)  ·  _med_

Enables the Korean Emergency Warning System (EWS) broadcast reception and alert functionality in the radio tuner.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 601 TV Function / 802 Korean version· token `EWS_KOREA`· source: firmware-token

### `3002/22/00000011b` — Front-seat memory (FBM) audio profile recall  ·  _med_

Controls whether the audio system is linked to the seat memory (FBM) profile recall. When set, audio source/volume settings are restored together with the seat memory position.

| value | meaning |
|---|---|
| `0` | Off (not linked) |
| `1` | MMI (iDrive settings recalled) |
| `2` | Audio (audio settings recalled) |

default `00`· token `FBM_SEATMEMORY`· source: firmware-token

### `3002/22/11111100b` — Reserved (byte 22, bits 7–2)  ·  _low_

Purpose not determined from available sources. Reserved/unallocated bits in the audio/tuner/traffic coding page; no firmware consumer or descriptor found.

_From resolved_unnamed: RESERVED_3002_22_bits7,6,5,4,3,2. Named byte neighbor: FBM_SEATMEMORY._

source: firmware-trace

### `3002/23/11111111b` — Reserved (bytes 23–24)  ·  _low_

Purpose not determined from available sources. Unnamed multi-byte reserved block in the audio/tuner/traffic coding page.

_From resolved_unnamed: RESERVED_3002_BYTES_23_24._

source: firmware-trace

### `3002/25/00000011b` — Reserved (byte 25, bits 1–0)  ·  _low_

Purpose not determined from available sources. Reserved/unallocated bits adjacent to microphone and mute-pin fields.

_From resolved_unnamed: RESERVED_3002_25_bits1,0. Named byte neighbors: MUTE_PIN, MICROPHONE_POSITION, MICROPHONE_PARAMETER._

source: firmware-trace

### `3002/25/00001100b` — External audio mute pin function  ·  _high_

Configures the function of the external mute pin on the audio hardware. Can be set to mute entertainment audio, or act as a mono or stereo auxiliary input trigger.

| value | meaning |
|---|---|
| `0` | No function |
| `1` | Mute entertainment (MUTE_ENT) |
| `2` | Mono input |
| `3` | Stereo input |

default `00`· gate: FA-gated (depends on vehicle options)· token `MUTE_PIN`· source: firmware-token

### `3002/25/00110000b` — Microphone position  ·  _med_

Selects which physical microphone position/mounting variant is used in this vehicle. Affects the audio processing chain for voice recognition and telephony.

| value | meaning |
|---|---|
| `0` | Position 1 |
| `1` | Position 2 |
| `2` | Position 3 |
| `3` | Position 4 |

default `00`· gate: always (no FA gate)· token `MICROPHONE_POSITION`· source: firmware-token

### `3002/25/11000000b` — Microphone parameter set  ·  _med_

Selects the microphone parameter/calibration profile. Numeric value matching the installed microphone hardware characteristics.

default `00`· gate: always (no FA gate)· token `MICROPHONE_PARAMETER`· source: firmware-token

### `3002/26/00000001b` — TLAM volume processing  ·  _low_

Turns on the volume-dependent part of the TLAM audio processing. Best left unchanged.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `TLAM_VOLUME`· source: firmware-trace

### `3002/26/00000110b` — Audio tuner profile  ·  _med_

Selects the audio tuner processing profile variant. Affects internal signal-processing parameters for the radio tuner.

| value | meaning |
|---|---|
| `0` | Profile 1 |
| `1` | Profile 2 |
| `2` | Profile 3 |
| `3` | Profile 4 |

default `00`· gate: always (no FA gate)· token `AUDIO_PROFILE`· source: firmware-token

### `3002/26/00111000b` — Chime sound set  ·  _med_

Chooses which brand's set of chimes and signal tones the head unit plays: BMW, MINI, Rolls-Royce, BMW i or the Toyota Supra. Set it to match the car's brand.

| value | meaning |
|---|---|
| `0` | BMW |
| `1` | MINI |
| `2` | Rolls-Royce |
| `3` | BMW i |
| `4` | Toyota Supra |

default `00`· gate: always (no FA gate)· token `SOUND_SIGNAL_SET`· source: firmware-trace

### `3002/26/01000000b` — Reserved (byte 26, bit 6)  ·  _low_

Purpose not determined from available sources. Reserved/unallocated bit in the audio/tuner/traffic coding page.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

_From resolved_unnamed: RESERVED_3002_26_bit6._

source: firmware-trace

### `3002/26/10000000b` — Telephone reference channel enable  ·  _med_

Enables a dedicated audio reference channel for telephone calls, used for echo cancellation and noise reduction calibration.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `REFERENCE_CHANNEL_TEL`· source: firmware-token

### `3002/27/00000011b` — Telephone reference channel mode  ·  _med_

Selects the operating mode for the telephone reference audio channel (echo cancellation/noise reduction mode variant).

| value | meaning |
|---|---|
| `0` | Mode 0 |
| `1` | Mode 1 |
| `2` | Mode 2 |
| `3` | Mode 3 |

default `00`· gate: always (no FA gate)· token `REFERENCE_CHANNEL_TEL_MODE`· source: firmware-token

### `3002/27/00000100b` — SiriusXM song tagging  ·  _high_

Enables SiriusXM song tagging, allowing users to tag currently playing songs for later purchase/identification via iTunes or similar services.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `SDARS_TAGGING`· source: firmware-token

### `3002/27/00001000b` — SiriusXM album art display  ·  _high_

Enables display of full album artwork from the SiriusXM satellite radio stream. Distinct from SDARS_ALBUM_COVER which controls cover-art thumbnail.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On (AKTIV) |

default `00`· gate: always (no FA gate)· token `SDARS_ALBUM_ART`· source: firmware-token

### `3002/27/00010000b` — TV antenna diversity  ·  _high_

Enables antenna diversity for the TV tuner, switching between multiple antennas to maintain the best TV reception. Inactive on cars without TV tuner.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `TV_DIVERSITY`· source: firmware-token

### `3002/27/00100000b` — SiriusXM Tune Start  ·  _high_

Enables the SiriusXM Tune Start feature, which replays the beginning of the current song when switching to a channel that is mid-song.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· token `SDARS_TUNE_START`· source: firmware-token

### `3002/27/01000000b` — Reserved (byte 27, bit 6)  ·  _low_

Purpose not determined from available sources. Reserved/unallocated bit in the audio/tuner/traffic coding page.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

_From resolved_unnamed: RESERVED_3002_27_bit6._

source: firmware-trace

### `3002/27/10000000b` — IBOC (HD Radio) enable  ·  _high_

Enables In-Band On-Channel (IBOC) digital radio reception, known commercially as HD Radio. Allows the tuner to receive the digital HD Radio signal on standard AM/FM frequencies. Active on vehicles with US-market type keys.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93)· token `RADIO_IBOC`· source: firmware-token

### `3002/28/00000001b` — Traffic programme (TP) checkbox  ·  _high_

Enables the TP (Traffic Programme) RDS filter checkbox in the tuner UI, allowing the user to restrict station seek to traffic-information-broadcasting stations only.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: NOT 802 Korean version / 807 Japanese version / 810 Australian version / 8AA Chinese version / vehicle type-key attribute group (FP category 17; 232 type tokens, e.g. 11CK,11CL,11DE,12CK) / 645 Radio control US / 825 Radio control Oceania / 8LS Country control 00780 / 8LH Country control 04142 / 8LT Country control 04825 · token `CHECKBOX_TP`· source: firmware-token

### `3002/28/00000010b` — Weather Band radio  ·  _high_

Enables the NOAA Weather Band radio tuner band (162.400–162.550 MHz), used in North America for weather broadcasts.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `RADIO_WEATHERBAND`· source: firmware-token

### `3002/28/00000100b` — DAB digital radio enable  ·  _high_

Enables DAB (Digital Audio Broadcasting) digital radio reception. Active on vehicles equipped with DAB tuner (option 654) or certain market configurations.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 601 TV Function / 609 Professional navigation system / 654 DAB tuner / 802 Korean version· token `RADIO_DAB`· source: firmware-token

### `3002/28/00111000b` — DAB standard/mode  ·  _high_

Selects the Digital Audio Broadcasting standard supported by the tuner. Determines which DAB variants (DAB, DAB+, DMB-Audio, DMB-Video) are enabled.

| value | meaning |
|---|---|
| `0` | DAB (original standard) |
| `1` | DAB+ (MPEG-4 HE-AAC) |
| `2` | DMB Audio |
| `3` | DMB Video |

default `00`· gate: FA-gated (depends on vehicle options)· token `DAB_STANDARD`· source: firmware-token

### `3002/28/11000000b` — DAB tuner hardware layout  ·  _high_

Tells the head unit which DAB tuner hardware layout is installed. Only the dual-tuner layout is offered. Best left unchanged.

| value | meaning |
|---|---|
| `2` | Dual tuner, dual hardware |

_Not a user setting: No reader: TunerApp reads the other byte-28 fields (RADIO_DAB 0x04, DAB_STANDARD 0x38) but no binary (OMAP, Jacinto IFS/EFS incl. CDabMain) has an accessor for byte 28 mask 0xC0; one value offered._

default `02`· token `RADIO_DAB_VARIANTEN`· source: firmware-trace

### `3002/29/00000011b` — DAB/DMB HMI display mode  ·  _high_

Controls whether the DAB/DMB source is displayed as a radio station (DAB radio) or as a TV source (DMB replacing TV) in the HMI menus.

| value | meaning |
|---|---|
| `0` | DAB/DMB as radio (DAB_DMB_RADIO) |
| `1` | DMB replaces TV (DMB_STATT_TV) |

default `00`· token `HMI_FUER_DAB_DMB`· source: firmware-token

### `3002/29/00111100b` — Sound system type  ·  _med_

Tells the head unit which sound system is installed, from the base stereo up to the premium systems. Set it to match the car's speakers and amplifier. The factory sets it from the HiFi loudspeaker system (S676).

| value | meaning |
|---|---|
| `0` | Stereo (base system) |
| `1` | HiFi |
| `2` | Top HiFi |
| `3` | Individual sound system |
| `4` | Harman Kardon surround sound |
| `5` | High premium |
| `6` | Harman Kardon HiFi system |

default `00`· gate: 676 HiFi loudspeaker system / HIFI Retrofit, HiFi system Alpine· token `AUDIO_SYSTEM`· source: firmware-token

### `3002/29/11000000b` — Amplifier type  ·  _med_

Tells the head unit which amplifier drives the speakers: its own built-in amplifier, a separate external amplifier or an external amplifier on the car's fiber-optic (MOST) network. Set it to match the car's audio hardware. The factory sets it from the HiFi loudspeaker system (S676) or Harman Kardon HiFi system (S674).

| value | meaning |
|---|---|
| `0` | Built-in amplifier |
| `1` | External amplifier |
| `2` | External, fiber-optic network |

default `00`· gate: 676 HiFi loudspeaker system / 674 HiFi loudspeaker system Harman Kardon / HIFI Retrofit, HiFi system Alpine· token `AMPLIFIER_VARIANT`· source: firmware-token

### `3002/30/00000001b` — Reserved (byte 30, bit 0)  ·  _low_

Purpose not determined from available sources. Reserved/unallocated bit in the audio/tuner/traffic coding page.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

_From resolved_unnamed: RESERVED_3002_30_bit0._

source: firmware-trace

### `3002/30/00000010b` — Multichannel audio enable  ·  _high_

Enables multichannel (surround) audio processing. When active, the head unit routes audio through a multi-channel amplifier/speaker configuration rather than standard stereo.

| value | meaning |
|---|---|
| `0` | Not active (stereo) |
| `1` | Active (multichannel/surround) |

default `00`· gate: FA-gated (depends on vehicle options)· token `MULTICHANNEL`· source: firmware-token

### `3002/30/00000100b` — Automatic analogue station store  ·  _med_

Enables automatic storing of the strongest analogue (AM/FM) stations to presets. When active, the tuner automatically populates preset memory with the best-received stations.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `AUTOSTORE_ANALOG`· source: firmware-token

### `3002/30/00001000b` — DAB following HMI checkbox  ·  _high_

Shows or hides the DAB-following (DAB→FM fallback) checkbox option in the tuner HMI. When shown, the user can enable/disable DAB→FM following from the radio settings menu.

| value | meaning |
|---|---|
| `0` | Hidden |
| `1` | Shown |

default `00`· gate: NOT 654 DAB tuner / 802 Korean version / 810 Australian version / 8AA Chinese version· token `DAB_FOLLOWING_CHECKB_HMI`· source: firmware-token

### `3002/30/11110000b` — TLAM audio characteristic map  ·  _low_

Selects one of twelve built-in characteristic maps for the TLAM stage of the audio processing, which works with loudness and volume. Best left unchanged.

| value | meaning |
|---|---|
| `1` | Map 1 |
| `2` | Map 2 |
| `3` | Map 3 |
| `4` | Map 4 |
| `5` | Map 5 |
| `6` | Map 6 |
| `7` | Map 7 |
| `8` | Map 8 |
| `9` | Map 9 |
| `10` | Map 10 |
| `11` | Map 11 |
| `12` | Map 12 |

default `01`· gate: always (no FA gate)· token `TLAM_KENNFELD`· source: firmware-trace

### `3002/31/00000111b` — Sound tuning set  ·  _high_

Picks which of up to eight factory sound tunings the head unit loads for its audio output, such as equalizer, gain and limiter settings. Tunings exist per model series and coded sound system; if the chosen one is missing for that combination, the head unit uses the default tuning for its amplifier type.

| value | meaning |
|---|---|
| `0` | Tuning set 1 |
| `1` | Tuning set 2 |
| `2` | Tuning set 3 |
| `3` | Tuning set 4 |
| `4` | Tuning set 5 |
| `5` | Tuning set 6 |
| `6` | Tuning set 7 |
| `7` | Tuning set 8 |

default `00`· token `EQ_VARIANT`· source: firmware-trace

### `3002/31/00001000b` — SiriusXM Electronic Programme Guide (EPG)  ·  _high_

Enables the SiriusXM Electronic Programme Guide, which displays current and upcoming programme schedules for satellite radio channels.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 655 Satellite Tuner· token `SDARS_EPG`· source: firmware-token

### `3002/31/00010000b` — SiriusXM Featured Favorites  ·  _med_

Turns on SiriusXM Featured Favorites: themed sets of channels that SiriusXM sends over the air, which the radio can offer alongside your own presets. For cars with a satellite tuner (S655).

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 655 Satellite Tuner· token `SDARS_FEATURED_FAVORITES`· source: firmware-token

### `3002/31/00100000b` — SiriusXM subscription status notification  ·  _high_

Enables display of SiriusXM subscription status and renewal notifications on the head-unit screen.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 655 Satellite Tuner· token `SDARS_STATUS_SUBSCRIP_NOTIFI`· source: firmware-token

### `3002/31/11000000b` — Reserved (byte 31, bits 7–6)  ·  _low_

Purpose not determined from available sources. Reserved/unallocated bits in the audio/tuner/traffic coding page.

_From resolved_unnamed: RESERVED_3002_31_bits7,6._

source: firmware-trace

### `3002/32/11111111b` — Reserved (bytes 32–51)  ·  _low_

Purpose not determined from available sources. Unnamed multi-byte reserved block in the audio/tuner/traffic coding page.

_From resolved_unnamed: RESERVED_3002_BYTES_32_51._

source: firmware-trace

### `3002/52/00000011b` — Reserved (byte 52, bits 1–0)  ·  _low_

Purpose not determined from available sources. Reserved/unallocated bits in the audio/tuner/traffic coding page.

_From resolved_unnamed: RESERVED_3002_52_bits1,0._

source: firmware-trace

### `3002/52/00000100b` — Medium-wave (AM) radio band enable  ·  _high_

Enables the Medium Wave (MW/AM) radio band in the tuner. When disabled, the AM broadcast band is not available for manual or seek tuning.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `01`· gate: always (no FA gate)· token `RADIO_BAND_MW`· source: firmware-token

### `3002/52/00001000b` — Shortwave band (SW)  ·  _med_

Makes the shortwave (SW) band available in the radio, alongside FM and AM. Set per market at the factory.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: NOT 802 Korean version / 807 Japanese version / 822 Gulf version / 8AA Chinese version / vehicle type-key attribute group (FP category 17; 232 type tokens, e.g. 11CK,11CL,11DE,12CK) / 645 Radio control US / 825 Radio control Oceania / 8LS Country control 00780 / 8LH Country control 04142 / 8LT Country control 04825 · token `RADIO_BAND_KW`· source: firmware-token

### `3002/52/00110000b` — DAB slideshow image timeout  ·  _high_

Sets the auto-timeout for DAB slideshow images displayed on screen. When set to OFF, slideshow images are displayed indefinitely until the next image arrives.

| value | meaning |
|---|---|
| `0` | Off (no timeout) |

default `02`· gate: FA-gated (depends on vehicle options)· token `DAB_SLIDESHOW_TIMEOUT`· source: firmware-token

### `3002/52/01000000b` — On-screen volume pop-up  ·  _med_

Shows a pop-up on the central display when you change the volume. Disabled at the factory with Switch off volume pop-up (SVPOF).

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: NOT VPOF Switch off Volume Pop-up· token `VOLUME_POPUP_DISPLAY`· source: firmware-token

### `3002/52/10000000b` — Volume popup suppression  ·  _high_

When active, suppresses (rejects) the volume popup display even if VOLUME_POPUP_DISPLAY is enabled. Acts as an override to disable the popup.

| value | meaning |
|---|---|
| `0` | Not active (popup allowed) |
| `1` | Active (popup suppressed) |

default `00`· gate: always (no FA gate)· token `VOLUME_POPUP_REJECTION`· source: firmware-token

### `3002/53/00000001b` — Volume popup exception  ·  _med_

Enables an exception to the volume popup suppression rule, allowing the popup to appear in specific defined circumstances even when normally suppressed.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `VOLUME_POPUP_EXCEPTION`· source: firmware-token

### `3002/53/00000010b` — USB bulk transfer mode  ·  _med_

Enables USB bulk transfer mode for media devices. When active, data transfers from USB media devices use bulk transfer protocol rather than interrupt-driven transfers.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `USB_BULK_TRANSFER`· source: firmware-token

### `3002/53/01111100b` — DAB regional variant  ·  _high_

Selects the regional/country-specific DAB configuration variant. Determines country-specific frequency plans, channel lists, and features for the DAB tuner.

| value | meaning |
|---|---|
| `1` | ECE (Europe) |
| `2` | Australia |
| `4` | Korea |
| `8` | Canada |
| `16` | Singapore |
| `17` | China |

default `01`· gate: 654 DAB tuner / 810 Australian version· token `DAB_LAENDERVARIANTEN`· source: firmware-token

### `3002/53/10000000b` — DAB→FM following enable  ·  _high_

Enables automatic fallback from DAB to FM reception when the DAB signal is lost. The system switches to the corresponding FM frequency to maintain uninterrupted listening.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· token `FOLLOWING_DAB_FM`· source: firmware-token

### `3002/54/00000001b` — DAB→DAB service following enable  ·  _high_

Enables DAB-to-DAB service following, allowing the tuner to follow a DAB service (station) across different DAB ensembles/multiplexes when the signal quality of the current ensemble degrades.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: NOT 802 Korean version· token `DAB_DABFOLLOWING`· source: firmware-token

### `3002/54/00001110b` — DAB frequency band selection  ·  _high_

Selects which DAB frequency bands the tuner scans and receives. Band III (174–240 MHz) is standard for Europe; Band L (1452–1492 MHz) is less common.

| value | meaning |
|---|---|
| `0` | No band (disabled) |
| `1` | Band III only |
| `2` | Band L only |
| `3` | Both bands (III and L) |

default `00`· gate: always (no FA gate)· token `DAB_BAND`· source: firmware-token

### `3002/54/01110000b` — DMB video maximum frame rate  ·  _med_

Limits the maximum frame rate for DMB (Digital Multimedia Broadcasting) video decoding. Lower frame rates reduce processing load; higher values allow smoother video.

| value | meaning |
|---|---|
| `3` | 3 fps |
| `4` | 4 fps |
| `5` | 5 fps |
| `6` | 6 fps |
| `7` | 7 fps (max) |

default `00`· gate: always (no FA gate)· token `DMB_MAX_FRAMERATE`· source: firmware-token

### `3002/54/10000000b` — DAB slideshow enable  ·  _high_

Enables the DAB slideshow feature, which displays images broadcast alongside DAB radio stations (DAB Slideshow/DLS data service).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· token `DAB_SLIDESHOW`· source: firmware-token

### `3002/55/00000001b` — DAB Journaline text service enable  ·  _high_

Enables the DAB Journaline data service, which provides text-based news, sports, weather, and programme information alongside DAB broadcasts.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 601 TV Function / 609 Professional navigation system / 654 DAB tuner / 802 Korean version / 807 Japanese version / 8AA Chinese version / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / 8LH Country control 04142 / 8LT Country control 04825  / 6NH Hands-free system with USB interface / 6NS Comfort telephony with expanded smartphone connection / 6AE TeleServices / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `DAB_JOURNALINE`· source: firmware-token

### `3002/55/00000010b` — Telephony audio offset enable  ·  _med_

Enables an audio level offset applied to telephone calls, compensating for level differences between the telephony audio channel and entertainment audio.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 6NH Hands-free system with USB interface / 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / 6NW Telephony with wireless charging / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `AUDIO_OFFSET`· source: firmware-token

### `3002/55/00001100b` — DAB traffic announcements mode  ·  _high_

Configures which DAB traffic announcements trigger audio interruption. Can be restricted to traffic-only or include all announcement types.

| value | meaning |
|---|---|
| `1` | Traffic announcements only |
| `2` | All announcements |

default `00`· gate: FA-gated (depends on vehicle options)· token `DAB_ANNOUNCEMENTS`· source: firmware-token

### `3002/55/00110000b` — Number of microphones  ·  _med_

Specifies the number of microphone channels installed in the vehicle. Affects voice recognition and telephony processing.

| value | meaning |
|---|---|
| `0` | 0 microphones |
| `1` | 1 microphone |
| `2` | 2 microphones |

default `00`· token `MICROPHONE_NUMBER`· source: firmware-token

### `3002/55/11000000b` — DAB Electronic Programme Guide (EPG) view  ·  _high_

Selects the EPG display format for DAB radio. Determines whether the programme guide shows now/next only, or includes a full day view with programme details.

| value | meaning |
|---|---|
| `1` | Now/Next + Details |
| `2` | Now/Next + Details + Day view |

default `00`· gate: 802 Korean version / 8LS Country control 00780 / 8LH Country control 04142· token `DAB_EPG`· source: firmware-token

### `3002/56/11111111b` — Audio signal routing block  ·  _med_

Multi-byte audio signal routing configuration array (bytes 56–79, 24 bytes). Defines the audio routing matrix between input sources and output channels. Non-trivial factory default (00F500F5.) encodes channel assignments.

_From resolved_unnamed: AUDIO_SIGNAL_ROUTING_BLOCK. Named sub-field AUDIO_SIGNAL_ROUTING at byte 56 bits 1–0._

default `00F500F5000000F500F500F500F500F500000000000000F5`· source: firmware-trace

### `3002/80/00000011b` — DAB station list checkbox display  ·  _high_

Controls how the station-selection checkbox is displayed in the DAB station list HMI. Can show checkbox in on or off state, or hide it entirely.

| value | meaning |
|---|---|
| `0` | Show checkbox (selected state on) |
| `1` | Show checkbox (selected state off) |
| `2` | Hide checkbox (on state) |
| `3` | Hide checkbox (off state) |

default `00`· gate: FA-gated (depends on vehicle options)· token `DAB_HMI_LIST_VIEW`· source: firmware-token

### `3002/80/00001100b` — AM/FM station list checkbox display  ·  _high_

Controls how the station-selection checkbox is displayed in the AM/FM station list HMI.

| value | meaning |
|---|---|
| `0` | Show checkbox (selected state on) |
| `1` | Show checkbox (selected state off) |
| `2` | Hide checkbox (on state) |
| `3` | Hide checkbox (off state) |

default `00`· gate: FA-gated (depends on vehicle options)· token `AM_FM_HMI_LIST_VIEW`· source: firmware-token

### `3002/80/00110000b` — TV channel list checkbox display  ·  _med_

Controls how the channel-selection checkbox is displayed in the TV channel list HMI.

| value | meaning |
|---|---|
| `0` | Off/default |
| `1` | Show checkbox (selected) |
| `3` | Hide checkbox (off) |

default `00`· gate: FA-gated (depends on vehicle options)· token `TV_HMI_LIST_VIEW`· source: firmware-token

### `3002/80/11000000b` — SiriusXM channel list checkbox display  ·  _med_

Controls how the channel-selection checkbox is displayed in the SiriusXM satellite radio channel list HMI.

| value | meaning |
|---|---|
| `0` | Off/default |
| `1` | Show checkbox (selected) |
| `3` | Hide checkbox (off) |

default `00`· gate: FA-gated (depends on vehicle options)· token `SDARS_HMI_LIST_VIEW`· source: firmware-token

### `3002/81/00000001b` — TV CA (conditional access) ID menu  ·  _med_

Enables the conditional access ID menu in the TV tuner interface (CDMM = Conditional Access/Digital Media Management), used to display or configure pay-TV smart card/module information.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `CDMM_TV_CA_ID_MENUE`· source: firmware-token

### `3002/81/00000010b` — Smartphone apps: Android phones  ·  _med_

Lets Android phones use the head unit's smartphone apps connection, so supported apps on the phone work through iDrive. Enabled at the factory with Apps or TeleServices (S6NR or S6AE).

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 6NR Apps / 6AE TeleServices· token `A4A_ANDROID`· source: firmware-trace

### `3002/81/11111100b` — Reserved (byte 81, bits 7–2)  ·  _low_

Purpose not determined from available sources. Reserved/unallocated bits in the audio/tuner/traffic coding page.

_From resolved_unnamed: RESERVED_3002_81_bits7,6,5,4,3,2._

source: firmware-trace

### `3002/82/11111111b` — Reserved (bytes 82–149)  ·  _low_

Purpose not determined from available sources. Large unnamed reserved block at the end of the audio/tuner/traffic coding page.

_From resolved_unnamed: RESERVED_3002_BYTES_82_149._

source: firmware-trace

## Datagroup 0x3003 (163 parameters)

### `3003/0/11111111b` — Phone connection delay at startup  ·  _med_

Sets how long the head unit may hold back the Bluetooth hands-free connection to a phone while it starts up; the phone connects once startup is done or the time is up. When disabled, the phone connects right away.

| value | meaning |
|---|---|
| `0` | Disabled |

Number: raw 0–255 × 1 + 0 s; typical 5, 10, 15

default `00`· gate: FA-gated (depends on vehicle options)· token `HEAD_BOOT_UP_TIMEOUT`· source: firmware-trace

### `3003/1/00000001b` — CDMM global cover (USB/iPod metadata cover art)  ·  _med_

Enables global cover-art fetching in the CDMM (Content Device Media Manager) for USB and iPod sources. When active, album artwork is retrieved and displayed for all sources.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· token `CDMM_GLOBAL_COVER`· source: firmware-token

### `3003/1/00000010b` — CBS lifelong service interval (MobiGuard)  ·  _med_

Enables Condition Based Service (CBS) integration with MobiGuard for lifelong/permanent service interval tracking via the telematics connection.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `CBS_MOBIGUAR_LIFELONG`· source: firmware-token

### `3003/1/00000100b` — RSE service messages  ·  _med_

Enables display of service/reminder messages on the rear-seat entertainment (RSE) screens.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `RSE_SERVICE_MESSAGES`· source: firmware-token

### `3003/1/00001000b` — Vanity (alpha) dialling  ·  _med_

Enables vanity (letter-to-digit) dialling on the phone keypad, allowing the user to enter alphanumeric phone numbers (e.g. 1-800-BMW-CALL). Active on Canadian-spec vehicles.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 838 Canadian version / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93)· token `VANITY_DIALING`· source: firmware-token

### `3003/1/00010000b` — Speech-to-text input  ·  _med_

Enables voice-dictation / speech-to-text conversion for composing messages or other text fields. Requires 6NL Bluetooth+USB+BMW Assist option.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 6NL Connecting Bluetooth and USB devices including BMW assist· token `SPEECH_2_TEXT`· source: firmware-token

### `3003/1/00100000b` — USB/iPod phonebook (CDMM pod book)  ·  _med_

Enables CDMM phonebook synchronisation over USB/iPod. When active, the head unit can read contacts stored on a connected iPod or USB device.

| value | meaning |
|---|---|
| `0` | Off (not active) |
| `1` | On (active) |

default `00`· gate: always (no FA gate)· token `CDMM_USB_POD_BOOK`· source: firmware-token

### `3003/1/01000000b` — Message timestamp display  ·  _med_

Enables display of timestamps on received messages (SMS, email) in the PIM/phone message list.

| value | meaning |
|---|---|
| `1` | Active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TIMESTAMP_DISPLAY`· source: firmware-token

### `3003/1/10000000b` — New talking-head UI concept  ·  _med_

Enables the updated 'talking head' graphical concept for the Bluetooth/phone call screen, showing an animated graphic during calls.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· token `NEW_TALKING_HEAD_CONCEPT`· source: firmware-token

### `3003/2/00000001b` — Wireless CarPlay / iOS wireless A4A  ·  _med_

Enables wireless Apple CarPlay (A4A — Apps for Automobile, iOS) over Wi-Fi. When off, only wired USB CarPlay is available.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `01`· gate: 6NR Apps / 6AE TeleServices· token `A4A_WIRELESS_IOS`· source: firmware-token

### `3003/2/00000010b` — Wireless Android Auto / Android wireless A4A  ·  _med_

Enables wireless Android Auto (A4A — Apps for Automobile, Android) over Wi-Fi. When off, only wired USB Android Auto is available.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `01`· gate: 6NR Apps / 6AE TeleServices· token `A4A_WIRELESS_ANDROID`· source: firmware-token

### `3003/2/00011100b` — A4A/smartphone integration API type  ·  _high_

Selects which smartphone integration API protocol the head unit exposes on the USB port. NONE disables the API; NBT = standard NBT protocol; ENTRY_NAV_MEDIA = Entry/Entry-Nav media-only subset.

| value | meaning |
|---|---|
| `0` | None (disabled) |
| `5` | NBT |
| `6` | Entry Nav Media |

default `00`· token `API_TYPE`· source: firmware-token

### `3003/2/00100000b` — MTP USB device mode enable  ·  _med_

Enables the MTP (Media Transfer Protocol) USB mode, allowing the head unit to access media files on Android devices connected via USB.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `API_MTP_EIN_AUS`· source: firmware-token

### `3003/2/01000000b` — iPod USB device mode enable  ·  _med_

Enables the iPod/iPhone accessory protocol (iAP) over USB, allowing the head unit to control and browse an iPod/iPhone connected via USB cable.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `API_IPOD_EIN_AUS`· source: firmware-token

### `3003/2/10000000b` — Bluetooth HCI debug trace enable  ·  _med_

Enables debug-level HCI (Host Controller Interface) trace logging for the Bluetooth stack. Intended for workshop/engineering diagnosis; has no user-visible effect under normal use.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: HUEN Head-unit variant: NBT-Evo Entry/High present (HO-word) / HUTR Head-unit transport/standby mode word (HO-word)· token `DEBUG_HCI_TRACE_EIN_AUS`· source: firmware-token

### `3003/3/00000001b` — Bluetooth audio player (A2DP)  ·  _med_

Enables the A2DP Bluetooth audio player, allowing high-quality stereo audio streaming from a connected Bluetooth device to the vehicle audio system.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 6NH Hands-free system with USB interface / 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `AUDIO_PLAYER_ON_OFF`· source: firmware-token

### `3003/3/00000010b` — Bluetooth DUN profile (dial-up networking)  ·  _med_

Enables the Bluetooth DUN (Dial-Up Networking) profile, allowing the head unit to use a paired phone's mobile data connection. Mostly legacy.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `DUN_PROFILE`· source: firmware-token

### `3003/3/00000100b` — Bluetooth PAN profile (personal area network)  ·  _med_

Enables the Bluetooth PAN (Personal Area Network) profile, allowing IP networking over Bluetooth between the head unit and a paired phone.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `PAN_PROFILE`· source: firmware-token

### `3003/3/00001000b` — Smartphone voice recognition passthrough  ·  _med_

Enables use of the connected smartphone's own voice recognition (e.g. Siri, Google Assistant) triggered from the vehicle. The voice command is passed through to the CE (consumer electronics) device rather than processed locally.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 6NH Hands-free system with USB interface / 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / 6NW Telephony with wireless charging / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `CE_DEVICE_SPEECH_RECOGNITION`· source: firmware-token

### `3003/3/00010000b` — Two phones simultaneously (dual HFP)  ·  _med_

Enables simultaneous connection of two phones via Bluetooth, allowing both to be active for calls and audio at the same time. Requires 6NK/6NL/6NS/6NW telephony options.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / 6NW Telephony with wireless charging· token `TWO_PHONES_PARALLEL`· source: firmware-token

### `3003/3/11100000b` — Telematics ECU type  ·  _high_

Specifies which telematics control unit is fitted. Selects between TCB (Telematics Communication Box), TPL (Telematics Platform), or ATM (Advanced Telematics Module) variants to match installed hardware.

| value | meaning |
|---|---|
| `1` | TCB (Telematics Communication Box) |
| `2` | TPL (Telematics Platform) |
| `3` | ATM (Advanced Telematics Module) |

default `00`· gate: 6AE TeleServices / 6AF Statutory emergency request· token `TELEMATIC_ECU`· source: firmware-token

### `3003/4/11111111b` — Phone type  ·  _high_

Specifies the type of telephone hardware present or expected. NO_PHONE means no integrated phone module; INTERNAL_PHONE indicates a built-in cellular module (rare, legacy fitment).

| value | meaning |
|---|---|
| `0` | No phone |
| `6` | Internal phone module |

default `00`· gate: 6NH Hands-free system with USB interface / 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / 6NW Telephony with wireless charging / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `PHONE_TYPE`· source: firmware-token

### `3003/5/00000001b` — Phone in rear-seat entertainment (RSE)  ·  _med_

Enables phone/telephony controls and display on the rear-seat entertainment screens, allowing rear passengers to view and potentially control calls.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `PHONE_RSE`· source: firmware-token

### `3003/5/00000010b` — Phone MPC integration  ·  _med_

Enables the phone module integration with MPC (Multi Purpose Controller / multimedia head unit controller). Controls whether the phone application is accessible via the MPC interface.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `PHONE_MPC`· source: firmware-token

### `3003/5/00000100b` — Bluetooth object push menu (OPP)  ·  _med_

Enables the Bluetooth OPP (Object Push Profile) menu, allowing files such as contacts (vCard) or images to be exchanged between the head unit and a paired phone via Bluetooth.

| value | meaning |
|---|---|
| `0` | Off (not active) |
| `1` | On (active) |

default `00`· gate: 807 Japanese version / 6NH Hands-free system with USB interface / 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / 6NW Telephony with wireless charging / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `PHONE_OBJPUSH_MENUE`· source: firmware-token

### `3003/5/00001000b` — Phone conference call  ·  _med_

Enables the ability to merge active and held calls into a three-way conference call via the hands-free phone interface.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: NOT 807 Japanese version / 6NH Hands-free system with USB interface / 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / 6NW Telephony with wireless charging / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `PHONE_CONFERENCE_CALL`· source: firmware-token

### `3003/5/00010000b` — Phone answer/hold function  ·  _med_

Enables the ability to place an active call on hold and answer a second incoming call (call waiting with hold), or to swap between two calls.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 807 Japanese version / 6NH Hands-free system with USB interface / 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / 6NW Telephony with wireless charging / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `PHONE_RESPONSE_HOLD`· source: firmware-token

### `3003/5/00100000b` — Phonebook name display order  ·  _high_

Sets the display order for contact names in the phonebook. Active on English-speaking markets (UK, Australia, Gulf, Canada) where first-name-first is conventional.

| value | meaning |
|---|---|
| `0` | Last name, first name |
| `1` | First name, last name |

default `00`· gate: 810 Australian version / 812 Great Britain/Ireland version / 822 Gulf version / 838 Canadian version / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93)· token `PHONEBOOK_NAME_DISPL_ORD`· source: firmware-token

### `3003/5/01000000b` — Phonebook sort order  ·  _med_

Sets the sort order for contacts in the phonebook list. Controls whether the phonebook is sorted alphabetically by last name or first name.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· token `PHONEBOOK_NAME_ORD`· source: firmware-token

### `3003/5/10000000b` — Microphone sensitivity level  ·  _high_

Selects the hands-free microphone sensitivity level: L4 (standard sensitivity) or L6 (higher sensitivity) to match the installed microphone hardware.

| value | meaning |
|---|---|
| `0` | L4 microphone (standard sensitivity) |
| `1` | L6 microphone (higher sensitivity) |

default `00`· gate: FA-gated (depends on vehicle options)· token `MICROPHONE_SENSITIVITY`· source: firmware-token

### `3003/6/00001111b` — Voice memo maximum length  ·  _high_

Sets the longest voice memo you can record in the Office menu. When disabled, a recording stops as soon as it starts.

| value | meaning |
|---|---|
| `0` | Disabled |

Number: raw 0–15 × 30 + 0 s; typical 60, 120, 240

default `00`· gate: FA-gated (depends on vehicle options)· token `PIM_AUDIO_RECORDING_LENGTH`· source: firmware-trace

### `3003/6/00010000b` — Address book enable  ·  _med_

Enables the address book / contacts application in the phone menu, allowing the head unit to display and dial contacts downloaded from a paired Bluetooth phone.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: NOT 807 Japanese version / 6NH Hands-free system with USB interface / 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / 6NW Telephony with wireless charging / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `ADRESSBOOK`· source: firmware-token

### `3003/6/00100000b` — Bluetooth module enable  ·  _med_

Master enable for the Bluetooth hardware module. When off, all Bluetooth functionality (phone, audio streaming, OPP) is disabled.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 6NH Hands-free system with USB interface / 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / 6NW Telephony with wireless charging / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `BT_MODUL_ON_OFF`· source: firmware-token

### `3003/6/01000000b` — Unified call lists (merged call history)  ·  _med_

Enables a single merged call history list combining call logs from all paired phones, rather than showing a separate list per device.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `01`· gate: always (no FA gate)· token `UNIFIED_CALL_LISTS`· source: firmware-token

### `3003/6/10000000b` — In-band ringtone  ·  _med_

Plays the phone's own ringtone through the car speakers for incoming calls, when the phone sends it over the Bluetooth hands-free link. When disabled, the car plays its own ringtone instead.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `INBAND_RINGING`· source: firmware-token

### `3003/7/00000001b` — Download contacts only when data changed  ·  _med_

Optimises phonebook synchronisation by only downloading contacts from the phone when a change is detected, reducing sync time after initial download.

| value | meaning |
|---|---|
| `0` | Off (always download) |
| `1` | On (download on change only) |

default `00`· gate: FA-gated (depends on vehicle options)· token `CONTACTS_DOWNLOAD_ONLY_WHEN_DATA_CHANGED`· source: firmware-token

### `3003/7/00000010b` — Contacts from online source  ·  _med_

Enables retrieval of contacts/phonebook data from an online/cloud source (e.g. BMW ConnectedDrive or synced contacts service) in addition to or instead of the locally paired phone.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· token `CONTACTS_FROM_ONLINE_SOURCE`· source: firmware-token

### `3003/7/00000100b` — USB out-of-band Bluetooth pairing (OOB)  ·  _med_

Enables Out-of-Band (OOB) Bluetooth pairing via USB cable. This allows initial Bluetooth pairing to be performed automatically when the phone is first connected via USB, skipping manual PIN entry.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `USB_OOB_BT_PAIRING`· source: firmware-token

### `3003/7/11111000b` — Reserved bits (3003 byte 7, bits 7-3)  ·  _low_

Purpose not determined from available sources. Unnamed/reserved coding bits in the phone/telematics page; no descriptor record and no firmware consumer identified.

source: inferred

### `3003/8/00000011b` — Ringtone brand  ·  _med_

Chooses which brand's built-in ringtone the head unit plays for incoming calls. Pick the brand that matches the car.

| value | meaning |
|---|---|
| `0` | BMW |
| `1` | MINI |
| `2` | BMW i |
| `3` | Rolls-Royce |

default `00`· gate: always (no FA gate)· token `RINGTONE`· source: firmware-token

### `3003/8/00000100b` — Contacts and navigation separated  ·  _med_

When active, the contacts/phonebook and navigation destination entry are shown as separate menu items rather than integrated into a combined address-search view.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· token `CONTACTS_NAVI_SEPARATED`· source: firmware-token

### `3003/8/00001000b` — Bluetooth connection mode (single / multi-link)  ·  _high_

Sets whether the head unit supports a single simultaneous Bluetooth device connection (Singlelink) or multiple parallel Bluetooth connections (Multilink), enabling two phones to be linked at once.

| value | meaning |
|---|---|
| `0` | Singlelink (one device at a time) |
| `1` | Multilink (multiple simultaneous devices) |

default `00`· gate: 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / 6NW Telephony with wireless charging· token `SINGLE_OR_MULTILINK`· source: firmware-token

### `3003/8/00010000b` — Contact phone numbers via Bluetooth  ·  _med_

Enables display of phone numbers from contacts downloaded via Bluetooth, as opposed to only showing contact names.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `CONTACT_NUMBERS_BT`· source: firmware-token

### `3003/8/00100000b` — Contact book photos  ·  _med_

Enables display of contact photos/pictures downloaded from the paired phone alongside contact names in the phonebook list.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: NOT 807 Japanese version / 810 Australian version / 8LH Country control 04142 / 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / 6NW Telephony with wireless charging· token `CONTACT_BOOK_PICTURES`· source: firmware-token

### `3003/8/01000000b` — Bluetooth handset (cordless handset support)  ·  _med_

Enables support for a separate Bluetooth cordless handset accessory connected to the vehicle, allowing calls to be taken on a detachable handset. Legacy feature.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `BLUETOOTH_HANDSET`· source: firmware-token

### `3003/8/10000000b` — Bluetooth SAP profile (SIM access)  ·  _med_

Enables the Bluetooth SAP (SIM Access Profile), allowing the vehicle's built-in cellular module to use the SIM card from a paired phone.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `BLUETOOTH_SAP_SUPPORT`· source: firmware-token

### `3003/9/11111111b` — Bluetooth phone instance ID  ·  _med_

Identifies which Bluetooth phone instance slot is active (used when multiple phone module instances are supported). Value 0 = first/default instance.

| value | meaning |
|---|---|
| `0` | Instance 0 (default) |

default `00`· gate: FA-gated (depends on vehicle options)· token `BT_PHONE_INSTANCE_ID`· source: firmware-token

### `3003/10/00000001b` — Bluetooth second HFP connection  ·  _med_

Enables a second simultaneous Bluetooth HFP (Hands-Free Profile) connection, allowing two phones to be active for calls concurrently (complementary to TWO_PHONES_PARALLEL).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / 6NW Telephony with wireless charging· token `BLUETOOTH_2ND_HFP`· source: firmware-token

### `3003/10/00000110b` — Reserved bits (3003 byte 10, bits 2-1)  ·  _low_

Purpose not determined from available sources. Unnamed/reserved coding bits in the phone/telematics page; no descriptor record and no firmware consumer identified.

source: inferred

### `3003/10/00001000b` — Macro PIM enable  ·  _med_

Enables the macro-level PIM (Personal Information Manager) feature set, providing calendar, messages, and notes integration in the iDrive menu. Requires 6NK/6NL/6NS/6NW and excludes Japanese market.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: NOT 807 Japanese version / 8LH Country control 04142 / 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / 6NW Telephony with wireless charging· token `MACRO_PIM`· source: firmware-token

### `3003/10/00110000b` — Reserved bits (3003 byte 10, bits 5-4)  ·  _low_

Purpose not determined from available sources. Unnamed/reserved coding bits in the phone/telematics page; no descriptor record and no firmware consumer identified.

source: inferred

### `3003/10/01000000b` — PIM cross-device use  ·  _med_

Enables PIM (calendar/contacts/messages) data sharing across multiple connected CE (consumer electronics) devices, so all paired phones see the same PIM state.

| value | meaning |
|---|---|
| `0` | Off (not active) |
| `1` | On (active) |

default `00`· gate: always (no FA gate)· token `PIM_CROSS_USE`· source: firmware-token

### `3003/10/10000000b` — PIM text-to-speech (TTS) readout  ·  _med_

Enables text-to-speech readout of PIM messages (SMS, calendar entries, emails) through the vehicle audio system, allowing the driver to listen to messages without looking at the screen.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 606 Navigation system Business / 609 Professional navigation system / 249 Multifunction for steering wheel / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `PIM_TTS`· source: firmware-token

### `3003/11/00000111b` — Text while driving: Office entries  ·  _med_

Limits how much of a message, email or other Office entry appears on screen while the car is moving. Rules on driver distraction vary by country.

| value | meaning |
|---|---|
| `0` | No details |
| `1` | First page only |
| `2` | Up to three lines |
| `3` | No message body |
| `4` | No details, with buttons |
| `7` | Full text |

default `00`· gate: FA-gated (depends on vehicle options)· token `PIM_DRIVING_TEXT_LENGTH`· source: firmware-token

### `3003/11/00001000b` — PIM navigate to meeting location  ·  _high_

Enables a one-tap option in calendar meeting entries to navigate directly to the meeting location using the navigation system.

| value | meaning |
|---|---|
| `0` | Off (not active) |
| `1` | On (active) |

default `00`· gate: 606 Navigation system Business / 609 Professional navigation system / 6AE TeleServices· token `PIM_NAVI_TO_MEETING_LOCATION`· source: firmware-token

### `3003/11/00010000b` — PIM message speech-to-text dictation  ·  _med_

Enables speech-to-text dictation for composing PIM messages (SMS/email reply) using the vehicle's microphone and voice recognition engine.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 606 Navigation system Business / 609 Professional navigation system / 249 Multifunction for steering wheel / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `PIM_SPEECH_TO_TEXT`· source: firmware-token

### `3003/11/00100000b` — PIM message sending (compose and send)  ·  _med_

Enables the ability to compose and send messages (SMS, email) from the PIM application in the head unit, not just read incoming messages.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `PIM_MESSAGE_SENDING`· source: firmware-token

### `3003/11/01000000b` — PIM reminder pop-ups  ·  _med_

Enables pop-up notification overlays on the iDrive screen when a PIM calendar reminder fires, alerting the driver to upcoming appointments.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `PIM_REMINDER_POPUPS`· source: firmware-token

### `3003/11/10000000b` — PIM create new entry  ·  _med_

Enables the 'Create new' function in the PIM application, allowing the driver to create new calendar events, notes, or contact entries directly from the head unit.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `PIM_CREATE_NEW`· source: firmware-token

### `3003/12/00000001b` — PIM new element: voice/email  ·  _med_

Enables creation of a new PIM element of the voice-email type (a voice message recorded and sent as an email attachment). When disabled, only text-based elements can be created.

| value | meaning |
|---|---|
| `0` | Off (not active) |

default `00`· gate: 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / 6NW Telephony with wireless charging· token `PIM_NEW_ELEMENT_VOICE_EMAIL`· source: firmware-token

### `3003/12/00000010b` — PIM multi-device CE support  ·  _med_

Enables PIM data synchronisation with multiple simultaneous consumer-electronics (CE) devices (e.g. two paired phones each contributing contacts and calendar data).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `PIM_MULTIPLE_CE_DEVICES`· source: firmware-token

### `3003/12/00000100b` — PIM notes USB export  ·  _med_

Enables export of PIM notes and memos to a USB storage device, allowing the user to save created notes externally.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `PIM_NOTES_USB_EXPORT`· source: firmware-token

### `3003/12/00001000b` — PIM HTML email browser  ·  _med_

Enables HTML rendering in the PIM email viewer, displaying rich-text/formatted emails rather than plain-text only.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `PIM_HTML_EMAIL_BROWSER`· source: firmware-token

### `3003/12/00010000b` — Contacts icon display  ·  _med_

Enables display of a graphical icon/avatar for contacts in the phonebook list when no photo is available, instead of a generic placeholder.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `CONTACTS_ICON`· source: firmware-token

### `3003/12/11100000b` — Reserved bits (3003 byte 12, bits 7-5)  ·  _low_

Purpose not determined from available sources. Unnamed/reserved coding bits in the phone/telematics page; no descriptor record and no firmware consumer identified.

source: inferred

### `3003/13/11111111b` — Reserved byte (3003 byte 13)  ·  _low_

Purpose not determined from available sources. Unnamed reserved byte in the phone/telematics/online coding page; no descriptor record and no firmware consumer identified.

source: inferred

### `3003/14/00000001b` — Wideband speech (HD Voice)  ·  _med_

Enables HD Voice / wideband speech audio for Bluetooth hands-free calls, providing significantly improved call audio quality over narrowband when both phone and network support it.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: NOT DHDT Conversion deactivation of the HD telephone· token `WIDEBAND_SPEECH`· source: firmware-token

### `3003/14/00000010b` — RDU remote control  ·  _med_

Enables RDU (Remote Diagnostic Unit / remote control module) control features reachable via BMW ConnectedDrive services, such as remote locking, climate preconditioning triggers, etc.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `RDU_CONTROL`· source: firmware-token

### `3003/14/00000100b` — SVR (stolen vehicle recovery)  ·  _high_

Enables SVR (Stolen Vehicle Recovery) telematics service, which allows BMW Assist to track and report vehicle location in the event of theft.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `SVR`· source: firmware-token

### `3003/14/00001000b` — Remote heating control (BMW Remote)  ·  _high_

Enables remote pre-conditioning heating control via the BMW Remote / ConnectedDrive app, allowing the driver to start or schedule cabin heating from a smartphone.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `HEATING_CONTROL`· source: firmware-token

### `3003/14/00010000b` — Remote ventilation control (BMW Remote)  ·  _high_

Enables remote cabin ventilation/cooling control via the BMW Remote / ConnectedDrive app, allowing the driver to start ventilation from a smartphone.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `VENTILATION_CONTROL`· source: firmware-token

### `3003/14/00100000b` — Remote light control (BMW Remote)  ·  _high_

Enables remote exterior light flashing control via BMW Remote / ConnectedDrive app, allowing the driver to flash headlights to locate the vehicle.

| value | meaning |
|---|---|
| `1` | Active |

default `00`· gate: always (no FA gate)· token `LIGHT_CONTROL`· source: firmware-token

### `3003/14/01000000b` — Remote horn control (BMW Remote)  ·  _high_

Enables remote horn honking via BMW Remote / ConnectedDrive app, allowing the driver to sound the horn briefly to locate the vehicle.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `HORN_CONTROL`· source: firmware-token

### `3003/14/10000000b` — BMW Assist vehicle finder show  ·  _high_

Controls whether the Vehicle Finder feature (using BMW Assist / ConnectedDrive to display the parked car location on a smartphone map) is displayed in the head unit menu.

| value | meaning |
|---|---|
| `0` | Hidden (not active) |
| `1` | Shown (active) |

default `00`· token `ASSIST_VEHICLEFINDER_SHOW`· source: firmware-token

### `3003/15/00000001b` — BMW Assist SVR show in menu  ·  _high_

Controls whether the Stolen Vehicle Recovery (SVR) entry is shown in the BMW Assist / ConnectedDrive services menu. Active on vehicles with 6AE TeleServices.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / 6AE TeleServices· token `ASSIST_SVR_SHOW`· source: firmware-token

### `3003/15/00000010b` — BMW Assist B-Call contact numbers  ·  _med_

Enables display of BMW Assist B-Call (Breakdown Call) service phone numbers in the contacts/Assist menu. Excluded for Korean and Japanese market variants.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: NOT 802 Korean version / 807 Japanese version· token `CONTACT_NUMBERS_BCALL`· source: firmware-token

### `3003/15/00000100b` — Dealer contact numbers  ·  _med_

Enables display of the dealer/BMW service centre phone number in the BMW Assist or contacts menu. Excluded for Korean market.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: NOT 802 Korean version· token `CONTACT_NUMBERS_DEALER`· source: firmware-token

### `3003/15/00001000b` — BMW Assist hotline contact numbers  ·  _med_

Enables display of BMW Assist customer hotline phone numbers in the BMW Assist menu. Excluded for Japanese market.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: NOT 807 Japanese version· token `CONTACT_NUMBERS_HOTLINE`· source: firmware-token

### `3003/15/00110000b` — BMW Online and Internet portals  ·  _med_

Chooses which built-in online portals the head unit offers: the BMW Online service portal and the BMW Internet web browser.

| value | meaning |
|---|---|
| `0` | None |
| `1` | BMW Online |
| `2` | BMW Internet |
| `3` | BMW Online and BMW Internet |

Bits (set = on): bit 0 BMW Online; bit 1 BMW Internet

default `00`· gate: always (no FA gate)· token `ONLINE_BROWSER`· source: firmware-token

### `3003/15/01000000b` — Startup (telematics/online startup sequence)  ·  _med_

Enables a telematics or online-services startup sequence at vehicle power-on, triggering initial connection and service registration for ConnectedDrive.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `STARTUP`· source: firmware-token

### `3003/15/10000000b` — Online services enable  ·  _high_

Master enable for BMW ConnectedDrive Online Services (real-time traffic, weather, BMW Online portal, remote services). Requires 6AE TeleServices or 6AF Emergency Call option; disabled if TELD (telematics deactivation) is set.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: NOT TELD Deactivation of Telematics / 6AE TeleServices / 6AF Statutory emergency request· token `ONLINE_SERVICES`· source: firmware-token

### `3003/16/00000001b` — Online services GLS (geographic location services)  ·  _med_

Enables GLS (Geographic / GPS Location Services) as part of BMW Online Services, used for real-time traffic routing, local search, and location-aware ConnectedDrive features.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 6AE TeleServices· token `ONLINE_SERVICES_GLS`· source: firmware-token

### `3003/16/00000010b` — Telematics / ConnectedDrive online services enable  ·  _med_

Enables the telematics/online services subsystem (TELEX). Gated by NOT TELD (telematics deactivation) and NOT 6AE (TeleServices); set when telematics hardware is fitted and active.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: NOT TELD Deactivation of Telematics / 6AE TeleServices· token `TELEX`· source: firmware-token

### `3003/16/00111100b` — NGTP key table index  ·  _high_

Selects which NGTP (Next Generation Telematics Protocol) key table is used for secure BMW ConnectedDrive communication. Supports up to 14 key-table variants (TABLE_0–TABLE_13).

| value | meaning |
|---|---|
| `0` | TABLE_0 |
| `1` | TABLE_1 |
| `2` | TABLE_2 |
| `3` | TABLE_3 |
| `4` | TABLE_4 |
| `5` | TABLE_5 |
| `6` | TABLE_6 |
| `7` | TABLE_7 |
| `8` | TABLE_8 |
| `9` | TABLE_9 |
| `10` | TABLE_10 |
| `11` | TABLE_11 |
| `12` | TABLE_12 |
| `13` | TABLE_13 |

default `00`· gate: FA-gated (depends on vehicle options)· token `NGTP_KEY_TABLE`· source: firmware-token

### `3003/16/01000000b` — TDA high-level data configuration enable  ·  _med_

Enables the TDA (Telematics Data Application) high-level car data (HLC_DATA) path, which allows the telematics ECU to exchange vehicle data at the application layer with BMW backend services.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· token `TDA_CFG_HLC_DATA`· source: firmware-token

### `3003/16/10000000b` — BMW Assist (emergency call) enable  ·  _med_

Enables the BMW Assist telematics service, including automatic and manual emergency call (eCall/SOS) functionality. Gated on NOT TELD, NOT 6AE, and NOT 6AF (statutory emergency call option).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: NOT TELD Deactivation of Telematics / 6AE TeleServices / 6AF Statutory emergency request· token `ASSIST`· source: firmware-token

### `3003/17/11111111b` — Telematics/online configuration table index  ·  _high_

Selects the active configuration table (CONFIG_TABLE_0 through CONFIG_TABLE_10) for the telematics/online subsystem, allowing market- or variant-specific parameter sets to be applied without changing individual fields.

| value | meaning |
|---|---|
| `0` | CONFIG_TABLE_0 |
| `1` | CONFIG_TABLE_1 |
| `2` | CONFIG_TABLE_2 |
| `3` | CONFIG_TABLE_3 |
| `4` | CONFIG_TABLE_4 |
| `5` | CONFIG_TABLE_5 |
| `6` | CONFIG_TABLE_6 |
| `7` | CONFIG_TABLE_7 |
| `8` | CONFIG_TABLE_8 |
| `9` | CONFIG_TABLE_9 |
| `10` | CONFIG_TABLE_10 |

default `00`· token `CONFIG_INDEX`· source: firmware-token

### `3003/18/00000001b` — GPS position source: navigation system  ·  _med_

When enabled, the telematics/online services obtain GPS position data from the fitted professional navigation system (609) rather than from a standalone GPS receiver.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 609 Professional navigation system· token `GPS_FROM_NAVI`· source: firmware-token

### `3003/18/00000010b` — TOL export USB overwrite enable  ·  _med_

Allows a USB-connected device to overwrite the TOL (Telematics Online) export/configuration data. Engineering/production flag.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TOL_CFG_EXP_USB_OVERWRITE`· source: firmware-token

### `3003/18/00001100b` — Online browser live-data mode  ·  _med_

Selects the live-data mode for the integrated online browser (BMW ConnectedDrive web portal). 2-bit field with no symbolic enum.

default `00`· gate: FA-gated (depends on vehicle options)· token `ONLINE_BROWSER_LIVE`· source: firmware-token

### `3003/18/00010000b` — Data communication CSIM enable  ·  _med_

Enables the CSIM (Card Services Interface Module) data communication path, used when a C-SIM (embedded cellular SIM) is the data bearer for telematics connectivity.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `DATACOMM_CSIM`· source: firmware-token

### `3003/18/00100000b` — Contacts: Asian initial-character speller  ·  _high_

Enables the Asian (Japanese/Chinese) initial-character speller layout for the phone contacts search screen. Active for Japanese (807), Chinese (8AA), and specific country-control codes (8LH, 8LT) markets.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 807 Japanese version / 8AA Chinese version / 8LH Country control 04142 / 8LT Country control 04825 · token `CONTACTS_INITIAL_SPELLER_ASIA`· source: firmware-token

### `3003/18/01000000b` — Contacts: Japan phonetic search enable  ·  _high_

Enables Japan-specific phonetic (kana) search ordering for the phone contacts list, where contacts are sorted and searched by pronunciation rather than character.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 807 Japanese version· token `CONTACTS_JAPAN_SEARCH`· source: firmware-token

### `3003/18/10000000b` — Navigation address validation enable  ·  _high_

Enables server-side address validation for navigation destination input (online POI/address check). Requires navigation system option (606 Business or 609 Professional).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 606 Navigation system Business / 609 Professional navigation system· token `ADDRESS_VALIDATION`· source: firmware-token

### `3003/19/00000001b` — Bluetooth audio streaming (BTAS) iAP enable  ·  _high_

Enables the iAP (iPod Accessory Protocol) command channel used by the Bluetooth audio streaming subsystem (BTAS) for Apple device control over Bluetooth. When disabled (NICHT_AKTIV), iAP commands are not issued.

| value | meaning |
|---|---|
| `0` | Off (NICHT_AKTIV) |

default `00`· gate: always (no FA gate)· token `ENT_BTAS_IAP`· source: firmware-token

### `3003/19/00000010b` — TDA BDA remote help enable  ·  _med_

Enables the BMW Digital Assistant (BDA) remote help feature through the Telematics Data Application (TDA) layer, allowing remote BMW assistance operations via telematics.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: always (no FA gate)· token `TDA_CFG_BDA_REMOTE_HELP`· source: firmware-token

### `3003/19/00000100b` — Bluetooth audio streaming (BTAS) metadata enable  ·  _high_

Enables the retrieval and display of track metadata (artist, title, album) from Bluetooth-connected devices via the BTAS subsystem. Requires a Bluetooth/USB phone option (6NH, 6NK, 6NL, 6NS, or 6NW).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 6NH Hands-free system with USB interface / 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / 6NW Telephony with wireless charging / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `ENT_BTAS_METADATA`· source: firmware-token

### `3003/19/00001000b` — Bluetooth audio streaming (BTAS) media browsing enable  ·  _high_

Enables AVRCP media browsing over Bluetooth, allowing the iDrive to browse playlists and tracks on the connected phone. Active when TV (601) or professional navi (609) are NOT fitted.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: NOT 601 TV Function / 609 Professional navigation system· token `ENT_BTAS_BROWSING`· source: firmware-token

### `3003/19/00010000b` — Phone contacts display enable  ·  _high_

Enables the phone contacts (phonebook) feature on the iDrive, allowing imported contacts from a paired Bluetooth device to be viewed and dialled. Requires a Bluetooth/USB telephony option.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 6NH Hands-free system with USB interface / 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / 6NW Telephony with wireless charging / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `CONTACTS_EIN_AUS`· source: firmware-token

### `3003/19/00100000b` — PIM photo/image sync enable  ·  _high_

Enables synchronisation of images/photos from the paired phone to the Personal Information Manager (PIM) on the head unit. Not available for Japanese (807), Australian (810), and certain Chinese/Bluetooth-only markets.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: NOT 807 Japanese version / 810 Australian version / 8LH Country control 04142 / 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / 6NW Telephony with wireless charging· token `PIM_BILDER_EIN_AUS`· source: firmware-token

### `3003/19/01000000b` — PIM calendar sync enable  ·  _high_

Enables synchronisation of calendar entries from a paired phone to the iDrive PIM calendar application. Requires professional navigation (609) and a Bluetooth/USB telephony option.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 609 Professional navigation system / 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / 6NW Telephony with wireless charging· token `CALENDAR_EIN_AUS`· source: firmware-token

### `3003/19/10000000b` — PIM tasks sync enable  ·  _high_

Enables synchronisation of task/to-do entries from a paired phone to the iDrive PIM tasks application. Requires professional navigation (609) and a Bluetooth/USB telephony option.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 609 Professional navigation system / 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / 6NW Telephony with wireless charging· token `TASK_EIN_AUS`· source: firmware-token

### `3003/20/00000001b` — PIM reminders sync enable  ·  _high_

Enables synchronisation of reminder/alarm entries from a paired phone to the iDrive PIM application. Requires professional navigation (609) and a Bluetooth/USB telephony option.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 609 Professional navigation system / 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / 6NW Telephony with wireless charging· token `REMINDER_EIN_AUS`· source: firmware-token

### `3003/20/00000010b` — OGG Vorbis audio codec enable  ·  _high_

Enables playback of OGG Vorbis compressed audio files from USB or other media sources. Always active (no FA gate); disabling removes OGG format support.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: always (no FA gate)· token `OGG_CODEC_ON_OFF`· source: firmware-token

### `3003/20/00000100b` — PIM text notes sync enable  ·  _high_

Enables synchronisation of text notes/memos from a paired phone to the iDrive PIM note application. Requires professional navigation (609) and a Bluetooth/USB telephony option.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 609 Professional navigation system / 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / 6NW Telephony with wireless charging· token `TEXT_NOTES_EIN_AUS`· source: firmware-token

### `3003/20/00001000b` — PIM audio notes enable  ·  _high_

Enables recording and playback of voice/audio memos in the iDrive PIM application. Requires a Bluetooth/USB telephony option (6NK, 6NL, 6NS, or 6NW).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / 6NW Telephony with wireless charging· token `AUDIO_NOTES_EIN_AUS`· source: firmware-token

### `3003/20/00010000b` — SMS messaging enable  ·  _high_

Enables the iDrive SMS (text message) reader/sender for paired Bluetooth phones. When not active (NICHT_AKTIV), the SMS menu is hidden. Requires a Bluetooth/USB telephony option.

| value | meaning |
|---|---|
| `0` | Off (NICHT_AKTIV) |
| `1` | On (AKTIV) |

default `00`· gate: 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / 6NW Telephony with wireless charging· token `SMS_EIN_AUS`· source: firmware-token

### `3003/20/00100000b` — Email access enable  ·  _high_

Enables access to email messages on the iDrive from a paired Bluetooth phone. Requires a Bluetooth/USB telephony option (6NK, 6NL, 6NS, or 6NW).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / 6NW Telephony with wireless charging· token `EMAIL_EIN_AUS`· source: firmware-token

### `3003/20/01000000b` — Wi-Fi diagnostic mode  ·  _low_

Turns on a Wi-Fi diagnostic mode for workshop and development use. Not a CarPlay setting.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 601 TV Function / 609 Professional navigation system / 6NS Comfort telephony with expanded smartphone connection / 6NW Telephony with wireless charging / 6CP Smartphone Integration· token `WLAN_DIAGNOSE`· source: firmware-token

### `3003/20/10000000b` — WLAN status display enable  ·  _med_

Enables display of the Wi-Fi/WLAN connection status indicator in the iDrive.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `WLAN_STATUS`· source: firmware-token

### `3003/21/00000001b` — WLAN signal strength model  ·  _high_

Selects the signal-strength calibration model for the Wi-Fi antenna: OUTDOOR (open-air antenna placement) or INCAR (antenna mounted inside the vehicle body).

| value | meaning |
|---|---|
| `0` | Outdoor antenna model |
| `1` | In-car antenna model |

default `00`· gate: always (no FA gate)· token `WLAN_SIGNAL_STRENGTH`· source: firmware-token

### `3003/21/00000010b` — WLAN Wi-Fi Direct enable  ·  _high_

Enables Wi-Fi Direct (peer-to-peer Wi-Fi) mode on the head unit's WLAN module, allowing direct connections to devices without a router.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `WLAN_WIFI_DIRECT`· source: firmware-token

### `3003/21/00000100b` — WLAN client mode enable  ·  _high_

Enables the WLAN module to operate in client (station) mode, connecting to an external Wi-Fi access point.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `WLAN_CLIENT`· source: firmware-token

### `3003/21/00001000b` — WLAN access point mode enable  ·  _high_

Enables the WLAN module to operate as a Wi-Fi access point (hotspot mode), broadcasting its own SSID.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `WLAN_AP`· source: firmware-token

### `3003/21/11110000b` — WLAN channel selection  ·  _high_

Selects the default Wi-Fi channel (1–14) for the WLAN access point or direct-connect mode. Channel range varies by regulatory domain (WLAN_DOMAIN). Default is channel 1.

| value | meaning |
|---|---|
| `1` | Channel 1 |
| `2` | Channel 2 |
| `3` | Channel 3 |
| `4` | Channel 4 |
| `5` | Channel 5 |
| `6` | Channel 6 |
| `7` | Channel 7 |
| `8` | Channel 8 |
| `9` | Channel 9 |
| `10` | Channel 10 |
| `11` | Channel 11 |
| `12` | Channel 12 |
| `13` | Channel 13 |
| `14` | Channel 14 |

default `01`· gate: FA-gated (depends on vehicle options)· token `WLAN_CHANNEL`· source: firmware-token

### `3003/22/00001111b` — WLAN regulatory domain  ·  _high_

Selects the Wi-Fi regulatory domain/region, which determines permitted channels and transmit power limits for the WLAN module.

| value | meaning |
|---|---|
| `0` | STRICT (restricted/minimal channel set) |
| `1` | ETSI (Europe, most channels) |
| `2` | FCC 11-channel (USA/Canada) |
| `3` | FCC 13-channel (Americas extended) |
| `4` | MKK (Japan, all 14 channels) |

default `00`· gate: FA-gated (depends on vehicle options)· token `WLAN_DOMAIN`· source: firmware-token

### `3003/22/00010000b` — iPod 2-wire (USB) audio interface enable  ·  _med_

Enables the older 2-wire USB audio data path for iPod/iPhone devices instead of the digital audio interface. legacy iPod connector feature.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `API_IPOD_2WIRE_ON_OFF`· source: firmware-token

### `3003/22/00100000b` — USB Mass Storage Device (MSD) media enable  ·  _high_

Enables USB Mass Storage Device class support on the media interface port, allowing USB drives and media players (not iPod protocol) to be read as a media source.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 6NH Hands-free system with USB interface / 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `API_MSD_EIN_AUS`· source: firmware-token

### `3003/22/01000000b` — Apple authentication chip enable  ·  _high_

Enables hardware-level Apple MFi authentication chip interaction on the USB/accessory port, required for iAP2 communication with iPhone/iPod devices. Always active (no FA gate).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: always (no FA gate)· token `API_APPLE_AUTH_CHIP_ON_OFF`· source: firmware-token

### `3003/22/10000000b` — USB read/write (bidirectional USB) enable  ·  _high_

Enables bidirectional USB data access (both read and write) on the media port. When disabled (NICHT_AKTIV), only read access is permitted.

| value | meaning |
|---|---|
| `0` | Off (NICHT_AKTIV — read-only) |

default `00`· gate: FA-gated (depends on vehicle options)· token `API_USB_READ_WRITE`· source: firmware-token

### `3003/23/00000011b` — iPod/iPhone logo variant for car type  ·  _high_

Selects which iPod/iPhone-compatible logo artwork variant is displayed in the iDrive media source list, based on the vehicle model family. 0=no logo (NONE).

| value | meaning |
|---|---|
| `0` | None (NONE) |

default `00`· gate: 6NH Hands-free system with USB interface / 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `API_CAR_TYPE_IPOD_LOGO`· source: firmware-token

### `3003/23/00000100b` — MP4 video playback via USB enable  ·  _high_

Enables playback of MP4 video files from a USB-connected device on the iDrive screen. Requires a USB/BT telephony option.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 6NH Hands-free system with USB interface / 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `API_MP4_ON_OFF`· source: firmware-token

### `3003/23/00001000b` — WLAN hotspot via telematics ECU enable  ·  _high_

Enables the Wi-Fi hotspot function routed through the telematics ECU (TCB), allowing the car to share its cellular data connection as a Wi-Fi access point. Requires option 6WD (Personal Hotspot).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 6WD Personal hotspot· token `WLAN_HOTSPOT_TELEMATIC_ECU`· source: firmware-token

### `3003/23/00010000b` — CDMM USB tag manager enable  ·  _med_

Enables the USB tag-manager component of the Content and Data Media Manager (CDMM), used to read metadata tags from USB media files.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `CDMM_USB_TAG_MGR`· source: firmware-token

### `3003/23/00100000b` — USB cover art display enable  ·  _high_

Enables display of album artwork embedded in USB media files (ID3/MP4 cover art). Disabled for certain Chinese market vehicles (8LH country control).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: NOT 8LH Country control 04142· token `CDMM_USB_COVER_ART`· source: firmware-token

### `3003/23/01000000b` — iPod cover art display enable  ·  _high_

Enables display of album artwork from iPod/iPhone devices connected via USB iAP. Disabled for certain Chinese market vehicles (8LH country control).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: NOT 8LH Country control 04142· token `CDMM_USB_COVER_ART_IPOD`· source: firmware-token

### `3003/23/10000000b` — Reserved bit (byte 23, bit 7)  ·  _low_

Purpose not determined from available sources. This bit is not present in the firmware descriptor table, has no named consumer in the OMAP image, and is the unallocated remainder of byte 23 alongside API_CAR_TYPE_IPOD_LOGO, API_MP4_ON_OFF, WLAN_HOTSPOT_TELEMATIC_ECU, CDMM_USB_TAG_MGR, CDMM_USB_COVER_ART, and CDMM_USB_COVER_ART_IPOD.

_Resolved from resolved_unnamed.json: RESERVED_3003_23_bit7. Spare/reserved bit._

source: firmware-trace

### `3003/24/00000011b` — Reserved bits (byte 24, bits 1-0)  ·  _low_

Purpose not determined from available sources. Not present in the firmware descriptor table; no consumer reads this mask in the OMAP image. Spare/reserved bits cohabiting the USB iPod audio byte alongside USB1_IPOD_AUDIO and USB2_IPOD_AUDIO.

_Resolved from resolved_unnamed.json: RESERVED_3003_24_bits1,0._

source: firmware-trace

### `3003/24/00001100b` — USB port 1 iPod audio path  ·  _high_

Selects the audio data path for iPod/iPhone devices on USB port 1: Digital (iAP digital audio), Analog (line-level output), or Auto (firmware auto-detects the preferred path).

| value | meaning |
|---|---|
| `0` | Digital |
| `1` | Analog |
| `2` | Auto |

default `00`· gate: FA-gated (depends on vehicle options)· token `USB1_IPOD_AUDIO`· source: firmware-token

### `3003/24/00110000b` — USB port 2 iPod audio path  ·  _med_

Selects the audio data path for iPod/iPhone devices on USB port 2 (when fitted). 2-bit field; syset carries only raw codes [1,2] with no symbolic names. By analogy with USB1_IPOD_AUDIO the values likely correspond to Analog and Auto, but no symbolic enum is confirmed.

default `00`· gate: FA-gated (depends on vehicle options)· token `USB2_IPOD_AUDIO`· source: firmware-token

### `3003/24/11000000b` — Reserved bits (byte 24, bits 7-6)  ·  _low_

Purpose not determined from available sources. Not present in the firmware descriptor table; no consumer reads this mask in the OMAP image. Spare/reserved bits in the USB iPod audio configuration byte.

_Resolved from resolved_unnamed.json: RESERVED_3003_24_bits7,6._

source: firmware-trace

### `3003/25/11111111b` — Online services connection profile  ·  _high_

Picks the built-in connection profile the head unit's online services start from: the BMW provisioning server, mobile-data access point and proxy for a region. The test-server profiles point to BMW's development backend instead of the live service. A value without a profile leaves the head unit with no default profile.

| value | meaning |
|---|---|
| `0` | None |
| `1` | Worldwide, test servers |
| `2` | Worldwide |
| `3` | USA, test servers |
| `4` | USA |
| `5` | China, test servers |
| `6` | China |
| `7` | Japan, test servers |
| `8` | China SIM, global test servers |
| `9` | China SIM, global servers |
| `10` | None |
| `11` | None |
| `12` | None |
| `13` | None |
| `14` | None |
| `15` | None |

default `00`· token `DPAS_INDEX`· source: firmware-trace

### `3003/26/11111111b` — Reserved bytes (bytes 26-27)  ·  _low_

Purpose not determined from available sources. Two-byte unnamed/reserved block in the TELEFON_TELEMATIK_ONLINE coding page. No descriptor record or firmware consumer found for these bytes.

_Resolved from resolved_unnamed.json: RESERVED_3003_BYTES_26_27. Follows DPAS_INDEX; purpose undetermined._

source: firmware-trace

### `3003/28/11111111b` — Navigation info service instance  ·  _med_

Identifies which instance of the navigation information service the head unit uses.

| value | meaning |
|---|---|
| `1` | Value 1 |
| `2` | Value 2 |
| `3` | Value 3 |

_Not a user setting: Service instance number of the navigation information service; a bus parameter (the firmware note shows it only selects which service properties are subscribed), with no driver-visible setting._

default `03`· gate: 606 Navigation system Business / 609 Professional navigation system· token `NAVI_INFO_INSTANCE_ID`· source: firmware-trace

### `3003/29/00000111b` — Reserved bits (byte 29, bits 2-0)  ·  _low_

Purpose not determined from available sources. Not present in the firmware descriptor table; no consumer reads this mask in the OMAP image. Spare/reserved bits in the software update configuration byte.

_Resolved from resolved_unnamed.json: RESERVED_3003_29_bits2,1,0. Byte 29 is the SWUP config byte; these 3 bits are the unallocated low nibble._

source: firmware-trace

### `3003/29/00001000b` — Software update: shutdown timeout enable  ·  _high_

When enabled, a watchdog shutdown timer is active during software update (SWUP) operations to prevent the vehicle being stranded with a partially updated system if the process stalls.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

_Token SwupEnableShutdownTimeout (firmware log) / SWUP_ENABLE_SHUTDOWN_TIMEOUT (syset descriptor). Firmware-traced: CUpdateAgentSysSettings reader FUN_001fe958, accessor FUN_00333e2c._

default `00`· gate: FA-gated (depends on vehicle options)· token `SwupEnableShutdownTimeout`· source: firmware-trace

### `3003/29/00010000b` — Software update agent role  ·  _high_

Determines the SWUP agent's role in multi-ECU update orchestration: CLIENT (receives update instructions from a master) or MASTER (orchestrates updates across ECUs).

| value | meaning |
|---|---|
| `0` | Client (receives updates from master) |
| `1` | Master (orchestrates ECU updates) |

default `00`· gate: FA-gated (depends on vehicle options)· token `SWUP_AGENT_TYPE`· source: firmware-token

### `3003/29/00100000b` — Software update: separate/sequential updates enable  ·  _med_

When enabled, software updates are applied to each SWE (Software Element) separately in sequence rather than in a combined package, allowing more granular retry/rollback behaviour.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SWUP_SEPARATE_UPDATES`· source: firmware-token

### `3003/29/01000000b` — Software update: user popup screens enable  ·  _high_

When enabled, the iDrive displays progress and confirmation popup screens to the driver during a software update. may suppress HMI feedback during OTA updates.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SWUP_ENABLE_POPUP_SCREENS`· source: firmware-token

### `3003/29/10000000b` — Software update: vehicle speed lock  ·  _high_

When enabled, software update installation is prevented while the vehicle is moving above a threshold speed, reducing driver distraction risk during update. Always active (no FA gate).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

_Token InstallSpeedLock (firmware log) / SWUP_INSTALL_SPEED_LOCK (syset descriptor). Firmware-traced: reader FUN_001fec10, accessor FUN_00333b98, log: '[kisu] CUpdateAgentSysSettings - InstallSpeedLock = %d'._

default `00`· gate: always (no FA gate)· token `InstallSpeedLock`· source: firmware-trace

### `3003/30/11111111b` — Software update: cyclic reset threshold  ·  _high_

Sets the maximum number of cyclic reset attempts permitted before the update agent aborts an update cycle. Values: 0 (disabled/no limit), 5 (5 retries), or 255 (maximum).

| value | meaning |
|---|---|
| `0` | Disabled (WERT_0) |
| `5` | 5 resets (WERT_5) |
| `255` | 255 resets (WERT_255) |

default `00`· gate: FA-gated (depends on vehicle options)· token `SWUP_CYCLIC_RESET_THRESHOLD`· source: firmware-token

### `3003/31/00000001b` — Software updates master enable  ·  _high_

Master enable flag for all software update (SWUP/KISU) functionality. When disabled, no over-the-air or USB software updates can be initiated regardless of other SWUP settings.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

_Token EnableSwUpdates (firmware log) / SWUP_ENABLE_SW_UPDATES (syset descriptor). Firmware-traced: reader FUN_001feb9c, accessor FUN_00333d24, log: '[kisu] CUpdateAgentSysSettings - EnableSwUpdates = %d'._

default `00`· gate: always (no FA gate)· token `EnableSwUpdates`· source: firmware-trace

### `3003/31/00000010b` — Engineering software updates enable  ·  _high_

Allows installation of engineering/development-signed software packages, beyond normal production updates. intended for BMW engineering vehicles.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

_Token EnableEngUpdates (firmware log) / SWUP_ENABLE_ENG_UPDATES (syset descriptor). Firmware-traced: reader FUN_001feb28, accessor FUN_00333eb0, log: '[kisu] CUpdateAgentSysSettings - EnableEngUpdates = %d'._

default `00`· gate: FA-gated (depends on vehicle options)· token `EnableEngUpdates`· source: firmware-trace

### `3003/31/00000100b` — Software update: require user confirmation  ·  _high_

When enabled, the driver must explicitly confirm before a software update is installed. When disabled, updates install automatically without user interaction.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

_Token AskConfirmation (firmware log) / SWUP_ASK_CONF_ENABLED (syset descriptor). Firmware-traced: reader FUN_001feab4, accessor FUN_00333ca0, log: '[kisu] CUpdateAgentSysSettings - AskConfirmation = %d'._

default `00`· gate: always (no FA gate)· token `AskConfirmation`· source: firmware-trace

### `3003/31/00001000b` — Software update source: USB  ·  _high_

Enables USB mass storage as an allowed software update source (KISU/SWUP via USB). Requires navigation, telephony, or telematics SA option.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

_Token SwupSrcUSB (firmware log) / SWUP_SOURCE_USBMSCDD (syset descriptor). Firmware-traced: reader FUN_001fea40, accessor FUN_00333c1c, log: '[kisu] CUpdateAgentSysSettings - SwupSrcUSB = %d'._

default `00`· gate: 606 Navigation system Business / 609 Professional navigation system / 6NH Hands-free system with USB interface / 6NR Apps / 6NS Comfort telephony with expanded smartphone connection / 6AE TeleServices / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `SwupSrcUSB`· source: firmware-trace

### `3003/31/00010000b` — Software update source: online/OTA  ·  _high_

Enables online/over-the-air update delivery as an allowed software update source. Requires 6AE (TeleServices).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

_Syset token = SWUP_SOURCE_ONLINE; firmware log accessor token = SwupSrcOTA. The syset descriptor name (SWUP_SOURCE_ONLINE) is broader than 'OTA' — it covers any online delivery channel, not exclusively cellular OTA. Description updated to 'online/OTA' to accurately reflect both. Firmware-traced: reader FUN_001fe9cc, accessor FUN_00333da8, log: '[kisu] CUpdateAgentSysSettings - SwupSrcOTA = %d'._

default `00`· gate: 6AE TeleServices· token `SwupSrcOTA`· source: firmware-trace

### `3003/31/00100000b` — PIM new email notification enable  ·  _high_

Enables display of an iDrive notification when a new email is received from the paired phone via the PIM (Personal Information Manager) sync.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / 6AE TeleServices / 6NW Telephony with wireless charging· token `PIM_NEW_ELEMENT_EMAIL`· source: firmware-token

### `3003/31/01000000b` — PIM new SMS notification enable  ·  _high_

Enables display of an iDrive notification when a new SMS text message is received from the paired phone via the PIM sync.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / 6AE TeleServices / 6NW Telephony with wireless charging· token `PIM_NEW_ELEMENT_SMS`· source: firmware-token

### `3003/31/10000000b` — PIM new text note notification enable  ·  _high_

Enables display of an iDrive notification when a new text note/memo is synced from the paired phone via the PIM.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `PIM_NEW_ELEMENT_TEXT_NOTE`· source: firmware-token

### `3003/32/00000001b` — PIM new audio note notification enable  ·  _high_

Enables display of an iDrive notification when a new voice/audio memo is synced from the paired phone via the PIM.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 6NK Connection for Bluetooth and USB devices / 6NL Connecting Bluetooth and USB devices including BMW assist / 6NS Comfort telephony with expanded smartphone connection / 6NW Telephony with wireless charging· token `PIM_NEW_ELEMENT_AUDIO_NOTE`· source: firmware-token

### `3003/32/00000110b` — USB ports for video files  ·  _med_

Chooses the USB ports on which video files from a USB drive or player can play. With no port checked, USB video is blocked. The factory sets it from the TV function (S601), Navigation Professional (S609), the smartphone options (S6NF, S6NR or S6NS) and the market (S8LH).

| value | meaning |
|---|---|
| `0` | None |
| `1` | First USB port |
| `2` | Second USB port |
| `3` | Both USB ports |

Bits (set = on): bit 0 First USB port; bit 1 Second USB port

default `00`· gate: 601 TV Function / 609 Professional navigation system / 8LH Country control 04142 / 6NF Music interface for smartphones / 6NR Apps / 6NS Comfort telephony with expanded smartphone connection· token `API_USB_VIDEO`· source: firmware-token

### `3003/32/00011000b` — iPod video playback port assignment  ·  _high_

Selects which USB port(s) support video streaming from iPod/iPhone devices (iAP video). Mirrors USB video port selection but for iPod-protocol devices.

| value | meaning |
|---|---|
| `1` | First USB port only |
| `2` | Second USB port only |
| `3` | Both USB ports |

default `00`· gate: FA-gated (depends on vehicle options)· token `API_IPOD_VIDEO`· source: firmware-token

### `3003/32/11100000b` — Reserved bits (byte 32, bits 7-5)  ·  _low_

Purpose not determined from available sources. Not present in the firmware descriptor table; no consumer reads this mask in the OMAP image. Spare/reserved upper bits of the USB video configuration byte.

_Resolved from resolved_unnamed.json: RESERVED_3003_32_bits7,6,5._

source: firmware-trace

### `3003/33/11111111b` — eCall instance ID  ·  _high_

Identifies the SOME/IP service instance used by the eCall (emergency call) system in the telematics module. Required for statutory eCall (6AF) fitments. Default 0 (WERT_0); value 0xEC (236) maps to an alternative instance.

| value | meaning |
|---|---|
| `0` | Instance 0 (WERT_0) |
| `236` | Instance 1 (WERT_1) |

default `00`· gate: FA-gated (depends on vehicle options)· token `ECALL_INSTANCE_ID`· source: firmware-token

### `3003/34/00001111b` — NGTP security mode: authentication algorithm (session handshake)  ·  _med_

Selects the cryptographic authentication algorithm used for NGTP (telematics protocol) session handshake (ASH = Authentication Security Handshake). 4-bit field; syset carries no symbolic enum names for this coord.

default `00`· gate: always (no FA gate)· token `M_SECURITY_MODE_ASH`· source: firmware-token

### `3003/34/11110000b` — NGTP security mode: encryption algorithm (session handshake)  ·  _high_

Selects the encryption algorithm for NGTP session data (AEH = Authentication Encryption Handshake). DES_CBC is the only named value, indicating DES in CBC mode for this telematics protocol phase.

| value | meaning |
|---|---|
| `2` | DES-CBC encryption |

default `00`· gate: always (no FA gate)· token `M_SECURITY_MODE_AEH`· source: firmware-token

### `3003/35/00001111b` — NGTP security mode: authentication algorithm (payload)  ·  _high_

Selects the message authentication algorithm applied to NGTP payload data (ASP = Authentication Security Payload): DES-CBC-MAC, HMAC-SHA-1, or HMAC-SHA-256.

| value | meaning |
|---|---|
| `1` | DES-CBC-MAC |
| `3` | HMAC-SHA-1 |
| `5` | HMAC-SHA-256 |

default `00`· gate: FA-gated (depends on vehicle options)· token `M_SECURITY_MODE_ASP`· source: firmware-token

### `3003/35/11110000b` — NGTP security mode: encryption algorithm (payload)  ·  _high_

Selects the encryption algorithm applied to NGTP payload data (AEP = Authentication Encryption Payload): DES-CBC or AES-128.

| value | meaning |
|---|---|
| `2` | DES-CBC |
| `4` | AES-128 |

default `00`· gate: always (no FA gate)· token `M_SECURITY_MODE_AEP`· source: firmware-token

### `3003/36/11111111b` — USB video sync delay  ·  _high_

Picture-to-sound delay for video from a USB source. The head unit doesn't use it.

| value | meaning |
|---|---|
| `0` | 0 ms |

_Not a user setting: Single-value timing field with no reader: no syset client (ConnStarter, NBTMediaMainApp, MediaPreStarter) reads it and the HMI never asks for it; the media engine's video delay is fixed in its own configuration._

default `00`· token `API_VIDEO_DELAY_USB`· source: firmware-trace

### `3003/37/11111111b` — iPod video sync delay  ·  _high_

Picture-to-sound delay for video from an iPod or iPhone. The head unit doesn't use it.

| value | meaning |
|---|---|
| `128` | 800 ms |

_Not a user setting: Single-value timing field with no reader: no syset client (ConnStarter, NBTMediaMainApp, MediaPreStarter) reads it and the HMI never asks for it; the media engine's video delay is fixed in its own configuration._

default `80`· token `API_VIDEO_DELAY_IPOD`· source: firmware-trace

### `3003/38/00000111b` — Bluetooth device friendly name (brand)  ·  _high_

Sets the brand name prefix used for the Bluetooth device friendly name (the name shown to pairing phones). Selects between BMW group brand identities.

| value | meaning |
|---|---|
| `0` | BMW |
| `1` | MINI |
| `2` | BBA (BMW Brilliance Automotive — China) |
| `3` | Rolls-Royce |
| `4` | BMW i |
| `5` | BMW M |
| `6` | Toyota |

default `00`· gate: FA-gated (depends on vehicle options)· token `BT_USER_FRIENDLY_NAME`· source: firmware-token

### `3003/38/11111000b` — Reserved bits (byte 38, bits 7-3)  ·  _low_

Purpose not determined from available sources. Not present in the firmware descriptor table; no consumer reads this mask in the OMAP image. Upper 5 bits of the Bluetooth brand-name byte, unallocated.

_Resolved from resolved_unnamed.json: RESERVED_3003_38_bits7,6,5,4,3._

source: firmware-trace

### `3003/39/11111111b` — Reserved trailing bytes (bytes 39-148)  ·  _low_

Purpose not determined from available sources. A 110-byte unnamed block at the end of the TELEFON_TELEMATIK_ONLINE coding page. No descriptor record or firmware consumer found for these bytes.

_Resolved from resolved_unnamed.json: RESERVED_3003_BYTES_39_148. Likely padding/reserved space in the CAFD page layout._

source: firmware-trace

## Datagroup 0x3004 (74 parameters)

### `3004/0/00000001b` — Reset info screen  ·  _med_

Controls whether the yellow system-information screen (service/diagnostic info screen) is reset on next boot. Activated only when FA option SCRY (Yellow Screen activation) is present.

| value | meaning |
|---|---|
| `0` | Inactive (no reset) |
| `1` | Active (reset on boot) |

default `00`· gate: SCRY Activation of YELLOW SCREEN· token `RESET_INFO_SCREEN`· source: firmware-token

### `3004/0/00000010b` — iAP2 (Lightning/USB) entertainment support  ·  _med_

Enables iAP2 (Apple Lightning/USB accessory protocol v2) support for iPod/iPhone audio and control in the entertainment system. Suppressed when TV (601) or Professional Navigation (609) is present.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: NOT 601 TV Function / 609 Professional navigation system· token `ENT_IAP2_SUPPORT`· source: firmware-token

### `3004/0/00000100b` — CarPlay coding check  ·  _high_

The bit the head unit checks before it offers Apple CarPlay. CarPlay appears only when this is 1 and the CarPlay FSC (AppNo 0x0143) is accepted. It is the only coding bit the CarPlay check reads.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

_Traced in NBTCarHU: CSPDiagnosticSWTController::isAppCoded (FUN_002f58c4) case 0xB (CarPlay) reads one field, byte 0 mask 0x04 (FUN_0033403c / FUN_00333ff8). FUN_002fba18 maps app 0xB to AppNo 0x143, and FUN_002f6060 requires both the coding check and the FSC. Set 0 -> 1 in the reference unit's working CarPlay coding._

default `00`· gate: NOT 6AE TeleServices / 6CP Smartphone Integration· token `CARPLAY_SWT`· source: firmware-trace

### `3004/0/01111000b` — Check Control and CBS service version  ·  _high_

Picks which version of the instrument cluster's network service the central display uses to get Check Control messages and Condition Based Service (CBS) data. Match it to the car's instrument cluster; with the wrong version these messages and service data can be missing.

| value | meaning |
|---|---|
| `0` | First cluster interface |
| `1` | Second cluster interface |

default `00`· gate: FA-gated (depends on vehicle options)· token `CC_CBS_ETH_SERVICE_VERSION`· source: firmware-trace

### `3004/0/10000000b` — Touch Command CDS FKA luminance support  ·  _med_

Enables Touch Command (TC) Car Data Service (CDS) support for FKA (front-facing driver-assistance camera) luminance data.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_CDS_FKA_LUM_SUPPORT`· source: firmware-token

### `3004/1/00000001b` — Personal profile master  ·  _med_

Makes the head unit the master control unit for personal profiles, storing them and coordinating profile changes with the rest of the car. Leave it unchanged; other control units rely on it.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: always (no FA gate)· token `fPIA_PORTIERUNGSMASTER`· source: firmware-trace

### `3004/1/00000010b` — Profile reset to defaults  ·  _med_

Lets the driver reset a personal profile to its factory default settings from the profile menu, clearing the preferences saved in it.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: always (no FA gate)· token `fPIA_RUECKSETZEN_AUF_DEFAULT`· source: firmware-trace

### `3004/1/00011100b` — Portation (profile transfer) menu mode  ·  _high_

Selects which portation-related menu items appear in the system settings. Controls whether the full portation menu, a subset, or no menu at all is shown to the user.

| value | meaning |
|---|---|
| `0` | No portation menu |
| `1` | Full portation menu |
| `2` | All except profile transfer |
| `3` | All except transfer and delete |

default `00`· gate: FA-gated (depends on vehicle options)· token `PIA_MMI`· source: firmware-token

### `3004/1/00100000b` — Profile copying  ·  _med_

Lets the personal profile system copy profiles, so the settings saved in one profile can be reused in another without setting them up again.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: always (no FA gate)· token `fKOPIEREN_VON_PROFILEN`· source: firmware-trace

### `3004/1/01000000b` — Profile export and import  ·  _med_

Turns on profile export and import, which lets personal profile settings be saved to and loaded from external storage such as a USB stick. It's the main switch above the other profile transfer options.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: always (no FA gate)· token `fPORTIERUNG`· source: firmware-trace

### `3004/1/10000000b` — Allow temporary profile switch  ·  _high_

Permits a temporary (session-only) switch to a different user profile. The temporary profile reverts when the ignition cycle ends, without overwriting the stored profile.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

_Token fTEMPORAERER_PROFILWECHSEL (real name TEMPORAERER_PROFILWECHSEL); German: 'temporary profile switch'; nameless enum (code 1 only); trace 'Pom: fTEMPORAERER_PROFILWECHSEL'; accessor FUN_0033424c._

default `00`· gate: always (no FA gate)· token `fTEMPORAERER_PROFILWECHSEL`· source: firmware-trace

### `3004/2/00000001b` — Allow permanent profile switch  ·  _high_

Enables the ability to permanently switch the active user profile, persisting the selection across ignition cycles.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

_Token fPERMANENTER_PROFILWECHSEL (real name PERMANENTER_PROFILWECHSEL); nameless enum (code 1 only); accessor FUN_003343d8._

default `00`· gate: always (no FA gate)· token `fPERMANENTER_PROFILWECHSEL`· source: firmware-trace

### `3004/2/00000010b` — SmartSol feature  ·  _low_

Enables the SmartSol feature (BMW SmartSolution / smart personalisation solution).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `SMARTSOL`· source: firmware-token

### `3004/2/00000100b` — NFC operation mode  ·  _high_

Selects the NFC (Near Field Communication) reader operating mode. Rotation mode cycles through NFC polling; Passive mode keeps the reader in passive/listen state.

| value | meaning |
|---|---|
| `0` | Rotation (polling) |
| `1` | Passive |

default `00`· gate: FA-gated (depends on vehicle options)· token `NFC_OPERATION_MODE`· source: firmware-token

### `3004/2/00001000b` — iDrive rotary controller zoom direction  ·  _high_

Defines which rotary direction on the ZBE (iDrive controller) zooms in on the map or list. Left = rotate left to zoom in; Right = rotate right to zoom in.

| value | meaning |
|---|---|
| `0` | Left (rotate left = zoom in) |
| `1` | Right (rotate right = zoom in) |

default `00`· token `ZOOM_IN_DIRECTION_ZBE`· source: firmware-token

### `3004/2/00010000b` — Use gateway transport VIN  ·  _med_

Instructs the head unit to read the vehicle VIN from the gateway (GW) transport layer rather than from its own stored value.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `USE_GW_TR_VIN`· source: firmware-token

### `3004/2/00100000b` — Profile settings from mobile device  ·  _med_

Lets the head unit receive personal profile settings from a connected mobile device and apply them to a profile. When disabled, such transfers are ignored.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: NOT 6NR Apps / 6VB Infotainment control / 6AE TeleServices· token `fPIA_A4A`· source: firmware-trace

### `3004/2/01000000b` — Approved-device check for profiles  ·  _med_

Before accepting profile settings from a mobile device, checks it against the list of approved devices and asks the driver to confirm one that isn't on the list. When disabled, the check is skipped.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: always (no FA gate)· token `fPIA_A4A_WHITELIST_CHECK`· source: firmware-trace

### `3004/2/10000000b` — Car-sharing profile mode  ·  _med_

Turns on the personal profile system's car-sharing mode, which handles profiles for a changing group of drivers in shared cars.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `fPIA_CARSHARING`· source: firmware-trace

### `3004/3/00000001b` — Profile 2-second timer  ·  _low_

Timing setting for the personal profile system that turns on a 2-second timer used when handling profile changes. Best left unchanged.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

_Not a user setting: Timing parameter inside the personal profile system (NBTCarHU portation master 'Pom: fBEHANDLUNG_2s_TIMER'); no driver-visible effect established (STYLE: timing parameters hidden)._

default `00`· gate: FA-gated (depends on vehicle options)· token `fBEHANDLUNG_2s_TIMER`· source: firmware-trace

### `3004/3/00000010b` — Steering wheel side (left-hand drive / right-hand drive)  ·  _high_

Specifies whether the vehicle is left-hand drive (LHD, steering on left) or right-hand drive (RHD, steering on right). Used for layout and ergonomics decisions in the HMI.

| value | meaning |
|---|---|
| `0` | Left-hand drive (LHD) |
| `1` | Right-hand drive (RHD) |

default `00`· gate: vehicle type-key attribute group (FP category 7; 162 type tokens, e.g. 11CK,11CL,11DE,1A10)· token `TYP_LENKUNG`· source: firmware-token

### `3004/3/00000100b` — 100BASE-TX PHY on activation line  ·  _high_

Controls whether the 100BASE-TX Ethernet PHY/switch port is brought up when the head-unit activation (wake) line is asserted. Relevant for the FEM-to-NBT ENET link bring-up sequence.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

_Token 100BASETX_ON_ON_ACTIVATION_LINE; recovered from sysetshellevo descriptor table (file 0x05014c, area/type 2240=dg3004, byte=3, mask=0x04); default field value=1 (active)._

default `01`· gate: always (no FA gate)· source: firmware-trace

### `3004/3/00001000b` — ZBE hardware generation 3.5+ (CIC-era controller)  ·  _med_

Indicates that a ZBE (iDrive controller) from the 3.5-generation or later (CIC/NBT era) is fitted. Affects input-event handling and feature availability for the iDrive rotary/button cluster.

| value | meaning |
|---|---|
| `0` | Off (earlier ZBE) |
| `1` | On (ZBE 3.5+ fitted) |

default `00`· gate: FA-gated (depends on vehicle options)· token `ZBE_35UP`· source: firmware-token

### `3004/3/11110000b` — Reserved / undocumented (dg3004 byte 3 bits 7-4)  ·  _low_

Purpose not determined from available sources. Shares byte 3 with named fields BEHANDLUNG_2s_TIMER, TYP_LENKUNG, 100BASETX_ON_ON_ACTIVATION_LINE, and ZBE_35UP. No descriptor record found in the firmware descriptor table.

source: inferred

### `3004/4/11111111b` — Vehicle series code (Baureihe)  ·  _high_

Identifies the BMW vehicle series (Baureihe) to which this head unit is coded. Used by the portation master to select series-specific profile and behaviour defaults.

| value | meaning |
|---|---|
| `0` | Unknown |
| `1` | F01 |
| `2` | F02 |
| `3` | F03 |
| `4` | F04 |
| `6` | F06 |
| `7` | F07 |
| `10` | F10 |
| `11` | F11 |
| `12` | F12 |
| `13` | F13 |
| `15` | F15 |
| `16` | RR04 |
| `17` | F16 |
| `18` | F18 |
| `20` | F20 |
| `21` | F21 |
| `22` | F22 |
| `23` | F23 |
| `25` | F25 |
| `26` | F26 |
| `33` | G11 |
| `34` | G12 |
| `35` | G05 |
| `36` | G06 |
| `37` | G07 |
| `38` | G14 |
| `39` | G15 |
| `40` | G16 |
| `42` | G20 |
| `43` | G21 |
| `44` | G22 |
| `45` | G23 |
| `46` | G24 |
| `47` | G26 |
| `48` | G30 |
| `49` | G31 |
| `50` | G38 |
| `51` | G32 |
| `52` | RR21 |
| `53` | RR22 |
| `58` | G28 |
| `59` | G29 |
| `60` | J29 |
| `64` | F30 |
| `65` | F31 |
| `66` | F32 |
| `67` | F33 |
| `68` | F34 |
| `69` | F35 |
| `70` | F36 |
| `71` | F40 |
| `72` | F39 |

default `00`· gate: FA-gated (depends on vehicle options)· token `fBAUREIHE`· source: firmware-token

### `3004/5/11111111b` — Shutdown delay timer 1 (post-ignition-off delay)  ·  _high_

Sets the first post-ignition-off delay before the head unit begins its shutdown sequence. A value of 0 means immediate shutdown; 20 encodes a 20-second delay.

| value | meaning |
|---|---|
| `0` | 0 seconds (immediate) |
| `20` | 20 seconds |

default `00`· gate: always (no FA gate)· token `SHUTDOWN_DELAY_TIMER_1`· source: firmware-token

### `3004/6/11111111b` — Shutdown delay timer 2 (secondary post-ignition delay)  ·  _high_

Sets the second (secondary) post-ignition-off shutdown delay. A value of 0 means no secondary delay; 15 encodes a 15-second secondary delay before final power-off.

| value | meaning |
|---|---|
| `0` | 0 seconds (no delay) |
| `15` | 15 seconds |

default `00`· gate: always (no FA gate)· token `SHUTDOWN_DELAY_TIMER_2`· source: firmware-token

### `3004/7/00000111b` — Default date display format  ·  _high_

Sets the default date format displayed in the system settings and clock. The user can usually override this at runtime; this is the factory default.

| value | meaning |
|---|---|
| `0` | MM/DD/YYYY (US format) |
| `1` | DD.MM.YYYY (European format) |
| `4` | YYYY.MM.DD (ISO / dot-separated) |
| `5` | YYYY/MM/DD (ISO / slash-separated) |

default `01`· token `DEFAULT_DATUM`· source: firmware-token

### `3004/7/00001000b` — Delete personal data on next start  ·  _med_

When set, triggers deletion of stored personal/user data on the next system start. Gated by absence of car-sharing (ECSM) or flexible car-use (5GC) options.

| value | meaning |
|---|---|
| `0` | Off (keep data) |
| `1` | On (delete on next start) |

default `00`· gate: NOT ECSM Deletion of Car Sharing Module / 5GC Preparation of Flexible Car Use· token `DEL_PERS_DATA`· source: firmware-token

### `3004/7/00010000b` — Software update manager  ·  _med_

Turns on the head unit's software update manager, which finds and installs software updates delivered by USB or over the air.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: always (no FA gate)· token `SOFTWARE_UPDATE_MANAGER`· source: firmware-trace

### `3004/7/00100000b` — Software Update Assistant enable  ·  _high_

Enables the Software Update Assistant — a guided on-screen update workflow presented to the user. FA-gated; active only with certain navigation, telephony, telematics, or car-sharing options.

| value | meaning |
|---|---|
| `0` | Inactive |

default `00`· gate: 606 Navigation system Business / 609 Professional navigation system / 6NH Hands-free system with USB interface / 6NR Apps / 6NS Comfort telephony with expanded smartphone connection / 6AE TeleServices / ECSM Deletion of Car Sharing Module / 5GC Preparation of Flexible Car Use / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `SOFTWARE_UPDATE_ASSISTANT`· source: firmware-token

### `3004/7/01000000b` — Connectivity system version identification method  ·  _med_

Selects how the connectivity system version is reported / identified. The only defined value uses the part number (Teilenummer).

| value | meaning |
|---|---|
| `0` | Part number (Teilenummer) |

default `00`· gate: always (no FA gate)· token `CONNECTIVITY_SYSTEM_VER`· source: firmware-token

### `3004/7/10000000b` — Default distance unit  ·  _high_

Sets the default unit for displaying distances (odometer, range, navigation). FA-gated by 548 (speedometer with km reading).

| value | meaning |
|---|---|
| `0` | Kilometres (km) |
| `1` | Miles |

default `00`· gate: 548 Speedometer with kilometer reading· token `DEFAULT_WEG_EINHEIT`· source: firmware-token

### `3004/8/00000011b` — Default tyre pressure unit  ·  _high_

Sets the factory-default unit for tyre pressure display (RDC / tyre-pressure monitoring system).

| value | meaning |
|---|---|
| `0` | kPa |
| `1` | bar |
| `2` | psi |

default `01`· token `DEFAULT_DRUCK_EINHEIT`· source: firmware-token

### `3004/8/00000100b` — Default temperature unit  ·  _high_

Sets the factory-default unit for temperature display (outside temperature, climate settings, etc.).

| value | meaning |
|---|---|
| `0` | Fahrenheit (°F) |
| `1` | Celsius (°C) |

default `01`· token `DEFAULT_TEMPERATUR`· source: firmware-token

### `3004/8/00001000b` — ZBE touch-screen slide (touch-sensitive iDrive surface)  ·  _med_

Enables touch-slide (swipe/gesture) input on a touch-sensitive ZBE (iDrive controller surface).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `ZBE_TOUCH_SL`· source: firmware-token

### `3004/8/00010000b` — Default time format  ·  _high_

Sets the default time format for the clock display. FA-gated for Japanese, Gulf, and certain type-key regions.

| value | meaning |
|---|---|
| `0` | 12-hour (AM/PM) |
| `1` | 24-hour |

default `00`· gate: 807 Japanese version / 822 Gulf version / vehicle type-key attribute group (FP category 7; 103 type tokens, e.g. 12CK,12CL,12DE,1A12) / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93)· token `DEFAULT_ZEIT_EINHEIT`· source: firmware-token

### `3004/8/00100000b` — Miles variant (US or UK)  ·  _high_

When distance is displayed in miles, specifies whether US miles or UK miles (slightly different conversion context, used for speed/fuel calculations) are used.

| value | meaning |
|---|---|
| `0` | US miles |
| `1` | UK miles |

default `00`· token `EINSTELLUNG_MEILEN`· source: firmware-token

### `3004/8/11000000b` — Default fuel consumption unit  ·  _high_

Sets the factory-default unit for fuel consumption display. FA-gated (not Japan / not GB/Ireland).

| value | meaning |
|---|---|
| `0` | L/100 km (all other markets) |
| `1` | mpg (UK) |
| `2` | mpg (US) |
| `3` | km/L |

default `00`· gate: NOT 807 Japanese version / 812 Great Britain/Ireland version / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93)· token `VERBRAUCH`· source: firmware-token

### `3004/9/00000011b` — Transmission type  ·  _high_

Specifies the type of gearbox fitted. Used by the HMI to tailor gear-display and driving-dynamics UI. FA-gated by steptronic/DCT options.

| value | meaning |
|---|---|
| `1` | Manual (Handschalter) |
| `2` | Automatic (Steptronic/DCT) |

default `01`· gate: 205 Steptronic transmission / 2TB Steptronic sport transmission / 2MK M Double Clutch Transmission with Drivelogic· token `GETRIEBETYP`· source: firmware-token

### `3004/9/01111100b` — Body style (Bauart)  ·  _high_

Identifies the vehicle body style. The HMI uses this to select appropriate vehicle silhouette graphics and feature defaults. FA-gated by vehicle type-key group.

| value | meaning |
|---|---|
| `0` | Security vehicle (Sicherheitsfahrzeug) |
| `1` | Saloon / Sedan (Limousine) |
| `2` | Estate / Touring |

default `01`· gate: vehicle type-key attribute group (FP category 4; 55 type tokens, e.g. 11CL,12CL,1K51,1K52)· token `BAUART`· source: firmware-token

### `3004/9/10000000b` — Default voice-command dialog style  ·  _high_

Selects the default verbosity/style of BMW voice-command (SVS) dialogs. Standard shows full prompts; Short gives abbreviated prompts for experienced users.

| value | meaning |
|---|---|
| `0` | Standard (full prompts) |
| `1` | Short (brief prompts) |

default `00`· gate: FA-gated (depends on vehicle options)· token `DEFAULT_SVS_DIALOG`· source: firmware-token

### `3004/10/00000001b` — Drive type (all-wheel / rear-wheel drive)  ·  _med_

Specifies the vehicle drivetrain type. Used by the HMI and portation master for drivetrain-specific feature selection. FA-gated by vehicle type-key group.

| value | meaning |
|---|---|
| `0` | Rear-wheel drive (RWD) |
| `1` | All-wheel drive (xDrive/AWD) |

default `00`· gate: vehicle type-key attribute group (FP category 128; 192 type tokens, e.g. 11CK,11CL,11DE,12CK)· token `ANTRIEB`· source: firmware-token

### `3004/10/00000010b` — ZBE low-end controller fitted  ·  _med_

Indicates that a low-specification ZBE (iDrive controller, e.g. for entry-level navigation or audio systems) is fitted rather than the full Professional ZBE. Suppressed when TV, Business Nav, or Professional Nav is present.

| value | meaning |
|---|---|
| `0` | Off (standard ZBE) |
| `1` | On (low ZBE fitted) |

default `00`· gate: NOT 601 TV Function / 606 Navigation system Business / 609 Professional navigation system· token `ZBE_LOW`· source: firmware-token

### `3004/10/00000100b` — External MOST bus connected  ·  _high_

Indicates whether an external MOST (Media Oriented Systems Transport) optical bus is connected to the head unit, used for DVD changer or extended-equipment KOMBI. When inactive (code 0), no external MOST device is present.

| value | meaning |
|---|---|
| `0` | Not active (no external MOST) |
| `1` | Active (external MOST connected) |

default `01`· gate: 696 DVD changer for 6 DVDs / 6WA KOMBI with extended equipment specification / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `EXTERNER_MOST`· source: firmware-token

### `3004/10/00111000b` — Reserved / undocumented (dg3004 byte 10 bits 5-3)  ·  _low_

Purpose not determined from available sources. Shares byte 10 with ANTRIEB, ZBE_LOW, EXTERNER_MOST, HTTP_ILEVEL_UPDATE, and ZBE_TOUCH.

source: inferred

### `3004/10/01000000b` — HTTP iLevel update enable  ·  _high_

Enables or disables the HTTP-based iLevel (i-step level) update mechanism, which allows the head unit to receive software component updates over HTTP from BMW's servers.

| value | meaning |
|---|---|
| `0` | Inactive |
| `1` | Active |

default `01`· gate: always (no FA gate)· token `HTTP_ILEVEL_UPDATE`· source: firmware-token

### `3004/10/10000000b` — ZBE touch-display (touch-screen iDrive) fitted  ·  _high_

Indicates that a touch-screen ZBE (iDrive controller with touch-sensitive display) is fitted. Enables touch input event routing. FA-gated by 609 (Professional Navigation).

| value | meaning |
|---|---|
| `0` | Not active (no touch ZBE) |
| `1` | Active (touch ZBE fitted) |

default `00`· gate: 609 Professional navigation system· token `ZBE_TOUCH`· source: firmware-token

### `3004/11/11111111b` — Diagnostic trace / logging mode  ·  _high_

Selects the diagnostic trace/logging channel active on this head unit. External tracing routes logs to an external tester/logger; internal tracing uses the on-device gnlog facility.

| value | meaning |
|---|---|
| `1` | External tracing (EXT_TRACING) |
| `2` | Internal tracing (INT_TRACING) |

default `01`· gate: HUTR Head-unit transport/standby mode word (HO-word)· token `TRACE`· source: firmware-token

### `3004/12/11111111b` — Sleep delay after clamp 30B drop (seconds, encoded)  ·  _high_

Sets the minimum time the head unit waits after the 30B clamp (battery-backed standby power) drops before entering deep sleep. The raw field value encodes time in units of 10 seconds.

| value | meaning |
|---|---|
| `42` | 420 seconds (7 minutes) |
| `144` | 1440 seconds (24 minutes) |
| `234` | 2340 seconds (39 minutes) |

default `FF`· gate: FA-gated (depends on vehicle options)· token `SLEEPDELAY_CLAMP30B_MIN`· source: firmware-token

### `3004/13/11111111b` — Sleep delay timer value (encoded seconds)  ·  _high_

Sets the sleep delay timer value (secondary sleep timer). Raw field value encodes time in units of 10 seconds; the defined settings correspond to 60, 180, 300, and 540 seconds.

| value | meaning |
|---|---|
| `6` | 60 seconds (1 minute) |
| `18` | 180 seconds (3 minutes) |
| `30` | 300 seconds (5 minutes) |
| `54` | 540 seconds (9 minutes) |

default `00`· gate: FA-gated (depends on vehicle options)· token `SLEEPDELAY_TIMERVALUE`· source: firmware-token

### `3004/14/00000001b` — Active Sound Design loudspeaker diagnostics mode  ·  _high_

Controls the Active Sound Design (ASD) loudspeaker diagnostic mode. When LS_DIAG_ON, speaker self-diagnostics are enabled; LS_DIAG_OFF suppresses them. FA-gated by vehicle type-key groups.

| value | meaning |
|---|---|
| `0` | Speaker diagnostics on (LS_DIAG_ON) |
| `1` | Speaker diagnostics off (LS_DIAG_OFF) |

default `00`· gate: vehicle type-key attribute group (FP category 12; 86 type tokens, e.g. 11CK,11CL,12CK,12CL) / vehicle type-key attribute group (FP category 12; 79 type tokens, e.g. 11DE,12DE,1A31,1A32) / vehicle type-key attribute group (FP category 13; 28 type tokens, e.g. 1B71,1B72,1B91,1H91) / vehicle type-key attribute group (FP category 13; 23 type tokens, e.g. 1A50,1A51,1A52,1D51) / vehicle type-key attribute group (FP category 1; 71 type tokens, e.g. 1A10,1A11,1A12,1A31) / vehicle type-key attribute group (FP category 13; 4 type tokens, e.g. 1F93,1G93,1K93,1L93) / vehicle type-key attribute group (FP category 1; 61 type tokens, e.g. 1D11,1D12,1D31,1D32) / vehicle type-key attribute group (FP category 1; 65 type tokens, e.g. 11CK,11DE,12CK,12DE) / vehicle type-key attribute group (FP category 1; 55 type tokens, e.g. 11CL,12CL,1K51,1K52) / vehicle type-key attribute group (FP category 13; 28 type tokens, e.g. 11DE,12DE,1S11,1S12) / vehicle type-key attribute group (FP category 13; 8 type tokens, e.g. 2F93,2H93,2J13,2J33) / numeric value-attribute 0321 (FP category 255) / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `ASD`· source: firmware-token

### `3004/14/00011110b` — Reserved / undocumented (dg3004 byte 14 bits 4-1)  ·  _low_

Purpose not determined from available sources. Shares byte 14 with ASD, ENT_MODE_NAVIGATION, and CAN_ANSCHLUSS_HEADUNIT.

source: inferred

### `3004/14/01100000b` — Navigation entertainment mode (entitlement model)  ·  _med_

Controls how navigation features are enabled/authorised. When set to 'active with authorisation', navigation content requires an online authorisation step before becoming available. FA-gated; not active in car-sharing or flexible car-use scenarios.

| value | meaning |
|---|---|
| `0` | Off / no restriction |
| `2` | Active with authorisation required |

default `00`· gate: NOT ECSM Deletion of Car Sharing Module / 5GC Preparation of Flexible Car Use· token `ENT_MODE_NAVIGATION`· source: firmware-token

### `3004/14/10000000b` — Head unit CAN bus connection  ·  _high_

Specifies which CAN bus the head unit is physically connected to. Body CAN is standard for most models; IK-CAN (instrument cluster CAN) is used in some configurations.

| value | meaning |
|---|---|
| `0` | Body CAN (HU_AN_BODY_CAN) |
| `1` | IK-CAN / instrument cluster CAN (HU_AN_IK_CAN) |

default `00`· gate: always (no FA gate)· token `CAN_ANSCHLUSS_HEADUNIT`· source: firmware-token

### `3004/15/00000011b` — BMW Connected Services entertainment mode (entitlement)  ·  _med_

Controls how BMW online/Connected Services features are authorised in the entertainment mode. 'Active with authorisation' requires an online authorisation step. FA-gated; not active in car-sharing scenarios.

| value | meaning |
|---|---|
| `0` | Off / no restriction |
| `2` | Active with authorisation required |

default `00`· gate: NOT ECSM Deletion of Car Sharing Module / 5GC Preparation of Flexible Car Use· token `ENT_MODE_BMW_SERVICES`· source: firmware-token

### `3004/15/00001100b` — Partial network (sub-bus) operation mode  ·  _high_

Enables partial network (Teilnetzbetrieb) mode, allowing the head unit to operate on a reduced-power sub-network. Version selects the 2013 or 2015 partial-network protocol variant.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | Active (2013 variant) |
| `2` | Active (2015 variant) |

default `00`· gate: FA-gated (depends on vehicle options)· token `TEILNETZBETRIEB`· source: firmware-token

### `3004/15/00110000b` — Connectivity entertainment mode (entitlement)  ·  _med_

Controls how connectivity features (e.g. Wi-Fi hotspot, online services) are authorised. FA-gated; not active in car-sharing scenarios.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | Mode 1 (active) |
| `2` | Mode 2 (active, extended) |

default `00`· gate: NOT ECSM Deletion of Car Sharing Module / 5GC Preparation of Flexible Car Use· token `ENT_MODE_CONNECTIVITY`· source: firmware-token

### `3004/15/01000000b` — Screen mirroring enable  ·  _high_

Enables the screen mirroring feature (MIRS — Mirroring on switch), allowing a connected device's display to be mirrored on the iDrive screen. FA-gated by MIRS option.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: MIRS Mirroring on switch in head units· token `MIRRORING`· source: firmware-token

### `3004/15/10000000b` — Reserved / undocumented (dg3004 byte 15 bit 7)  ·  _low_

Purpose not determined from available sources. Shares byte 15 with ENT_MODE_BMW_SERVICES, TEILNETZBETRIEB, ENT_MODE_CONNECTIVITY, and MIRRORING.

source: inferred

### `3004/16/00001111b` — Product line  ·  _med_

Tells the head unit which BMW Group product line the car belongs to. The personal profile system and other functions use it to pick line-specific defaults. Set it to match the car.

| value | meaning |
|---|---|
| `0` | Unknown |
| `1` | Product line G |
| `2` | Product line K |
| `3` | Product line U-B |
| `4` | Product line U-M |
| `6` | Product line I |
| `7` | Product line R |
| `8` | Product line 35up |

default `01`· gate: FA-gated (depends on vehicle options)· token `PRODUKTLINIE`· source: firmware-trace

### `3004/16/00010000b` — HDCP copy protection  ·  _high_

Turns on HDCP (High-bandwidth Digital Content Protection) on the head unit's digital video connections, the copy protection that protected video content requires. Best left unchanged.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `01`· gate: FA-gated (depends on vehicle options)· token `fHDCP`· source: firmware-trace

### `3004/16/11100000b` — Reserved / undocumented (dg3004 byte 16 bits 7-5)  ·  _low_

Purpose not determined from available sources. Shares byte 16 with PRODUKTLINIE and HDCP.

source: inferred

### `3004/17/11111111b` — Reserved / undocumented block (dg3004 bytes 17-18)  ·  _low_

Purpose not determined from available sources. Two-byte unnamed block following PRODUKTLINIE and HDCP fields.

source: inferred

### `3004/19/00000111b` — Service pack level  ·  _med_

Encodes the installed software service-pack level for the head unit. Raw numeric value 0-5; no symbolic names defined.

default `00`· gate: FA-gated (depends on vehicle options)· token `SERVICE_PACK`· source: firmware-token

### `3004/19/00001000b` — CAN selective wakeup  ·  _high_

Enables CAN selective wakeup (CPS — CAN partial networking / selective wakeup), allowing the head unit to be woken by specific CAN frames rather than requiring full bus activity.

| value | meaning |
|---|---|
| `0` | CPS (selective wakeup base mode) |

default `00`· gate: FA-gated (depends on vehicle options)· token `CAN_SELECTIVE_WAKEUP`· source: firmware-token

### `3004/19/00110000b` — Vehicle state concept  ·  _med_

Tells the head unit which power-state model the car uses: the conventional model based on ignition terminals, or the newer park, reside and drive model (PWF). The personal profile system relies on it to time profile actions. Set it to match the car.

| value | meaning |
|---|---|
| `0` | Conventional terminals |
| `1` | Park, reside, drive |

default `00`· gate: always (no FA gate)· token `fVEHICLE_STATE_CONCEPT`· source: firmware-trace

### `3004/19/11000000b` — Reserved / undocumented (dg3004 byte 19 bits 7-6)  ·  _low_

Purpose not determined from available sources. Shares byte 19 with SERVICE_PACK, CAN_SELECTIVE_WAKEUP, and VEHICLE_STATE_CONCEPT.

source: inferred

### `3004/20/11111111b` — Touch proximity sensor Z-axis calibration range  ·  _med_

4-byte calibration range for the touch-proximity sensor Z-axis (depth/distance from screen). Encodes minimum and maximum threshold values used by the proximity detection subsystem. value format is type0x66 (signed 16-bit pair: min/max).

default `811881AE`· gate: FA-gated (depends on vehicle options)· token `PROXIMITY_Z`· source: firmware-token

### `3004/24/11111111b` — Touch proximity sensor Y-axis calibration range  ·  _med_

4-byte calibration range for the touch-proximity sensor Y-axis (vertical position). Encodes minimum and maximum threshold values.

default `00AA8096`· gate: FA-gated (depends on vehicle options)· token `PROXIMITY_Y`· source: firmware-token

### `3004/28/11111111b` — Touch proximity sensor X-axis calibration range  ·  _med_

4-byte calibration range for the touch-proximity sensor X-axis (horizontal position). Encodes minimum and maximum threshold values.

default `80EB81A9`· gate: FA-gated (depends on vehicle options)· token `PROXIMITY_X`· source: firmware-token

### `3004/32/00000011b` — CarPlay / navigation NMEA coordinate variant  ·  _high_

Selects the GPS coordinate format/datum used for CarPlay and navigation data exchange. WGS-84 is the global standard; GCJ-02 (shifted) is required for mainland China. DR suffix adds dead-reckoning support. FA-gated by Chinese (8AA) and country-control (8LH) options.

| value | meaning |
|---|---|
| `0` | WGS-84 (global standard) |
| `1` | WGS-84 with dead reckoning |
| `2` | GCJ-02 shifted (China mainland) |
| `3` | GCJ-02 shifted with dead reckoning |

default `00`· gate: 8AA Chinese version / 8LH Country control 04142· token `CP_NMEA_VARIANT`· source: firmware-token

### `3004/32/11111100b` — Reserved / undocumented (dg3004 byte 32 bits 7-2)  ·  _low_

Purpose not determined from available sources. Shares byte 32 with CP_NMEA_VARIANT.

source: inferred

### `3004/33/11111111b` — Long VIN storage block  ·  _med_

17-byte block (bytes 33-49) storing the full 17-character vehicle VIN in the system settings page. All-zero default indicates not yet programmed.

_token=null; resolved_unnamed: LONGVIN_BLOCK; syset_fielddict has sub-field LONGVIN at 3004/33/0x02; 17-byte span (bytes 33-49); default all zeros._

default `0000000000000000000000000000000000`· source: firmware-trace

## Datagroup 0x3005 (96 parameters)

### `3005/0/11111111b` — Display dimming curve X1 (ambient light input, point 1)  ·  _med_

First X-axis breakpoint of the 3-point ambient-light-to-brightness mapping curve for the central display. Defines the lower ambient light sensor level at which the brightness curve starts. This is a 16-bit value split across bytes 0-1.

default `0000`· token `DIM_CURVE_X1`· source: firmware-token

### `3005/2/11111111b` — Display dimming curve X2 (ambient light input, point 2)  ·  _med_

Second (middle) X-axis breakpoint of the 3-point ambient-light-to-brightness mapping curve for the central display. Default 0x1FC0 = 8128 (mid-range sensor value).

default `1FC0`· token `DIM_CURVE_X2`· source: firmware-token

### `3005/4/11111111b` — Display dimming curve X3 (ambient light input, point 3)  ·  _med_

Third (upper) X-axis breakpoint of the ambient-light-to-brightness mapping curve for the central display. Default 0x7F00 = 32512 (near-maximum sensor reading).

default `7F00`· token `DIM_CURVE_X3`· source: firmware-token

### `3005/6/11111111b` — Display dimming curve Y1 (brightness output, point 1)  ·  _med_

First Y-axis breakpoint of the brightness mapping curve — the brightness level output at the lowest ambient light sensor value (X1). Default 0x0145 = 325. This is a 16-bit value across bytes 6-7.

default `0145`· token `DIM_CURVE_Y1`· source: firmware-token

### `3005/8/11111111b` — Display dimming curve Y2 (brightness output, point 2)  ·  _med_

Second (middle) Y-axis breakpoint of the brightness mapping curve — the brightness level at the midpoint ambient sensor value (X2). Default 0x1FC0 = 8128.

default `1FC0`· token `DIM_CURVE_Y2`· source: firmware-token

### `3005/10/11111111b` — Display dimming curve Y3 (brightness output, point 3)  ·  _med_

Third (upper) Y-axis breakpoint of the brightness mapping curve — the maximum brightness output at the highest ambient sensor value (X3). Default 0x7F00 = 32512.

default `7F00`· token `DIM_CURVE_Y3`· source: firmware-token

### `3005/12/11111111b` — Display dimming filter change sensitivity  ·  _med_

Sensitivity threshold for the low-pass / change-detection filter that controls how aggressively the display brightness responds to ambient light fluctuations. Higher values make the display less reactive to quick lighting changes. Default 0 (minimum filtering).

default `0000`· token `DIM_FILT_CHANGE_SENS`· source: firmware-token

### `3005/14/11111111b` — Display dimming alpha tolerance  ·  _med_

Alpha (percentage/fraction) tolerance band around the current brightness target; the dimmer does not react until the ambient light change exceeds this proportional threshold. Default 15.

| value | meaning |
|---|---|
| `15` | WERT_15 |

default `0F`· token `DIM_TOLERANCE_ALPHA`· source: firmware-token

### `3005/15/11111111b` — Display dimming absolute tolerance  ·  _med_

Absolute (count) tolerance band; the dimmer ignores ambient sensor changes smaller than this absolute value. Prevents flicker due to sensor noise. Default 10.

| value | meaning |
|---|---|
| `10` | WERT_10 |

default `0A`· token `DIM_TOLERANCE_ABS`· source: firmware-token

### `3005/16/11111111b` — Display dimming differential gain  ·  _med_

Gain factor applied to the differential (rate-of-change) component of the ambient light signal before feeding into the dimming controller. Higher values make the display react more quickly to fast light changes. Default 1.

| value | meaning |
|---|---|
| `1` | WERT_1 |

default `01`· token `DIM_DIFF_GAIN`· source: firmware-token

### `3005/17/11111111b` — Display dimming differential threshold  ·  _med_

Minimum rate-of-change of the ambient light signal required to trigger the differential (fast-response) path of the dimming controller. Default 10.

| value | meaning |
|---|---|
| `10` | WERT_10 |

default `0A`· token `DIM_DIFF_THRESHOLD`· source: firmware-token

### `3005/18/11111111b` — Display dimming differential bias  ·  _med_

Offset added to the differential brightness adjustment step; provides a base increment when the differential path activates. Default 4.

| value | meaning |
|---|---|
| `4` | WERT_4 |

default `04`· token `DIM_DIFF_BIAS`· source: firmware-token

### `3005/19/11111111b` — Display dimming differential maximum step  ·  _med_

Maximum brightness adjustment step size that the differential path can apply per cycle, capping how fast the display can change brightness. Default 128.

| value | meaning |
|---|---|
| `128` | WERT_128 |

default `80`· token `DIM_DIFF_MAX`· source: firmware-token

### `3005/20/11111111b` — Display dimming differential minimum step  ·  _med_

Minimum non-zero brightness adjustment step produced by the differential path; prevents sub-threshold corrections from stalling. Default 7.

| value | meaning |
|---|---|
| `7` | WERT_7 |

default `07`· token `DIM_DIFF_MIN`· source: firmware-token

### `3005/21/11111111b` — Display dimming minimum brightness increase step  ·  _med_

Minimum step size per dimming cycle when brightness is increasing (dim-up). Prevents imperceptibly slow brightening transitions. Default 1 (WERT_01); alternate code 20 = WERT_14 (step size 14).

| value | meaning |
|---|---|
| `1` | Step 1 (minimum, default) |
| `20` | Step 14 |

default `01`· gate: always (no FA gate)· token `DIM_UP_MIN`· source: firmware-token

### `3005/22/11111111b` — Display dimming minimum brightness decrease step  ·  _med_

Minimum step size per dimming cycle when brightness is decreasing (dim-down). Prevents imperceptibly slow dimming transitions. Default 1; alternate value 180 applies larger minimum step.

| value | meaning |
|---|---|
| `1` | Step 1 (minimum, default) |
| `180` | Step 180 (large minimum) |

default `01`· gate: always (no FA gate)· token `DIM_DOWN_MIN`· source: firmware-token

### `3005/23/11111111b` — Display dimming maximum brightness offset  ·  _med_

Maximum upward offset from the curve-calculated brightness that can be applied (e.g. by a user preference boost or environmental override). Default 127.

| value | meaning |
|---|---|
| `127` | WERT_127 |

default `7F`· token `DIM_MAX_OFFSET_BRIG`· source: firmware-token

### `3005/24/11111111b` — Display dimming fade time T0  ·  _med_

Duration (in display-subsystem time units) of the initial fade phase T0 when transitioning brightness. Default 0 (immediate transition start, no delay).

default `00`· token `DIM_FADE_TIME_T0`· source: firmware-token

### `3005/25/11111111b` — Display dimming fade time T1  ·  _med_

Duration of the first fade ramp phase T1 when transitioning the central display brightness. Default 15 (units depend on firmware timer base).

| value | meaning |
|---|---|
| `15` | WERT_15 |

default `0F`· token `DIM_FADE_TIME_T1`· source: firmware-token

### `3005/26/11111111b` — Display dimming fade time T2  ·  _med_

Duration of the second fade ramp phase T2 of the central display brightness transition. Default 5.

| value | meaning |
|---|---|
| `5` | WERT_5 |

default `05`· token `DIM_FADE_TIME_T2`· source: firmware-token

### `3005/27/11111111b` — Display dimming fade exponent T1  ·  _med_

Exponent (curve shape) applied to the T1 fade ramp; controls whether the brightness ramp is linear (1) or accelerated/decelerated. Default 1 (linear).

| value | meaning |
|---|---|
| `1` | WERT_1 |

default `01`· token `DIM_FADE_EXPO_T1`· source: firmware-token

### `3005/28/11111111b` — Display dimming fade exponent T2  ·  _med_

Exponent applied to the T2 fade ramp for the central display brightness transition. Default 1.

default `01`· token `DIM_FADE_EXPO_T2`· source: firmware-token

### `3005/29/11111111b` — Display dimming minimum brightness offset  ·  _med_

Minimum downward offset from the curve-calculated brightness target (i.e. how far below the curve the display can be driven). Default 0 (no lower offset allowed).

| value | meaning |
|---|---|
| `0` | WERT_0 |

default `00`· token `DIM_MIN_OFFSET_BRIG`· source: firmware-token

### `3005/30/11111111b` — Endianness adapted flag  ·  _med_

Internal flag indicating whether byte-endianness adaptation has been applied to this coding page data. Should remain 0 (not adapted) under normal circumstances.

| value | meaning |
|---|---|
| `0` | WERT_0 |

default `00`· token `ENDIANESS_ADAPTED`· source: firmware-token

### `3005/31/11111111b` — Padding byte 3  ·  _high_

Reserved padding byte with no functional meaning. Fixed at 0xFF to fill the coding page structure; must not be changed.

| value | meaning |
|---|---|
| `255` | Reserved (default 0xFF) |

default `FF`· token `PADDING3`· source: firmware-token

### `3005/32/11111111b` — Display thermal protection threshold 1  ·  _med_

First (lowest) temperature threshold (in tenths of a degree Kelvin or raw sensor units) at which the display begins reducing brightness for thermal protection. Default 0x0672 = 1650. This is a 16-bit value across bytes 32-33.

default `0672`· token `TEMP_THRESHOLD1`· source: firmware-token

### `3005/34/11111111b` — Display thermal protection threshold 2  ·  _med_

Second temperature threshold for display brightness reduction. Default 0x06D6 = 1750. Above this level an additional brightness reduction step is applied.

default `06D6`· token `TEMP_THRESHOLD2`· source: firmware-token

### `3005/36/11111111b` — Display thermal protection threshold 3  ·  _med_

Third temperature threshold for display brightness reduction. Default 0x073A = 1850.

default `073A`· token `TEMP_THRESHOLD3`· source: firmware-token

### `3005/38/11111111b` — Display thermal protection threshold 4  ·  _med_

Fourth (highest) temperature threshold for display brightness reduction. Default 0x079E = 1950. Above this level the display applies maximum brightness reduction to prevent overheating.

default `079E`· token `TEMP_THRESHOLD4`· source: firmware-token

### `3005/40/11111111b` — ZIN display dimming curve X1 (ambient input, point 1)  ·  _med_

First X-axis breakpoint of the 3-point ambient-light-to-brightness mapping curve for the ZIN (central information display / rear zone). 16-bit value across bytes 40-41. Default 0 (lowest sensor reading).

default `0000`· token `ZIN_DIM_CURVE_X1`· source: firmware-token

### `3005/42/11111111b` — ZIN display dimming curve X2 (ambient input, point 2)  ·  _med_

Second X-axis breakpoint of the ZIN ambient-light-to-brightness curve. Default 0x1FC0 = 8128.

default `1FC0`· token `ZIN_DIM_CURVE_X2`· source: firmware-token

### `3005/44/11111111b` — ZIN display dimming curve X3 (ambient input, point 3)  ·  _med_

Third X-axis breakpoint of the ZIN ambient-light-to-brightness curve. Default 0x7F00 = 32512.

default `7F00`· token `ZIN_DIM_CURVE_X3`· source: firmware-token

### `3005/46/11111111b` — ZIN display dimming curve Y1 (brightness output, point 1)  ·  _med_

First Y-axis breakpoint of the ZIN brightness output curve — the brightness level at the lowest ambient sensor value. Default 0x03E8 = 1000 (brighter minimum than the CID curve).

default `03E8`· token `ZIN_DIM_CURVE_Y1`· source: firmware-token

### `3005/48/11111111b` — ZIN display dimming curve Y2 (brightness output, point 2)  ·  _med_

Second Y-axis breakpoint of the ZIN brightness output curve. Default 0x1FC0 = 8128.

default `1FC0`· token `ZIN_DIM_CURVE_Y2`· source: firmware-token

### `3005/50/11111111b` — ZIN display dimming curve Y3 (brightness output, point 3)  ·  _med_

Third Y-axis breakpoint of the ZIN brightness output curve — maximum brightness. Default 0x7F00 = 32512.

default `7F00`· token `ZIN_DIM_CURVE_Y3`· source: firmware-token

### `3005/52/11111111b` — ZIN display dimming maximum brightness offset  ·  _med_

Maximum upward brightness offset allowed for the ZIN display above the curve-calculated target. Default 127.

| value | meaning |
|---|---|
| `127` | WERT_127 |

default `7F`· token `ZIN_DIM_MAX_OFFSET_BRIG`· source: firmware-token

### `3005/53/11111111b` — ZIN display dimming minimum brightness offset  ·  _med_

Minimum downward brightness offset for the ZIN display below the curve-calculated target. Default 0 (no downward offset).

| value | meaning |
|---|---|
| `0` | WERT_0 |

default `00`· token `ZIN_DIM_MIN_OFFSET_BRIG`· source: firmware-token

### `3005/54/11111111b` — ZIN display dimming minimum brightness decrease step  ·  _med_

Minimum step size per cycle when decreasing ZIN display brightness. Default 120 (larger minimum than CID, producing a faster observable dim-down).

| value | meaning |
|---|---|
| `120` | Step 120 (default) |

default `78`· token `ZIN_DIM_DOWN_MIN`· source: firmware-token

### `3005/55/11111111b` — ZIN display dimming minimum brightness increase step  ·  _med_

Minimum step size per cycle when increasing ZIN display brightness. Default 1; alternate value 2 activates hub-step mode.

| value | meaning |
|---|---|
| `1` | Step 1 (minimum, default) |
| `2` | Hub-values step |

default `01`· token `ZIN_DIM_UP_MIN`· source: firmware-token

### `3005/56/11111111b` — ZIN display fade-in time T1  ·  _med_

Duration of the first ramp phase when the ZIN display fades in (increases brightness). Default 3 (time units).

| value | meaning |
|---|---|
| `3` | WERT_3 |

default `03`· token `ZIN_DIM_FADE_IN_T1`· source: firmware-token

### `3005/57/11111111b` — ZIN display fade-in time T2  ·  _med_

Duration of the second ramp phase of the ZIN display fade-in transition. Default 6.

| value | meaning |
|---|---|
| `6` | WERT_6 |

default `06`· token `ZIN_DIM_FADE_IN_T2`· source: firmware-token

### `3005/58/11111111b` — ZIN display fade-in time T3  ·  _med_

Duration of the third ramp phase of the ZIN display fade-in transition. Default 12.

| value | meaning |
|---|---|
| `12` | WERT_12 |

default `0C`· token `ZIN_DIM_FADE_IN_T3`· source: firmware-token

### `3005/59/11111111b` — ZIN display dimming timeout T1  ·  _med_

First timeout duration for the ZIN display dimming state machine — how long the display stays at a transient brightness level before proceeding to the next step. Default 12.

default `0C`· token `ZIN_DIM_TIME_OUT_T1`· source: firmware-token

### `3005/60/11111111b` — ZIN display dimming timeout T2  ·  _med_

Second timeout duration in the ZIN display dimming state machine. Default 37.

| value | meaning |
|---|---|
| `37` | WERT_37 |

default `25`· token `ZIN_DIM_TIME_OUT_T2`· source: firmware-token

### `3005/61/11111111b` — ZIN display dimming timeout T3  ·  _med_

Third (longest) timeout duration in the ZIN display dimming state machine. Default 50.

| value | meaning |
|---|---|
| `50` | WERT_50 |

default `32`· token `ZIN_DIM_TIME_OUT_T3`· source: firmware-token

### `3005/62/11111111b` — Center instrument data checksum (CRC)  ·  _med_

Checksum (CRC) calculation for the data exchanged with the MINI center instrument. Best left unchanged.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `ZIN_CRC_CALC`· source: firmware-token

### `3005/63/00000001b` — ZIN animation config 1  ·  _med_

First animation configuration bit for the ZIN display. Controls an unspecified animation parameter or mode flag for the ZIN (central information display) subsystem. Not active on this vehicle.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ZIN_ANIMATION_CONFIG1`· source: firmware-token

### `3005/63/00000010b` — ZIN animation config 2  ·  _med_

Second animation configuration bit for the ZIN display. Controls a second animation mode flag. Not active on this vehicle.

| value | meaning |
|---|---|
| `0` | Inactive |
| `1` | Active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ZIN_ANIMATION_CONFIG2`· source: firmware-token

### `3005/63/00000100b` — ZIN animation config 3  ·  _med_

Third animation configuration bit for the ZIN display. Controls a third animation mode flag. Not active on this vehicle.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ZIN_ANIMATION_CONFIG3`· source: firmware-token

### `3005/63/00001000b` — ZIN animation config 4  ·  _med_

Fourth animation configuration bit for the ZIN display. Not active on this vehicle.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ZIN_ANIMATION_CONFIG4`· source: firmware-token

### `3005/63/00010000b` — ZIN animation config 5  ·  _med_

Fifth animation configuration bit for the ZIN display. Not active on this vehicle.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ZIN_ANIMATION_CONFIG5`· source: firmware-token

### `3005/63/00100000b` — ZIN animation config 6  ·  _med_

Sixth animation configuration bit for the ZIN display. Not active on this vehicle.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ZIN_ANIMATION_CONFIG6`· source: firmware-token

### `3005/63/01000000b` — ZIN animation config 7  ·  _med_

Seventh animation configuration bit for the ZIN display. Not active on this vehicle.

| value | meaning |
|---|---|
| `0` | Inactive |
| `1` | Active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ZIN_ANIMATION_CONFIG7`· source: firmware-token

### `3005/63/10000000b` — ZIN animation config 8  ·  _med_

Eighth animation configuration bit for the ZIN display. Not active on this vehicle.

| value | meaning |
|---|---|
| `0` | Inactive |
| `1` | Active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ZIN_ANIMATION_CONFIG8`· source: firmware-token

### `3005/64/11111111b` — ZIN display variant  ·  _high_

Selects which ZIN (central information display) hardware variant is fitted. KEIN_ZIN = no ZIN display present; RADIO_ZIN = ZIN display driven by the radio/HU. Not active (no ZIN) on this vehicle.

| value | meaning |
|---|---|
| `0` | No ZIN display (KEIN_ZIN) |
| `3` | Radio ZIN display (RADIO_ZIN) |

default `00`· gate: FA-gated (depends on vehicle options)· token `ZIN_VARIANT`· source: firmware-token

### `3005/65/11111111b` — ZIN display maximum target brightness  ·  _med_

Maximum allowed target brightness level for the ZIN display. Default 0x7F00 (INITWERT = initial/nominal maximum). Used to cap ZIN brightness regardless of the dimming curve output.

default `7F00`· gate: FA-gated (depends on vehicle options)· token `ZIN_MAX_TARGET_BRIGHTNESS`· source: firmware-token

### `3005/67/00000001b` — ZIN blower fan variant  ·  _high_

Selects the cooling fan (blower) hardware variant used for the ZIN display. BASE = standard blower; HIGH = high-performance blower (requires different thermal management tuning).

| value | meaning |
|---|---|
| `0` | Base blower (standard) |
| `1` | High-performance blower |

default `00`· gate: always (no FA gate)· token `ZIN_BLOWER_VARIANT`· source: firmware-token

### `3005/67/00000010b` — CID touch proximity sensor  ·  _med_

Enables the proximity (hover) detection sensor on the CID (Central Information Display) touchscreen. When active, the display can detect a hand approaching before physical contact. Not active on this vehicle.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `CID_TOUCH_PROXIMITY`· source: firmware-token

### `3005/67/00000100b` — CID touchscreen speed-lock enable  ·  _med_

Enables speed-lock (input restriction at speed) specifically for the CID touchscreen. When active, touch input on the CID may be restricted above a vehicle speed threshold. Not active on this vehicle.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `CID_TOUCH_SL`· source: firmware-token

### `3005/67/11111000b` — CID display pixel aspect ratio  ·  _high_

Configures the pixel aspect ratio correction factor applied to CID display output. RATIO_1_00 = square pixels (1:1); RATIO_1_07 = 1.07:1 non-square correction for panels with non-square pixels.

| value | meaning |
|---|---|
| `15` | 1:1 square pixels (RATIO_1_00) |
| `22` | 1.07:1 non-square pixels (RATIO_1_07) |

default `0F`· token `CID_DISP_AR`· source: firmware-token

### `3005/68/00000001b` — CID touchscreen enable  ·  _high_

Enables touchscreen functionality on the CID (Central Information Display). Active on vehicles with 601 TV Function or 609 Professional navigation system.

| value | meaning |
|---|---|
| `0` | Touch disabled |
| `1` | Touch enabled |

default `00`· gate: 601 TV Function / 609 Professional navigation system· token `CID_TOUCH`· source: firmware-token

### `3005/68/00001110b` — CID APIX interface mode  ·  _high_

Selects the APIX (Automotive Pixel Link) communication protocol version used between the head unit and the CID display. AUTO lets the HU negotiate; APIX1/2/3 force a specific version.

| value | meaning |
|---|---|
| `0` | Auto-negotiate |
| `1` | APIX1 |
| `2` | APIX2 |
| `3` | APIX3 |

default `02`· token `CID_APIX_MODE`· source: firmware-token

### `3005/68/00110000b` — CID display color depth  ·  _med_

Selects the color bit depth transmitted over the APIX link to the CID. Raw enum codes present (1, 2) but no symbolic names; default corresponds to 18-bit color (per cur_desc).

default `02`· token `CID_COLOR_DEPTH`· source: firmware-token

### `3005/68/11000000b` — CID communication mode  ·  _med_

Selects the physical communication interface mode used by the CID controller. Raw codes only (value 2 is the fitted default); no symbolic names available in the firmware descriptor.

default `02`· token `CID_COM_MODE`· source: firmware-token

### `3005/69/00000111b` — CID display resolution  ·  _med_

Selects the CID panel resolution. Active on vehicles with 609 Professional navigation. Default value 1 corresponds to 800x480 per cur_desc; raw codes 1-5 cover various resolution options.

default `01`· gate: 609 Professional navigation system· token `CID_DISPLAY_RES`· source: firmware-token

### `3005/69/00111000b` — CID display physical size  ·  _med_

Selects the CID panel physical size variant. Default code 1 = 6.5-inch panel per cur_desc. Codes 1-4 cover different display sizes. Not active on this vehicle.

default `01`· gate: FA-gated (depends on vehicle options)· token `CID_DISPLAY_SIZE`· source: firmware-token

### `3005/69/01000000b` — Display dimming algorithm variant  ·  _high_

Selects between the old (ALTE_DIMMUNG) and new (NEUE_DIMMUNG) automatic brightness control algorithm. Not active on this vehicle (uses new algorithm by default via DIM_VARIANT).

| value | meaning |
|---|---|
| `0` | Old dimming algorithm (ALTE_DIMMUNG) |
| `1` | New dimming algorithm (NEUE_DIMMUNG) |

default `00`· gate: FA-gated (depends on vehicle options)· token `DIMMUNGSVARIANTE`· source: firmware-token

### `3005/69/10000000b` — CID HMI wakeup via touch  ·  _med_

Enables waking up the HMI (display/user-interface) from sleep/standby by touching the CID touchscreen. Not active on this vehicle.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `CID_HMI_ACTIVATION_VIA_TOUCH`· source: firmware-token

### `3005/70/00000001b` — DISPLAY_PIP_CONFIG boolean flag (byte 70 bit 0)  ·  _low_

A boolean flag within the DISPLAY_PIP_CONFIG coding page (byte 70, bit 0). Active on this vehicle. Exact field name not individually pinned in the firmware name table; likely an RSE (rear-seat entertainment) or PIP (picture-in-picture) enable flag given its location adjacent to RSE_APIX_MODE.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

token `DISPLAY_PIP_CONFIG byte 70 (boolean flag (Bool)`· source: inferred

### `3005/70/00001110b` — RSE display APIX interface mode  ·  _high_

Selects the APIX protocol version for the RSE (Rear-Seat Entertainment) display link. AUTO lets the HU negotiate; APIX1/2/3 force a specific version. Not active on this vehicle.

| value | meaning |
|---|---|
| `0` | Auto-negotiate |
| `1` | APIX1 |
| `2` | APIX2 |
| `3` | APIX3 |

default `02`· gate: FA-gated (depends on vehicle options)· token `RSE_APIX_MODE`· source: firmware-token

### `3005/70/00110000b` — RSE display color depth  ·  _med_

Selects the color bit depth for the RSE display APIX link. Raw codes only (value 2 is the default). Not active on this vehicle.

default `02`· gate: FA-gated (depends on vehicle options)· token `RSE_COLOR_DEPTH`· source: firmware-token

### `3005/70/11000000b` — RSE display communication mode  ·  _high_

Selects the physical communication interface for the RSE display controller. SPI = Serial Peripheral Interface; MII = Media Independent Interface (Ethernet-family). Not active on this vehicle.

| value | meaning |
|---|---|
| `1` | SPI |
| `2` | MII |

default `01`· gate: FA-gated (depends on vehicle options)· token `RSE_COM_MODE`· source: firmware-token

### `3005/71/00000011b` — RSE display resolution  ·  _med_

Selects the RSE panel resolution. Raw codes 1 and 2; default 2 per cur_desc (800x480 noted). Not active on this vehicle.

default `02`· gate: FA-gated (depends on vehicle options)· token `RSE_DISPLAY_RES`· source: firmware-token

### `3005/71/00001100b` — RSE display physical size  ·  _med_

Selects the RSE panel physical size variant. Raw codes 0-2 available; no symbolic names. Not active on this vehicle.

default `00`· gate: FA-gated (depends on vehicle options)· token `RSE_DISPLAY_SIZE`· source: firmware-token

### `3005/71/11110000b` — DISPLAY_PIP_CONFIG 4-bit field (byte 71 bits7-4)  ·  _low_

A 4-bit field within the DISPLAY_PIP_CONFIG coding page (byte 71, bits 7-4). Active on this vehicle. Exact field name not individually pinned in the firmware name table; likely one of the remaining DRIVING_MODE or PIP geometry parameters listed in the page description.

token `DISPLAY_PIP_CONFIG byte 71 (4-bit field (00..00))`· source: inferred

### `3005/72/11111111b` — ZIN permanent display content  ·  _high_

Selects what is permanently shown on the ZIN display when no other priority content is active. OFF = blank; DREHZAHL = rev counter; DRIVING_MODE = current driving mode; ALWAYS_OPEN = always show main view; colour options (BLUE/YELLOW etc.) select a coloured ambient display; JCW = John Cooper Works mode; PHEV = plug-in hybrid display. Not active (no ZIN) on this vehicle.

| value | meaning |
|---|---|
| `0` | Off (blank) |
| `1` | Rev counter (DREHZAHL) |
| `2` | Driving mode display |
| `3` | Always open |
| `4` | Blue ambient |
| `5` | Yellow ambient |
| `6` | Orange ambient |
| `7` | Pink ambient |
| `8` | Green ambient |
| `9` | Red ambient |
| `10` | JCW mode |
| `11` | PHEV display |

default `01`· gate: FA-gated (depends on vehicle options)· token `ZIN_PERMANENT_DISPLAY`· source: firmware-token

### `3005/73/00000001b` — ZIN heartbeat semi-permanent display  ·  _high_

Enables the 'heartbeat' status indicator as a semi-permanent overlay on the ZIN display (shown when no priority content is active). Not active on this vehicle.

| value | meaning |
|---|---|
| `0` | Inactive |
| `1` | Active |

default `01`· gate: FA-gated (depends on vehicle options)· token `ZIN_SEMI_PERMANENT_DISPLAYS_HEARTBEAT`· source: firmware-token

### `3005/73/00000010b` — ZIN MSA semi-permanent display  ·  _high_

Enables the MSA (Motor Stop/Start Automatic — auto start-stop status) indicator as a semi-permanent overlay on the ZIN display. Not active on this vehicle.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ZIN_SEMI_PERMANENT_DISPLAYS_MSA`· source: firmware-token

### `3005/73/00000100b` — ZIN navigation semi-permanent display  ·  _high_

Enables navigation turn-by-turn instructions as a semi-permanent overlay on the ZIN display. Not active on this vehicle.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ZIN_SEMI_PERMANENT_DISPLAYS_NAVI`· source: firmware-token

### `3005/73/00001000b` — ZIN PDC/PMA semi-permanent display  ·  _high_

Enables the PDC (Park Distance Control) or PMA (Park Manoeuvre Assist) sensor view as a semi-permanent overlay on the ZIN display during parking. Not active on this vehicle.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `01`· gate: FA-gated (depends on vehicle options)· token `ZIN_SEMI_PERMANENT_DISPLAYS_PDC_PMA`· source: firmware-token

### `3005/73/00010000b` — ZIN telephone semi-permanent display  ·  _high_

Enables telephone/call status as a semi-permanent overlay on the ZIN display. Not active on this vehicle.

| value | meaning |
|---|---|
| `0` | Inactive |
| `1` | Active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ZIN_SEMI_PERMANENT_DISPLAYS_TELEPHONE`· source: firmware-token

### `3005/73/00100000b` — ZIN USB/Bluetooth semi-permanent display  ·  _high_

Enables USB/Bluetooth media playback status as a semi-permanent overlay on the ZIN display. Not active on this vehicle.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ZIN_SEMI_PERMANENT_DISPLAYS_USB_BLUETOOTH`· source: firmware-token

### `3005/73/01000000b` — ZIN climate control semi-permanent display  ·  _high_

Enables climate control status (temperature, fan, etc.) as a semi-permanent overlay on the ZIN display. Not active on this vehicle.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `01`· gate: FA-gated (depends on vehicle options)· token `ZIN_SEMI_PERMANENT_DISPLAYS_CLIMATE`· source: firmware-token

### `3005/73/10000000b` — ZIN audio semi-permanent display  ·  _high_

Enables audio/entertainment status (track info, source) as a semi-permanent overlay on the ZIN display. Not active on this vehicle.

| value | meaning |
|---|---|
| `0` | Inactive |
| `1` | Active |

default `01`· gate: FA-gated (depends on vehicle options)· token `ZIN_SEMI_PERMANENT_DISPLAYS_AUDIO`· source: firmware-token

### `3005/74/00000001b` — ZIN SDE semi-permanent display  ·  _med_

Enables the SDE (Service Display / Sonderdisplay Einheit — special display unit) content as a semi-permanent overlay on the ZIN display. Not active on this vehicle.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `01`· gate: FA-gated (depends on vehicle options)· token `ZIN_SEMI_PERMANENT_DISPLAYS_SDE`· source: firmware-token

### `3005/74/00000010b` — ZIN iDrive 4 semi-permanent display  ·  _med_

Enables the iDrive 4 (ID4) menu/status as a semi-permanent overlay on the ZIN display. Not active on this vehicle.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `01`· gate: FA-gated (depends on vehicle options)· token `ZIN_SEMI_PERMANENT_DISPLAYS_ID4`· source: firmware-token

### `3005/74/11111100b` — DISPLAY_PIP_CONFIG 6-bit field (byte 74 bits7-2)  ·  _low_

A 6-bit field within the DISPLAY_PIP_CONFIG coding page (byte 74, bits 7-2). Active on this vehicle. Exact field name not individually pinned in the firmware name table; likely a reserved or PIP geometry field.

token `DISPLAY_PIP_CONFIG byte 74 (6-bit field (00..00))`· source: inferred

### `3005/75/00000001b` — Display dimming algorithm variant (DIM_VARIANT)  ·  _high_

Selects the active brightness control algorithm variant. NEW = modern algorithm; OLD = legacy algorithm. Default is OLD (0x01). Controls which dimming state machine path is used by the display manager.

| value | meaning |
|---|---|
| `0` | New algorithm |
| `1` | Old algorithm (default) |

default `01`· token `DIM_VARIANT`· source: firmware-token

### `3005/75/11111110b` — DISPLAY_PIP_CONFIG 7-bit enum (byte 75 bits7-1)  ·  _low_

A 7-bit enum field within the DISPLAY_PIP_CONFIG coding page (byte 75, bits 7-1), with 11 possible states (0x00 to 0x64 range). Not active on this vehicle. Exact field name not individually pinned in the firmware name table; likely a DRIVING_MODE colour-set selector given the page context.

default `0A`· gate: FA-gated (depends on vehicle options)· token `DISPLAY_PIP_CONFIG byte 75 (7-bit enum)`· source: inferred

### `3005/76/00000111b` — APIX cable length — CID  ·  _high_

Configures the APIX cable length compensation setting for the CID (Central Information Display) video link. Correct setting ensures signal integrity over the actual harness length. Not active on this vehicle.

| value | meaning |
|---|---|
| `0` | Short |
| `1` | Medium |
| `2` | Long |
| `3` | Extra long |
| `7` | Not available |

default `00`· gate: FA-gated (depends on vehicle options)· token `APIX_LENGTH_CID`· source: firmware-token

### `3005/76/00111000b` — APIX cable length — instrument cluster (KOMBI)  ·  _med_

Configures the APIX cable length compensation for the instrument cluster (KOMBI) display link. No symbolic enum names are defined for this field; raw codes 1, 3, 4 are the only documented values. Not active on this vehicle.

default `00`· gate: FA-gated (depends on vehicle options)· token `APIX_LENGTH_KOMBI`· source: firmware-token

### `3005/76/11000000b` — DISPLAY_PIP_CONFIG 2-bit field (byte 76 bits7-6)  ·  _low_

A 2-bit field within the DISPLAY_PIP_CONFIG coding page (byte 76, bits 7-6). Active on this vehicle. Exact field name not individually pinned in the firmware name table.

token `DISPLAY_PIP_CONFIG byte 76 (2-bit field (00..00))`· source: inferred

### `3005/77/00000111b` — APIX cable length — RSE FOMO left display  ·  _high_

Configures the APIX cable length compensation for the left rear-seat entertainment (RSE FOMO — Front Of Monitor Option, left) display link. Not active on this vehicle.

| value | meaning |
|---|---|
| `0` | Short |
| `1` | Medium |
| `2` | Long |
| `3` | Extra long |
| `7` | Not available |

default `07`· gate: FA-gated (depends on vehicle options)· token `APIX_LENGTH_RSE_FOMO_LEFT`· source: firmware-token

### `3005/77/00111000b` — APIX cable length — RSE FOMO right display  ·  _med_

Configures the APIX cable length compensation for the right rear-seat entertainment (RSE FOMO right) display link. Raw codes 1, 3, 4 available. Not active on this vehicle.

default `07`· gate: FA-gated (depends on vehicle options)· token `APIX_LENGTH_RSE_FOMO_RIGHT`· source: firmware-token

### `3005/77/11000000b` — DISPLAY_PIP_CONFIG 2-bit field (byte 77 bits7-6)  ·  _low_

A 2-bit field within the DISPLAY_PIP_CONFIG coding page (byte 77, bits 7-6). Active on this vehicle. Exact field name not individually pinned in the firmware name table.

token `DISPLAY_PIP_CONFIG byte 77 (2-bit field (00..00))`· source: inferred

### `3005/78/11111111b` — DISPLAY_PIP_CONFIG trailing multi-byte block (bytes 78-149)  ·  _low_

Remaining unresolved multi-byte block at the end of the DISPLAY_PIP_CONFIG coding page (bytes 78-149, 72 bytes). Active on this vehicle. Page context suggests this region contains additional DRIVING_MODE colour-set parameters or PIP geometry values not individually pinned in the firmware name table.

token `DISPLAY_PIP_CONFIG byte 78 (multi-byte value (syset Int/UInt8/16))`· source: inferred

## Datagroup 0x3006 (156 parameters)

### `3006/0/00000001b` — Navigation free-text search  ·  _high_

Enables free-text (keyword) destination search in the navigation system, allowing the driver to type arbitrary words rather than structured address fields. Active with navigation option 606 or 609.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 606 Navigation system Business / 609 Professional navigation system· token `NAVI_FREE_TEXT_SEARCH`· source: firmware-token

### `3006/0/00000010b` — Navigation new-start guidance  ·  _med_

Enables the revised/new-style route guidance start sequence introduced in the NBT Evo navigation stack (updated turn-by-turn guidance initiation flow). Requires Professional navigation (609).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 609 Professional navigation system· token `NAVI_NEW_START_GUIDANCE`· source: firmware-token

### `3006/0/00000100b` — US-style destination input  ·  _med_

Activates the US-market destination entry UI, which uses US-format address input (number before street name) rather than European format. Gated on US vehicle type-key.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93)· token `NAVI_DESTINATION_INPUT_US`· source: firmware-token

### `3006/0/00011000b` — Navigation fuel-consumption difference display mode  ·  _high_

Controls how the navigation system displays fuel consumption savings for eco-routes: no display, percentage difference, or absolute value difference.

| value | meaning |
|---|---|
| `0` | None (off) |
| `1` | Percentage (%) |
| `2` | Absolute value |

default `00`· gate: FA-gated (depends on vehicle options)· token `NAVI_CONSUMPTION_DIFF`· source: firmware-token

### `3006/0/00100000b` — Profile import/export feature  ·  _med_

Enables the profile/data import-export feature in the USB portation subsystem. Controls whether the head unit exposes import and export functions for user profile data via USB.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `SL03_IMPORT_EXPORT`· source: firmware-token

### `3006/0/01000000b` — Asia-market navigation POI  ·  _med_

Enables Asia-market-specific points-of-interest categories and features in the navigation system. Active with Professional navigation (609) or Japanese version (807).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 609 Professional navigation system / 807 Japanese version· token `SL17_ASIA_NAVI_POI`· source: firmware-token

### `3006/0/10000000b` — Asia-market navigation search  ·  _med_

Enables Asia-market-specific search features and input methods for navigation (e.g. character-based or phonetic search for Asian languages). Active with navigation options 606/609 or Japanese version.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 606 Navigation system Business / 609 Professional navigation system / 807 Japanese version· token `SL18_ASIA_SEARCH`· source: firmware-token

### `3006/1/00000001b` — Asia-market navigation settings  ·  _med_

Enables Asia-market-specific navigation settings menus and options (e.g. locale-specific preferences). Active with Professional navigation (609) or Japanese version (807).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 609 Professional navigation system / 807 Japanese version· token `SL19_ASIA_SETTINGS`· source: firmware-token

### `3006/1/00000010b` — Upcoming road map bitmap display  ·  _med_

Enables a bitmap graphical preview of the upcoming road or manoeuvre (FPK coming-road preview image).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `FPK_COMING_ROAD_BMP`· source: firmware-token

### `3006/1/00000100b` — Intelligent Transport System (ITS) support  ·  _med_

Enables ITS (Intelligent Transport System) integration in the navigation, which includes infrastructure-based traffic data exchange (V2X / roadside unit communications). Requires Professional navigation (609) or Japanese version.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: 609 Professional navigation system / 807 Japanese version· token `ITS`· source: firmware-token

### `3006/1/00001000b` — Show geographic coordinates  ·  _med_

Shows geographic coordinates (latitude and longitude) in navigation, for example for the current position or a chosen destination.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· token `NAVI_SHOW_GEOCORDINATES`· source: firmware-token

### `3006/1/00010000b` — Online check of contact addresses  ·  _med_

Uses an online service to check addresses from your phone contacts, so they can be used as navigation destinations. Enabled at the factory with Navigation Business or Professional (S606 or S609) and TeleServices (S6AE).

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 606 Navigation system Business / 609 Professional navigation system / 6AE TeleServices· token `CONTACT_ONLINE_ADDRESS_VALIDATION`· source: firmware-token

### `3006/1/00100000b` — Automatic map mode  ·  _low_

Setting for the navigation map's automatic mode, in which the map picks its display mode on its own. Best left unchanged.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: always (no FA gate)· token `NAVI_MAPMODE_AUTOMATIC`· source: firmware-token

### `3006/1/01000000b` — Qiblah (direction of Mecca)  ·  _med_

Offers the Qiblah display in navigation, which shows the direction of Mecca from the car's position.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· token `NAVI_MECCA_INDICATOR`· source: firmware-trace

### `3006/1/10000000b` — Full-screen alternative routes view  ·  _med_

Shows the alternative route suggestions on a full-screen map, so you can compare them more easily before choosing one.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `NAVI_ALTERNATIVE_ROUTES_FULLSCREEN`· source: firmware-token

### `3006/2/00000001b` — Traffic information on the map  ·  _low_

Shows traffic information, such as congestion and incidents, directly on the navigation map. Set at the factory by market and traffic services, such as Traffic Information (S6UH).

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: NOT 802 Korean version / 807 Japanese version / 810 Australian version / 838 Canadian version / 8AA Chinese version / 645 Radio control US / 825 Radio control Oceania / 6UH Traffic Information / 8LH Country control 04142 / 8LT Country control 04825  / 6AE TeleServices· token `NAVI_TRAFFIC_INFO_MAP`· source: firmware-token

### `3006/2/00000010b` — A to Z search for points of interest  ·  _med_

Lets you search points of interest by name in an alphabetical list, in addition to browsing them by category.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· token `POI_AZ_SEARCH`· source: firmware-token

### `3006/2/00000100b` — Enhanced FM VICS traffic info (Japan)  ·  _med_

Turns on the enhanced FM radio service of Japan's Vehicle Information and Communication System (VICS) for traffic information. Enabled at the factory for the Japanese version (S807) with Navigation Professional (S609).

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 609 Professional navigation system / 807 Japanese version· token `TI_FMVICS_ENHANCEMENT`· source: firmware-token

### `3006/2/00001000b` — ADAS 2D heading — do not expand one-way streets  ·  _med_

Controls ADAS (Advanced Driver Assistance Systems) horizon data output: when enabled, the system does not expand one-way street segments in 2D heading mode, preventing incorrect lane-level data being sent to ADAS consumers.

| value | meaning |
|---|---|
| `0` | Off (expand one-way streets) |
| `1` | On (do not expand) |

default `00`· gate: always (no FA gate)· token `ADAS_2DH_NOT_EXPAND_ONEWAY`· source: firmware-token

### `3006/2/00010000b` — Map scroll light-beam effect  ·  _med_

Enables a visual light-beam/sweep animation effect when scrolling the navigation map, providing smooth map panning feedback.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `NAVI_MAPSCROLL_LIGHTBEAM`· source: firmware-token

### `3006/2/00100000b` — Refueling stop suggestions  ·  _low_

Lets navigation propose a refueling stop at a fuel station along or near your route.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· token `NAVI_FUELSTOP_PROPOSAL`· source: firmware-token

### `3006/2/01000000b` — Arrow/schematic map view (Pfeilansicht)  ·  _med_

Enables the simplified arrow/schematic navigation view as an alternative to the full 2D/3D map view. This stripped-down view shows only directional arrows. Excluded on Business (606) and Professional (609) navigation systems and Asian market variants.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: NOT 606 Navigation system Business / 609 Professional navigation system / 802 Korean version / 807 Japanese version / 8AA Chinese version / 8LH Country control 04142 / 8LT Country control 04825 · token `NAVI_PFEILANSICHT`· source: firmware-token

### `3006/2/10000000b` — Intersection zoom  ·  _high_

Shows an enlarged view of complex intersections and highway junctions as you approach them during route guidance. Enabled at the factory with Navigation Professional (S609).

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 609 Professional navigation system· token `NAVI_KREUZUNGSZOOM`· source: firmware-token

### `3006/3/00000001b` — Trip import  ·  _low_

Lets you import trips, with their destinations and stops, into navigation, for example from a USB device, and then start route guidance with them.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: NOT 609 Professional navigation system / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93)· token `NAVI_TRIP_IMPORT`· source: firmware-token

### `3006/3/00000010b` — Trip export  ·  _low_

Lets you export saved navigation trips, with their destinations and stops, from the head unit, for example to a USB device. Enabled at the factory with Navigation Professional (S609) and in the Asian-market versions.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 609 Professional navigation system / 802 Korean version / 807 Japanese version / 8AA Chinese version / 8LH Country control 04142 / 8LT Country control 04825 · token `NAVI_TRIP_EXPORT`· source: firmware-token

### `3006/3/00000100b` — Destination import  ·  _low_

Lets you import navigation destinations into the head unit, for example from a USB device, so you don't have to enter them by hand. Enabled at the factory with Navigation Business or Professional (S606 or S609) and in the Asian-market versions.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 606 Navigation system Business / 609 Professional navigation system / 802 Korean version / 807 Japanese version / 8AA Chinese version / 8LH Country control 04142 / 8LT Country control 04825 · token `NAVI_DEST_IMPORT`· source: firmware-token

### `3006/3/00001000b` — Destination export  ·  _low_

Lets you export saved navigation destinations from the head unit, for example to a USB device, to keep a copy or use them in another car. Enabled at the factory with Navigation Business or Professional (S606 or S609) and in the Asian-market versions.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 606 Navigation system Business / 609 Professional navigation system / 802 Korean version / 807 Japanese version / 8AA Chinese version / 8LH Country control 04142 / 8LT Country control 04825 · token `NAVI_DEST_EXPORT`· source: firmware-token

### `3006/3/00010000b` — My Points of Interest: import  ·  _med_

Lets you import your own points of interest (My Points of Interest) into navigation, for example from a USB device, so they appear on the map and in search.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: NOT 609 Professional navigation system / 802 Korean version / 807 Japanese version / 8AA Chinese version / 8LH Country control 04142 / 8LT Country control 04825 · token `NAVI_MYPOI_IMPORT`· source: firmware-token

### `3006/3/00100000b` — My Points of Interest: export  ·  _low_

Lets you export your own points of interest (My Points of Interest) from navigation, for example to a USB device, to keep a copy or move them to another car.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `NAVI_MYPOI_EXPORT`· source: firmware-token

### `3006/3/01000000b` — Route recording  ·  _low_

Lets navigation record the route you actually drive, so you can save it and use it again later.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: NOT 609 Professional navigation system / 802 Korean version / 807 Japanese version / 8AA Chinese version / 8LH Country control 04142 / 8LT Country control 04825 · token `NAVI_ROUTE_RECORD`· source: firmware-token

### `3006/3/10000000b` — Arrow display in map views  ·  _low_

Offers the arrow display among the navigation map views: a simplified view that shows the next maneuver as a large arrow. Set at the factory according to the navigation, such as Navigation Business (S606), and the market. See also “Arrow display guidance” (`3006/2/01000000b`).

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: NOT 606 Navigation system Business / 802 Korean version / 807 Japanese version / 8AA Chinese version / 8LH Country control 04142 / 8LT Country control 04825 · token `NAVI_MAP_ARROWVIEW`· source: firmware-trace

### `3006/4/00000001b` — Route option: electronic toll roads  ·  _med_

Adds roads that collect tolls only electronically to the route options, so route calculation can avoid them when you have no toll tag.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93)· token `NAVI_ELECTRONIC_TOLL_COLLECTION_ROADS`· source: firmware-token

### `3006/4/00000010b` — Full guidance pop-up  ·  _low_

Shows the route guidance instruction for the next maneuver as a full pop-up on the central display. Set at the factory according to Navigation Business (S606) and the instrument cluster with extended features (S6WA).

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: NOT 606 Navigation system Business / 6WA KOMBI with extended equipment specification· token `NAVI_FULL_GUIDINGPOPUP`· source: firmware-token

### `3006/4/00000100b` — Route study  ·  _low_

Navigation setting for the route study feature. Best left unchanged.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 609 Professional navigation system / 802 Korean version / 807 Japanese version / 8AA Chinese version / 8LH Country control 04142 / 8LT Country control 04825  / ECSM Deletion of Car Sharing Module / 5GC Preparation of Flexible Car Use· token `NAVI_ROUTE_STUDY`· source: firmware-token

### `3006/4/00001000b` — Speed limit info on navigation display (SLI)  ·  _med_

Enables the Speed Limit Information (SLI) display on the navigation screen, showing the current road speed limit retrieved from the navigation map data.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· token `SLI_NAVI_DISPLAY`· source: firmware-token

### `3006/4/00010000b` — Incremental map updates  ·  _low_

Lets the navigation map be updated in parts rather than replaced as a whole. Best left unchanged.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `INCREMENTAL_UPDATE`· source: firmware-token

### `3006/4/00100000b` — Eco route info text  ·  _low_

Shows an information text about the eco route in navigation.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: NOT vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `ECO_ROUTE_TEXT`· source: firmware-token

### `3006/4/01000000b` — M Laptimer  ·  _low_

Navigation setting for the M Laptimer, which records lap times and driving data. Best left unchanged.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `M_LAPTIMER`· source: firmware-token

### `3006/4/10000000b` — Save trip to memory  ·  _high_

Enables the ability to save a completed navigation trip to internal memory for later retrieval or repeat navigation. Requires Professional navigation (609).

| value | meaning |
|---|---|
| `1` | On |

default `00`· gate: 609 Professional navigation system· token `NAVI_SAVE_TRIP`· source: firmware-token

### `3006/5/00000001b` — Route option: avoid vignette roads  ·  _high_

Adds “Avoid vignette roads” to the route options, so route guidance can stay off roads that need a vignette, the prepaid toll sticker some countries require on highways. Enabled at the factory with Navigation Business or Professional (S606 or S609) on some models.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 606 Navigation system Business / 609 Professional navigation system / vehicle type-key attribute group (FP category 17; 232 type tokens, e.g. 11CK,11CL,11DE,12CK)· token `AVOID_VIGNETTE`· source: firmware-trace

### `3006/5/00000010b` — Map scrolling in 3D view  ·  _low_

Lets you move the navigation map around with the controller while it's shown in the 3D perspective view.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: NOT 609 Professional navigation system / 802 Korean version / 807 Japanese version / 8AA Chinese version / 8LH Country control 04142 / 8LT Country control 04825 · token `MAP_SCROLL_3D`· source: firmware-token

### `3006/5/00000100b` — Ambiguous destination entry  ·  _low_

Setting for how destination entry handles ambiguous input, such as a place name that matches several locations. Best left unchanged.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: NOT 802 Korean version / 807 Japanese version / 8AA Chinese version / 8LH Country control 04142 / 8LT Country control 04825 · token `ZIELEINGABE_MEHRDEUTIG`· source: firmware-token

### `3006/5/00001000b` — POI online search mode (Japan)  ·  _high_

Controls whether the navigation system's online POI search for Japan uses the integrated browser or a native (built-in) search UI. Japan-specific; uses the configured online POI service.

| value | meaning |
|---|---|
| `0` | Browser (web-based POI search) |
| `1` | Native (built-in POI search UI) |

default `00`· gate: 807 Japanese version· token `NAVI_POI_ONLINE_SEARCH`· source: firmware-token

### `3006/5/00010000b` — ADAS lane position output  ·  _med_

Enables output of the vehicle's estimated lane position data from the ADAS/ADASIS horizon to lane-departure or driver-assistance consumers.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `ADAS_OUTPUT_LANE_POS`· source: firmware-token

### `3006/5/00100000b` — Express/highway-specific road category  ·  _med_

Enables the express road (limited-access highway / express route) road category in navigation routing and avoidance preferences. Gated on specific vehicle type-key (US market).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93)· token `NAVI_EXPRESS_ROADS`· source: firmware-token

### `3006/5/01000000b` — Route option: avoid carpool roads  ·  _med_

Adds “Avoid carpool roads” to the route options, so route guidance can stay off roads reserved for vehicles with several occupants.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93)· token `NAVI_CARPOOL_ROADS`· source: firmware-trace

### `3006/5/10000000b` — Augmented-reality navigation view  ·  _low_

Shows navigation directions over a live camera image of the road ahead. Enable it only when the car's camera and navigation support it.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `NAVI_AUGMENTED_REALITY`· source: firmware-token

### `3006/6/00000001b` — Brand dealers as points of interest  ·  _med_

Includes dealers of the car's brand, such as BMW or MINI dealers, as a point-of-interest category, so you can find one and start route guidance to it.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `01`· gate: always (no FA gate)· token `POI_BRAND_DEALERS`· source: firmware-token

### `3006/6/00000010b` — Auto zoom map view  ·  _med_

Offers the auto zoom map view, which changes the map scale on its own during route guidance. See also “Automatic map zoom” (`3006/9/01000000b`). Enabled at the factory except in the Asian-market versions.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: NOT 802 Korean version / 807 Japanese version / 8AA Chinese version / 8LH Country control 04142 / 8LT Country control 04825 · token `NAVI_AUTOZOOM`· source: firmware-trace

### `3006/6/00000100b` — Scrolling along planned route  ·  _high_

Enables the navigation map to automatically scroll/advance along the planned route ahead of the vehicle, previewing upcoming road segments. Active on Asian/Korean market variants.

| value | meaning |
|---|---|
| `1` | On |

default `00`· gate: 802 Korean version / 807 Japanese version / 8AA Chinese version / 8LH Country control 04142 / 8LT Country control 04825 · token `NAVI_SCROLLING_ALONG_ROUTE`· source: firmware-token

### `3006/6/00001000b` — Route magnet  ·  _med_

Offers the route magnet in navigation, which lets you pull the planned route in any direction so it runs through an area you choose. Enabled at the factory with Navigation Business or Professional (S606 or S609) and in the Asian-market versions.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 606 Navigation system Business / 609 Professional navigation system / 802 Korean version / 807 Japanese version / 8AA Chinese version / 8LH Country control 04142 / 8LT Country control 04825 · token `NAVI_ROUTENMAGNET`· source: firmware-trace

### `3006/6/00110000b` — Undocumented field (PortationMaster byte 6, bits 5-4)  ·  _low_

Purpose not determined from available sources. 2-bit field in the PortationMaster / Produktlinie coding page; consumed by an on-device process not tested in the HU engine binary.

token `PortationMaster coding page byte 6 (2-bit field (00..00))`· source: inferred

### `3006/6/01000000b` — Point-of-interest alerts  ·  _low_

Lets navigation alert you as you approach certain points of interest.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `NAVI_ALERT_POI`· source: firmware-token

### `3006/6/10000000b` — Avoid areas  ·  _med_

Lets you mark areas on the map for route calculation to avoid, such as a district you would rather not drive through. Enabled at the factory with Navigation Professional (S609) and in the Asian-market versions.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 609 Professional navigation system / 802 Korean version / 807 Japanese version / 8AA Chinese version / 8LH Country control 04142 / 8LT Country control 04825 · token `NAVI_AVOID_AREA`· source: firmware-token

### `3006/7/00000001b` — Online route optimization button  ·  _low_

Shows a button in navigation that has the route optimized by an online service. Enabled at the factory with Navigation Professional (S609).

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 609 Professional navigation system· token `NAVI_ONLINE_OPTIMIZATION_BUTTON`· source: firmware-token

### `3006/7/00000010b` — Range map  ·  _med_

Shows a range map in navigation that marks the area you can reach with the remaining charge or fuel.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `NAVI_REICHWEITENKARTE`· source: firmware-token

### `3006/7/00000100b` — Route export  ·  _low_

Lets you export a planned navigation route from the head unit, for example to a USB device, so you can keep it or use it again later.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· token `NAVI_ROUTE_EXPORT`· source: firmware-token

### `3006/7/00011000b` — Undocumented field (PortationMaster byte 7, bits 4-3)  ·  _low_

Purpose not determined from available sources. 2-bit field in the PortationMaster / Produktlinie coding page; consumed by an on-device process not tested in the HU engine binary.

token `PortationMaster coding page byte 7 (2-bit field (00..00))`· source: inferred

### `3006/7/00100000b` — Coordinate entry for destinations  ·  _high_

Lets you enter a navigation destination as geographic coordinates (latitude and longitude) instead of an address.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: NOT 606 Navigation system Business / 609 Professional navigation system / 802 Korean version / 807 Japanese version / 8AA Chinese version / 8LH Country control 04142 / 8LT Country control 04825 · token `NAVI_GEO_COORDINATE_INPUT`· source: firmware-token

### `3006/7/01000000b` — Built-in gyro sensor  ·  _med_

Tells navigation that the head unit has its own gyro sensor, which keeps the position accurate through turns and where GPS reception is weak, such as in tunnels. Enable it only when the head unit has one.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: GYIN Gyroscope / inertial sensor present (HO-word)· token `GYRO_INTERN`· source: firmware-token

### `3006/7/10000000b` — ETC (Electronic Toll Collection) transponder fitted (Japan)  ·  _high_

Indicates that a Japanese ETC toll transponder (in-vehicle unit) is fitted, enabling the navigation system to display ETC-lane guidance and communicate with the transponder. Japan-specific; requires Professional navigation (609) or Japanese version (807) and Japan ETC mirror option (449).

| value | meaning |
|---|---|
| `0` | Not fitted |
| `1` | Fitted |

default `00`· gate: 609 Professional navigation system / 807 Japanese version / 449 Toll interior mirror for Japan· token `ETC`· source: firmware-token

### `3006/8/11111111b` — Navigation road name text on main map (RNC)  ·  _high_

Controls display of road name text rendered directly on the main navigation map (RNC = Raster Navigation Content). Off = no overlay; Permanent = always show road names.

| value | meaning |
|---|---|
| `0` | Off (no road name text) |
| `255` | Permanent (always show) |

default `00`· gate: FA-gated (depends on vehicle options)· token `NAVI_RNC_MAINMAP_TEXT`· source: firmware-token

### `3006/9/00001111b` — Navigation map variant / regional edition  ·  _high_

Selects the regional navigation map edition and feature set. Determines which geographic map data set and market-specific navigation features are activated.

| value | meaning |
|---|---|
| `0` | No navigation |
| `1` | ECE (Europe) |
| `2` | US |
| `3` | Japan |
| `4` | China |
| `5` | Korea |
| `6` | Hong Kong |
| `7` | Taiwan |

default `00`· gate: 606 Navigation system Business / 609 Professional navigation system / 8AA Chinese version· token `NAVI_VARIANTE`· source: firmware-token

### `3006/9/00010000b` — Traffic categories filter  ·  _med_

Enables user-selectable traffic event category filters in the navigation traffic display, allowing the driver to show/hide specific traffic event types.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `TRAFFIC_CATEGORIES`· source: firmware-token

### `3006/9/00100000b` — Undocumented field (PortationMaster byte 9, bit 5)  ·  _low_

Purpose not determined from available sources. Boolean flag in the PortationMaster / Produktlinie coding page; consumed by an on-device process not tested in the HU engine binary.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

token `PortationMaster coding page byte 9 (boolean flag (Bool)`· source: inferred

### `3006/9/01000000b` — Automatic map zoom  ·  _low_

Lets the navigation map change its scale on its own while you drive. See also “Auto zoom map view” (`3006/6/00000010b`).

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: always (no FA gate)· token `AUTO_MAP_ZOOM`· source: firmware-token

### `3006/9/10000000b` — Time-dependent routing  ·  _high_

Enables time-dependent (historical traffic pattern) routing, where the navigation system uses historical speed/flow data for the time of day and day of week to calculate faster routes.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `TIME_DEPENDING_ROUTING`· source: firmware-token

### `3006/10/00000001b` — Encrypted TMC: France (Mediamobile)  ·  _med_

Lets navigation decode the encrypted TMC traffic service from Mediamobile in France, broadcast over FM radio, for more detailed traffic information there.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· token `TI_CA_TMC_FRANCE_MEDIAMOBILE`· source: firmware-token

### `3006/10/00000010b` — Traffic CA / TMC UK (ITIS)  ·  _high_

Enables the ITIS conditional-access TMC provider for the UK, used to decode the UK encrypted FM-TMC traffic data broadcasts.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· token `TI_CA_TMC_UK_ITIS`· source: firmware-token

### `3006/10/00000100b` — Street names in voice guidance  ·  _med_

Has the voice guidance say street names along with the turn instructions, for example “Turn right onto Main Street”.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: always (no FA gate)· token `STREET_NAME_VOICE_GUIDING`· source: firmware-token

### `3006/10/00001000b` — Last destination  ·  _low_

Lets navigation offer your last destination for quick reuse, so you can restart route guidance to it without entering it again.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `LAST_DESTINATION`· source: firmware-token

### `3006/10/11110000b` — Range map maximum scale  ·  _med_

Sets the maximum map scale level (zoom-out limit) for the range/reachability map (Reichweitenkarte) display. Numeric value 0-5 where higher = more zoomed out.

default `00`· gate: FA-gated (depends on vehicle options)· token `REICHWEITENKARTE_SCALE_MAX`· source: firmware-token

### `3006/11/11111111b` — Undocumented field (PortationMaster bytes 11-16)  ·  _low_

Purpose not determined from available sources. Multi-byte value spanning bytes 11-16 in the PortationMaster / Produktlinie coding page; consumed by an on-device process not tested in the HU engine binary.

token `PortationMaster coding page byte 11 (multi-byte value (syset Int/UInt8/16))`· source: inferred

### `3006/17/00000111b` — Undocumented field (PortationMaster byte 17, bits 2-0)  ·  _low_

Purpose not determined from available sources. 3-bit field in the PortationMaster / Produktlinie coding page; consumed by an on-device process not tested in the HU engine binary.

token `PortationMaster coding page byte 17 (3-bit field (00..00))`· source: inferred

### `3006/17/00001000b` — Guided tours  ·  _low_

Makes guided tours available in navigation: prepared routes with several stops that you can pick and then follow with route guidance.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `GUIDED_TOURS`· source: firmware-token

### `3006/17/00010000b` — Details for points of interest  ·  _med_

Shows a details page for points of interest, with information such as the address and phone number where the map data includes it.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: always (no FA gate)· token `POI_DETAILS`· source: firmware-token

### `3006/17/00100000b` — IPD data handling  ·  _low_

Setting for how navigation handles IPD areas on a route, including guidance when entering and leaving them. Best left unchanged.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `IPD_BEHANDLUNG`· source: firmware-trace

### `3006/17/01000000b` — Guided tours route ID  ·  _med_

Enables the route ID subsystem for the guided tours feature, associating tours with unique identifiers for tracking and management.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `ROUTEN_ID_GUIDEDTOURS`· source: firmware-token

### `3006/17/10000000b` — Portation/product-line flag (byte 17 bit 7)  ·  _low_

Unnamed boolean flag in the PortationMaster/Produktlinie coding page (dg 3006). Consumed by an on-device process other than the main HU engine (CPortationMasterDataManager); exact function not determined from available sources.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

token `PortationMaster coding page byte 17 (boolean flag (Bool)`· source: inferred

### `3006/18/00000001b` — Alternative routes  ·  _med_

Enables the navigation system's alternative-routes feature, allowing the driver to view and select alternative route proposals during guidance.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `ALTERNATIV_ROUTEN`· source: firmware-token

### `3006/18/00001110b` — Distance unit system  ·  _med_

Selects the measurement unit used for distance and navigation guidance — kilometres, miles/yards, or miles/feet — depending on market region.

| value | meaning |
|---|---|
| `1` | Miles and yards |
| `2` | Miles and feet |
| `3` | Kilometres only |

default `01`· gate: 802 Korean version / 807 Japanese version / 8AA Chinese version / 8LH Country control 04142 / 8LT Country control 04825 · token `EINHEITEN_WEGSTRECKE`· source: firmware-token

### `3006/18/00010000b` — Portation/product-line flag (byte 18 bit 4)  ·  _low_

Unnamed boolean flag in the PortationMaster/Produktlinie coding page (dg 3006). Consumed by an on-device process other than the main HU engine; exact function not determined from available sources.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

token `PortationMaster coding page byte 18 (boolean flag (Bool)`· source: inferred

### `3006/18/00100000b` — Rotate/cycle measurement units  ·  _med_

When enabled, allows the system to rotate or cycle through available measurement-unit choices for displayed values. Inactive on this vehicle.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `ROTATION_WERTE_EINHEITEN`· source: firmware-token

### `3006/18/11000000b` — Portation/product-line field (byte 18 bits 7,6)  ·  _low_

Unnamed 2-bit field in the PortationMaster/Produktlinie coding page (dg 3006). Consumed by an on-device process other than the main HU engine; exact function not determined from available sources.

token `PortationMaster coding page byte 18 (2-bit field (00..00))`· source: inferred

### `3006/19/11111111b` — Portation/product-line value (bytes 19-21)  ·  _low_

Unnamed multi-byte (3-byte) integer value in the PortationMaster/Produktlinie coding page. Consumed by an on-device process other than the main HU engine; exact function not determined from available sources.

token `PortationMaster coding page byte 19 (multi-byte value (syset Int/UInt8/16))`· source: inferred

### `3006/22/11111111b` — Vehicle fuel type  ·  _high_

Specifies the vehicle's fuel type for navigation purposes, primarily used to filter and display relevant POIs (e.g. petrol stations, charging stations) on the map.

| value | meaning |
|---|---|
| `1` | Petrol (gasoline) |
| `2` | Diesel |
| `3` | All fuel types |
| `4` | Diesel and AdBlue (urea) |
| `5` | Electric |
| `6` | Petrol, diesel, and electric (hybrid) |
| `8` | Liquid hydrogen (LH2) |

default `03`· token `TYPE_OF_FUEL`· source: firmware-token

### `3006/23/11111111b` — Portation/product-line value (byte 23)  ·  _low_

Unnamed single-byte integer value in the PortationMaster/Produktlinie coding page. Consumed by an on-device process other than the main HU engine; exact function not determined from available sources.

token `PortationMaster coding page byte 23 (multi-byte value (syset Int/UInt8/16))`· source: inferred

### `3006/24/11111111b` — Full-screen map auto-exit timer  ·  _med_

Timeout in seconds before the full-screen map view automatically exits and returns to the split-screen or normal view. A value of 0xFF (255) keeps the full-screen map permanently active.

| value | meaning |
|---|---|
| `255` | Permanent (no auto-exit) |

default `00`· gate: FA-gated (depends on vehicle options)· token `TIMER_VOLLBILDKARTE`· source: firmware-token

### `3006/25/11111111b` — Speed lock: navigation lower threshold  ·  _low_

Sets the lower speed threshold for the navigation speed lock, which restricts some navigation inputs while the car is moving. It works together with the upper threshold. Rules on driver distraction vary by country.

| value | meaning |
|---|---|
| `0` | Disabled |
| `3` | 3 km/h |
| `8` | 8 km/h |

default `03`· token `SPEEDLOCK_X_KMH_MIN`· source: firmware-token

### `3006/26/11111111b` — Speed lock: navigation upper threshold  ·  _low_

Sets the upper speed threshold for the navigation speed lock, which restricts some navigation inputs while the car is moving. It works together with the lower threshold. Set at the factory for the Korean, Japanese and Chinese versions (S802, S807 or S8AA). Rules on driver distraction vary by country.

| value | meaning |
|---|---|
| `0` | Disabled |
| `3` | 3 km/h |
| `10` | 10 km/h |

default `03`· gate: 802 Korean version / 807 Japanese version / 8AA Chinese version· token `SPEEDLOCK_X_KMH_MAX`· source: firmware-token

### `3006/27/11111111b` — Portation/product-line value (byte 27)  ·  _low_

Unnamed single-byte integer value in the PortationMaster/Produktlinie coding page. Consumed by an on-device process other than the main HU engine; exact function not determined from available sources.

token `PortationMaster coding page byte 27 (multi-byte value (syset Int/UInt8/16))`· source: inferred

### `3006/28/00001111b` — Portation/product-line field (byte 28 bits 3-0)  ·  _low_

Unnamed 4-bit field in the PortationMaster/Produktlinie coding page. Consumed by an on-device process other than the main HU engine; exact function not determined from available sources.

token `PortationMaster coding page byte 28 (4-bit field (00..00))`· source: inferred

### `3006/28/00010000b` — GPS receiver present  ·  _med_

Indicates whether an integrated GPS receiver is fitted in the system. Enables GPS-based positioning for navigation.

| value | meaning |
|---|---|
| `0` | Not fitted |
| `1` | Fitted |

default `00`· token `SYSTEM_GPS_RECEIVER`· source: firmware-token

### `3006/28/00100000b` — Service menu enable  ·  _med_

Enables the hidden service/diagnostic menu accessible within the head-unit UI, providing additional diagnostic and calibration options.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: always (no FA gate)· token `SERVICE_MENUE`· source: firmware-token

### `3006/28/01000000b` — Developer menu enable  ·  _med_

Enables the developer/engineering menu in the head-unit UI, providing advanced diagnostic and development options. Gated by NBT-Evo Head-unit variant FA options.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: HUEN Head-unit variant: NBT-Evo Entry/High present (HO-word) / HUDM Head-unit display-manager variant word (HO-word)· token `ENTWICKLER_MENUE`· source: firmware-token

### `3006/28/10000000b` — Developer menu enable (Asia variant)  ·  _med_

Enables an Asia-market-specific variant of the developer/engineering menu. Inactive on non-Asian market vehicles.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENTWICKLER_MENUE_ASIEN`· source: firmware-token

### `3006/29/00000001b` — ECO PRO route (Asian-market navigation)  ·  _med_

Offers the ECO PRO route type, which favors fuel-saving roads, in the navigation used for Asian markets. Enabled at the factory for the Asian-market versions.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 802 Korean version / 807 Japanese version / 8AA Chinese version / 8LH Country control 04142 / 8LT Country control 04825 · token `ECO_PRO_ROUTE_ALPINE`· source: firmware-trace

### `3006/29/00000010b` — Map colour scheme selection  ·  _med_

Enables user-selectable colour schemes (day/night/auto themes) for the map viewer display.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: always (no FA gate)· token `MAPVIEWER_FARBSET_AUSWAHL`· source: firmware-token

### `3006/29/00111100b` — Display size and resolution  ·  _med_

Specifies the physical display size and pixel resolution used by the system for rendering. Value 2 is the default (6.5-inch main NBT display); values 4 and 5 are rear-seat entertainment (RSE) screen sizes.

| value | meaning |
|---|---|
| `2` | 6.5-inch display, 800x480 (main NBT display) |
| `4` | 9.2-inch RSE display, 800x480 |
| `5` | 10-inch RSE display, 1280x720 |

default `02`· token `DISPLAY_SIZE_RESOLUTION`· source: firmware-token

### `3006/29/01000000b` — Portation/product-line flag (byte 29 bit 6)  ·  _low_

Unnamed boolean flag in the PortationMaster/Produktlinie coding page (dg 3006). Consumed by an on-device process other than the main HU engine; exact function not determined from available sources.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

token `PortationMaster coding page byte 29 (boolean flag (Bool)`· source: inferred

### `3006/29/10000000b` — Favourite POI  ·  _med_

Enables the Favourite POI feature in navigation, allowing users to mark and quickly access preferred points of interest. Gated by Business or Professional navigation system FA options.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 606 Navigation system Business / 609 Professional navigation system· token `FAVORED_POI`· source: firmware-token

### `3006/30/00000011b` — Vehicle type for POI filter  ·  _high_

Selects which type of refuelling/recharging infrastructure the POI (points of interest) system prioritises based on the vehicle's powertrain type.

| value | meaning |
|---|---|
| `0` | Charging stations (EV) |
| `1` | Petrol and diesel stations |
| `2` | Petrol, diesel, and charging stations |

default `00`· gate: always (no FA gate)· token `CAR_TYPE_POI`· source: firmware-token

### `3006/30/00000100b` — Adaptive destination prediction  ·  _med_

Enables the adaptive destination feature, which learns the driver's frequent destinations and proactively suggests navigation targets based on driving patterns.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: always (no FA gate)· token `ADAPTIV_DESTINATION`· source: firmware-token

### `3006/30/00001000b` — Adaptive map content  ·  _med_

Enables adaptive map display, where map content (zoom level, shown detail, overlays) adjusts automatically based on driving context and learned behaviour.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: always (no FA gate)· token `ADAPTIV_MAP`· source: firmware-token

### `3006/30/00010000b` — Traffic information dynamic routing  ·  _med_

Enables dynamic re-routing based on real-time traffic information, allowing the navigation system to automatically calculate alternative routes around congestion.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: always (no FA gate)· token `TI_DYNAMIC_ROUTING`· source: firmware-token

### `3006/30/00100000b` — Manoeuvre list  ·  _med_

Enables the turn-by-turn manoeuvre list view in navigation, showing a scrollable list of upcoming guidance steps. Gated by Business navigation or Chinese-market FA.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 606 Navigation system Business / 8AA Chinese version· token `MANEUVER_LIST`· source: firmware-token

### `3006/30/01000000b` — Range estimate correction  ·  _low_

Setting for how the range assistant corrects its range estimate. Best left unchanged.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `RANGE_CORRECTION_KI`· source: firmware-trace

### `3006/30/10000000b` — Recent charging stations history  ·  _med_

Enables display of recently visited charging stations as a quick-access list in navigation POI search, aiding EV drivers in finding familiar charging locations. Inactive on this vehicle.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `LETZTE_LADESTATIONEN`· source: firmware-token

### `3006/31/00000001b` — ADAS 2D road horizon data  ·  _med_

Enables the 2D road horizon interface for ADAS (Advanced Driver Assistance Systems), providing the navigation map's road geometry data to ADAS functions for predictive control (e.g. predictive speed control on curves).

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· token `ADAS_2D_HORIZON`· source: firmware-token

### `3006/31/00000010b` — ADAS 1D road horizon data  ·  _med_

Enables the 1D (linear) road horizon interface for ADAS, providing simplified ahead-road curvature and slope data to driver assistance systems.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· token `ADAS_1D_HORIZON`· source: firmware-token

### `3006/31/00000100b` — ADAS GPS position output  ·  _med_

Enables transmission of the GPS position data to ADAS functions, allowing predictive driver-assistance systems to use the navigation system's position fix.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· token `ADAS_GPS`· source: firmware-token

### `3006/31/00001000b` — ADAS system information output  ·  _med_

Enables the ADAS system-information channel, through which the navigation system reports status and diagnostic information to ADAS modules.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· token `ADAS_SYS_INF`· source: firmware-token

### `3006/31/00010000b` — ADAS current road segment data  ·  _med_

Enables output of the current road-segment data (road class, speed limit, geometry) from navigation to ADAS systems for predictive control.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· token `ADAS_CUR_SEG`· source: firmware-token

### `3006/31/00100000b` — IAK capture mode  ·  _low_

Setting for the navigation map's IAK capture mode, used when picking places on the map. Best left unchanged.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `IAK_FANGMODUS`· source: firmware-trace

### `3006/31/01000000b` — EV range assistant  ·  _med_

Enables the Range Assistant feature for electric vehicles, providing guidance on whether the destination is reachable on current battery charge and suggesting charging stops if needed. Inactive on this vehicle.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `RANGE_ASSISTANT`· source: firmware-token

### `3006/31/10000000b` — Return journey planning  ·  _med_

Enables the Return Journey feature in navigation, allowing the driver to easily plan a route back to a previously set home or departure point. Inactive on this vehicle.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `RETURN_JOURNEY`· source: firmware-token

### `3006/32/11111111b` — Portation/product-line value (byte 32)  ·  _low_

Unnamed single-byte integer value in the PortationMaster/Produktlinie coding page. Consumed by an on-device process other than the main HU engine; exact function not determined from available sources.

token `PortationMaster coding page byte 32 (multi-byte value (syset Int/UInt8/16))`· source: inferred

### `3006/33/00000001b` — ADAS 1D horizon PHEV extension  ·  _med_

Enables an extended 1D road horizon data set for plug-in hybrid electric vehicles (PHEV), providing additional look-ahead data to optimise electric/combustion mode switching. Inactive on this vehicle.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ADAS_1DH_PHEV_EXT`· source: firmware-token

### `3006/33/00000010b` — Route flight view  ·  _med_

Offers the route flight, an animated view that flies along the planned route on the navigation map.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: NOT 609 Professional navigation system / 802 Korean version / 807 Japanese version / 8AA Chinese version / 8LH Country control 04142 / 8LT Country control 04825 · token `ROUTE_FLIGHT`· source: firmware-trace

### `3006/33/00001100b` — EV charging configuration  ·  _high_

Specifies the electric vehicle charging hardware type, used by navigation to filter and display compatible charging station POIs. Inactive on this vehicle (no EV drivetrain).

| value | meaning |
|---|---|
| `1` | AC 3.7 kW (slow/standard AC charging) |
| `2` | AC 7.4 kW (fast AC charging) |
| `3` | DC (rapid/fast DC charging) |

default `00`· gate: FA-gated (depends on vehicle options)· token `EV_CONFIG`· source: firmware-token

### `3006/33/11110000b` — Portation/product-line field (byte 33 bits 7-4)  ·  _low_

Unnamed 4-bit field in the PortationMaster/Produktlinie coding page. Consumed by an on-device process other than the main HU engine; exact function not determined from available sources.

token `PortationMaster coding page byte 33 (4-bit field (00..00))`· source: inferred

### `3006/34/00000001b` — TI default category: Weather  ·  _med_

Enables weather as a default-enabled traffic information (TI) category in the connected navigation service, so weather overlays are shown by default on the map.

| value | meaning |
|---|---|
| `0` | Disabled by default |
| `1` | Enabled by default |

default `00`· gate: always (no FA gate)· token `TI_CAT_DEFAULT_WEATHER`· source: firmware-token

### `3006/34/00000010b` — TI virtual map category: Weather  ·  _med_

Enables weather as a selectable category on the virtual map (VMAP) traffic information overlay layer, allowing weather data to be shown on the interactive online map.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: always (no FA gate)· token `TI_CAT_VMAP_WEATHER`· source: firmware-token

### `3006/34/00000100b` — TI virtual map category: Public parking  ·  _med_

Enables public parking as a selectable category on the virtual map (VMAP) traffic information overlay, showing real-time parking availability data.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: always (no FA gate)· token `TI_CAT_VMAP_PARK_PUBL`· source: firmware-token

### `3006/34/00001000b` — TI virtual map category: On-route info  ·  _med_

Enables on-route information as a selectable category on the virtual map (VMAP) traffic information overlay, highlighting relevant incidents or services along the active route. Inactive on this vehicle.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `TI_CAT_VMAP_ONROUTE`· source: firmware-token

### `3006/34/00010000b` — TI default category: Traffic flow  ·  _med_

Enables traffic flow (congestion level) as a default-enabled traffic information category, showing current road speed/flow data on the map by default.

| value | meaning |
|---|---|
| `0` | Disabled by default |
| `1` | Enabled by default |

default `00`· gate: always (no FA gate)· token `TI_CAT_DEFAULT_FLOW`· source: firmware-token

### `3006/34/00100000b` — TI default category: Traffic forecast  ·  _med_

Enables traffic forecast (predicted future congestion) as a default-enabled traffic information category on the map.

| value | meaning |
|---|---|
| `0` | Disabled by default |
| `1` | Enabled by default |

default `00`· gate: always (no FA gate)· token `TI_CAT_DEFAULT_FORECAST`· source: firmware-token

### `3006/34/01000000b` — TI default category: Traffic incidents  ·  _med_

Enables traffic incidents (accidents, hazards) as a default-enabled traffic information category, showing incident markers on the map by default.

| value | meaning |
|---|---|
| `0` | Disabled by default |
| `1` | Enabled by default |

default `00`· gate: always (no FA gate)· token `TI_CAT_DEFAULT_INCIDENTS`· source: firmware-token

### `3006/34/10000000b` — TI default category: Roadworks  ·  _med_

Enables roadworks (construction zones) as a default-enabled traffic information category, showing roadwork markers on the map by default.

| value | meaning |
|---|---|
| `0` | Disabled by default |
| `1` | Enabled by default |

default `00`· gate: always (no FA gate)· token `TI_CAT_DEFAULT_ROADWORKS`· source: firmware-token

### `3006/35/00000001b` — TI default category: Road closures  ·  _med_

Enables road closures as a default-enabled traffic information category, showing closed-road markers on the map by default.

| value | meaning |
|---|---|
| `0` | Disabled by default |
| `1` | Enabled by default |

default `00`· gate: always (no FA gate)· token `TI_CAT_DEFAULT_CLOSED`· source: firmware-token

### `3006/35/00000010b` — TI default category: Public parking  ·  _med_

Enables public parking availability as a default-enabled traffic information category on the map.

| value | meaning |
|---|---|
| `0` | Disabled by default |
| `1` | Enabled by default |

default `00`· gate: always (no FA gate)· token `TI_CAT_DEFAULT_PARK_PUBL`· source: firmware-token

### `3006/35/00000100b` — TI default category: On-route info  ·  _med_

Enables on-route information as a default-enabled traffic information category, highlighting relevant events along the active navigation route by default.

| value | meaning |
|---|---|
| `0` | Disabled by default |
| `1` | Enabled by default |

default `00`· gate: always (no FA gate)· token `TI_CAT_DEFAULT_ONROUTE`· source: firmware-token

### `3006/35/00001000b` — Traffic information via VICS beacons (Japan)  ·  _med_

Enables reception of traffic information via Japanese VICS (Vehicle Information and Communication System) roadside IR/radio beacons, used for real-time traffic data in Japan.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 609 Professional navigation system / 807 Japanese version / 449 Toll interior mirror for Japan· token `TI_BEACONS_JAPAN`· source: firmware-token

### `3006/35/00010000b` — Traffic information via TMC  ·  _med_

Enables reception of traffic information via TMC (Traffic Message Channel) — a broadcast FM radio-based traffic data standard used primarily in Europe.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· token `TI_TMC`· source: firmware-token

### `3006/35/00100000b` — Traffic information via CA-TMC (Canada TMC)  ·  _med_

Enables Canada-specific TMC traffic information reception. Inactive on this vehicle (European/US market).

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `TI_CA_TMC`· source: firmware-token

### `3006/35/01000000b` — Traffic information via TPEG  ·  _med_

Enables reception of traffic and travel information via TPEG (Transport Protocol Experts Group) — a digital broadcast data format for real-time traffic information, typically over DAB/DARC.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 802 Korean version / 6UH Traffic Information· token `TI_TPEG`· source: firmware-token

### `3006/35/10000000b` — Traffic information via CA-TPEG (Canada TPEG)  ·  _med_

Enables Canada-specific TPEG traffic information reception. Inactive on this vehicle.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `TI_CA_TPEG`· source: firmware-token

### `3006/36/00000001b` — Traffic information: Regional TMC enabled  ·  _med_

Enables regional TMC traffic information reception, allowing market-specific or region-specific TMC data to supplement the main TMC feed.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / 6UH Traffic Information· token `TI_TMC_REGIONAL`· source: firmware-token

### `3006/36/00000010b` — Traffic information: Fallback disabled  ·  _med_

When enabled, disables the fallback mechanism that switches to an alternative traffic information source (e.g. TMC fallback) when the primary source is unavailable.

| value | meaning |
|---|---|
| `0` | Fallback allowed |
| `1` | Fallback disabled |

default `00`· gate: vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / 6UH Traffic Information· token `TI_FALLBACK_DISABLED`· source: firmware-token

### `3006/36/00000100b` — Traffic information: Combined source disabled  ·  _med_

When enabled, disables the combined (combi) traffic information source mode, preventing the system from merging multiple traffic data streams. Inactive on this vehicle.

| value | meaning |
|---|---|
| `0` | Combined source allowed |
| `1` | Combined source disabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `TI_USE_COMBI_DISABLED`· source: firmware-token

### `3006/36/00001000b` — Traffic information via VICS (Japan)  ·  _med_

Enables reception of VICS (Vehicle Information and Communication System) traffic data in Japan, including radio-wave and optical beacon traffic information. Inactive on this vehicle.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `TI_VICS`· source: firmware-token

### `3006/36/00010000b` — Traffic information via Vinfo (online service)  ·  _med_

Enables Vinfo — BMW's online connected traffic information service — as a traffic data source, providing live data via the telematics connection.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: NOT 802 Korean version / 807 Japanese version / 810 Australian version / 8AA Chinese version / 825 Radio control Oceania / 6UH Traffic Information / 8LH Country control 04142 / 8LT Country control 04825  / 6NL Connecting Bluetooth and USB devices including BMW assist / 6AE TeleServices· token `TI_VINFO`· source: firmware-token

### `3006/36/00100000b` — TI virtual map category: Traffic flow  ·  _med_

Enables traffic flow as a selectable category on the virtual map (VMAP) online traffic overlay. Inactive on this vehicle.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `TI_CAT_VMAP_FLOW`· source: firmware-token

### `3006/36/01000000b` — TI virtual map category: Traffic forecast  ·  _med_

Enables traffic forecast as a selectable category on the virtual map (VMAP) online traffic overlay layer.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: always (no FA gate)· token `TI_CAT_VMAP_FORECAST`· source: firmware-token

### `3006/36/10000000b` — TI virtual map category: Traffic incidents  ·  _med_

Enables traffic incidents as a selectable category on the virtual map (VMAP) online traffic overlay layer.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: always (no FA gate)· token `TI_CAT_VMAP_INCIDENTS`· source: firmware-token

### `3006/37/00000001b` — TI virtual map category: Roadworks  ·  _med_

Enables roadworks as a selectable category on the virtual map (VMAP) online traffic overlay layer.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: always (no FA gate)· token `TI_CAT_VMAP_ROADWORKS`· source: firmware-token

### `3006/37/00000010b` — TI virtual map category: Road closures  ·  _med_

Enables road closures as a selectable category on the virtual map (VMAP) online traffic overlay layer.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: always (no FA gate)· token `TI_CAT_VMAP_CLOSED`· source: firmware-token

### `3006/37/00000100b` — Portation/product-line flag (byte 37 bit 2)  ·  _low_

Unnamed boolean flag in the PortationMaster/Produktlinie coding page (dg 3006). Consumed by an on-device process other than the main HU engine; exact function not determined from available sources.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

token `PortationMaster coding page byte 37 (boolean flag (Bool)`· source: inferred

### `3006/37/00001000b` — TI virtual map category: Free-flow traffic  ·  _med_

Enables free-flow traffic (roads running at or above speed limit with no congestion) as a selectable category on the virtual map overlay. Inactive on this vehicle.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `TI_CAT_VMAP_FREEFLOW`· source: firmware-token

### `3006/37/00010000b` — TI default category: Free-flow traffic  ·  _med_

Enables free-flow traffic as a default-enabled traffic information category on the map, showing roads with no congestion in a distinct colour.

| value | meaning |
|---|---|
| `0` | Disabled by default |
| `1` | Enabled by default |

default `00`· gate: always (no FA gate)· token `TI_CAT_DEFAULT_FREEFLOW`· source: firmware-token

### `3006/37/00100000b` — Portation/product-line flag (byte 37 bit 5)  ·  _low_

Unnamed boolean flag in the PortationMaster/Produktlinie coding page (dg 3006). Consumed by an on-device process other than the main HU engine; exact function not determined from available sources.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

token `PortationMaster coding page byte 37 (boolean flag (Bool)`· source: inferred

### `3006/37/01000000b` — Traffic detour button disabled  ·  _med_

When enabled, hides or disables the manual traffic-detour request button in the navigation UI, preventing the driver from manually triggering an alternative route around a reported incident. Inactive on this vehicle.

| value | meaning |
|---|---|
| `0` | Detour button enabled |
| `1` | Detour button disabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `TI_DETOUR_BUTTON_DISABLED`· source: firmware-token

### `3006/37/10000000b` — TPEG TAP (TPEG Application Profile) enable  ·  _med_

Enables TPEG TAP — a specific TPEG application profile used to deliver structured traffic and travel information from the telematics/TeleServices connection. Gated by 6AE TeleServices FA option.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 6AE TeleServices· token `TPEG_TAP`· source: firmware-token

### `3006/38/00000001b` — Portation/product-line flag (byte 38 bit 0)  ·  _low_

Unnamed boolean flag in the PortationMaster/Produktlinie coding page (dg 3006). Consumed by an on-device process other than the main HU engine; exact function not determined from available sources.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

token `PortationMaster coding page byte 38 (boolean flag (Bool)`· source: inferred

### `3006/38/11111110b` — Market country code  ·  _high_

Specifies the country/market for which this head-unit is configured, enabling country-specific navigation, traffic, and regulatory features. Inactive on this vehicle (field not active on European non-country-specific FA).

| value | meaning |
|---|---|
| `1` | Australia |
| `2` | Germany |
| `3` | Egypt |
| `4` | Canada |
| `5` | Japan |
| `6` | China |
| `7` | Korea |
| `8` | Hong Kong |
| `9` | Taiwan |
| `10` | ECE (Europe) |
| `11` | United States |

default `02`· gate: FA-gated (depends on vehicle options)· token `COUNTRY`· source: firmware-token

### `3006/39/11111111b` — Portation/product-line value (bytes 39-99)  ·  _low_

Unnamed multi-byte block (bytes 39-99, 61 bytes) in the PortationMaster/Produktlinie coding page. Consumed by on-device processes other than the main HU engine; exact function not determined from available sources. This is the tail-end reserved/unallocated region of the dg 3006 page.

token `PortationMaster coding page byte 39 (multi-byte value (syset Int/UInt8/16))`· source: inferred

## Datagroup 0x3007 (32 parameters)

### `3007/0/00000011b` — German language availability  ·  _high_

Controls whether German is available as a selectable UI language. When set to MASTER (1), German is the primary/default language slot; LIST (2) makes it a secondary selectable option.

| value | meaning |
|---|---|
| `0` | Not active (language disabled) |
| `1` | Master (primary language) |
| `2` | List (secondary/selectable option) |

default `00`· gate: NOT 853 Language version English / 854 Language version French / 855 Language version Italian / 868 Language version Dutch / 6UD Language version Russian / 856 Language version Spanish / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / 6S1 Language version Turkish / 6S3 Language version Portuguese / 6S4 Language version Swedish / 6S2 Language version Greek / 8A1 Language version Polish / 8A2 Language version Hungarian / 8A3 Arabic language version / 8A4 Language version Czech / 8A5 Language version Slovakian / 8A6 Slovenian language version / 8A7 Norwegian language version / 8A8 Danish language version / 8A9 Finnish language version / 6S5 Language version Bahasa Indonesian· token `LANGUAGE_GERMAN`· source: firmware-token

### `3007/0/00001100b` — English (UK) language availability  ·  _high_

Controls whether British English is available as a selectable UI language. MASTER (1) = primary slot, LIST (2) = secondary option. Always active with no FA gate restriction; default value is 01 (MASTER), making UK English the unconditional primary language.

| value | meaning |
|---|---|
| `0` | Not active (language disabled) |
| `1` | Master (primary language) |
| `2` | List (secondary/selectable option) |

default `01`· token `LANGUAGE_ENGLISH_UK`· source: firmware-token

### `3007/0/00110000b` — English (US) language availability  ·  _high_

Controls whether American English is available as a selectable UI language. Separate from UK English; allows market-specific default spellings and terminology (e.g. 'gas' vs 'petrol' prompts in navigation).

| value | meaning |
|---|---|
| `0` | Not active (language disabled) |
| `1` | Master (primary language) |
| `2` | List (secondary/selectable option) |

default `00`· token `LANGUAGE_ENGLISH_US`· source: firmware-token

### `3007/0/11000000b` — Spanish language availability  ·  _high_

Controls whether Spanish is available as a selectable UI language. Enabled by FA option 856 (Language version Spanish) or any of the listed language FA options.

| value | meaning |
|---|---|
| `0` | Not active (language disabled) |
| `1` | Master (primary language) |
| `2` | List (secondary/selectable option) |

default `00`· gate: 851 Language version German / 853 Language version English / 854 Language version French / 855 Language version Italian / 868 Language version Dutch / 6UD Language version Russian / 6S1 Language version Turkish / 6S3 Language version Portuguese / 6S4 Language version Swedish / 6S2 Language version Greek / 8A1 Language version Polish / 8A2 Language version Hungarian / 8A3 Arabic language version / 8A4 Language version Czech / 8A5 Language version Slovakian / 8A6 Slovenian language version / 8A7 Norwegian language version / 8A8 Danish language version / 8A9 Finnish language version / 6S5 Language version Bahasa Indonesian· token `LANGUAGE_SPANISH`· source: firmware-token

### `3007/1/00000011b` — French language availability  ·  _high_

Controls whether French is available as a selectable UI language. Enabled by FA option 854 (Language version French) or when other listed language options are present.

| value | meaning |
|---|---|
| `0` | Not active (language disabled) |
| `1` | Master (primary language) |
| `2` | List (secondary/selectable option) |

default `00`· gate: 851 Language version German / 853 Language version English / 855 Language version Italian / 868 Language version Dutch / 6UD Language version Russian / 856 Language version Spanish / 6S1 Language version Turkish / 6S3 Language version Portuguese / 6S4 Language version Swedish / 6S2 Language version Greek / 8A1 Language version Polish / 8A2 Language version Hungarian / 8A3 Arabic language version / 8A4 Language version Czech / 8A5 Language version Slovakian / 8A6 Slovenian language version / 8A7 Norwegian language version / 8A8 Danish language version / 8A9 Finnish language version / 6S5 Language version Bahasa Indonesian· token `LANGUAGE_FRENCH`· source: firmware-token

### `3007/1/00001100b` — Italian language availability  ·  _high_

Controls whether Italian is available as a selectable UI language. Enabled by FA option 855 (Language version Italian) or when other listed language options are present.

| value | meaning |
|---|---|
| `0` | Not active (language disabled) |
| `1` | Master (primary language) |
| `2` | List (secondary/selectable option) |

default `00`· gate: NOT 851 Language version German / 853 Language version English / 854 Language version French / 868 Language version Dutch / 6UD Language version Russian / 856 Language version Spanish / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / 6S1 Language version Turkish / 6S3 Language version Portuguese / 6S4 Language version Swedish / 6S2 Language version Greek / 8A1 Language version Polish / 8A2 Language version Hungarian / 8A3 Arabic language version / 8A4 Language version Czech / 8A5 Language version Slovakian / 8A6 Slovenian language version / 8A7 Norwegian language version / 8A8 Danish language version / 8A9 Finnish language version / 6S5 Language version Bahasa Indonesian· token `LANGUAGE_ITALIAN`· source: firmware-token

### `3007/1/00110000b` — Hungarian language availability  ·  _high_

Controls whether Hungarian is available as a selectable UI language. Enabled by FA option 8A2 (Language version Hungarian) or when other listed language options are present.

| value | meaning |
|---|---|
| `0` | Not active (language disabled) |
| `1` | Master (primary language) |
| `2` | List (secondary/selectable option) |

default `00`· gate: NOT 851 Language version German / 853 Language version English / 854 Language version French / 855 Language version Italian / 868 Language version Dutch / 6UD Language version Russian / 856 Language version Spanish / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / 6S1 Language version Turkish / 6S3 Language version Portuguese / 6S4 Language version Swedish / 6S2 Language version Greek / 8A1 Language version Polish / 8A3 Arabic language version / 8A4 Language version Czech / 8A5 Language version Slovakian / 8A6 Slovenian language version / 8A7 Norwegian language version / 8A8 Danish language version / 8A9 Finnish language version / 6S5 Language version Bahasa Indonesian· token `LANGUAGE_HUNGARIAN`· source: firmware-token

### `3007/1/11000000b` — Dutch language availability  ·  _med_

Controls whether Dutch is available as a selectable UI language. Enabled by FA option 868 (Language version Dutch). This is the only 2-bit slot in byte 1 not individually named in the firmware string pool; the Dutch assignment is strongly supported by FA gate evidence and the presence of LANGUAGE_DUTCH as value 3 in the LANGUAGE_INDONESIAN descriptor.

| value | meaning |
|---|---|
| `0` | Not active (language disabled) |
| `1` | Master (primary language) |
| `2` | List (secondary/selectable option) |

default `00`· gate: NOT 851 Language version German / 853 Language version English / 854 Language version French / 855 Language version Italian / 6UD Language version Russian / 856 Language version Spanish / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / 6S1 Language version Turkish / 6S3 Language version Portuguese / 6S4 Language version Swedish / 6S2 Language version Greek / 8A1 Language version Polish / 8A2 Language version Hungarian / 8A3 Arabic language version / 8A4 Language version Czech / 8A5 Language version Slovakian / 8A6 Slovenian language version / 8A7 Norwegian language version / 8A8 Danish language version / 8A9 Finnish language version / 6S5 Language version Bahasa Indonesian· token `LANGUAGE byte 1 (2-bit enum)`· source: inferred

### `3007/2/00000011b` — Polish language availability  ·  _high_

Controls whether Polish is available as a selectable UI language. Enabled by FA option 8A1 (Language version Polish) or when other listed language options are present.

| value | meaning |
|---|---|
| `0` | Not active (language disabled) |
| `1` | Master (primary language) |
| `2` | List (secondary/selectable option) |

default `00`· gate: NOT 851 Language version German / 853 Language version English / 854 Language version French / 855 Language version Italian / 868 Language version Dutch / 6UD Language version Russian / 856 Language version Spanish / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / 6S1 Language version Turkish / 6S3 Language version Portuguese / 6S4 Language version Swedish / 6S2 Language version Greek / 8A2 Language version Hungarian / 8A3 Arabic language version / 8A4 Language version Czech / 8A5 Language version Slovakian / 8A6 Slovenian language version / 8A7 Norwegian language version / 8A8 Danish language version / 8A9 Finnish language version / 6S5 Language version Bahasa Indonesian· token `LANGUAGE_POLISH`· source: firmware-token

### `3007/2/00001100b` — Portuguese (European) language availability  ·  _high_

Controls whether European Portuguese is available as a selectable UI language. Distinct from Brazilian Portuguese (LANGUAGE_PORTUGUESE_BR at 3007/6/00110000b). Enabled by FA option 6S3.

| value | meaning |
|---|---|
| `0` | Not active (language disabled) |
| `1` | Master (primary language) |
| `2` | List (secondary/selectable option) |

default `00`· gate: NOT 851 Language version German / 853 Language version English / 854 Language version French / 855 Language version Italian / 868 Language version Dutch / 6UD Language version Russian / 856 Language version Spanish / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / 8LB Country-specific control 00464 (Brazil) / 6S1 Language version Turkish / 6S4 Language version Swedish / 6S2 Language version Greek / 8A1 Language version Polish / 8A2 Language version Hungarian / 8A3 Arabic language version / 8A4 Language version Czech / 8A5 Language version Slovakian / 8A6 Slovenian language version / 8A7 Norwegian language version / 8A8 Danish language version / 8A9 Finnish language version / 6S5 Language version Bahasa Indonesian· token `LANGUAGE_PORTUGUESE`· source: firmware-token

### `3007/2/00110000b` — Russian language availability  ·  _high_

Controls whether Russian is available as a selectable UI language. Enabled by FA option 6UD (Language version Russian).

| value | meaning |
|---|---|
| `0` | Not active (language disabled) |
| `1` | Master (primary language) |
| `2` | List (secondary/selectable option) |

default `00`· gate: NOT 851 Language version German / 853 Language version English / 854 Language version French / 855 Language version Italian / 868 Language version Dutch / 856 Language version Spanish / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / 6S1 Language version Turkish / 6S3 Language version Portuguese / 6S4 Language version Swedish / 6S2 Language version Greek / 8A1 Language version Polish / 8A2 Language version Hungarian / 8A3 Arabic language version / 8A4 Language version Czech / 8A5 Language version Slovakian / 8A6 Slovenian language version / 8A7 Norwegian language version / 8A8 Danish language version / 8A9 Finnish language version / 6S5 Language version Bahasa Indonesian· token `LANGUAGE_RUSSIAN`· source: firmware-token

### `3007/2/11000000b` — Swedish language availability  ·  _high_

Controls whether Swedish is available as a selectable UI language. Enabled by FA option 6S4 (Language version Swedish).

| value | meaning |
|---|---|
| `0` | Not active (language disabled) |
| `1` | Master (primary language) |
| `2` | List (secondary/selectable option) |

default `00`· gate: NOT 851 Language version German / 853 Language version English / 854 Language version French / 855 Language version Italian / 868 Language version Dutch / 6UD Language version Russian / 856 Language version Spanish / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / 6S1 Language version Turkish / 6S3 Language version Portuguese / 6S2 Language version Greek / 8A1 Language version Polish / 8A2 Language version Hungarian / 8A3 Arabic language version / 8A4 Language version Czech / 8A5 Language version Slovakian / 8A6 Slovenian language version / 8A7 Norwegian language version / 8A8 Danish language version / 8A9 Finnish language version / 6S5 Language version Bahasa Indonesian· token `LANGUAGE_SWEDISH`· source: firmware-token

### `3007/3/00000011b` — Turkish language availability  ·  _high_

Controls whether Turkish is available as a selectable UI language. Enabled by FA option 6S1 (Language version Turkish). The syset descriptor only supplies the symbolic name for value 2 (LIST); values 0 and 1 are inferred from the common LANGUAGE_ field pattern.

| value | meaning |
|---|---|
| `0` | Not active (language disabled) |
| `1` | Master (primary language) |
| `2` | List (secondary/selectable option) |

default `00`· gate: NOT 851 Language version German / 853 Language version English / 854 Language version French / 855 Language version Italian / 868 Language version Dutch / 6UD Language version Russian / 856 Language version Spanish / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / 6S3 Language version Portuguese / 6S4 Language version Swedish / 6S2 Language version Greek / 8A1 Language version Polish / 8A2 Language version Hungarian / 8A3 Arabic language version / 8A4 Language version Czech / 8A5 Language version Slovakian / 8A6 Slovenian language version / 8A7 Norwegian language version / 8A8 Danish language version / 8A9 Finnish language version / 6S5 Language version Bahasa Indonesian· token `LANGUAGE_TURKISH`· source: firmware-token

### `3007/3/00001100b` — Greek language availability  ·  _high_

Controls whether Greek is available as a selectable UI language. Enabled by FA option 6S2 (Language version Greek).

| value | meaning |
|---|---|
| `0` | Not active (language disabled) |
| `1` | Master (primary language) |
| `2` | List (secondary/selectable option) |

default `00`· gate: NOT 851 Language version German / 853 Language version English / 854 Language version French / 855 Language version Italian / 868 Language version Dutch / 6UD Language version Russian / 856 Language version Spanish / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / 6S1 Language version Turkish / 6S3 Language version Portuguese / 6S4 Language version Swedish / 8A1 Language version Polish / 8A2 Language version Hungarian / 8A3 Arabic language version / 8A4 Language version Czech / 8A5 Language version Slovakian / 8A6 Slovenian language version / 8A7 Norwegian language version / 8A8 Danish language version / 8A9 Finnish language version / 6S5 Language version Bahasa Indonesian· token `LANGUAGE_GREEK`· source: firmware-token

### `3007/3/00110000b` — Arabic language availability  ·  _high_

Controls whether Arabic is available as a selectable UI language. Enabled by FA option 8A3 (Arabic language version). Not active on this vehicle.

| value | meaning |
|---|---|
| `0` | Not active (language disabled) |
| `1` | Master (primary language) |
| `2` | List (secondary/selectable option) |

default `00`· gate: FA-gated (depends on vehicle options)· token `LANGUAGE_ARABIC`· source: firmware-token

### `3007/3/11000000b` — Simplified Chinese language availability  ·  _high_

Controls whether Simplified Chinese (Mandarin, PRC) is available as a selectable UI language. Enabled by FA option 866 or country control codes 8LH/8LT (China/Taiwan markets). Descriptor confirms value 1 as MASTER.

| value | meaning |
|---|---|
| `0` | Not active (language disabled) |
| `1` | Master (primary language) |
| `2` | List (secondary/selectable option) |

default `00`· gate: 866 Language version simplified Chinese / 8LH Country control 04142 / 8LT Country control 04825 · token `LANGUAGE_CHINESE_SIMPLIFIED`· source: firmware-token

### `3007/4/00000011b` — Traditional Chinese language availability  ·  _high_

Controls whether Traditional Chinese (Taiwan/Hong Kong markets) is available as a selectable UI language. Active when FA option 866 (Simplified Chinese) is NOT present — Traditional and Simplified Chinese are mutually exclusive variants.

| value | meaning |
|---|---|
| `0` | Not active (language disabled) |
| `1` | Master (primary language) |
| `2` | List (secondary/selectable option) |

default `00`· gate: NOT 866 Language version simplified Chinese / 8LH Country control 04142 / 8LT Country control 04825 · token `LANGUAGE_CHINESE_TRADITIONAL`· source: firmware-token

### `3007/4/00001100b` — Japanese language availability  ·  _high_

Controls whether Japanese is available as a selectable UI language. Not active on this vehicle. The syset descriptor explicitly names only value 0 (NICHT_AKTIV) for this field, indicating no other values are documented in the descriptor.

| value | meaning |
|---|---|
| `0` | Not active (language disabled) |

default `00`· gate: FA-gated (depends on vehicle options)· token `LANGUAGE_JAPANESE`· source: firmware-token

### `3007/4/00110000b` — Korean language availability  ·  _high_

Controls whether Korean is available as a selectable UI language. Not active on this vehicle.

| value | meaning |
|---|---|
| `0` | Not active (language disabled) |
| `1` | Master (primary language) |
| `2` | List (secondary/selectable option) |

default `00`· gate: FA-gated (depends on vehicle options)· token `LANGUAGE_KOREAN`· source: firmware-token

### `3007/4/11000000b` — Czech language availability  ·  _high_

Controls whether Czech is available as a selectable UI language. Enabled by FA option 8A4 (Language version Czech).

| value | meaning |
|---|---|
| `0` | Not active (language disabled) |
| `1` | Master (primary language) |
| `2` | List (secondary/selectable option) |

default `00`· gate: NOT 851 Language version German / 853 Language version English / 854 Language version French / 855 Language version Italian / 868 Language version Dutch / 6UD Language version Russian / 856 Language version Spanish / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / 6S1 Language version Turkish / 6S3 Language version Portuguese / 6S4 Language version Swedish / 6S2 Language version Greek / 8A1 Language version Polish / 8A2 Language version Hungarian / 8A3 Arabic language version / 8A5 Language version Slovakian / 8A6 Slovenian language version / 8A7 Norwegian language version / 8A8 Danish language version / 8A9 Finnish language version / 6S5 Language version Bahasa Indonesian· token `LANGUAGE_CZECH`· source: firmware-token

### `3007/5/00000011b` — Slovenian language availability  ·  _high_

Controls whether Slovenian is available as a selectable UI language. Enabled by FA option 8A6 (Slovenian language version).

| value | meaning |
|---|---|
| `0` | Not active (language disabled) |
| `1` | Master (primary language) |
| `2` | List (secondary/selectable option) |

default `00`· gate: NOT 851 Language version German / 853 Language version English / 854 Language version French / 855 Language version Italian / 868 Language version Dutch / 6UD Language version Russian / 856 Language version Spanish / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / 6S1 Language version Turkish / 6S3 Language version Portuguese / 6S4 Language version Swedish / 6S2 Language version Greek / 8A1 Language version Polish / 8A2 Language version Hungarian / 8A3 Arabic language version / 8A4 Language version Czech / 8A5 Language version Slovakian / 8A7 Norwegian language version / 8A8 Danish language version / 8A9 Finnish language version / 6S5 Language version Bahasa Indonesian· token `LANGUAGE_SLOVENIAN`· source: firmware-token

### `3007/5/00001100b` — Slovakian language availability  ·  _high_

Controls whether Slovakian is available as a selectable UI language. Enabled by FA option 8A5 (Language version Slovakian).

| value | meaning |
|---|---|
| `0` | Not active (language disabled) |
| `1` | Master (primary language) |
| `2` | List (secondary/selectable option) |

default `00`· gate: NOT 851 Language version German / 853 Language version English / 854 Language version French / 855 Language version Italian / 868 Language version Dutch / 6UD Language version Russian / 856 Language version Spanish / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / 6S1 Language version Turkish / 6S3 Language version Portuguese / 6S4 Language version Swedish / 6S2 Language version Greek / 8A1 Language version Polish / 8A2 Language version Hungarian / 8A3 Arabic language version / 8A4 Language version Czech / 8A6 Slovenian language version / 8A7 Norwegian language version / 8A8 Danish language version / 8A9 Finnish language version / 6S5 Language version Bahasa Indonesian· token `LANGUAGE_SLOVAKIAN`· source: firmware-token

### `3007/5/00110000b` — Danish language availability  ·  _high_

Controls whether Danish is available as a selectable UI language. Enabled by FA option 8A8 (Danish language version).

| value | meaning |
|---|---|
| `0` | Not active (language disabled) |
| `1` | Master (primary language) |
| `2` | List (secondary/selectable option) |

default `00`· gate: NOT 851 Language version German / 853 Language version English / 854 Language version French / 855 Language version Italian / 868 Language version Dutch / 6UD Language version Russian / 856 Language version Spanish / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / 6S1 Language version Turkish / 6S3 Language version Portuguese / 6S4 Language version Swedish / 6S2 Language version Greek / 8A1 Language version Polish / 8A2 Language version Hungarian / 8A3 Arabic language version / 8A4 Language version Czech / 8A5 Language version Slovakian / 8A6 Slovenian language version / 8A7 Norwegian language version / 8A9 Finnish language version / 6S5 Language version Bahasa Indonesian· token `LANGUAGE_DANISH`· source: firmware-token

### `3007/5/11000000b` — Finnish language availability  ·  _high_

Controls whether Finnish is available as a selectable UI language. Enabled by FA option 8A9 (Finnish language version).

| value | meaning |
|---|---|
| `0` | Not active (language disabled) |
| `1` | Master (primary language) |
| `2` | List (secondary/selectable option) |

default `00`· gate: NOT 851 Language version German / 853 Language version English / 854 Language version French / 855 Language version Italian / 868 Language version Dutch / 6UD Language version Russian / 856 Language version Spanish / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / 6S1 Language version Turkish / 6S3 Language version Portuguese / 6S4 Language version Swedish / 6S2 Language version Greek / 8A1 Language version Polish / 8A2 Language version Hungarian / 8A3 Arabic language version / 8A4 Language version Czech / 8A5 Language version Slovakian / 8A6 Slovenian language version / 8A7 Norwegian language version / 8A8 Danish language version / 6S5 Language version Bahasa Indonesian· token `LANGUAGE_FINNISH`· source: firmware-token

### `3007/6/00000011b` — Norwegian language availability  ·  _high_

Controls whether Norwegian is available as a selectable UI language. Enabled by FA option 8A7 (Norwegian language version).

| value | meaning |
|---|---|
| `0` | Not active (language disabled) |
| `1` | Master (primary language) |
| `2` | List (secondary/selectable option) |

default `00`· gate: NOT 851 Language version German / 853 Language version English / 854 Language version French / 855 Language version Italian / 868 Language version Dutch / 6UD Language version Russian / 856 Language version Spanish / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / 6S1 Language version Turkish / 6S3 Language version Portuguese / 6S4 Language version Swedish / 6S2 Language version Greek / 8A1 Language version Polish / 8A2 Language version Hungarian / 8A3 Arabic language version / 8A4 Language version Czech / 8A5 Language version Slovakian / 8A6 Slovenian language version / 8A8 Danish language version / 8A9 Finnish language version / 6S5 Language version Bahasa Indonesian· token `LANGUAGE_NORWEGIAN`· source: firmware-token

### `3007/6/00000100b` — iSpeech Russian voice recognition enable  ·  _high_

Enables the Russian (ru-RU) iSpeech voice recognition engine. iSpeech is BMW's speech processing subsystem; this flag enables the Russian language pack for voice commands.

| value | meaning |
|---|---|
| `0` | Off (Russian iSpeech disabled) |
| `1` | Active (Russian iSpeech enabled) |

default `00`· gate: always (no FA gate)· token `LANGUAGE_ISPEECH_RU_RU`· source: firmware-token

### `3007/6/00001000b` — iSpeech Portuguese voice recognition enable  ·  _high_

Enables the European Portuguese (pt-PT) iSpeech voice recognition engine. Separate from Brazilian Portuguese; enables voice commands in Portuguese for EU/Portugal market vehicles.

| value | meaning |
|---|---|
| `0` | Off (Portuguese iSpeech disabled) |
| `1` | Active (Portuguese iSpeech enabled) |

default `00`· gate: always (no FA gate)· token `LANGUAGE_ISPEECH_PT_PT`· source: firmware-token

### `3007/6/00110000b` — Brazilian Portuguese language availability  ·  _high_

Controls whether Brazilian Portuguese (pt-BR) is available as a selectable UI language. Distinct from European Portuguese (LANGUAGE_PORTUGUESE). Enabled by country control 8LB (Brazil) or when not gated out by European language FA options.

| value | meaning |
|---|---|
| `0` | Not active (language disabled) |
| `1` | Master (primary language) |
| `2` | List (secondary/selectable option) |

default `00`· gate: NOT 851 Language version German / 853 Language version English / 854 Language version French / 855 Language version Italian / 868 Language version Dutch / 6UD Language version Russian / 856 Language version Spanish / vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93) / 8LB Country-specific control 00464 (Brazil) / 6S1 Language version Turkish / 6S4 Language version Swedish / 6S2 Language version Greek / 8A1 Language version Polish / 8A2 Language version Hungarian / 8A3 Arabic language version / 8A4 Language version Czech / 8A5 Language version Slovakian / 8A6 Slovenian language version / 8A7 Norwegian language version / 8A8 Danish language version / 8A9 Finnish language version / 6S5 Language version Bahasa Indonesian· token `LANGUAGE_PORTUGUESE_BR`· source: firmware-token

### `3007/6/11000000b` — Bahasa Indonesian language availability  ·  _high_

Controls whether Bahasa Indonesian is available as a selectable UI language. Enabled by FA option 6S5. Not active on this vehicle. This coord has the most complete enum descriptor in the page, explicitly naming all four values including an unusual value 3 ('LANGUAGE_DUTCH') which the firmware descriptor defines as a named state for this field.

| value | meaning |
|---|---|
| `0` | Not active (language disabled) |
| `1` | Master (primary language) |
| `2` | List (secondary/selectable option) |
| `3` | Dutch language slot (LANGUAGE_DUTCH) |

default `00`· gate: FA-gated (depends on vehicle options)· token `LANGUAGE_INDONESIAN`· source: firmware-token

### `3007/7/00000011b` — Thai language availability  ·  _high_

Controls whether Thai is available as a selectable UI language. Not active on this vehicle.

| value | meaning |
|---|---|
| `0` | Not active (language disabled) |
| `1` | Master (primary language) |
| `2` | List (secondary/selectable option) |

default `00`· gate: FA-gated (depends on vehicle options)· token `LANGUAGE_THAI`· source: firmware-token

### `3007/7/11111100b` — Undocumented field (LANGUAGE byte 7 6-bit)  ·  _low_

Purpose not determined from available sources. Occupies bits 7.2 of byte 7 in the LANGUAGE coding page. Default and current value are both 0x00.

token `LANGUAGE byte 7 (6-bit field (00..00))`· source: inferred

### `3007/8/11111111b` — Undocumented field (LANGUAGE page bytes 8-49)  ·  _low_

Purpose not determined from available sources. Spans bytes 8 through 49 of the LANGUAGE coding page (42 bytes). Default value is 0x00 throughout.

token `LANGUAGE byte 8 (multi-byte value (syset Int/UInt8/16))`· source: inferred

## Datagroup 0x3008 (48 parameters)

### `3008/0/00000001b` — Driving Experience Control  ·  _med_

Tells the head unit the car has Driving Experience Control, the switch that selects driving modes such as COMFORT, SPORT and ECO PRO. The head unit's driving mode displays and settings depend on it, so set it to match the car.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: always (no FA gate)· token `FES_FEATURE`· source: firmware-token

### `3008/0/00000010b` — SPORT BASE driving mode available  ·  _med_

Enables the SPORT (base) driving mode in the Driving Experience Control menu. When active, the standard SPORT programme is offered as a selectable mode.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `FES_SPORT_BASE`· source: firmware-token

### `3008/0/00000100b` — SPORT EXPERT driving mode available  ·  _med_

Enables the SPORT Expert (enhanced/advanced) driving mode in the Driving Experience Control menu, providing the more aggressive dynamic programme.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `FES_SPORT_EXPERT`· source: firmware-token

### `3008/0/00001000b` — SPORT CUSTOM driving mode available  ·  _med_

Enables a user-configurable SPORT CUSTOM driving mode in the Driving Experience Control menu, allowing individual sub-system settings within the SPORT programme.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `FES_SPORT_CUSTOM`· source: firmware-token

### `3008/0/00010000b` — COMFORT BASE driving mode available  ·  _med_

Enables the COMFORT (base) driving mode in the Driving Experience Control menu. Standard COMFORT programme selection.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `FES_COMFORT_BASE`· source: firmware-token

### `3008/0/00100000b` — COMFORT PLUS driving mode available  ·  _med_

Enables the COMFORT PLUS (enhanced comfort) driving mode within the Driving Experience Control system.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `FES_COMFORT_PLUS`· source: firmware-token

### `3008/0/01000000b` — ECO PRO BASE driving mode available  ·  _med_

Enables the ECO PRO (base) driving mode in the Driving Experience Control menu. Base efficiency programme offering fuel-saving coaching.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `FES_ECO_BASE`· source: firmware-token

### `3008/0/10000000b` — ECO PRO PLUS driving mode available  ·  _med_

Enables the ECO PRO PLUS driving mode, which adds extended coasting/sailing and additional energy-saving measures beyond ECO PRO base.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `FES_ECO_PLUS`· source: firmware-token

### `3008/1/00000001b` — ECO PRO CUSTOM driving mode available  ·  _med_

Enables a user-configurable ECO PRO CUSTOM driving mode, letting the driver individually adjust ECO-related sub-systems.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `FES_ECO_CUSTOM`· source: firmware-token

### `3008/1/00000010b` — ADAPTIVE driving mode available  ·  _med_

Enables the ADAPTIVE driving mode, which dynamically adjusts suspension, steering, and drivetrain based on current driving style.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `FES_ADAPTIVE`· source: firmware-token

### `3008/1/00000100b` — SPORT mode: damper/chassis attenuation configurable  ·  _med_

When set, the suspension/chassis attenuation (damper) setting is individually adjustable within the SPORT driving mode configuration.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SPORT_CONF_ATTENUATION`· source: firmware-token

### `3008/1/00001000b` — SPORT mode: steering configurable  ·  _med_

When set, the steering weight/ratio is individually configurable within the SPORT driving mode.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SPORT_CONF_STEERING`· source: firmware-token

### `3008/1/00010000b` — SPORT mode: engine response configurable  ·  _med_

When set, the engine throttle/response mapping is individually configurable within the SPORT driving mode.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SPORT_CONF_ENGINE`· source: firmware-token

### `3008/1/01100000b` — SPORT mode: transmission type  ·  _high_

Identifies the gearbox type present, which determines which SPORT mode gear-shift configuration options are offered (manual vs automatic Sport programmes).

| value | meaning |
|---|---|
| `0` | Not set |
| `1` | Manual gearbox |
| `2` | Automatic gearbox |

default `00`· gate: FA-gated (depends on vehicle options)· token `SPORT_CONF_GEAR_TYPE`· source: firmware-token

### `3008/1/10000000b` — SPORT mode: driver seat configurable  ·  _med_

When set, the front driver's seat (bolster/position) is individually adjustable within the SPORT driving mode configuration.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SPORT_CONF_SEAT`· source: firmware-token

### `3008/2/00000001b` — SPORT mode: auto start/stop (MSA) configurable  ·  _med_

When set, the auto start/stop (MSA — Motor-Start-Automatik) function is individually selectable within the SPORT driving mode.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SPORT_CONF_MSA`· source: firmware-token

### `3008/2/00000010b` — ECO PRO mode: damper/chassis attenuation configurable  ·  _med_

When set, the suspension/chassis attenuation (damper) setting is individually adjustable within the ECO PRO driving mode configuration.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ECO_CONF_ATTENUATION`· source: firmware-token

### `3008/2/00000100b` — ECO PRO mode: steering configurable  ·  _med_

When set, the steering weight is individually configurable within the ECO PRO driving mode.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ECO_CONF_STEERING`· source: firmware-token

### `3008/2/00001000b` — ECO PRO mode: coasting/sailing configurable  ·  _med_

When set, the engine sailing/coasting function (engine-off coasting to save fuel) is individually selectable within the ECO PRO mode.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ECO_CONF_SAILING`· source: firmware-token

### `3008/2/00010000b` — ECO PRO mode: seat heating configurable  ·  _med_

When set, seat heating availability/behaviour is configurable within the ECO PRO driving mode (seat heating may be reduced to save energy).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ECO_CONF_SEATHEATING`· source: firmware-token

### `3008/2/00100000b` — ECO PRO mode: climate control configurable  ·  _med_

When set, the climate control (AC compressor / heating) setting is individually configurable within the ECO PRO mode.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ECO_CONF_CLIMATE`· source: firmware-token

### `3008/2/11000000b` — ECO PRO mode: lights and visibility scope  ·  _high_

Selects which energy consumers ECO PRO mode governs: either lights and visibility systems (e.g. rear defroster), or visibility systems only.

| value | meaning |
|---|---|
| `0` | Not set |
| `1` | Lights and visibility systems |
| `2` | Visibility systems only |

default `00`· gate: FA-gated (depends on vehicle options)· token `ECO_CONF_LIGHT_SIGHT`· source: firmware-token

### `3008/3/00000001b` — ECO PRO mode: speed limiter configurable  ·  _med_

When set, the speed limiter function is individually configurable within the ECO PRO driving mode (ECO speed cap).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ECO_CONF_LIMIT`· source: firmware-token

### `3008/3/00000010b` — ECO PRO mode: speed limit assistant (VZA) configurable  ·  _med_

When set, the speed limit assistant (VZA — Verkehrszeichen-Assistent / traffic-sign recognition) behaviour is configurable within ECO PRO mode.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ECO_CONF_VZA`· source: firmware-token

### `3008/3/00000100b` — ECO PRO mode: CID tips/hints active  ·  _high_

Controls whether ECO PRO tips and coaching hints are shown on the Central Information Display (CID). When inactive, the on-screen ECO coaching overlay is suppressed.

| value | meaning |
|---|---|
| `0` | Not active (no CID tips) |
| `1` | Active (show CID tips) |

default `00`· gate: FA-gated (depends on vehicle options)· token `ECO_CONF_CID_TIPPS`· source: firmware-token

### `3008/3/00001000b` — SPORT mode: co-driver seat configurable  ·  _med_

When set, the front passenger (co-driver) seat bolster/position is individually adjustable within the SPORT driving mode configuration.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SPORT_CONF_SEAT_CODRIVER`· source: firmware-token

### `3008/3/00010000b` — Driving Experience Control: reset configuration available  ·  _med_

When set, a reset option is offered in the Driving Experience Control configuration menu, allowing the user to revert all driving mode settings to factory defaults.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `FES_CONF_RESET`· source: firmware-token

### `3008/3/00100000b` — COMFORT PLUS mode: damper/chassis attenuation configurable  ·  _med_

When set, the suspension/chassis attenuation (damper) setting is individually adjustable within the COMFORT PLUS driving mode.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ECO_CONF_ATTENUATION_COMFPLUS`· source: firmware-token

### `3008/3/01000000b` — COMFORT PLUS mode: steering configurable  ·  _med_

When set, the steering weight/ratio is individually configurable within the COMFORT PLUS driving mode.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ECO_CONF_STEERING_COMFPLUS`· source: firmware-token

### `3008/3/10000000b` — ECO PRO mode: speed limit text display style  ·  _high_

Selects how the ECO PRO speed limit notification is presented on the display — as a hint/advisory text at activation, or as an active limit indicator while driving.

| value | meaning |
|---|---|
| `0` | Hint shown at activation (HINWEIS_BEI) |
| `1` | Limit shown while active (LIMIT_BEI) |

default `00`· gate: always (no FA gate)· token `ECO_CONF_LIMIT_TEXT`· source: firmware-token

### `3008/4/00000001b` — Stability control (DSC) mode-change popup  ·  _med_

When set, a popup/warning notification is displayed when the DSC (Dynamic Stability Control) mode is changed via the Driving Experience Control settings.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `STABILITY_CONTROL_POPUP`· source: firmware-token

### `3008/4/00000010b` — ECO PRO mode: auto start/stop (MSA) configurable  ·  _med_

When set, the auto start/stop (MSA) function is individually selectable within the ECO PRO driving mode.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ECO_CONF_MSA`· source: firmware-token

### `3008/4/00000100b` — Global coasting/sailing configurable  ·  _med_

When set, the engine sailing/coasting function is available as a global (vehicle-level) configurable option, not tied to a specific driving mode.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `GLOBAL_CONF_SAILING`· source: firmware-token

### `3008/4/00001000b` — Rolls-Royce DSC-OFF mode available  ·  _med_

Indicates that the DSC-OFF (Dynamic Stability Control fully off) mode is available. The 'RR' prefix in the token designates a Rolls-Royce vehicle variant; this flag is not applicable to standard xDrive or F-series vehicles.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `RR_DSCOFF_AVL`· source: firmware-token

### `3008/4/11110000b` — Undocumented field (FES byte 4, bits 7-4)  ·  _low_

Purpose not determined from available sources. A 4-bit field in the FES (Feature-Enable Set) coding page at byte 4, bits 7-4 (mask 0xF0). Active on this vehicle but no symbolic enum or individual token name is available.

token `FES byte 4 (4-bit field (00..00))`· source: inferred

### `3008/5/11111111b` — Undocumented field (FES bytes 5-77, multi-byte block)  ·  _low_

Purpose not determined from available sources at this granularity. A multi-byte block spanning bytes 5 through 77 of the FES (Feature-Enable Set) coding page. Individual named fields within this range (VIDEO_SPEEDLOCK_CONDITION, CONNECTED_DRIVE, NFC_SMART_ACCESS, A4A_SWT, IPCE_WEBSERVER, etc.) are resolved in other chunks; this single CAFD record covers the unresolved interior.

token `FES byte 5 (multi-byte value (syset Int/UInt8/16))`· source: inferred

### `3008/78/00001111b` — Undocumented field (FES byte 78, bits 3-0)  ·  _low_

Purpose not determined from available sources. A 4-bit field in the FES coding page at byte 78, bits 3-0 (mask 0x0F). Active on this vehicle but no symbolic enum or individual token name is available.

token `FES byte 78 (4-bit field (00..00))`· source: inferred

### `3008/78/00010000b` — ECO PRO hint display style  ·  _high_

Selects how ECO PRO mode activation hints are shown — as an advisory message at the point of activation (HINWEIS_BEI), or as an active limit indicator during driving (LIMIT_BEI).

| value | meaning |
|---|---|
| `0` | Hint/note shown at activation (HINWEIS_BEI) |
| `1` | Limit indicator shown while active (LIMIT_BEI) |

default `00`· gate: always (no FA gate)· token `ECO_PRO_HINT`· source: firmware-token

### `3008/78/00100000b` — ECO info display enabled  ·  _med_

When set, ECO PRO mode information (fuel saving indicators, efficiency data) is shown on the Central Information Display during ECO PRO operation.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· token `ECO_INFO_DISPLAY`· source: firmware-token

### `3008/78/01000000b` — Efficiency/dynamic coasting (sailing) available  ·  _high_

When active, the engine sailing/coasting function (engine-off free-roll to save fuel) is available as an efficiency-dynamic feature on this vehicle. Gate excludes Steptronic and certain market/type variants.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: NOT 205 Steptronic transmission / 812 Great Britain/Ireland version / 2TB Steptronic sport transmission / vehicle type-key attribute group (FP category 13; 23 type tokens, e.g. 1A10,1A11,1A12,1A31) / vehicle type-key attribute group (FP category 23; 265 type tokens, e.g. 11CK,11CL,11DE,12CK)· token `EFF_DYN_SAILING`· source: firmware-token

### `3008/78/10000000b` — ECO PRO tips/coaching enabled  ·  _med_

When set, ECO PRO driving tips and efficiency coaching messages are enabled and displayed to the driver during ECO PRO operation.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· token `ECO_TIPPS`· source: firmware-token

### `3008/79/00000001b` — ECO PRO route function enabled  ·  _med_

When set, the ECO PRO navigation route optimisation function (fuel-efficient routing) is enabled, allowing the system to suggest or follow more economical routes.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ECO_ROUTE`· source: firmware-token

### `3008/79/00000010b` — ECO PRO speed limit function enabled  ·  _med_

When set, the ECO PRO speed limit/cap function is enabled, providing a driver-configurable top-speed limit within ECO PRO mode to maximise efficiency.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: always (no FA gate)· token `ECO_LIMIT`· source: firmware-token

### `3008/79/00000100b` — ECO PRO mode enabled  ·  _med_

Master enable for the ECO PRO driving mode. When set, ECO PRO appears as a selectable mode in the Driving Experience Control menu.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: always (no FA gate)· token `ECO_MODE`· source: firmware-token

### `3008/79/00001000b` — ECO PRO mode configurable by user  ·  _med_

When set, the ECO PRO mode parameters (climate, seat heating, etc.) are user-adjustable via the settings menu, enabling the ECO PRO Individual/Custom sub-mode.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· token `ECO_MODE_CONF`· source: firmware-token

### `3008/79/00010000b` — Driving Experience Control UI naming scheme  ·  _high_

Selects the naming/labelling convention used in the Driving Experience Control menu — either the post-July 2011 (current) naming or the earlier (pre-July 2011) naming scheme.

| value | meaning |
|---|---|
| `0` | From July 2011 onward (AB_0711) |
| `1` | Before July 2011 (BIS_0711) |

default `00`· gate: always (no FA gate)· token `FDS_NAMING_MODE`· source: firmware-token

### `3008/79/00100000b` — Driving Experience Control popup deactivated  ·  _med_

When set, the introductory/welcome popup shown when the Driving Experience Control menu is first accessed is suppressed.

| value | meaning |
|---|---|
| `0` | Off/inactive (popup shown) |
| `1` | On/active (popup suppressed) |

default `00`· token `FDS_POPUP_DEACTIVATE`· source: firmware-token

### `3008/79/11000000b` — Driving mode switch display  ·  _med_

Chooses how the head unit responds when the driver uses the driving mode switch: no display, a pop-up showing the selected mode, or that pop-up plus pages for configuring the modes.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Pop-up only |
| `2` | Pop-up and settings pages |

default `00`· gate: vehicle type-key attribute group (FP category 13; 7 type tokens, e.g. 1J31,1J32,1J33,2T73) / vehicle type-key attribute group (FP category 25; 27 type tokens, e.g. 11CK,11CL,11DE,12CK) / vehicle type-key attribute group (FP category 25; 3 type tokens, e.g. 1J31,1J32,1J33)· token `MACRO_FDS`· source: firmware-token

## Datagroup 0x3009 (74 parameters)

### `3009/0/11111111b` — EfficientDynamics drivetrain type (ECO display)  ·  _high_

Selects the powertrain variant used by the EfficientDynamics / ECO display subsystem to determine which energy-flow gauges and history charts to render. Must match the vehicle's actual powertrain; conventional petrol is value 0.

| value | meaning |
|---|---|
| `0` | Conventional petrol (KONV_OTTO) |
| `1` | Conventional diesel (KONV_DIESEL) |
| `2` | Battery-electric with range extender (BEV_REX) |
| `3` | Hybrid petrol (HEV_OTTO) |
| `4` | Hybrid diesel (HEV_DIESEL) |
| `5` | Plug-in hybrid petrol (PHEV_OTTO) |
| `6` | Plug-in hybrid diesel (PHEV_DIESEL) |
| `7` | Battery-electric without range extender (BEV_OHNE_REX) |

default `00`· gate: FA-gated (depends on vehicle options)· token `ECO_TYPE_DRIVETRAIN`· source: firmware-token

### `3009/1/00000001b` — ASD (active sound design) installed  ·  _med_

Indicates whether the vehicle is equipped with Active Sound Design (ASD) — the electronic engine sound synthesis system. When set, ASD sound profile fields in this page are evaluated.

| value | meaning |
|---|---|
| `0` | Not installed |
| `1` | Installed |

default `00`· gate: FA-gated (depends on vehicle options)· token `ASD_CONFIGURATION`· source: firmware-token

### `3009/1/00000010b` — ASD sound output disable  ·  _med_

When active, suppresses ASD audio output — the artificial engine sound is muted regardless of drive mode. Allows the system to be installed but silenced for specific market/variant configurations.

| value | meaning |
|---|---|
| `0` | ASD sound enabled |
| `1` | ASD sound off |

default `00`· gate: FA-gated (depends on vehicle options)· token `ASD_SOUND_OFF`· source: firmware-token

### `3009/1/00000100b` — ASD sound profile 1 available  ·  _high_

Enables ASD engine-sound profile slot 1. Each ASD_SOUND_n bit makes a specific synthesized sound profile available for selection in the drive-mode setup.

| value | meaning |
|---|---|
| `0` | Not active (NICHT_AKTIV) |
| `1` | Active (AKTIV) |

default `00`· gate: always (no FA gate)· token `ASD_SOUND_1`· source: firmware-token

### `3009/1/00001000b` — ASD sound profile 2 available  ·  _med_

Enables ASD engine-sound profile slot 2. Corresponds to a second synthesized engine-sound variant selectable in drive modes.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: always (no FA gate)· token `ASD_SOUND_2`· source: firmware-token

### `3009/1/00010000b` — ASD sound profile 3 available  ·  _med_

Enables ASD engine-sound profile slot 3. Third synthesized engine-sound variant for drive-mode selection.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: always (no FA gate)· token `ASD_SOUND_3`· source: firmware-token

### `3009/1/00100000b` — ASD sound profile 4 available  ·  _med_

Enables ASD engine-sound profile slot 4. Fourth synthesized engine-sound variant for drive-mode selection.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ASD_SOUND_4`· source: firmware-token

### `3009/1/01000000b` — EfficientDynamics history zoom  ·  _high_

Enables zoom interaction on the EfficientDynamics consumption-history bar chart, allowing the driver to expand individual time segments for detail.

| value | meaning |
|---|---|
| `0` | Zoom disabled (NICHT_AKTIV) |
| `1` | Zoom enabled (AKTIV) |

default `00`· gate: always (no FA gate)· token `HIST_ZOOM`· source: firmware-token

### `3009/1/10000000b` — EfficientDynamics drive-mode name display  ·  _med_

Controls whether the FDS (Fahrdynamiksystem / drive-mode system) mode name is shown as a text label in the EfficientDynamics history view. FA-gated: suppressed on certain vehicle type-key groups (electrified/entry variants).

| value | meaning |
|---|---|
| `0` | Mode name hidden |
| `1` | Mode name shown |

default `00`· gate: NOT vehicle type-key attribute group (FP category 13; 7 type tokens, e.g. 1J31,1J32,1J33,2T73) / vehicle type-key attribute group (FP category 25; 27 type tokens, e.g. 11CK,11CL,11DE,12CK) / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31) / vehicle type-key attribute group (FP category 25; 3 type tokens, e.g. 1J31,1J32,1J33)· token `HIST_FDS_MODE_NAME`· source: firmware-token

### `3009/2/00000001b` — EfficientDynamics drive-mode colour coding  ·  _med_

Enables colour-coding of FDS (drive-mode) segments in the EfficientDynamics history chart, distinguishing Comfort/Sport/Eco segments by bar colour.

| value | meaning |
|---|---|
| `0` | Colour coding disabled |
| `1` | Colour coding enabled |

default `00`· gate: NOT vehicle type-key attribute group (FP category 13; 7 type tokens, e.g. 1J31,1J32,1J33,2T73) / vehicle type-key attribute group (FP category 25; 27 type tokens, e.g. 11CK,11CL,11DE,12CK) / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31) / vehicle type-key attribute group (FP category 25; 3 type tokens, e.g. 1J31,1J32,1J33)· token `HIST_FDS_MODE_COLOR`· source: firmware-token

### `3009/2/00000110b` — EfficientDynamics average consumption display mode  ·  _med_

Selects which average-consumption value is shown in the history view. Numeric code; no symbolic names in firmware.

default `00`· gate: FA-gated (depends on vehicle options)· token `HIST_CONSUMP_AVERAGE`· source: firmware-token

### `3009/2/00001000b` — Drive Experience statistics reset  ·  _high_

When enabled, allows the Drive Experience trip statistics to be reset by the driver from the iDrive menu.

| value | meaning |
|---|---|
| `0` | Not available (NICHT_AKTIV) |
| `1` | Available (AKTIV) |

default `00`· gate: FA-gated (depends on vehicle options)· token `DRIVE_EXP_RESET`· source: firmware-token

### `3009/2/00010000b` — Drive Experience brake-regen widget  ·  _high_

Enables the brake-regeneration (BRW = Bremsenrückgewinnung) widget in the Drive Experience / EfficientDynamics display, showing energy recovered under braking.

| value | meaning |
|---|---|
| `0` | Widget disabled (NICHT_AKTIV) |
| `1` | Widget enabled (AKTIV) |

default `00`· gate: always (no FA gate)· token `DRIVE_EXP_BRW`· source: firmware-token

### `3009/2/00100000b` — Drive Experience feature available  ·  _med_

Master enable for the Drive Experience analysis feature. When active, the Drive Experience page is accessible in the iDrive menu. FA-gated: suppressed on specific base vehicle type-key group.

| value | meaning |
|---|---|
| `0` | Not available |
| `1` | Available |

default `00`· gate: NOT vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `DRIVE_EXPERIENCE`· source: firmware-token

### `3009/2/01000000b` — EV charging hospitality feature  ·  _med_

Enables the 'charging hospitality' function for plug-in vehicles — locating and routing to charging stations with amenities. Only relevant for PHEV/BEV variants.

| value | meaning |
|---|---|
| `0` | Inactive (INAKTIV) |

default `00`· gate: FA-gated (depends on vehicle options)· token `CHARGING_HOSPITALITY`· source: firmware-token

### `3009/2/10000000b` — EfficientDynamics history UI variant (DXE)  ·  _high_

Selects which generation of the EfficientDynamics history display layout (DXE = Driving Experience) is used. Controls whether the newer or older bar-chart variant is rendered.

| value | meaning |
|---|---|
| `0` | New DXE layout (DXE_NEW) |
| `1` | Legacy DXE layout (DXE_OLD) |

default `00`· token `HIST_PRESENT_VARIANT_DXE`· source: firmware-token

### `3009/3/00000001b` — Driving style analysis animation  ·  _med_

Enables the animated graphical display in the Fahrstilanalyse (driving style analysis) view — shows leaf/arc animations reflecting eco-driving score.

| value | meaning |
|---|---|
| `0` | Animation disabled |
| `1` | Animation enabled |

default `00`· gate: always (no FA gate)· token `FAHRSTILANALYSE_ANIMATION`· source: firmware-token

### `3009/3/01111110b` — Undocumented field (EFFICIENT_DYNAMICS byte 3, 6-bit)  ·  _low_

Purpose not determined from available sources. A 6-bit packed field in the EFFICIENT_DYNAMICS coding page whose individual sub-fields are not individually pinned by the firmware name table. Default 0x00.

token `EFFICIENT_DYNAMICS byte 3 (6-bit field (00..00))`· source: inferred

### `3009/3/10000000b` — Driving style analysis feature available  ·  _med_

Master enable for the Fahrstilanalyse (driving style analysis) page — an EfficientDynamics sub-page scoring driver eco-behaviour. FA-gated: suppressed on specific base vehicle type-key group.

| value | meaning |
|---|---|
| `0` | Not available |
| `1` | Available |

default `00`· gate: NOT vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `FAHRSTILANALYSE`· source: firmware-token

### `3009/4/00000111b` — EfficientDynamics history Y-axis scale step 6  ·  _med_

Sets the sixth configurable Y-axis graduation step for the EfficientDynamics consumption bar chart. This is one of a series of scale-step fields (HIST_Y_SCALE_STEP_1.6) that define chart grid lines. Numeric value; no symbolic names.

default `00`· gate: always (no FA gate)· token `HIST_Y_SCALE_STEP_6`· source: firmware-token

### `3009/4/00001000b` — EfficientDynamics petrol consumption bar visible  ·  _high_

Enables the petrol/gas consumption column in the EfficientDynamics history bar chart. FA-gated on KOMBI extended equipment or specific vehicle type-key group.

| value | meaning |
|---|---|
| `1` | Bar visible (AKTIV) |

default `00`· gate: 6WA KOMBI with extended equipment specification / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `HIST_GAS_CONSUMP`· source: firmware-token

### `3009/4/00010000b` — Sailing (coasting) counter display  ·  _med_

Enables the sailing/coasting counter widget in the EfficientDynamics view, showing the cumulative duration or count of engine-off coast events (BMW 'Sailing' function).

| value | meaning |
|---|---|
| `0` | Not shown |
| `1` | Shown |

default `00`· token `SAILING_COUNTER`· source: firmware-token

### `3009/4/01100000b` — Electric drive menu  ·  _med_

Controls whether the head unit offers its electric drive menu, and which version: the one for plug-in hybrids or the one for electric cars with a range extender (REX). Set it to match the car's powertrain.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Plug-in hybrid menu |
| `2` | Menu for range-extender cars |

default `00`· gate: always (no FA gate)· token `EV_MENU_AVAILABLE`· source: firmware-token

### `3009/4/10000000b` — PHEV energy management (VEM) available  ·  _med_

Enables the Vehicle Energy Management (VEM) display for plug-in hybrid variants, showing the charge/discharge balance between petrol and electric drive. Inactive on non-PHEV vehicles.

| value | meaning |
|---|---|
| `0` | Not available |
| `1` | Available |

default `00`· gate: FA-gated (depends on vehicle options)· token `VEM_PHEV_AVAILABLE`· source: firmware-token

### `3009/5/11111111b` — Consumption chart top value (L/100 km)  ·  _high_

Sets the value at the top of the vertical axis of the EfficientDynamics consumption history chart when fuel consumption is shown in L/100 km. The chart's bars and its average line are scaled to it, and anything higher is cut off at the top.

| value | meaning |
|---|---|
| `0` | Default (20 L/100 km) |

Number: raw 1–255 × 1 + 0 L/100 km; typical 10, 15, 20, 30

default `14`· token `HIST_GAS_CONSUMP_SCALE_1`· source: firmware-trace

### `3009/6/11111111b` — Consumption chart top value (mpg, UK)  ·  _high_

Sets the value at the top of the vertical axis of the EfficientDynamics consumption history chart when fuel consumption is shown in UK (imperial) miles per gallon. The chart's bars and its average line are scaled to it, and anything higher is cut off at the top.

| value | meaning |
|---|---|
| `0` | Default (80 mpg) |

Number: raw 1–255 × 1 + 0 mpg; typical 60, 80, 100

default `50`· gate: vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `HIST_GAS_CONSUMP_SCALE_2`· source: firmware-trace

### `3009/7/11111111b` — Consumption chart top value (mpg, US)  ·  _high_

Sets the value at the top of the vertical axis of the EfficientDynamics consumption history chart when fuel consumption is shown in US miles per gallon. The chart's bars and its average line are scaled to it, and anything higher is cut off at the top.

| value | meaning |
|---|---|
| `0` | Default (60 mpg) |

Number: raw 1–255 × 1 + 0 mpg; typical 40, 60, 80

default `3C`· gate: vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `HIST_GAS_CONSUMP_SCALE_3`· source: firmware-trace

### `3009/8/11111111b` — Consumption chart top value (km/L)  ·  _high_

Sets the value at the top of the vertical axis of the EfficientDynamics consumption history chart when fuel consumption is shown in km/L. The chart's bars and its average line are scaled to it, and anything higher is cut off at the top.

| value | meaning |
|---|---|
| `0` | Default (40 km/L) |

Number: raw 1–255 × 1 + 0 km/L; typical 20, 30, 50

default `28`· gate: vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `HIST_GAS_CONSUMP_SCALE_4`· source: firmware-trace

### `3009/9/00000011b` — EfficientDynamics hybrid type  ·  _high_

Specifies the hybrid architecture used by this vehicle for EfficientDynamics display purposes. Determines which energy-flow view (pure ICE vs belt/axle hybrid vs parallel hybrid) is rendered.

| value | meaning |
|---|---|
| `0` | No hybrid (KEIN_HYBRID) |
| `1` | Belt/axle hybrid (ACHSHYBRID) |
| `2` | Parallel hybrid (PARALLELHYBRID) |

default `00`· gate: FA-gated (depends on vehicle options)· token `EFF_DYN_TYPE_HYBRID`· source: firmware-token

### `3009/9/00001100b` — EfficientDynamics drivetrain layout  ·  _high_

Specifies the driven-axle layout (rear-wheel, front-wheel, or all-wheel drive) for the EfficientDynamics display. Determines power-flow animation direction in the energy diagram.

| value | meaning |
|---|---|
| `0` | Rear-wheel drive (HECK) |
| `1` | Front-wheel drive (FRONT) |
| `2` | All-wheel drive (ALLRAD) |

default `00`· gate: vehicle type-key attribute group (FP category 128; 192 type tokens, e.g. 11CK,11CL,11DE,12CK)· token `EFF_DYN_TYPE_DRIVETRAIN`· source: firmware-token

### `3009/9/00010000b` — Sport display on central display  ·  _med_

Makes the sport display available on the central display, as part of the EfficientDynamics functions. Enabled at the factory on some models with Navigation Business (S606), Navigation Professional (S609) or Radio BMW Professional (S663).

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 606 Navigation system Business / 609 Professional navigation system / 663 Radio BMW Professional / vehicle type-key attribute group (FP category 1; 71 type tokens, e.g. 1A10,1A11,1A12,1A31) / vehicle type-key attribute group (FP category 1; 61 type tokens, e.g. 1D11,1D12,1D31,1D32) / vehicle type-key attribute group (FP category 1; 65 type tokens, e.g. 11CK,11DE,12CK,12DE) / vehicle type-key attribute group (FP category 1; 55 type tokens, e.g. 11CL,12CL,1K51,1K52) / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `EFF_DYN_SPORT_CID`· source: firmware-token

### `3009/9/00100000b` — Sport display unit  ·  _low_

Setting for the sport display pages. Best left unchanged.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: always (no FA gate)· token `EFF_DYN_SPORT_UNIT`· source: firmware-token

### `3009/9/11000000b` — State-of-charge display signal source  ·  _high_

Selects the CAN signal source used to display battery state-of-charge (SoC) in the EfficientDynamics view. Only relevant for hybrid/electric variants.

| value | meaning |
|---|---|
| `0` | No SoC signal (KEIN_SIGNAL) |
| `1` | HEV SoC signal (HEV_SIGNAL) |
| `2` | PHEV SoC signal (PHEV_SIGNAL) |

default `00`· gate: FA-gated (depends on vehicle options)· token `SOC_DISP_SIGNAL`· source: firmware-token

### `3009/10/00000001b` — Seat heating as energy consumer (EfficientDynamics)  ·  _med_

Registers the seat heating system as a tracked energy consumer in the EfficientDynamics display, contributing to the auxiliary load breakdown. Only relevant on equipped vehicles.

| value | meaning |
|---|---|
| `0` | Not tracked |
| `1` | Tracked as consumer |

default `00`· gate: FA-gated (depends on vehicle options)· token `SEAT_HEATING_CONSUMER`· source: firmware-token

### `3009/10/00000110b` — Charging cable port position  ·  _high_

Specifies which side of the vehicle the AC charging port is located on. Controls charging-port indicator graphics in the iDrive EV/PHEV menus.

| value | meaning |
|---|---|
| `0` | No charge port (KEIN_STECKER) |
| `1` | Left side (LINKS) |
| `2` | Right side (RECHTS) |

default `00`· gate: always (no FA gate)· token `CHARGING_CABLE_SIDE`· source: firmware-token

### `3009/10/00001000b` — Instrument cluster SoC display selection  ·  _med_

When enabled, the battery state-of-charge (SoC) percentage is displayed on the instrument cluster (KI = Kombi-Instrument) via a dedicated selection/override. Hybrid/EV-specific.

| value | meaning |
|---|---|
| `0` | Not shown on cluster |
| `1` | SoC shown on cluster |

default `00`· gate: FA-gated (depends on vehicle options)· token `KI_SELECTION_SOC`· source: firmware-token

### `3009/10/01110000b` — EfficientDynamics hybrid forecast display variant  ·  _high_

Selects which variant of the hybrid energy-forecast view is displayed in the EfficientDynamics section. Used on HEV/PHEV models to show predictive charge-depletion or route-based energy planning.

| value | meaning |
|---|---|
| `1` | Forecast variant 1 (WERT_1) |
| `2` | Forecast variant 2 (WERT_2) |

default `01`· gate: FA-gated (depends on vehicle options)· token `EFF_DYN_FORECAST_HYB`· source: firmware-token

### `3009/10/10000000b` — Hybrid consumption bar in history chart  ·  _med_

Enables a separate hybrid-mode (electric) consumption bar alongside the petrol bar in the EfficientDynamics history chart. Only meaningful on HEV/PHEV variants.

| value | meaning |
|---|---|
| `0` | Not shown |
| `1` | Shown |

default `00`· gate: FA-gated (depends on vehicle options)· token `HIST_HYB_CONSUMP`· source: firmware-token

### `3009/11/11111111b` — Hybrid consumption history scale — step 1  ·  _med_

First Y-axis reference scale value for the hybrid (electric) consumption history chart. Default 0x14 (=20 dec). Numeric; no symbolic names.

default `14`· token `HIST_HYB_CONSUMP_SCALE_1`· source: firmware-token

### `3009/12/11111111b` — Hybrid consumption history scale — step 2  ·  _med_

Second Y-axis reference scale value for the hybrid consumption history chart. Default 0x14 (=20 dec). Numeric; no symbolic names.

default `14`· token `HIST_HYB_CONSUMP_SCALE_2`· source: firmware-token

### `3009/13/11111111b` — Hybrid consumption history scale — step 3  ·  _med_

Third Y-axis reference scale value for the hybrid consumption history chart. Default 0x1E (=30 dec). Numeric; no symbolic names.

default `1E`· token `HIST_HYB_CONSUMP_SCALE_3`· source: firmware-token

### `3009/14/00000001b` — Hybrid / EV consumption chart display switch  ·  _med_

Enables the ability to toggle between hybrid and EV consumption views in the EfficientDynamics history display. Allows switching between PHEV electric and petrol history segments.

| value | meaning |
|---|---|
| `0` | Switch not available |
| `1` | Switch available |

default `00`· gate: FA-gated (depends on vehicle options)· token `HIST_HYB_CONSUMP_SWITCH`· source: firmware-token

### `3009/14/00000010b` — BEV consumption bar in history chart  ·  _med_

Enables the battery-electric vehicle (BEV) energy consumption bar in the EfficientDynamics history chart. Only relevant for BEV or PHEV-in-EV-mode operation.

| value | meaning |
|---|---|
| `0` | Not shown |
| `1` | Shown |

default `00`· gate: FA-gated (depends on vehicle options)· token `HIST_BEV_CONSUMP`· source: firmware-token

### `3009/14/00000100b` — Condition check feature available  ·  _med_

Enables the vehicle condition check function accessible from the EfficientDynamics / vehicle status page. When active, driver can initiate a readiness/health check from the iDrive menu.

| value | meaning |
|---|---|
| `0` | Not available |
| `1` | Available |

default `00`· gate: FA-gated (depends on vehicle options)· token `CONDITION_CHECK`· source: firmware-token

### `3009/14/00001000b` — EfficientDynamics system display on CID  ·  _med_

Enables the overall EfficientDynamics system display widget on the Central Information Display (CID). When active, the EfficientDynamics tile/page is available in the iDrive main menu.

| value | meaning |
|---|---|
| `0` | Not available |
| `1` | Available |

default `00`· gate: always (no FA gate)· token `EFF_DYN_SYS_CID`· source: firmware-token

### `3009/14/11110000b` — Undocumented field (EFFICIENT_DYNAMICS byte 14, 4-bit)  ·  _low_

Purpose not determined from available sources. A 4-bit packed field in the EFFICIENT_DYNAMICS coding page; individual sub-fields not individually pinned by the firmware name table. Default 0x00.

token `EFFICIENT_DYNAMICS byte 14 (4-bit field (00..00))`· source: inferred

### `3009/15/11111111b` — Consumption chart top value (kWh/100 km)  ·  _high_

Sets the value at the top of the vertical axis of the EfficientDynamics consumption history chart when electric consumption is shown in kWh/100 km. The chart's bars and its average line are scaled to it, and anything higher is cut off at the top.

| value | meaning |
|---|---|
| `0` | Default (50 kWh/100 km) |

Number: raw 1–255 × 1 + 0 kWh/100 km; typical 30, 40, 50

default `32`· token `HIST_BEV_CONSUMP_SCALE_1`· source: firmware-trace

### `3009/16/11111111b` — Consumption chart top value (mi/kWh)  ·  _high_

Sets the value at the top of the vertical axis of the EfficientDynamics consumption history chart when electric consumption is shown in mi/kWh. The chart's bars and its average line are scaled to it, and anything higher is cut off at the top.

| value | meaning |
|---|---|
| `0` | Default (10 mi/kWh) |

Number: raw 1–255 × 1 + 0 mi/kWh; typical 5, 8, 10

default `05`· token `HIST_BEV_CONSUMP_SCALE_2`· source: firmware-trace

### `3009/17/11111111b` — Consumption chart top value (km/kWh)  ·  _high_

Sets the value at the top of the vertical axis of the EfficientDynamics consumption history chart when electric consumption is shown in km/kWh. The chart's bars and its average line are scaled to it, and anything higher is cut off at the top.

| value | meaning |
|---|---|
| `0` | Default (15 km/kWh) |

Number: raw 1–255 × 1 + 0 km/kWh; typical 8, 10, 15

default `0A`· token `HIST_BEV_CONSUMP_SCALE_3`· source: firmware-trace

### `3009/18/11111111b` — BEV recuperation history scale — step 1  ·  _med_

First Y-axis reference scale value for the BEV regenerative-braking (recuperation) history chart. Default 0x14 (=20 dec). Numeric; no symbolic names.

default `14`· token `HIST_BEV_RECUP_SCALE_1`· source: firmware-token

### `3009/19/11111111b` — BEV recuperation history scale — step 2  ·  _med_

Second Y-axis reference scale value for the BEV regenerative-braking history chart. Default 0x14 (=20 dec). Observed variant value: 20. Numeric; no symbolic names.

default `14`· token `HIST_BEV_RECUP_SCALE_2`· source: firmware-token

### `3009/20/11111111b` — BEV recuperation history scale — step 3  ·  _med_

Third Y-axis reference scale value for the BEV regenerative-braking history chart. Default 0x1E (=30 dec). Observed variant value: 30. Numeric; no symbolic names.

default `1E`· token `HIST_BEV_RECUP_SCALE_3`· source: firmware-token

### `3009/21/00000111b` — EfficientDynamics history Y-axis scale step 1  ·  _med_

First configurable Y-axis graduation step for the EfficientDynamics consumption bar chart. Part of the HIST_Y_SCALE_STEP_1.6 series defining chart scale. Numeric value 0.4; no symbolic names.

default `00`· gate: FA-gated (depends on vehicle options)· token `HIST_Y_SCALE_STEP_1`· source: firmware-token

### `3009/21/00111000b` — EfficientDynamics history Y-axis scale step 2  ·  _med_

Second configurable Y-axis graduation step for the EfficientDynamics consumption bar chart. Numeric value 0.4; no symbolic names.

default `00`· gate: FA-gated (depends on vehicle options)· token `HIST_Y_SCALE_STEP_2`· source: firmware-token

### `3009/21/11000000b` — Undocumented field (EFFICIENT_DYNAMICS byte 21, 2-bit)  ·  _low_

Purpose not determined from available sources. A 2-bit packed field in the EFFICIENT_DYNAMICS coding page; not in the syset enum dictionary and not individually named in the firmware name table. Default 0x00.

token `EFFICIENT_DYNAMICS byte 21 (2-bit field (00..00))`· source: inferred

### `3009/22/00000111b` — EfficientDynamics history Y-axis scale step 3  ·  _med_

Third configurable Y-axis graduation step for the EfficientDynamics consumption bar chart. Numeric value 0.4; no symbolic names.

default `00`· gate: FA-gated (depends on vehicle options)· token `HIST_Y_SCALE_STEP_3`· source: firmware-token

### `3009/22/00111000b` — EfficientDynamics history Y-axis scale step 4  ·  _med_

Fourth configurable Y-axis graduation step for the EfficientDynamics consumption bar chart. Numeric value 0.4; no symbolic names.

default `00`· gate: FA-gated (depends on vehicle options)· token `HIST_Y_SCALE_STEP_4`· source: firmware-token

### `3009/22/11000000b` — Undocumented field (EFFICIENT_DYNAMICS byte 22, 2-bit)  ·  _low_

Purpose not determined from available sources. A 2-bit packed field in the EFFICIENT_DYNAMICS coding page; not in the syset enum dictionary and not individually named in the firmware name table. Default 0x00.

token `EFFICIENT_DYNAMICS byte 22 (2-bit field (00..00))`· source: inferred

### `3009/23/00000111b` — EfficientDynamics history Y-axis scale step 5  ·  _med_

Fifth configurable Y-axis graduation step for the EfficientDynamics consumption bar chart. Numeric value; no symbolic names.

default `00`· gate: always (no FA gate)· token `HIST_Y_SCALE_STEP_5`· source: firmware-token

### `3009/23/00001000b` — EfficientDynamics future (predictive) segment available  ·  _med_

Enables a predictive/future segment in the EfficientDynamics consumption history chart, showing expected future consumption based on navigation route data.

| value | meaning |
|---|---|
| `0` | Not available |
| `1` | Available |

default `00`· gate: FA-gated (depends on vehicle options)· token `HIST_FUTURE`· source: firmware-token

### `3009/23/00010000b` — EfficientDynamics current-trip segment shown  ·  _med_

Enables display of the current (present) trip segment in the EfficientDynamics consumption history chart, showing real-time consumption for the ongoing journey.

| value | meaning |
|---|---|
| `0` | Not shown |
| `1` | Shown |

default `00`· token `HIST_PRESENT`· source: firmware-token

### `3009/23/00100000b` — EfficientDynamics past-trips segment shown  ·  _med_

Enables display of the historical (past trips) segment in the EfficientDynamics consumption history chart. FA-gated on KOMBI extended equipment or specific vehicle type-key group.

| value | meaning |
|---|---|
| `0` | Not shown |
| `1` | Shown |

default `00`· gate: 6WA KOMBI with extended equipment specification / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `HIST_PAST`· source: firmware-token

### `3009/23/01000000b` — EfficientDynamics past-trips average consumption line  ·  _med_

Enables the average consumption reference line overlaid on the past-trips bars in the EfficientDynamics history chart, giving a visual benchmark across historical trips.

| value | meaning |
|---|---|
| `0` | Not shown |
| `1` | Shown |

default `00`· gate: always (no FA gate)· token `HIST_PAST_AVERAGE_CONSUMP`· source: firmware-token

### `3009/23/10000000b` — EfficientDynamics active bar highlight in past-trips view  ·  _med_

When enabled, the currently selected (active) bar in the past-trips consumption history is highlighted/underlined to distinguish it from surrounding bars.

| value | meaning |
|---|---|
| `0` | No highlight |
| `1` | Highlight shown |

default `00`· gate: FA-gated (depends on vehicle options)· token `HIST_PAST_ACT_BAR`· source: firmware-token

### `3009/24/00000001b` — EfficientDynamics active bar accent highlight  ·  _med_

Enables an additional accent highlight on the active bar in the past-trips history chart — distinct from the base bar highlight, typically used for a top-border or colour accent.

| value | meaning |
|---|---|
| `0` | Not shown |
| `1` | Shown |

default `00`· gate: FA-gated (depends on vehicle options)· token `HIST_PAST_ACT_BAR_HIGHLIGHT`· source: firmware-token

### `3009/24/00000010b` — EfficientDynamics past-trips bar colour — petrol  ·  _med_

Enables distinct colour coding for petrol/gas consumption bars in the past-trips EfficientDynamics history chart, distinguishing petrol segments from electric or hybrid segments.

| value | meaning |
|---|---|
| `0` | No colour differentiation |
| `1` | Petrol bars coloured |

default `00`· gate: always (no FA gate)· token `HIST_PAST_BAR_COLOUR_GAS`· source: firmware-token

### `3009/24/00000100b` — EfficientDynamics past-trips bar colour — PHEV electric  ·  _med_

Enables distinct colour coding for plug-in hybrid (PHEV) electric-mode consumption bars in the past-trips EfficientDynamics history chart. Only relevant on PHEV variants.

| value | meaning |
|---|---|
| `0` | No colour differentiation |
| `1` | PHEV electric bars coloured |

default `00`· gate: FA-gated (depends on vehicle options)· token `HIST_PAST_BAR_COLOUR_PHEV`· source: firmware-token

### `3009/24/00001000b` — EfficientDynamics past-trips cookie/marker  ·  _med_

Enables a 'cookie' marker overlay on individual bars in the past-trips history chart — a small icon or badge indicating a specific event or milestone trip (e.g. refuelling, charge cycle).

| value | meaning |
|---|---|
| `0` | Markers not shown |
| `1` | Markers shown |

default `00`· gate: FA-gated (depends on vehicle options)· token `HIST_PAST_COOKIE`· source: firmware-token

### `3009/24/00110000b` — EfficientDynamics MSA (auto start/stop) counter display  ·  _high_

Controls how the MSA (Motor-Stopp-Automatik / auto start/stop) event counter is shown in the past-trips EfficientDynamics history. Can show with or without seconds breakdown, or be hidden.

| value | meaning |
|---|---|
| `0` | Counter off (AUS) |
| `1` | Counter with seconds (MIT_SEK) |
| `2` | Counter without seconds (OHNE_SEK) |

default `00`· gate: always (no FA gate)· token `HIST_PAST_COUNTER_MSA`· source: firmware-token

### `3009/24/01000000b` — EfficientDynamics sailing/coasting counter in history  ·  _med_

Enables display of the sailing (engine-off coasting) event counter in the past-trips EfficientDynamics history chart, showing how many coasting events occurred per segment.

| value | meaning |
|---|---|
| `0` | Counter not shown |
| `1` | Counter shown |

default `00`· token `HIST_PAST_COUNTER_SAILING`· source: firmware-token

### `3009/24/10000000b` — EfficientDynamics eDrive counter in history  ·  _high_

Enables display of the eDrive (electric-mode driving) event counter in the past-trips EfficientDynamics history chart. Only meaningful on PHEV/BEV variants. Default: not active.

| value | meaning |
|---|---|
| `0` | Counter not shown (NICHT_AKTIV) |

default `00`· gate: FA-gated (depends on vehicle options)· token `HIST_PAST_COUNTER_EDRIVE`· source: firmware-token

### `3009/25/00000001b` — EfficientDynamics past-trips history reset available  ·  _med_

Enables the driver-accessible option to reset the past-trips EfficientDynamics consumption history from the iDrive menu.

| value | meaning |
|---|---|
| `0` | Reset not available |
| `1` | Reset available |

default `00`· gate: always (no FA gate)· token `HIST_PAST_RESET`· source: firmware-token

### `3009/25/11111110b` — Undocumented field (EFFICIENT_DYNAMICS byte 25, 7-bit)  ·  _low_

Purpose not determined from available sources. A 7-bit packed field in the EFFICIENT_DYNAMICS coding page; not individually named in the firmware name table, no syset enum, no resolved_unnamed entry. Default 0x00.

token `EFFICIENT_DYNAMICS byte 25 (7-bit field (00..00))`· source: inferred

### `3009/26/11111111b` — Undocumented multi-byte field (EFFICIENT_DYNAMICS bytes 26–75)  ·  _low_

Purpose not determined from available sources. A multi-byte value spanning bytes 26–75 (50 bytes) in the EFFICIENT_DYNAMICS coding page; not individually named in the firmware name table, no syset enum. Likely contains additional scale parameters, padding, or reserved space not fully mapped by the available decoder.

token `EFFICIENT_DYNAMICS byte 26 (multi-byte value (syset Int/UInt8/16))`· source: inferred

## Datagroup 0x300A (62 parameters)

### `300A/0/00000111b` — Driver assistance display stage  ·  _med_

Selects how the head unit presents driver assistance warnings, from simple status panels to one of two full display concepts. Best left unchanged.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Status panels only |
| `2` | Preliminary version |
| `3` | Full version 1 |
| `4` | Full version 2 |

default `00`· gate: FA-gated (depends on vehicle options)· token `INSZENIERUNG`· source: firmware-trace

### `300A/0/00011000b` — Forward collision warning (AUFFAHRWARNUNG)  ·  _med_

Enables the rear-end / tailgating collision warning function that alerts the driver when following distance becomes dangerously short.

| value | meaning |
|---|---|
| `0` | Not active (NICHT_AKTIV) |

default `00`· gate: FA-gated (depends on vehicle options)· token `AUFFAHRWARNUNG`· source: firmware-token

### `300A/0/00100000b` — Lane positioning display (LANE_POSITIONING)  ·  _med_

Enables on-screen lane-positioning display showing vehicle position within the current lane relative to lane markings.

| value | meaning |
|---|---|
| `0` | Not active (NICHT_AKTIV) |

default `00`· gate: FA-gated (depends on vehicle options)· token `LANE_POSITIONING`· source: firmware-token

### `300A/0/11000000b` — Pedestrian warning (daytime) (PERSONENWARNUNG_TAGS)  ·  _med_

Configures the daytime pedestrian detection and warning capability, alerting the driver when a pedestrian is detected in or near the vehicle's path.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 5AD Lane departure warning / 5AS Driving Assistant· token `PERSONENWARNUNG_TAGS`· source: firmware-token

### `300A/1/00000011b` — Pedestrian warning (nighttime) (PERSONENWARNUNG_NACHTS)  ·  _med_

Configures the nighttime pedestrian detection and warning function, typically using Night Vision (NIVI) camera data.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `PERSONENWARNUNG_NACHTS`· source: firmware-token

### `300A/1/00001100b` — Lane departure warning version  ·  _med_

Tells the head unit which version of lane departure warning the car has, so its settings and displays match. With generation 2 the Intelligent Safety menu labels one warning setting “Early” instead of “Always”, and notices can name a deactivated Lane Departure Warning or reduced steering intervention. Set at the factory with Lane departure warning (S5AD) or Driving Assistant (S5AS).

| value | meaning |
|---|---|
| `0` | None |
| `1` | Generation 1 |
| `2` | Generation 2 |

default `00`· gate: 5AD Lane departure warning / 5AS Driving Assistant· token `SPURVERLASSENSWARNUNG`· source: firmware-trace

### `300A/1/00110000b` — Lane change warning generation (SPURWECHSELWARNUNG)  ·  _med_

Selects the generation/variant of the lane change warning function (blind spot monitor style warning when changing lanes).

| value | meaning |
|---|---|
| `0` | Off (unnamed) |
| `2` | Generation 2 (GEN_2) |

default `00`· gate: FA-gated (depends on vehicle options)· token `SPURWECHSELWARNUNG`· source: firmware-token

### `300A/1/11000000b` — Side collision warning (SEITENKOLLISIONSWARNUNG)  ·  _med_

Enables the side collision warning function, which alerts the driver to objects alongside the vehicle that could cause a side impact.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SEITENKOLLISIONSWARNUNG`· source: firmware-token

### `300A/2/00001111b` — Lane departure warning min. speed (km/h)  ·  _high_

Tells the head unit the speed, in km/h, below which lane departure warning is inactive, so its driver assistance displays match the system. Best left unchanged.

Number: raw 0–15 × 5 + 0 km/h; typical 20, 40, 60

default `0A`· gate: FA-gated (depends on vehicle options)· token `VMIN_SPURVERLASSEN_KMH`· source: firmware-trace

### `300A/2/11110000b` — Lane change warning min. speed (km/h)  ·  _high_

Tells the head unit the speed, in km/h, below which lane change warning is inactive, so its driver assistance displays match the system. Best left unchanged.

Number: raw 0–15 × 5 + 0 km/h; typical 20, 40, 60

default `0A`· gate: FA-gated (depends on vehicle options)· token `VMIN_SPURWECHSEL_KMH`· source: firmware-trace

### `300A/3/00000011b` — Targeted headlight illumination (GEZIELTESANLEUCHTEN)  ·  _med_

Enables directed/targeted headlight illumination — the system that actively steers a spotlight toward a detected pedestrian or obstacle at night.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `GEZIELTESANLEUCHTEN`· source: firmware-token

### `300A/3/00001100b` — Cruise control (AUTOTEMPOMAT)  ·  _med_

Enables cruise control (Tempomat) — the speed-hold function displayed/managed via the HU Driving Assistant page.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `AUTOTEMPOMAT`· source: firmware-token

### `300A/3/00110000b` — Speed limiter (AUTOLIMITER)  ·  _med_

Enables the automatic speed limiter function, which prevents the vehicle from exceeding a set maximum speed.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `AUTOLIMITER`· source: firmware-token

### `300A/3/11000000b` — Lane departure warning timing (SPURVERLASSENSWARNZEITPUNKT)  ·  _med_

Selects when (how early) the lane departure warning triggers — the timing point relative to crossing the lane marking. Raw descriptor codes are 1 and 2; no symbolic names are defined.

default `00`· gate: FA-gated (depends on vehicle options)· token `SPURVERLASSENSWARNZEITPUNKT`· source: firmware-token

### `300A/4/00001111b` — Lane departure warning min. speed (mph)  ·  _high_

Tells the head unit the speed, in mph, below which lane departure warning is inactive, so its driver assistance displays match the system. Best left unchanged.

Number: raw 0–15 × 5 + 0 mph; typical 10, 25, 40

default `06`· gate: FA-gated (depends on vehicle options)· token `VMIN_SPURVERLASSEN_MPH`· source: firmware-trace

### `300A/4/11110000b` — Lane change warning min. speed (mph)  ·  _high_

Tells the head unit the speed, in mph, below which lane change warning is inactive, so its driver assistance displays match the system. Best left unchanged.

Number: raw 0–15 × 5 + 0 mph; typical 10, 25, 40

default `05`· gate: FA-gated (depends on vehicle options)· token `VMIN_SPURWECHSEL_MPH`· source: firmware-trace

### `300A/5/00000011b` — Lane change warning timing (SPURWECHSELWARNZEITPUNKT)  ·  _med_

Selects the timing point at which the lane change warning triggers relative to the lane crossing event. Raw descriptor codes are 1 and 2; no symbolic names are defined.

default `00`· gate: FA-gated (depends on vehicle options)· token `SPURWECHSELWARNZEITPUNKT`· source: firmware-token

### `300A/5/00001100b` — Steering wheel vibration (VIBRATIONSSTAERKE)  ·  _med_

Enables/disables the steering wheel haptic vibration used to alert the driver during lane departure or lane change warnings. This is a binary on/off field.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `VIBRATIONSSTAERKE`· source: firmware-token

### `300A/5/00110000b` — Lane departure steering intervention (SPURVERLASSENSLENKEINGRIFF)  ·  _med_

Enables active steering counter-correction when the vehicle is about to depart its lane — the system applies a corrective steering torque.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SPURVERLASSENSLENKEINGRIFF`· source: firmware-token

### `300A/5/11000000b` — Lane change steering intervention (SPURWECHSELLENKEINGRIFF)  ·  _med_

Enables active steering counter-correction during an unintentional lane change — system applies corrective torque to prevent drifting into an adjacent lane.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SPURWECHSELLENKEINGRIFF`· source: firmware-token

### `300A/6/11111111b` — Driver assistance base value  ·  _med_

Internal value for the head unit's driver assistance displays. The unit offers only one value.

| value | meaning |
|---|---|
| `5` | Value 1 |

_Not a user setting: Nothing reads it: HmiMain3D never queries its id (0xa10) through the variant server, libhmicoding derives no variant from it, and no other binary names it outside the syset tools; one value only._

default `05`· token `SARAH_PARAMETER`· source: firmware-trace

### `300A/7/00001111b` — Speed limit offset below limit (km/h)  ·  _high_

Sets the largest offset below the detected speed limit, in km/h, that the driver can choose for the speed limit functions. Best left unchanged.

| value | meaning |
|---|---|
| `7` | 15 km/h |

Number: raw 0–15 × 2 + 0 km/h; typical 10, 20, 30

default `05`· gate: FA-gated (depends on vehicle options)· token `VOFFSET_MIN_KMH`· source: firmware-trace

### `300A/7/11110000b` — Speed limit offset above limit (km/h)  ·  _high_

Sets the largest offset above the detected speed limit, in km/h, that the driver can choose for the speed limit functions. Best left unchanged.

| value | meaning |
|---|---|
| `7` | 15 km/h |

Number: raw 0–15 × 2 + 0 km/h; typical 10, 20, 30

default `05`· gate: FA-gated (depends on vehicle options)· token `VOFFSET_MAX_KMH`· source: firmware-trace

### `300A/8/00001111b` — Speed limit offset below limit (mph)  ·  _high_

Sets the largest offset below the detected speed limit, in mph, that the driver can choose for the speed limit functions. Best left unchanged.

Number: raw 0–15 × 1 + 0 mph; typical 5, 10, 15

default `05`· gate: FA-gated (depends on vehicle options)· token `VOFFSET_MIN_MPH`· source: firmware-trace

### `300A/8/11110000b` — Speed limit offset above limit (mph)  ·  _high_

Sets the largest offset above the detected speed limit, in mph, that the driver can choose for the speed limit functions. Best left unchanged.

Number: raw 0–15 × 1 + 0 mph; typical 5, 10, 15

default `05`· gate: FA-gated (depends on vehicle options)· token `VOFFSET_MAX_MPH`· source: firmware-trace

### `300A/9/00000011b` — Right-of-way / junction warning (VORFAHRTSWARNUNG)  ·  _high_

Enables the right-of-way warning at junctions, alerting the driver to cross-traffic when they may not have right of way.

| value | meaning |
|---|---|
| `0` | Not active (NICHT_AKTIV) |
| `1` | Generation 1 (GEN_1) |
| `2` | Generation 2 (GEN_2) |

default `00`· gate: FA-gated (depends on vehicle options)· token `VORFAHRTSWARNUNG`· source: firmware-token

### `300A/9/00111100b` — Side collision warning min. speed (km/h)  ·  _high_

Tells the head unit the speed, in km/h, below which side collision warning is inactive, so its driver assistance displays match the system. Best left unchanged.

Number: raw 0–15 × 5 + 0 km/h; typical 20, 40, 60

default `0A`· gate: FA-gated (depends on vehicle options)· token `VMIN_SEITENKOLLISION_KMH`· source: firmware-trace

### `300A/9/01000000b` — Reversing Assistant  ·  _med_

Shows the Reversing Assistant in the head unit's parking displays. Enable it only when the car has Reversing Assistant.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `MACRO_RFA`· source: firmware-trace

### `300A/9/10000000b` — Undocumented field (SARAH byte 9, bit 7)  ·  _low_

Purpose not determined from available sources. A boolean flag in the SARAH driver-assistance coding page at byte 9 bit 7; the exact field name is not individually pinned in firmware.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

token `SARAH byte 9 (boolean flag (Bool)`· source: inferred

### `300A/10/00001111b` — Side collision warning min. speed (mph)  ·  _high_

Tells the head unit the speed, in mph, below which side collision warning is inactive, so its driver assistance displays match the system. Best left unchanged.

Number: raw 0–15 × 5 + 0 mph; typical 10, 25, 40

default `06`· gate: FA-gated (depends on vehicle options)· token `VMIN_SEITENKOLLISION_MPH`· source: firmware-trace

### `300A/10/00110000b` — Intelligent Safety deactivation notice  ·  _med_

Sets the notice the central display shows when Intelligent Safety systems are switched off or reduced: a general notice that at least one system is deactivated, or one that names the change, such as “Lane Departure Warning deactivated.” It only takes effect when “Lane departure warning version” (`300A/1/00001100b`) is set to generation 2.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | General notice |
| `2` | Names the specific change |

default `00`· gate: FA-gated (depends on vehicle options)· token `INDIVIDUAL_INFO`· source: firmware-trace

### `300A/10/11000000b` — Front collision warning (FRONTKOLLISIONSWARNUNG)  ·  _med_

Enables the front collision warning, which alerts the driver to an imminent front-end collision with a vehicle or obstacle ahead.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `FRONTKOLLISIONSWARNUNG`· source: firmware-token

### `300A/11/00000011b` — Unintended vehicle movement prevention (ANFAHRVERHINDERUNG)  ·  _med_

Enables the unintended vehicle movement prevention feature — the system that prevents inadvertent vehicle motion from a standstill.

| value | meaning |
|---|---|
| `0` | Off (unnamed) |
| `1` | Generation 1 (GEN_1) |

default `00`· gate: FA-gated (depends on vehicle options)· token `ANFAHRVERHINDERUNG`· source: firmware-token

### `300A/11/00001100b` — Speed/velocity assistant (SPEEDGESCHWINDIGKEITSASSISTENT)  ·  _med_

Enables the speed-management component of the driving assistant, which monitors vehicle speed and assists with speed management.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SPEEDGESCHWINDIGKEITSASSISTENT`· source: firmware-token

### `300A/11/00110000b` — Route / road profile data use (STRECKENVERLAUF)  ·  _med_

Enables the use of road/route profile data (from navigation) by the driving assistant to anticipate curves and road conditions ahead.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `STRECKENVERLAUF`· source: firmware-token

### `300A/11/11000000b` — Lane change assist (SPURWECHSELASSISTENT)  ·  _med_

Enables the active lane change assist function, which supports the driver in performing safe lane changes.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SPURWECHSELASSISTENT`· source: firmware-token

### `300A/12/00000011b` — Narrow passage assist (ENGSTELLENASSISTENT)  ·  _med_

Enables the narrow passage / tight-space assistant, which provides visual/audible guidance when passing through narrow gaps or tight spots.

| value | meaning |
|---|---|
| `0` | Off (unnamed) |
| `1` | Generation 1 (GEN_1) |

default `00`· gate: FA-gated (depends on vehicle options)· token `ENGSTELLENASSISTENT`· source: firmware-token

### `300A/12/00001100b` — Steering wheel LED indicator (LENKRADLED)  ·  _med_

Enables LED indicators on the steering wheel rim used to provide haptic/visual driving assistant alerts (e.g. lane departure, collision warnings).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `LENKRADLED`· source: firmware-token

### `300A/12/00110000b` — Manual trailer detection (ANHAENGER_MANUELL)  ·  _med_

Enables manual trailer detection mode, where the driver confirms trailer presence rather than having it detected automatically.

| value | meaning |
|---|---|
| `0` | Not active (NICHT_AKTIV) |

default `00`· gate: FA-gated (depends on vehicle options)· token `ANHAENGER_MANUELL`· source: firmware-token

### `300A/12/11000000b` — Trailer info display (ANHAENGER_INFO)  ·  _med_

Enables display of trailer-related information in the Driving Assistant / HMI when a trailer is detected or connected.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `ANHAENGER_INFO`· source: firmware-token

### `300A/13/00000011b` — Speed assistant (GESCHWINDIGKEITSASSISTENT)  ·  _med_

Enables the speed assistant function — a speed management/advisory system in the Driving Assistant page.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `GESCHWINDIGKEITSASSISTENT`· source: firmware-token

### `300A/13/00001100b` — Intersection / cross-traffic warning (KREUZUNGSWARNUNG)  ·  _med_

Enables the intersection warning function, which detects and alerts to cross-traffic at junctions.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `KREUZUNGSWARNUNG`· source: firmware-token

### `300A/13/00110000b` — Speed limit info display (SPEEDLIMITINFO)  ·  _med_

Enables the speed limit information display on the HU, showing the current road speed limit derived from camera or map data.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `SPEEDLIMITINFO`· source: firmware-token

### `300A/13/11000000b` — Predictive look-ahead (VORAUSSCHAU)  ·  _med_

Enables predictive look-ahead functionality, where navigation/camera data about the road ahead is used to anticipate and pre-condition driving assistant systems.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `VORAUSSCHAU`· source: firmware-token

### `300A/14/00000011b` — Speed limit warning  ·  _med_

Tells the head unit which version of speed limit warning the car has, so the Speed Assistant settings describe it correctly. The warning alerts the driver when the car is faster than the detected or chosen limit. With generation 1 the settings describe a warning above the adjusted limit, the detected limit plus the driver's offset. Set it to match the car's equipment.

| value | meaning |
|---|---|
| `0` | None |
| `1` | Generation 1 |
| `2` | Generation 2 |

default `00`· gate: FA-gated (depends on vehicle options)· token `SPEEDLIMITWARNUNG`· source: firmware-trace

### `300A/14/00001100b` — Speed limit staging animation (SPEEDLIMITINSZENIERUNG)  ·  _high_

Configures the animation/staging displayed when a new speed limit is detected or when the speed limit warning triggers.

| value | meaning |
|---|---|
| `0` | Not active (NICHT_AKTIV) |
| `1` | Generation 1 (GEN_1) |

default `00`· gate: FA-gated (depends on vehicle options)· token `SPEEDLIMITINSZENIERUNG`· source: firmware-token

### `300A/14/00110000b` — Single-side pass-through guidance (EINSEITIGVORBEIFAHREN)  ·  _med_

Enables single-sided passing assistance — guidance when the vehicle passes a stationary obstacle or parked car where only one side has sufficient clearance.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `EINSEITIGVORBEIFAHREN`· source: firmware-token

### `300A/14/11000000b` — Speed limit offset  ·  _high_

Sets how far the driver can shift the speed limit functions above or below the detected limit in the Speed Assistant settings. With “Not set” the ±15 km/h or ±10 mph range applies.

| value | meaning |
|---|---|
| `0` | Not set |
| `1` | Up to ±15 km/h or ±10 mph |
| `2` | Up to ±10 km/h or ±5 mph |

default `00`· gate: NOT vehicle type-key attribute group (FP category 17; 33 type tokens, e.g. 1F53,1F73,1F93,1G93)· token `VOFFSET`· source: firmware-trace

### `300A/15/00000111b` — Speed Limit Assist manual mode (SLAMANUELL)  ·  _med_

Enables manual mode for the Speed Limit Assist (SLA) — allowing the driver to manually set the reference speed instead of relying on sign recognition.

| value | meaning |
|---|---|
| `0` | Off (unnamed) |
| `1` | Generation 1 (GEN_1) |

default `00`· gate: FA-gated (depends on vehicle options)· token `SLAMANUELL`· source: firmware-token

### `300A/15/11111000b` — Undocumented field (SARAH byte 15, bits 7-3)  ·  _low_

Purpose not determined from available sources. A 5-bit field in the SARAH driver-assistance coding page at byte 15 bits 7:3; exact field name not individually pinned in firmware.

token `SARAH byte 15 (5-bit field (00..00))`· source: inferred

### `300A/16/11111111b` — Undocumented field (SARAH bytes 16-47, multi-byte block)  ·  _low_

Purpose not determined from available sources. A 32-byte multi-byte data block in the SARAH driver-assistance coding page spanning bytes 16-47; exact field names not individually pinned in firmware.

token `SARAH byte 16 (multi-byte value (syset Int/UInt8/16))`· source: inferred

### `300A/48/00001111b` — Undocumented field (SARAH byte 48, bits 3-0)  ·  _low_

Purpose not determined from available sources. A 4-bit field in the SARAH driver-assistance coding page at byte 48 bits 3:0; exact field name not individually pinned in firmware.

token `SARAH byte 48 (4-bit field (00..00))`· source: inferred

### `300A/48/00010000b` — Pedestrian warning enable (PERSONEN_WARNUNG)  ·  _high_

Master enable for the pedestrian/person detection warning system. When active, the Driving Assistant will alert the driver when a pedestrian is detected in dangerous proximity.

| value | meaning |
|---|---|
| `0` | Not active (NICHT_AKTIV) |
| `1` | Active (AKTIV) |

default `00`· gate: 5AS Driving Assistant· token `PERSONEN_WARNUNG`· source: firmware-token

### `300A/48/11100000b` — Driving Assistant staging concept (FAS_INSZENIERUNG)  ·  _high_

Selects the visual staging/animation concept for the Driving Assistant (FAS = Fahrerassistenzsystem). Controls the presentation style of warnings including staging boards, preview, or full visual concept.

| value | meaning |
|---|---|
| `0` | Off (unnamed) |
| `1` | Warning boards (INSZENIERUNGSTAFELN) |
| `2` | SARAH pre-stage (SARAH_VORSTUFE) |
| `3` | SARAH full concept (SARAH_VOLLKONZEPT) |
| `4` | SARAH full concept mini (SARAH_VOLLKONZEPT_MINI) |

default `00`· token `FAS_INSZENIERUNG`· source: firmware-token

### `300A/49/00000001b` — Targeted headlight illumination v2 (GEZIELTES_ANLEUCHTEN)  ·  _high_

Enables directed headlight illumination towards detected pedestrians or objects at night. This is the newer token (byte 49) for this feature vs the earlier GEZIELTESANLEUCHTEN at byte 3.

| value | meaning |
|---|---|
| `0` | Off (unnamed) |
| `1` | Active (AKTIV) |

default `00`· gate: FA-gated (depends on vehicle options)· token `GEZIELTES_ANLEUCHTEN`· source: firmware-token

### `300A/49/00000010b` — Lane change warning enable (LANE_CHANGE_WARNING)  ·  _med_

Master enable bit for the lane change warning (blind spot warning style) function in the SARAH subsystem.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `LANE_CHANGE_WARNING`· source: firmware-token

### `300A/49/00000100b` — Brake assistant (BRAKE_ASSISTENT)  ·  _med_

Enables the base brake assistant function, which provides braking support in emergency situations by maximising braking force.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `BRAKE_ASSISTENT`· source: firmware-token

### `300A/49/00001000b` — Brake assistant 3 / Stop-and-Go (BRAKE_ASSISTENT_3)  ·  _high_

Enables the third-generation brake assistant function integrated with Active Cruise Control Stop-and-Go capability, providing enhanced automated braking support.

| value | meaning |
|---|---|
| `0` | Not active (NICHT_AKTIV) |
| `1` | Active (AKTIV) |

default `00`· gate: 5DF Active cruise control with Stop&Go function· token `BRAKE_ASSISTENT_3`· source: firmware-token

### `300A/49/00010000b` — Brake assistant CCM (BRAKE_ASSISTANT_CCM)  ·  _med_

Enables the Camera / Cross-traffic Monitor (CCM) variant of the brake assistant. Active when NOT equipped with lane departure warning / ACC Stop&Go / Driving Assistant (different sensor set).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: NOT 5AD Lane departure warning / 5DF Active cruise control with Stop&Go function / 5AS Driving Assistant· token `BRAKE_ASSISTANT_CCM`· source: firmware-token

### `300A/49/00100000b` — Brake assistant FCW (forward collision warning) (BRAKE_ASSISTANT_FCW)  ·  _high_

Enables the Forward Collision Warning variant of the brake assistant, which combines camera-based collision detection with automatic pre-braking preparation.

| value | meaning |
|---|---|
| `0` | Not active (NICHT_AKTIV) |
| `1` | Active (AKTIV) |

default `00`· gate: 5AD Lane departure warning· token `BRAKE_ASSISTANT_FCW`· source: firmware-token

### `300A/49/01000000b` — Lane departure warning enable (LANE_DEPARTURE_WARNING)  ·  _med_

Master enable for the lane departure warning system. When active, the system monitors lane markings and alerts the driver if the vehicle drifts across them without signalling.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 5AD Lane departure warning / 5AS Driving Assistant· token `LANE_DEPARTURE_WARNING`· source: firmware-token

### `300A/49/10000000b` — Night Vision 2 object detection (NIVI_2_OBJ_DETECTION)  ·  _med_

Enables second-generation Night Vision (NIVI 2) object detection, which uses the thermal/night camera to identify and classify objects (pedestrians, animals) in darkness.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `NIVI_2_OBJ_DETECTION`· source: firmware-token

## Datagroup 0x300B (37 parameters)

### `300B/0/00000001b` — Touch Command page enable flag  ·  _low_

Anonymous boolean flag at bit 0 of the TOUCH_COMMAND coding page (page 300B). Exact function not individually pinned in firmware symbol table; likely a master enable or reserved bit for the Touch Command staging block.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TOUCH_COMMAND byte 0 (boolean flag (Bool)`· source: inferred

### `300B/0/00000110b` — Panoramic roof type  ·  _high_

Declares whether the vehicle has a single-panel or two-panel panoramic glass roof. Tells the Touch Command subsystem which sunroof control UI to present.

| value | meaning |
|---|---|
| `1` | One-piece (single-panel panoramic roof) |
| `3` | Two-piece (dual-panel panoramic roof) |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_PANORAMADACH`· source: firmware-token

### `300B/0/00001000b` — Sliding/tilting sunroof present  ·  _med_

Indicates whether the vehicle has a conventional sliding/tilting sunroof (Schiebehebedach). Enables the corresponding Touch Command UI tile.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_SCHIEBEHEBEDACH`· source: firmware-token

### `300B/0/00010000b` — Air ionisation present  ·  _med_

Enables the air ionisation (ionizer) control tile in the Touch Command screen. Set when the vehicle is equipped with the cabin air ionisation system.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_IONISATION`· source: firmware-token

### `300B/0/00100000b` — Four-zone climate control present  ·  _med_

Indicates the vehicle has a 4-zone automatic climate control system. Activates the corresponding extended climate UI in Touch Command.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_CLIMATE_4_ZONES`· source: firmware-token

### `300B/0/01000000b` — Rear extended climate control present  ·  _med_

Indicates the vehicle has a rear-area extended climate control zone (beyond standard 2-zone rear). Enables additional rear climate controls in Touch Command.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_CLIMATE_REAR_EXTENDED`· source: firmware-token

### `300B/0/10000000b` — Rear window roller blind present  ·  _med_

Indicates whether the vehicle has a rear window roller sun blind. Enables the rear-curtain control tile in Touch Command.

| value | meaning |
|---|---|
| `0` | Not active (no rear window blind) |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_REAR_WINDOW_CURTAIN`· source: firmware-token

### `300B/1/00000001b` — Rear and side window roller blinds present  ·  _med_

Indicates the vehicle has roller sun blinds on both rear and side windows. Enables the combined rear+side curtain control in Touch Command.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | Active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_REAR_AND_SIDE_WINDOW_CURTAIN`· source: firmware-token

### `300B/1/00000010b` — Captain's chairs (individual rear seats) present  ·  _med_

Indicates the vehicle has individual rear captain's chairs rather than a bench seat. Enables the individual rear-seat control tile in Touch Command.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_CAPTAINCHAIR`· source: firmware-token

### `300B/1/00000100b` — Front seat multifunction controls present  ·  _med_

Indicates the front seats have multifunction memory/position controls (e.g. easy-entry, memory recall). Enables front seat control tile in Touch Command.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_SEAT_MULTIFUNCTION`· source: firmware-token

### `300B/1/00001000b` — Rear seat multifunction controls present  ·  _med_

Indicates the rear seats have multifunction electric adjustment controls. Enables rear seat control tile in Touch Command.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_SEAT_REAR_MULTIFUNCTION`· source: firmware-token

### `300B/1/00010000b` — Rear seat massage present  ·  _med_

Indicates the rear seats are equipped with a massage function. Enables the rear seat massage control tile in Touch Command.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_SEAT_REAR_MASSAGE`· source: firmware-token

### `300B/1/00100000b` — Front seat massage present  ·  _med_

Indicates the front seats are equipped with a massage function. Enables the front seat massage control tile in Touch Command.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_SEAT_FRONT_MASSAGE`· source: firmware-token

### `300B/1/01000000b` — Front seat lumbar support present  ·  _med_

Indicates the front seats are equipped with adjustable lumbar (lordosis) support. Enables the lumbar adjustment control in Touch Command.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_SEAT_FRONT_LORDOSE`· source: firmware-token

### `300B/1/10000000b` — Seat training/dynamic support present  ·  _med_

Indicates the seats are equipped with dynamic seat / training function (active back support that shifts during cornering). Enables seat training control in Touch Command.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_SEAT_TRAINING`· source: firmware-token

### `300B/2/00000001b` — Front seat heating present  ·  _med_

Indicates the front seats have heated seat elements. Enables the front seat heating control tile in Touch Command.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_SEAT_HEATING_FRONT`· source: firmware-token

### `300B/2/00000010b` — Rear seat heating present  ·  _med_

Indicates the rear seats have heated seat elements. Enables the rear seat heating control tile in Touch Command.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_SEAT_HEATING_REAR`· source: firmware-token

### `300B/2/00000100b` — Front seat ventilation present  ·  _med_

Indicates the front seats have ventilated/cooled seat elements. Enables the front seat ventilation tile in Touch Command.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_SEAT_VENTILATION_FRONT`· source: firmware-token

### `300B/2/00001000b` — Rear seat ventilation present  ·  _med_

Indicates the rear seats have ventilated/cooled seat elements. Enables the rear seat ventilation tile in Touch Command.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_SEAT_VENTILATION_REAR`· source: firmware-token

### `300B/2/00010000b` — Seat auto-climate function present  ·  _med_

Indicates the seat climate system supports an automatic/combined heating+ventilation mode. Enables the seat auto-climate control in Touch Command.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_SEAT_AUTO_CLIMATE`· source: firmware-token

### `300B/2/00100000b` — Individual special equipment (SA) mode  ·  _med_

Signals that the vehicle uses an individual/single special-equipment (Einzel-SA) configuration for Touch Command staging, rather than a bundled package. May affect which TC tiles are shown.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_EINZEL_SA`· source: firmware-token

### `300B/2/11000000b` — Bowers & Wilkins high-end audio staging  ·  _high_

Controls the Touch Command staging level for the Bowers & Wilkins (B&W) Diamond/high-end audio system. Determines whether the audio system gets no menu, basic display, light animation only, or full introduction staging.

| value | meaning |
|---|---|
| `0` | No menu (KEIN_MENUE — audio staging disabled) |
| `1` | Display without introduction (KEINE_INSZ — show but skip animation) |
| `2` | Light animation only (NUR_LICHTINSZ — ambient lighting intro only) |
| `3` | Full introduction staging (VOLLE_INSZ — full light + sound intro) |

default `00`· gate: always (no FA gate)· token `TC_HIGH_END_AUDIO_B_UND_W`· source: firmware-token

### `300B/3/00000011b` — Illuminated panoramic roof staging  ·  _high_

Controls whether the illuminated panoramic roof (Beleuchtetes Panoramadach) is presented in Touch Command and whether its lighting is linked to the ambient interior lighting system.

| value | meaning |
|---|---|
| `0` | Not active (NICHT_AKTIV — no illuminated panoramic roof) |
| `1` | Active (AKTIV — illuminated roof present, independent control) |
| `2` | Active with ambient light coupling (AKTIV_MIT_KOPPLUNG_AN_AMBIENTES_INNENLICHT — roof light synced to ambient lighting) |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_BELEUCHTETES_PANORAMADACH`· source: firmware-token

### `300B/3/00000100b` — Light sword (Lichtschwert) ambient strip present  ·  _med_

Indicates the vehicle has the 'Lichtschwert' (lit. light sword) illuminated ambient door strip feature. Enables the corresponding ambient lighting control in Touch Command.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_LICHTSCHWERT`· source: firmware-token

### `300B/3/00001000b` — Individual ambient lighting present  ·  _med_

Indicates the vehicle has the Individual ambient interior lighting package (colour-selectable ambient light). Enables individual ambient light colour control in Touch Command.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_INDIVIDUAL_AMBIENTELICHT`· source: firmware-token

### `300B/3/01110000b` — Colour switch ensemble count  ·  _med_

Configures the colour-switch ensemble variant for the ambient lighting system. Raw numeric field; exact meaning of each value is not symbolically named in the syset descriptor.

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_COLOUR_SWITCH_ENSEMBLE`· source: firmware-token

### `300B/3/10000000b` — Ambient light brightness control present  ·  _med_

Indicates the ambient lighting system supports user-adjustable brightness (Helligkeit). Enables the brightness slider in the Touch Command ambient lighting page.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_HELLIGKEIT_AMBILIGHT`· source: firmware-token

### `300B/4/00000001b` — WLAN hotspot tile present  ·  _med_

Enables the Wi-Fi hotspot control tile in Touch Command, allowing the driver to enable/disable the in-car WLAN hotspot from the touchscreen.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_WLAN_HOTSPOT`· source: firmware-token

### `300B/4/00000010b` — Diagnostics/test mode tile present  ·  _med_

Enables a diagnostics or test mode tile in the Touch Command screen. Intended for workshop or factory use; not typically enabled in production vehicles.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_DIAGNOSE_TEST_MODE`· source: firmware-token

### `300B/4/00011100b` — Number of Touch Command panels  ·  _high_

Configures how many Touch Command control panels (TC screens) are available in the iDrive menu. TC_0 means no TC panel; TC_1 through TC_3 enable increasing numbers of TC panels.

| value | meaning |
|---|---|
| `0` | TC_0 — no Touch Command panel |
| `1` | TC_1 — one Touch Command panel |
| `2` | TC_2 — two Touch Command panels |
| `3` | TC_3 — three Touch Command panels |

default `01`· gate: always (no FA gate)· token `TC_NUMBER_OF_TOUCH_COMMAND`· source: firmware-token

### `300B/4/00100000b` — Media library browsing enabled  ·  _med_

Enables media library browsing (e.g. browse by artist/album/genre) in the Touch Command / entertainment section of the iDrive system.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_MEDIA_BROWSING`· source: firmware-token

### `300B/4/01000000b` — V12 engine available  ·  _med_

Indicates the vehicle is fitted with a V12 engine. May enable V12-specific Touch Command engine display graphics or power/cylinder-deactivation controls.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `TC_V12_ENGINE_AVAILABLE`· source: firmware-token

### `300B/4/10000000b` — Folder browsing enabled  ·  _med_

Enables folder-based browsing of USB/storage media in the Touch Command entertainment section, allowing navigation by folder hierarchy rather than media library.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `01`· gate: FA-gated (depends on vehicle options)· token `TC_FOLDER_BROWSING`· source: firmware-token

### `300B/5/00000001b` — Touch operation of the central display  ·  _med_

Turns on touch operation of the central display, so the screen responds to taps and swipes as well as to the iDrive Controller. Enable it only when the central display is a touchscreen. Enabled at the factory with Navigation Professional (S609) or TV function (S601).

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: 601 TV Function / 609 Professional navigation system· token `CID_HMI_TOUCH`· source: firmware-token

### `300B/5/00000010b` — Rear-seat entertainment touchscreen present  ·  _high_

Indicates the vehicle has a touch-capable display for the Rear Seat Entertainment (RSE) system. Enables RSE touch input handling.

| value | meaning |
|---|---|
| `0` | Not active (no RSE touch display) |
| `1` | Active (RSE touchscreen present) |

default `00`· gate: FA-gated (depends on vehicle options)· token `CID_HMI_TOUCH_RSE`· source: firmware-token

### `300B/5/11111100b` — Touch Command page — reserved/unknown 6-bit field  ·  _low_

Anonymous 6-bit field occupying bits 7–2 of byte 5 in the TOUCH_COMMAND coding page. Exact function not individually pinned in firmware symbol table.

token `TOUCH_COMMAND byte 5 (6-bit field (00..00))`· source: inferred

### `300B/6/11111111b` — Touch Command page — extended/multi-byte data block (bytes 6–29)  ·  _low_

Anonymous multi-byte region spanning bytes 6–29 of the TOUCH_COMMAND coding page (24 bytes). Likely contains TL_ID (Telefon/Telematik/Online) configuration table entries and other extended Touch Command parameters not individually named.

token `TOUCH_COMMAND byte 6 (multi-byte value (syset Int/UInt8/16))`· source: inferred

## Datagroup 0x300C (42 parameters)

### `300C/0/00000001b` — HUD sport display enable  ·  _med_

Enables the sport-display content group in the head-up display (HUD). When active, sport-oriented readouts are available for the driver to select in HUD settings.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `HUD_SPORTANZEIGE_ENABLE`· source: firmware-token

### `300C/0/00000010b` — HUD sport display — FES variant  ·  _med_

Enables the FES (Fahrerassistenz — driver assistance) variant of the HUD sport display. Typically associated with assistance-oriented sport content in the HUD on FES-equipped cars.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `HUD_SPORTANZEIGE_FES_ENABLE`· source: firmware-token

### `300C/0/00000100b` — HUD sport display — motorsport lane view  ·  _med_

Enables the MS_GASSE (motorsport lane/corridor) sport-display variant in the HUD, showing a dynamic lane or corridor graphic during spirited driving or on track.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `HUD_SPORTANZEIGE_MS_GASSE_ENABLE`· source: firmware-token

### `300C/0/00001000b` — HUD entertainment list  ·  _med_

Enables the entertainment content list (audio source, track, station) as a selectable content group in the head-up display.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `HUD_ENTERTAINMENTLIST`· source: firmware-token

### `300C/0/00010000b` — HUD distance/following-distance info  ·  _med_

Enables ACC (adaptive cruise) following-distance information as a selectable content element in the HUD, showing the set gap to the vehicle ahead.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `HUD_DISTANCE_INFO`· source: firmware-token

### `300C/0/00100000b` — HUD settings: BMW M version  ·  _med_

Switches the head-up display settings on the central display to their BMW M version. For BMW M models with a head-up display.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `HUD_M`· source: firmware-trace

### `300C/0/01000000b` — HUD content: turn signals  ·  _low_

When enabled, the head-up display also indicates when a turn signal is on.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `HUD_TURNSIGNAL`· source: firmware-token

### `300C/0/10000000b` — HUD traffic sign recognition display  ·  _med_

Enables display of recognised traffic signs (speed limits, no-passing signs, etc.) from the vehicle's camera-based sign recognition (VZA) system in the head-up display.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `HUD_VZA`· source: firmware-token

### `300C/1/00000011b` — HUD image compression  ·  _med_

Image compression the head unit uses for navigation graphics in the head-up display and cluster. It must match the hardware generation.

| value | meaning |
|---|---|
| `0` | Type 1, L6 hardware |
| `1` | Type 2, L7 hardware |

_Not a user setting: Display-link encoding: NavNBTEvoController maps RLE_1 (Capricorn/Bosch/L6/FPK) / RLE_2 (Jade/Conti/L7) to the NBT_RLE32 (Bosch) or NBT_RLE16 (Conti) compressor for the guidance-viewer (ICHUD) maneuver graphics; it only has to match the receiving hardware, like LVDS tuning. A mismatch breaks the graphics rather than giving a different result._

default `00`· gate: FA-gated (depends on vehicle options)· token `HUD_KOMPRIMIERUNG_ART`· source: firmware-trace

### `300C/1/00000100b` — HUD image rotation  ·  _med_

Enables rotation of the HUD display image, used to compensate for optical path geometry when the projector unit requires a rotated raster.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `HUD_ROTATION`· source: firmware-token

### `300C/1/00001000b` — HUD position adjustment available  ·  _med_

Enables the user-accessible position adjustment function for the HUD. When set, the system supports HUD position control (used in conjunction with the specific slider controls in bytes 9-10).

| value | meaning |
|---|---|
| `0` | Off/not available |
| `1` | On/available |

default `00`· gate: always (no FA gate)· token `HUD_POSITION`· source: firmware-token

### `300C/1/00010000b` — HUD activation (fitted/activated)  ·  _med_

Marks the HUD as activated/enabled in the system — the primary fitment activation bit distinct from HUD_VERBAUT. When set, the head-up display subsystem initialises and presents HUD-related menus.

| value | meaning |
|---|---|
| `0` | Off/not activated |
| `1` | On/activated |

default `00`· gate: FA-gated (depends on vehicle options)· token `HUD_ACTIVATION`· source: firmware-token

### `300C/1/00100000b` — HUD speed control display  ·  _med_

Enables display of the active speed control set-speed (cruise control or speed limiter) as a content element in the HUD. The named firmware value NICHT_AKTIV (not active) is the default/off state.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: always (no FA gate)· token `HUD_SPEEDCONTROL`· source: firmware-token

### `300C/1/01000000b` — Navigation HUD available  ·  _med_

Declares that navigation turn-by-turn content is available for display in the HUD on this vehicle. Enables routing instructions (arrows, distance to manoeuvre) in the HUD.

| value | meaning |
|---|---|
| `0` | Not available |
| `1` | Available |

default `00`· gate: FA-gated (depends on vehicle options)· token `NAVI_HUD_AVAILABLE`· source: firmware-token

### `300C/1/10000000b` — Junction View in HUD  ·  _med_

Enables the Junction View (detailed intersection guidance graphic) to be shown in the HUD in addition to or instead of the standard navigation arrow. Requires Navigation HUD to be available.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: FA-gated (depends on vehicle options)· token `JUNCTION_VIEW_HUD`· source: firmware-token

### `300C/2/00000001b` — Head-up display installed  ·  _high_

Tells the head unit a head-up display (HUD) is installed, which enables the HUD menus and settings. Enable it only when the car has a HUD.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `HUD_VERBAUT`· source: firmware-token

### `300C/2/00001110b` — Undocumented field (HUD_RES)  ·  _low_

Purpose not determined from available sources. Although 'RES' superficially suggests resolution, a dedicated resolution field (HUD_AUFLOESUNG) already exists at byte 3; RES most likely denotes a reserved or unspecified field. No enum values are defined.

default `00`· gate: FA-gated (depends on vehicle options)· token `HUD_RES`· source: firmware-token

### `300C/2/01110000b` — HUD hardware generation  ·  _med_

Selects the generation of the HUD projector hardware fitted. Used by the system to select correct display parameters, calibration, and feature support for the installed unit.

default `00`· gate: always (no FA gate)· token `HUD_GENERATION`· source: firmware-token

### `300C/2/10000000b` — HUD content: junction view (day)  ·  _low_

Setting for the junction view in the head-up display, for daytime. Best left unchanged.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· token `JUNCTION_VIEW_HUD_DAY`· source: firmware-token

### `300C/3/00001111b` — HUD image resolution  ·  _med_

Sets the image resolution the head unit uses for navigation graphics in the head-up display, to suit the HUD generation. Best left unchanged.

| value | meaning |
|---|---|
| `0` | L6 HUD |
| `1` | L7 HUD |

default `00`· gate: FA-gated (depends on vehicle options)· token `HUD_AUFLOESUNG`· source: firmware-trace

### `300C/3/11110000b` — HUD radio-button (content selector) configuration  ·  _med_

Selects which radio-button layout/set is presented in the HUD content selector (the on-screen control that lets the driver choose what to display). KEINE_RADIOBUTTONS means no radio-button selector is shown.

| value | meaning |
|---|---|
| `2` | KEINE_RADIOBUTTONS (no radio buttons) |

default `02`· gate: FA-gated (depends on vehicle options)· token `HUD_RB_KONFIGURATION`· source: firmware-token

### `300C/4/00000111b` — HUD/cluster display dwell time  ·  _med_

Sets how long a HUD/instrument-cluster popup or notification is shown before automatically dismissing. The only named firmware value is WERT_1_250MS (value 1 = 250 ms); higher values select longer dwell times.

| value | meaning |
|---|---|
| `1` | 250 ms (WERT_1_250MS) |

default `00`· gate: FA-gated (depends on vehicle options)· token `DISPLAYTIME_LIST_HUD_KOMBI`· source: firmware-token

### `300C/4/00001000b` — HUD checkbox: on/off control  ·  _med_

Enables the master on/off checkbox in the HUD section of the iDrive settings menu, allowing the driver to completely enable or disable the head-up display.

| value | meaning |
|---|---|
| `0` | Off/not shown |
| `1` | On/shown |

default `00`· gate: always (no FA gate)· token `HUD_CB_EIN_AUS`· source: firmware-token

### `300C/4/00010000b` — HUD checkbox: showroom mode  ·  _med_

Enables the showroom/demonstration mode checkbox in HUD settings. When active, the HUD can be operated in showroom mode for dealer demonstration purposes.

| value | meaning |
|---|---|
| `0` | Off/not shown |
| `1` | On/shown |

default `00`· gate: always (no FA gate)· token `HUD_CB_SHOWROOM_MODE`· source: firmware-token

### `300C/4/00100000b` — HUD menu: Check Control checkbox  ·  _med_

Adds a Check Control checkbox to the head-up display settings, letting the driver choose whether Check Control messages, the car's warning and status notices, also appear in the HUD.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: always (no FA gate)· token `HUD_CB_CCM`· source: firmware-token

### `300C/4/01000000b` — HUD checkbox: content list  ·  _med_

Enables a content-list selection checkbox in the HUD iDrive settings, allowing the driver to toggle which content categories appear in the HUD display list.

| value | meaning |
|---|---|
| `0` | Off/not shown |
| `1` | On/shown |

default `00`· gate: FA-gated (depends on vehicle options)· token `HUD_CB_LISTEN`· source: firmware-token

### `300C/4/10000000b` — HUD checkbox: speed limit display  ·  _med_

Enables the speed-limit (Tempolimit) checkbox in the HUD iDrive settings, letting the driver choose whether the current speed limit is shown in the HUD.

| value | meaning |
|---|---|
| `0` | Off/not shown |
| `1` | On/shown |

default `00`· gate: always (no FA gate)· token `HUD_CB_TEMPOLIMIT`· source: firmware-token

### `300C/5/00000001b` — HUD checkbox: following-distance info  ·  _med_

Enables the Abstandsinfo (following-distance information) checkbox in HUD settings, letting the driver choose whether ACC gap-to-vehicle-ahead is shown in the HUD.

| value | meaning |
|---|---|
| `0` | Off/not shown |
| `1` | On/shown |

default `00`· gate: FA-gated (depends on vehicle options)· token `HUD_CB_ABSTANDSINFO`· source: firmware-token

### `300C/5/00000010b` — HUD checkbox: speed-limit info  ·  _med_

Enables the speed-limit-info checkbox in HUD iDrive settings (distinct from the alert/warning variant; may relate to advisory/road-sign-sourced speed limit display).

| value | meaning |
|---|---|
| `0` | Off/not shown |
| `1` | On/shown |

default `00`· gate: FA-gated (depends on vehicle options)· token `HUD_CB_SPEEDLIMITINFO`· source: firmware-token

### `300C/5/11111100b` — Undocumented field (HUD byte 5 high 6 bits)  ·  _low_

Purpose not determined from available sources. This 6-bit field occupies bits 7-2 of HUD page byte 5; the firmware descriptor names this page but does not assign a token to this specific (byte,mask) combination. No enum values are defined.

token `HUD byte 5 (6-bit field (00..00))`· source: inferred

### `300C/6/11111111b` — Undocumented field (HUD bytes 6-8 multi-byte)  ·  _low_

Purpose not determined from available sources. This is a multi-byte value spanning bytes 6-8 of the HUD coding page; the firmware descriptor names the page but does not assign a token to this specific field.

token `HUD byte 6 (multi-byte value (syset Int/UInt8/16))`· source: inferred

### `300C/9/00000001b` — HUD standstill view enable  ·  _med_

Enables a static/standstill display view in the HUD when the vehicle is at a standstill. Controls whether the HUD shows content while stationary (sub-bits in this byte select which content).

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `HUD_STANDANSICHT`· source: firmware-token

### `300C/9/00000010b` — HUD standstill view: no display  ·  _med_

When the HUD standstill view is active, this bit selects 'no content' (blank) as the standstill screen, overriding other standstill content bits.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On (blank/no display while stationary) |

default `00`· gate: FA-gated (depends on vehicle options)· token `HUD_STAND_KEINE_ANZEIGE`· source: firmware-token

### `300C/9/00000100b` — HUD standstill view: navigation  ·  _med_

Selects navigation content (e.g. destination, next manoeuvre) as the HUD content displayed when the vehicle is stationary.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `HUD_STAND_NAVIGATION`· source: firmware-token

### `300C/9/00001000b` — HUD standstill view: efficiency/EfficientDynamics  ·  _med_

Selects EfficientDynamics/efficiency data (e.g. current range, energy flow) as the HUD content displayed when the vehicle is stationary.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `HUD_STAND_EFFIZIENZ`· source: firmware-token

### `300C/9/00010000b` — HUD standstill view: calendar/appointments  ·  _med_

Selects calendar appointments (Termine) as the HUD content displayed when the vehicle is stationary, showing upcoming calendar events.

| value | meaning |
|---|---|
| `0` | Off |
| `1` | On |

default `00`· gate: FA-gated (depends on vehicle options)· token `HUD_STAND_TERMINE`· source: firmware-token

### `300C/9/01100000b` — Undocumented field (HUD byte 9 bits 6-5)  ·  _low_

Purpose not determined from available sources. This 2-bit field occupies bits 6-5 of HUD page byte 9; no token is assigned in the firmware descriptor for this specific (byte,mask).

token `HUD byte 9 (2-bit field (00..00))`· source: inferred

### `300C/9/10000000b` — HUD brightness slider  ·  _med_

Enables the brightness adjustment slider in the HUD iDrive settings menu, allowing the driver to manually adjust HUD image brightness.

| value | meaning |
|---|---|
| `0` | Off/not shown |
| `1` | On/shown |

default `00`· gate: always (no FA gate)· token `HUD_SLIDE_HELLIGKEIT`· source: firmware-token

### `300C/10/00000001b` — HUD height adjustment slider  ·  _med_

Enables the height (Hoehe) adjustment slider in the HUD iDrive settings menu, allowing the driver to raise or lower the projected HUD image to suit their seating position.

| value | meaning |
|---|---|
| `0` | Off/not shown |
| `1` | On/shown |

default `00`· gate: always (no FA gate)· token `HUD_SLIDE_HOEHE`· source: firmware-token

### `300C/10/00000010b` — HUD rotation adjustment slider  ·  _med_

Enables the rotation/tilt adjustment slider in the HUD iDrive settings menu, allowing the driver to correct the rotational angle of the projected HUD image.

| value | meaning |
|---|---|
| `0` | Off/not shown |
| `1` | On/shown |

default `00`· gate: always (no FA gate)· token `HUD_SLIDE_ROTATION`· source: firmware-token

### `300C/10/11111100b` — Undocumented field (HUD byte 10 bits 7-2)  ·  _low_

Purpose not determined from available sources. This 6-bit field occupies bits 7-2 of HUD page byte 10; no token is assigned in the firmware descriptor for this specific (byte,mask).

token `HUD byte 10 (6-bit field (00..00))`· source: inferred

### `300C/11/11111111b` — Undocumented field (HUD bytes 11-79 multi-byte)  ·  _low_

Purpose not determined from available sources. This is a large multi-byte value spanning bytes 11-79 of the HUD coding page; the firmware descriptor names the page but does not assign a token to this field range. May contain HUD optics calibration or geometry data.

token `HUD byte 11 (multi-byte value (syset Int/UInt8/16))`· source: inferred

## Datagroup 0x300D (44 parameters)

### `300D/0/00000001b` — Instrument cluster boolean flag (byte 0, bit 0)  ·  _low_

An unidentified boolean flag in the KOMBI coding page. Purpose not determined from available sources.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

token `KOMBI byte 0 (boolean flag (Bool)`· source: inferred

### `300D/0/00000010b` — Cluster MMI list mode (basic)  ·  _med_

Selects whether the instrument cluster uses a basic/simplified MMI list layout. Enabled when the car lacks a professional navigation system (SA 609) and the high-spec KOMBI variant (6WA).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: NOT 609 Professional navigation system / 6WA KOMBI with extended equipment specification / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31)· token `BASIS_KOMBI_MMI_LIST`· source: firmware-token

### `300D/0/00000100b` — Cluster ECO display (CSC)  ·  _low_

Setting for efficiency information shown in the instrument cluster (CSC). Best left unchanged.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: always (no FA gate)· token `ECO_CSC_KOMBI`· source: firmware-trace

### `300D/0/00001000b` — Loupe (magnified needle) speedometer in cluster  ·  _med_

Enables the loupe/magnified-needle (Lupenzeiger) speedometer display style in the instrument cluster, which renders the speedometer with a large stylized analog needle sweep.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `LOUPE_TACHO_KOMBI`· source: firmware-token

### `300D/0/00010000b` — Drive mode display in cluster  ·  _med_

Enables the driving mode (COMFORT/SPORT/ECO PRO) status indicator in the instrument cluster. When active, the selected drive mode is shown in the cluster.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `DRIVE_MODE_KOMBI`· source: firmware-token

### `300D/0/00100000b` — Calming display mode for cluster  ·  _med_

Enables the 'calming' visual mode in the instrument cluster, which reduces or simplifies displayed information (associated with Eco Pro mode calm-driving animations). Firmware enum value NICHT_AKTIV = not active.

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `00`· gate: NOT vehicle type-key attribute group (FP category 25; 27 type tokens, e.g. 11CK,11CL,11DE,12CK) / vehicle type-key attribute group (FP category 1; 13 type tokens, e.g. 1H91,1H92,1H93,1J31) / vehicle type-key attribute group (FP category 25; 3 type tokens, e.g. 1J31,1J32,1J33)· token `CALMING_KOMBI`· source: firmware-token

### `300D/0/01000000b` — MFID cluster display variant  ·  _med_

Selects a variant of the multi-function instrument display (MFID) layout in the cluster. Determines which graphical/content variant of the cluster screen is used.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `MFID_KOMBI_VARIANT`· source: firmware-token

### `300D/0/10000000b` — Navigation guidance switchable in cluster  ·  _med_

Enables the switchable turn-by-turn navigation guidance display (arrow/maneuver info) in the instrument cluster. Requires a navigation system (SA 606 or 609) to be fitted.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: 606 Navigation system Business / 609 Professional navigation system· token `KOMBIGUIDING_SCHALTBAR`· source: firmware-token

### `300D/1/00000011b` — Cluster CIC generation flag  ·  _med_

2-bit field relating to the CIC (Car Information Computer) generation compatibility of the instrument cluster. Only one enum value is known from firmware: KOMBI_HIGH (high-specification cluster variant). Other values are not documented.

| value | meaning |
|---|---|
| `1` | KOMBI_HIGH (high-spec cluster) |

default `00`· gate: FA-gated (depends on vehicle options)· token `KOMBI_CIC`· source: firmware-token

### `300D/1/00001100b` — Units master source  ·  _med_

Determines which ECU is the master for unit settings (metric/imperial, etc.). Only one enum value is documented from firmware: HMI (iDrive head unit as master). Other values are not individually documented.

| value | meaning |
|---|---|
| `1` | HMI (head unit master) |

default `00`· gate: FA-gated (depends on vehicle options)· token `EINHEITEN_MASTER`· source: firmware-token

### `300D/1/01110000b` — Range figures in cluster  ·  _med_

Chooses which range figures the instrument cluster shows: the minimum range, the maximum range or both. Check only figures the car's cluster can show.

| value | meaning |
|---|---|
| `0` | None |
| `1` | Minimum range |
| `2` | Maximum range |
| `3` | Minimum and maximum range |

Bits (set = on): bit 0 Minimum range; bit 1 Maximum range

default `00`· gate: always (no FA gate)· token `RANGE_VALUE_KOMBI_NEU`· source: firmware-trace

### `300D/1/10000000b` — Micro map in cluster  ·  _med_

Enables a small navigation map (mini-map / micromap) overlay in the instrument cluster display. Requires navigation system hardware.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `00`· gate: FA-gated (depends on vehicle options)· token `MICROMAP_KOMBI`· source: firmware-token

### `300D/2/00000011b` — Cluster screen resolution type (RES)  ·  _med_

2-bit field specifying the display resolution type/class of the instrument cluster screen. No individual enum values are documented for this field from available sources.

default `00`· gate: FA-gated (depends on vehicle options)· token `KOMBI_RES`· source: firmware-token

### `300D/2/00001100b` — Cluster resolution switch  ·  _low_

Setting for the resolution of the navigation map graphics the head unit draws for the instrument cluster. Best left unchanged.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Enabled |

default `00`· gate: FA-gated (depends on vehicle options)· token `KOMBI_AUFLOESUNG`· source: firmware-trace

### `300D/2/00010000b` — Welcome jingle request target (WBK)  ·  _med_

Single-bit field indicating whether the instrument cluster (KOMBI) is the target for the welcome/startup jingle sound. When set, the cluster plays the startup chime.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | KOMBI (cluster plays jingle) |

default `00`· gate: FA-gated (depends on vehicle options)· token `WBK_JINGLE_REQUEST`· source: firmware-token

### `300D/2/00100000b` — iDrive 5 color set  ·  _low_

Uses the iDrive 5 color scheme for the navigation map graphics the head unit draws for the instrument cluster. Best left unchanged.

| value | meaning |
|---|---|
| `0` | Enabled |
| `1` | Disabled |

default `01`· token `ID5_COLOR_SET`· source: firmware-trace

### `300D/2/11000000b` — Instrument cluster 2-bit field (byte 2, bits 7-6)  ·  _low_

An unidentified 2-bit field in the KOMBI coding page. Purpose not determined from available sources.

token `KOMBI byte 2 (2-bit field (00..00))`· source: inferred

### `300D/3/11111111b` — Cluster phone list update delay  ·  _med_

Sets the short delay the head unit waits before it updates the phone list shown in the instrument cluster. Best left unchanged.

| value | meaning |
|---|---|
| `30` | 150 ms |

_Not a user setting: Timing parameter: HmiMain3D reads it as a quantity (a raw x 5 ms timer for the cluster phone list), but timing settings stay hidden (decision 2); the unit's table holds one value only._

default `1E`· token `DEBOUNCE_KOMBI_BASIS`· source: firmware-trace

### `300D/4/00111111b` — Cluster hardware variant code (KI)  ·  _med_

6-bit code identifying the specific instrument cluster (KI = Kombiinstrument) hardware variant installed. Determines cluster feature set and display capabilities.

default `00`· gate: FA-gated (depends on vehicle options)· token `KI_KOMBI_VARIANT`· source: firmware-token

### `300D/4/01000000b` — Cluster panel configuration (KI Tafel)  ·  _med_

Configures the instrument cluster panel/display layout (Tafel = panel/board). Controls how the cluster's display area is structured or segmented.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `01`· gate: FA-gated (depends on vehicle options)· token `KI_TAFEL_KONFIGURATION`· source: firmware-token

### `300D/4/10000000b` — Cluster brightness control enabled  ·  _med_

Enables head-unit brightness control for the instrument cluster. When active, the HU can send brightness/backlight level commands to the cluster.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `01`· gate: FA-gated (depends on vehicle options)· token `KI_BRIGHTNESS`· source: firmware-token

### `300D/5/00000111b` — Cluster display mode choices  ·  _med_

Sets which instrument cluster display modes the driver can pick in the central display's instrument cluster settings: standard, a reduced view that shows less, and an individual view.

| value | meaning |
|---|---|
| `0` | Disabled |
| `1` | Standard or reduced |
| `2` | Standard, reduced or individual |

default `02`· gate: always (no FA gate)· token `KI_DISP_RB_PRESELECT`· source: firmware-trace

### `300D/5/00001000b` — Cluster checkbox: drive mode view  ·  _med_

Enables the drive mode view (Fahrmodusansicht) checkbox in the cluster display options, allowing the user to toggle the driving mode indicator in the cluster info area.

| value | meaning |
|---|---|
| `0` | Off/hidden |
| `1` | On/available |

default `01`· gate: FA-gated (depends on vehicle options)· token `KI_DISP_CB_FAHRMODUSANSICHT`· source: firmware-token

### `300D/5/00010000b` — Cluster checkbox: route overview  ·  _med_

Enables the route overview (Streckenuebersicht) checkbox in cluster display options, allowing the user to show a simplified route/navigation overview in the cluster.

| value | meaning |
|---|---|
| `0` | Off/hidden |
| `1` | On/available |

default `01`· gate: FA-gated (depends on vehicle options)· token `KI_DISP_CB_STRECKENUEBERSICHT`· source: firmware-token

### `300D/5/00100000b` — Cluster checkbox: additional road signs  ·  _med_

Enables the additional road sign display checkbox in the cluster, allowing supplementary traffic sign information (e.g. speed limit warnings) to be shown.

| value | meaning |
|---|---|
| `0` | Off/hidden |
| `1` | On/available |

default `01`· gate: FA-gated (depends on vehicle options)· token `KI_DISP_CB_ADDITIONAL_SIGN`· source: firmware-token

### `300D/5/01000000b` — Cluster checkbox: speedometer needle band  ·  _med_

Enables the speedometer needle band (Tachozeigerband) display checkbox in the cluster, which shows a colored band or sweep around the analog speedometer needle.

| value | meaning |
|---|---|
| `0` | Off/hidden |
| `1` | On/available |

default `01`· gate: FA-gated (depends on vehicle options)· token `KI_DISP_CB_TACHOZEIGERBAND`· source: firmware-token

### `300D/5/10000000b` — Instrument cluster boolean flag (byte 5, bit 7)  ·  _low_

An unidentified boolean flag in byte 5 of the KOMBI coding page. Purpose not determined from available sources. Default is 1 (on).

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

default `01`· gate: FA-gated (depends on vehicle options)· token `KOMBI byte 5 (boolean flag (Bool)`· source: inferred

### `300D/6/00000001b` — Cluster checkbox: M dynamic driving info  ·  _med_

Enables the M-model dynamic driving information checkbox (Fahrdynamik) in the cluster, making performance metrics (lateral g-force, engine output etc.) available in the cluster display.

| value | meaning |
|---|---|
| `0` | Off/hidden |
| `1` | On/available |

default `01`· gate: FA-gated (depends on vehicle options)· token `KI_DISP_CB_M_FAHRDYNAMIK`· source: firmware-token

### `300D/6/00000010b` — Cluster checkbox: Sport Performance Analyzer  ·  _med_

Enables the Sport Performance Analyzer (SPA) checkbox in the cluster display options. SPA provides real-time performance metrics in the cluster for M/sport vehicles.

| value | meaning |
|---|---|
| `0` | Off/hidden |
| `1` | On/available |

default `01`· gate: FA-gated (depends on vehicle options)· token `KI_DISP_CB_SPA`· source: firmware-token

### `300D/6/00000100b` — Cluster checkbox: digital speed display  ·  _med_

Enables the digital speed readout checkbox in the cluster display options, allowing the driver to toggle a numeric speed display alongside or instead of the analog speedometer.

| value | meaning |
|---|---|
| `0` | Off/hidden |
| `1` | On/available |

default `01`· gate: FA-gated (depends on vehicle options)· token `KI_DISP_CB_SPEED_DIGITAL`· source: firmware-token

### `300D/6/00001000b` — Cluster checkbox: clock display  ·  _med_

Enables the clock/time display checkbox in the cluster info area options, allowing the current time to be shown in the instrument cluster.

| value | meaning |
|---|---|
| `0` | Off/hidden |
| `1` | On/available |

default `01`· gate: FA-gated (depends on vehicle options)· token `KI_DISP_CB_CLOCK`· source: firmware-token

### `300D/6/00010000b` — Cluster checkbox: trip computer (BC) display  ·  _med_

Enables the trip computer / board computer (BC = Bordcomputer) checkbox in the cluster, making on-board computer info pages (fuel economy, range, etc.) accessible in the cluster.

| value | meaning |
|---|---|
| `0` | Off/hidden |
| `1` | On/available |

default `01`· gate: FA-gated (depends on vehicle options)· token `KI_DISP_CB_BC`· source: firmware-token

### `300D/6/00100000b` — Cluster checkbox: trip computer arrival time and distance  ·  _med_

Enables the arrival time and remaining distance trip computer fields in the cluster display. These are navigation-integrated BC fields showing ETA and distance to destination.

| value | meaning |
|---|---|
| `0` | Off/hidden |
| `1` | On/available |

default `01`· gate: FA-gated (depends on vehicle options)· token `KI_DISP_CB_HMI_BC_ANKUNFTSZEIT_DISTANCE_ENABLE`· source: firmware-token

### `300D/6/01000000b` — Cluster checkbox: trip computer range display  ·  _med_

Enables the remaining fuel/energy range field in the cluster trip computer display. Shows estimated driving range remaining.

| value | meaning |
|---|---|
| `0` | Off/hidden |
| `1` | On/available |

default `01`· gate: FA-gated (depends on vehicle options)· token `KI_DISP_CB_BC_RANGE_ENABLE`· source: firmware-token

### `300D/6/10000000b` — Cluster checkbox: instantaneous fuel consumption (combustion)  ·  _med_

Enables the real-time/momentary fuel consumption display for the combustion engine in the cluster trip computer. Firmware enum value NICHT_AKTIV = not active (off).

| value | meaning |
|---|---|
| `0` | Not active |
| `1` | Active |

default `01`· gate: FA-gated (depends on vehicle options)· token `KI_DISP_CB_BC_MOM_VERBR_VERBRENNER_ENABLE`· source: firmware-token

### `300D/7/00000001b` — Cluster checkbox: instantaneous electric consumption  ·  _med_

Enables the real-time/momentary electric energy consumption display in the cluster trip computer. Applicable to hybrid/EV vehicles.

| value | meaning |
|---|---|
| `0` | Off/hidden |
| `1` | On/available |

default `01`· gate: FA-gated (depends on vehicle options)· token `KI_DISP_CB_BC_MOM_VERBR_ELEKTR_ENABLE`· source: firmware-token

### `300D/7/00000010b` — Cluster checkbox: average speed and consumption  ·  _med_

Enables the average speed and average fuel/energy consumption fields in the cluster trip computer display.

| value | meaning |
|---|---|
| `0` | Off/hidden |
| `1` | On/available |

default `01`· gate: FA-gated (depends on vehicle options)· token `KI_DISP_CB_BC_AVERAGE_SPEED_CONS_ENABLE`· source: firmware-token

### `300D/7/00000100b` — Cluster checkbox: engine coolant temperature  ·  _med_

Enables the engine coolant/oil temperature display checkbox in the cluster trip computer. When active, engine temperature is shown as a BC field.

| value | meaning |
|---|---|
| `0` | Off/hidden |
| `1` | On/available |

default `01`· gate: FA-gated (depends on vehicle options)· token `KI_DISP_CB_MOTOR_TEMP_BC_ENABLE`· source: firmware-token

### `300D/7/00001000b` — Cluster checkbox: EDA trip counter enable  ·  _med_

Enables the EDA (abbreviated eco/efficiency display counter) checkbox in the cluster trip computer. EDA full expansion is not confirmed in available sources but is context-consistent with eco-driving efficiency tracking.

| value | meaning |
|---|---|
| `0` | Off/hidden |
| `1` | On/available |

default `00`· gate: FA-gated (depends on vehicle options)· token `KI_DISP_CB_BC_EDA_ENABLE`· source: firmware-token

### `300D/7/00010000b` — Cluster checkbox: battery state-of-charge display  ·  _med_

Enables the high-voltage battery state-of-charge (SOC) display in the cluster trip computer. Relevant for hybrid/EV vehicles.

| value | meaning |
|---|---|
| `0` | Off/hidden |
| `1` | On/available |

default `01`· gate: FA-gated (depends on vehicle options)· token `KI_DISP_CB_HMI_BC_SOC_ENABLE`· source: firmware-token

### `300D/7/00100000b` — Cluster checkbox: electric trip counter average speed  ·  _med_

Enables the average speed counter for the electric (EV) trip segment in the cluster trip computer. Tracks average speed over an electric-driving trip.

| value | meaning |
|---|---|
| `0` | Off/hidden |
| `1` | On/available |

default `01`· gate: FA-gated (depends on vehicle options)· token `KI_DISP_CB_HMI_BC_E_COUNTER_AVG_SPEED`· source: firmware-token

### `300D/7/01000000b` — Cluster: average electric energy consumption display  ·  _med_

Enables display of average electric energy consumption (kWh/100km or similar) in the cluster trip computer area.

| value | meaning |
|---|---|
| `0` | Off/hidden |
| `1` | On/available |

default `01`· gate: FA-gated (depends on vehicle options)· token `KI_DISP_BC_AVG_CONSUMPTION_ELECTRIC`· source: firmware-token

### `300D/7/10000000b` — Instrument cluster boolean flag (byte 7, bit 7)  ·  _low_

An unidentified boolean flag in byte 7 of the KOMBI coding page. Purpose not determined from available sources.

| value | meaning |
|---|---|
| `0` | Off/inactive |
| `1` | On/active |

token `KOMBI byte 7 (boolean flag (Bool)`· source: inferred

### `300D/8/11111111b` — Instrument cluster multi-byte data block (byte 8+)  ·  _low_

A multi-byte data block starting at byte 8 and extending to byte 78 of the KOMBI coding page. This covers HUD radio-button configuration and other cluster parameters not individually decoded. Exact structure not resolved from available sources.

token `KOMBI byte 8 (multi-byte value (syset Int/UInt8/16))`· source: inferred

