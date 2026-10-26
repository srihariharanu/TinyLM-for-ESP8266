# Source and artifact guide

| Location | Role |
| --- | --- |
| prepare_focused.py | Generates original focused training/held-out examples |
| train_gru.py | Prepares data, trains PyTorch model and writes checkpoint |
| export_gru.py | Quantizes checkpoint, exports C arrays and evaluates host inference |
| build_web.py | Deterministically compresses editable page into firmware header |
| firmware/RecurrentLM/RecurrentLM.ino | Numeric encoder/GRU inference and serial loop |
| firmware/RecurrentLM/portal.h | ESP8266 AP, DNS, HTTP, sessions and incremental jobs |
| firmware/RecurrentLM/weights.h | Complete generated vocabulary and learned parameters |
| firmware/RecurrentLM/web_ui.h | Complete compressed page |
| web/index.html | Editable HTML/CSS/JavaScript, without remote assets |
| model/gru-best.pt | Reference trained checkpoint; load only trusted artifacts |
| model/gru-int8.npz | Host quantized arrays |
| model/gru-info.json | Architecture, run settings and measured results |
| model/evaluation-*.json | Full evaluation prompts/replies and keyword diagnostics |
| model/reference-int8.json | Small neural reference set for device comparison |
| data/ | All original/public source data, prepared pairs, token list and provenance |
| environment.ps1 / setup-developer.ps1 | Portable local dependency environment |
| build-firmware.ps1 / train-and-build.ps1 | Compile-only / full train-export-build pipelines |
| serial_console.py / chat.ps1 | USB console and exact inference comparison |
| tests/test_release.py | Source, syntax, page, firmware and privacy contract checks |
| tests/preview_server.py | Local mock server for UI testing, not model inference |
| tests/*ui_test.cjs | Mock/mobile and actual-device browser checks |
| tests/wifi_link.py / wifi_portal_test.py | Opt-in Windows Wi-Fi/network tests |
| ready-to-flash/ | End-user image, simple flash installer and manual |
| third_party/ | Original installed core snapshot for runtime modification/relinking |
| docs/validation/ | Sanitized prior hardware/UI/training evidence |
| docs/RELEASE_VALIDATION.json | Current local preparation check results |
| SHA256SUMS.txt | Exact file-integrity inventory |

Generated binary/checkpoint/data artifacts are deliberately included. Compiler
ELF/map files, installed packages and raw personal logs are not public inputs.

Project maintainer and original-work rights holder: **Sri Hariharan U**.
Rights contact: **srihariharanu@gmail.com**.
