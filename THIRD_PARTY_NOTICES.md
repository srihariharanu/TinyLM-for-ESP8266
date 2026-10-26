# Third-party notices and license scope

Original TinyLM application code is Apache-2.0 licensed. Distributed ESP8266 firmware
also links components with other terms. Retain this file and `licenses/`.

| Component | Version / source | Terms |
| --- | --- | --- |
| ESP8266 Arduino core, Wi-Fi, web server, DNS | 3.0.2; https://github.com/esp8266/Arduino/tree/3.0.2 | LGPL-2.1 plus component notices; installed runtime platform snapshot in developer `third_party/esp8266-arduino-core-3.0.2.zip` |
| Espressif NONOS SDK | bundled with core 3.0.2 | Espressif SDK license, restricted to Espressif ESP8266; `licenses/Espressif-SDK.txt` |
| lwIP, BearSSL, uzlib, allocators and other bundled code | core snapshot | Original component headers/notices are retained in the full snapshot; license-named files also in `licenses/esp8266-core/` |
| HuggingFaceTB SmolTalk / everyday-conversations | bundled dataset snapshot | Apache-2.0; provenance, original cards and license in developer `data/` |
| PyTorch, NumPy, PyArrow | developer requirements | Installed separately; original upstream terms apply |
| esptool | 5.6.0; https://github.com/espressif/esptool | GPL-2.0-or-later; installed separately by flash setup, not bundled |
| Arduino CLI and Xtensa compiler | developer build guide | External tools installed separately under upstream terms |

GCC runtime libraries use GPL-3.0 with GCC Runtime Library Exception 3.1;
see licenses/GPL-3.0.txt and licenses/GCC-Runtime-Exception-3.1.txt.
The exception allows eligible compiled combinations under their own terms.

## Runtime source and relinking

Distribute the companion developer package with every firmware release. It
contains complete application source, generated weights, build instructions,
and a runtime platform snapshot of installed core 3.0.2, its source,
prebuilt SDK libraries and original notices. Use docs/DEVELOPMENT.md to rebuild
and relink with a modified LGPL core. No signing keys or device locks are used.
Unused upstream examples/tests, demonstration keys and local bytecode caches
are excluded. Included runtime files are unchanged; developer third_party/
SNAPSHOT.md and SNAPSHOT_EXCLUSIONS.json document the scope.
The Xtensa toolchain is obtained through the pinned core package manager.
The SDK includes prebuilt components under its separate license; their source
availability is not claimed and they are not relicensed Apache-2.0.

Reverse engineering for debugging modifications to LGPL-covered portions is
permitted as required by LGPL-2.1 section 6. No project term restricts it.
Preserve all upstream notices when repackaging. Original TinyLM rights contact:
Sri Hariharan U, srihariharanu@gmail.com. Upstream ownership remains unchanged.
