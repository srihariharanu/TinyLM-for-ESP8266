# Dependency inventory

Reference versions appear in DEVELOPMENT.md. Runtime training dependencies are
pinned in requirements.txt; UI test tooling in package.json and package-lock.json.
Firmware uses ESP8266 Arduino core 3.0.2. Its exact installed platform snapshot
is in third_party/, preserving original licenses. Installed compiler/Python
packages are not redistributed as original Apache-2.0 work. Review compatibility and
licenses before dependency upgrades.

Official upstreams: https://pytorch.org/ , https://numpy.org/ ,
https://arrow.apache.org/docs/python/ , https://pyserial.readthedocs.io/ ,
https://docs.espressif.com/projects/esptool/ , https://github.com/esp8266/Arduino ,
https://github.com/arduino/arduino-cli , https://playwright.dev/ .

Project maintainer and original-work rights holder: **Sri Hariharan U**.
Rights contact: **srihariharanu@gmail.com**.
