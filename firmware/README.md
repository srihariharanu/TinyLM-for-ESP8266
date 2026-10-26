# TinyLM for ESP8266 — ready to flash

<p align="center"><img src="tinylm-logo.png" alt="TinyLM chip and neural circuit project logo" width="180"></p>

**Experimental • designed for ESP8266 • fully offline after flashing**

A tiny trained neural language model and mobile chat page in one firmware file.
No training, source editing, cloud account, API key, display or laptop server is
needed to chat. This is a narrow-domain experiment, not a general assistant.

## What you need

- ESP8266 board with **4 MB flash**, USB data cable and computer for installation.
- Python 3.12 recommended (Python 3.10+ required by the flashing tool).
- Correct USB serial driver, often CH340 or CP210x, from the chip/board maker's
  official site. Use a USB development board with regulator. Bare ESP8266
  modules require 3.3 V power and logic; do not connect them directly to 5 V.
- Internet once to install the free flash tool; use is offline afterwards.

## Windows installation

1. Extract the whole folder. Close serial monitors and other flashing programs.
2. Double-click **Setup and Flash.cmd**. It installs the tool inside this folder,
   lists USB ports, and asks you to choose your board.
3. Confirm by typing `FLASH`. This replaces the current application.
4. Wait for successful completion, then press RESET on the board.

Later use **Flash.cmd** to reuse the installed tool without downloading it.
The installer validates the firmware checksum before accessing the device.
Do not unplug during writing. Administrator access is normally unnecessary.

## Linux / macOS

Run `python3 -B flash.py --setup` from this folder, select the port and confirm.
Later use `python3 -B flash.py`. Linux may require USB serial group permissions.
These platforms have not been hardware-tested for this release.

## Open chat on your phone

1. Join **TinyLM-Offline**, password **TinyLM8266**.
2. Keep the connection when the phone says there is no internet.
3. Open **http://192.168.4.1/**. A captive sign-in notification may also appear.
4. Enter a non-sensitive display name and choose **Open chat**.
5. Try `hello`, `what is ram`, `what is flash used for`, `what is a language model`,
   or `tell me a joke`. Wait a few seconds for a reply.

Each message is independent. Maximum input: 120 characters; reply: 160 characters.
Answers can repeat learned phrases or be irrelevant on unfamiliar subjects.
Four sessions are supported, with one generation at a time. Sign-in is a local
display-name session, not a secure account. The published Wi-Fi password is a
demo default. Use in a trusted local environment without confidential inputs.

## Troubleshooting

- No port: try a data cable, another USB socket and the correct USB driver.
- Connection fails: close serial apps. For boards without working auto-reset,
  hold FLASH/BOOT, tap RESET, release FLASH/BOOT when the connection begins;
  consult the board instructions if its buttons differ.
- No hotspot: press RESET and confirm 4 MB flash hardware.
- Page missing: enter the HTTP address manually; mobile data switching or a VPN
  can route away from the hotspot. Keep the no-internet Wi-Fi connection.
- Busy: wait for the active request. Reset if the board becomes unresponsive.
- Missing Python/pip: install from https://www.python.org/downloads/ with pip
  and the launcher enabled, then rerun setup.

## Files and rights

`TinyLM-ESP8266.bin` contains model and UI. `firmware.json` specifies its hash,
hardware target, offset `0x0`, DOUT mode and 4 MB flash. No filesystem image is
needed. The binary was previously tested on ESP8266EX; packaging does not imply
a new hardware test, commercial certification, or support for every board.

Creator: **Sri Hariharan U**. Rights: **srihariharanu@gmail.com**.
Original project work is Apache-2.0 licensed, free of charge. Combined firmware has
additional upstream terms: retain THIRD_PARTY_NOTICES.md and licenses/.
Complete source and rebuild instructions are in the sibling source/ folder
and the pinned source link in SOURCE_CODE.md. Distribute source access with
the firmware release. Future updates: ROADMAP.md.
