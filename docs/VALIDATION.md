# Validation and known limitations

## Prior actual-device evidence

ESP8266EX with 4 MB flash, 160 MHz, Windows host. The release binary is byte-identical
to the previously tested portal firmware. Packaging does not imply a new device
flash or test on additional boards.

- Compiler program: 644,241 bytes; full flash image: 648,400 bytes.
- Compiler static memory: 38,408 bytes.
- Heap: about 39,000 bytes after hotspot startup; 37,456 after real Wi-Fi chat.
- Nineteen portal checks passed: page equality, captive redirect, DNS, sessions,
  limits, concurrent-job rejection, result isolation, neural reply equality and
  actual mobile-browser chat flow among them.
- UI widths checked: 320, 390 and 768 pixels.
- Earlier USB-only inference: about 19.7 characters/s, not a guarantee for portal
  load or every prompt.

Sanitized evidence is under docs/validation/. Private network state, raw serial/
flash logs, screenshots, debug ELF/map files and prior PDFs are excluded.

## This release's preparation

Python syntax, firmware hashes, embedded-page/source equality, expected file
coverage, licensing, local documentation links and private-path scanning are
checked. See RELEASE_VALIDATION.json for executed results. GitHub workflows now run on the public repository. Initial publication checks
passed for package validation and ESP8266 firmware compilation. The JSON records
local preparation state; see the current Actions run for remote CI status.

https://github.com/srihariharanu/TinyLM-for-ESP8266/actions

Support is demonstrated on one ESP8266EX configuration. Other boards, Linux/macOS
flashing and modified runtime builds need validation. No ESP32 support, commercial
certification, external security audit or broad conversational benchmark is claimed.

Project maintainer and original-work rights holder: **Sri Hariharan U**.
Rights contact: **srihariharanu@gmail.com**.
