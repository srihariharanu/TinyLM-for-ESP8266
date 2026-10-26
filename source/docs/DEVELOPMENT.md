# Developer setup and firmware build

## Reference environment

Windows; Python 3.12.10; PyTorch 2.6.0+cu124; NumPy 2.5.4; PyArrow 26.0.0;
pyserial 3.5; esptool 5.6.0; Arduino CLI 1.5.2-rc.1; ESP8266 core 3.0.2.
Python dependencies are pinned; GPU is optional. Install Python 3.12 and Arduino
CLI from their official sources. Node.js 20+ is only needed for browser tests.

## Windows setup and build

From the source/ workspace inside the repository:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup-developer.ps1
. .\environment.ps1
arduino-cli core update-index --additional-urls https://arduino.esp8266.com/stable/package_esp8266com_index.json
arduino-cli core install esp8266:esp8266@3.0.2 --additional-urls https://arduino.esp8266.com/stable/package_esp8266com_index.json
powershell -ExecutionPolicy Bypass -File .\build-firmware.ps1
```

Use `setup-developer.ps1 -Cuda` for CUDA 12.4 PyTorch on compatible NVIDIA hardware
with a suitable driver. CPU training also works. Python is installed in `.venv/`;
caches, temporary output and Arduino packages are stored inside the checkout.
Compiler installations are obtained through the Arduino core manager.

Compilation uses supplied weights without retraining. Outputs are under
`build/export/`. It does not overwrite the ready-to-flash product. Updating that
product requires new metadata, checksums, tests, version and release notes.

## Linux / macOS equivalents

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -B build_web.py
arduino-cli core update-index --additional-urls https://arduino.esp8266.com/stable/package_esp8266com_index.json
arduino-cli core install esp8266:esp8266@3.0.2 --additional-urls https://arduino.esp8266.com/stable/package_esp8266com_index.json
arduino-cli compile --fqbn esp8266:esp8266:generic:xtal=160,FlashMode=dout,eesz=4M1M --output-dir build/export firmware/RecurrentLM
```

These non-Windows recipes are provided for portability, not a claim of hardware
validation. Set project-local caches if desired.

## Flash a developer build

```sh
python -m esptool --chip esp8266 --port COM3 --baud 115200 write-flash --flash-mode dout --flash-size 4MB 0x0 build/export/RecurrentLM.ino.bin
```

Replace the port with the actual device, for example `/dev/ttyUSB0` on Linux.
This replaces the current application; close serial monitors first and reset
afterwards. The packaged image instead uses `../firmware/flash.py`, which
checks its image hash before accessing hardware.

## Rebuild and relink with a modified LGPL core

`third_party/esp8266-arduino-core-3.0.2.zip` contains the installed
runtime platform, library sources, linker scripts, prebuilt SDK archives and
notices. Unused examples/tests, demo key fixtures and local bytecode are excluded;
see third_party/SNAPSHOT.md. Included runtime files remain unchanged.
Install core 3.0.2 through CLI first to obtain the external Xtensa toolchain.
Extract the snapshot, then replace the installed 3.0.2 platform content with it
or a modified version, preserving the directory structure. Windows local path:
`.arduino/data/packages/esp8266/hardware/esp8266/3.0.2/`.
Clean your local `build/objects/` and compile again using the supplied application
source and generated weights. No signing key or device lock is used. Application
source is Apache-2.0 licensed; retain LGPL and vendor notices for the linked runtime.

## Tests

```sh
python -B -m unittest discover -s tests -p "test_*.py"
python -B build_web.py
```

For browser checks, run `npm ci` and `npx playwright install chromium`. Start
`python -B tests/preview_server.py`, then run `npm run test:ui` in another terminal.
To use an existing Chromium-family browser, set BROWSER_EXECUTABLE_PATH to its
executable path; otherwise Playwright uses its installed Chromium.
The preview uses a fixed mock reply for UI testing. It is never part of firmware
and does not substitute for neural inference validation.

For hardware: `python -B serial_console.py --port COM3 --test` may reset the board.
Join the ESP hotspot manually before `npm run test:live`. The opt-in Windows test
`tests/wifi_portal_test.py` temporarily switches Wi-Fi and attempts to restore it;
run only when an interruption is acceptable. These tests are not part of CI.

Only load trusted PyTorch checkpoints: `.pt` can use pickle. Supplied artifact
hashes are recorded; arbitrary downloaded checkpoints may execute unsafe code.

Project maintainer and original-work rights holder: **Sri Hariharan U**.
Rights contact: **srihariharanu@gmail.com**.
