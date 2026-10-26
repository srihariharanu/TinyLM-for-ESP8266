# TinyLM for ESP8266

**A trained neural language model and offline mobile chat portal on an ESP8266.**

[![Build and package checks](https://github.com/srihariharanu/TinyLM-for-ESP8266/actions/workflows/validate.yml/badge.svg)](https://github.com/srihariharanu/TinyLM-for-ESP8266/actions/workflows/validate.yml)
![Target: ESP8266](https://img.shields.io/badge/target-ESP8266-2c6772)
![Status: experimental](https://img.shields.io/badge/status-experimental-d69e2e)
![Original project license: Apache 2.0](https://img.shields.io/badge/license-Apache--2.0-3776ab)
![Release candidate: 0.1.0](https://img.shields.io/badge/version-0.1.0--experimental-627d49)

Created and maintained by **Sri Hariharan U** · Rights contact:
**srihariharanu@gmail.com**

TinyLM explores how much learned text generation can fit on a small microcontroller.
The ESP8266 stores its model in flash, performs neural inference itself, creates
its own Wi-Fi hotspot, and serves a mobile chat page. A phone is the interface;
it does not run the model. No cloud API, API key, internet connection or laptop
server is required during normal use after flashing.

> **Experimental research software, designed for ESP8266.** The reference target
> is an ESP8266EX with 4 MB flash at 160 MHz. This is a narrow-domain language-model
> demonstration, not a general assistant or a production-certified product.

## Choose your folder

| Folder | Audience | Contents |
| --- | --- | --- |
| [source/](source/README.md) | Firmware and model development | Full model/training source, data, checkpoint, build scripts and tests |
| [firmware/](firmware/README.md) | Ready-to-flash firmware | Firmware, simple installer and step-by-step mobile-chat instructions |

Both are maintained in this one repository. End users can use the product folder
without installing the developer training stack.

## Contents

- [Start here](#start-here)
- [Quick start](#quick-start)
- [What runs on the device](#what-runs-on-the-device)
- [Architecture](#architecture)
- [Measured results](#measured-results)
- [Development and training](#development-and-training)
- [Repository map](#repository-map)
- [Privacy and limitations](#privacy-and-limitations)
- [Documentation](#documentation)
- [Contributing and future updates](#contributing-and-future-updates)
- [Ownership and licensing](#ownership-and-licensing)

## Start here

| You want to… | Use |
| --- | --- |
| Install the existing model without editing source | [Ready-to-flash product and manual](firmware/README.md) |
| Compile firmware using the supplied trained weights | [Developer guide](source/docs/DEVELOPMENT.md) |
| Reproduce data preparation, training and export | [Training guide](source/docs/TRAINING.md) |
| Understand model behavior and limits | [Model card](source/docs/MODEL_CARD.md) |
| Integrate with the local HTTP interface | [API reference](source/docs/API_REFERENCE.md) |
| Inspect evidence or contribute | [Validation](source/docs/VALIDATION.md), [contribution guide](CONTRIBUTING.md) |

This repository includes both the complete complete source and the simple
end-user product in `firmware/`. The product image already contains the
trained model, hotspot server and page; no dataset or separate filesystem image
needs to be uploaded to the board.

## Quick start

### 1. Install once from a computer

Use an ESP8266 USB development board with **4 MB flash**, a USB data cable and
Python 3.12 recommended. The flashing tool needs internet for its initial setup.
Download/extract this repository and open `firmware/`.

On Windows, double-click **Setup and Flash.cmd**, choose the ESP8266 port and
confirm the firmware replacement by typing `FLASH`. Wait for completion and
press RESET on the board. For subsequent offline flashing, use **Flash.cmd**.

On Linux/macOS, run `python3 -B flash.py --setup` from that folder. These platforms
have instructions provided but have not been hardware-validated for this release.
See the [installation manual](firmware/README.md) for drivers, boot-button
recovery and troubleshooting. The installer verifies its firmware hash before
accessing a device.

### 2. Open the chat on a phone

| Setting | Value |
| --- | --- |
| Wi-Fi network | `TinyLM-Offline` |
| Demonstration Wi-Fi password | `TinyLM8266` |
| Local address | **http://192.168.4.1/** |
| Sign-in | A local display name; no online account |

Keep the Wi-Fi connection when the phone reports no internet. Open the local
address manually if no captive sign-in notification appears. Enter a display
name, choose **Open chat**, and send a short message.

Try `hello`, `what is ram`, `what is flash used for`, `what is a language model`,
or `tell me a joke`. Allow a few seconds for generation. Each message is independent;
previous turns are not remembered. Unfamiliar questions can produce irrelevant
answers.

## What runs on the device

| Component | Implementation |
| --- | --- |
| Input encoder | Learned word embeddings with attention pooling; input word order is discarded |
| Decoder | Character-level recurrent GRU with greedy decoding |
| Parameters | 284,551 learned parameters |
| Input vocabulary | 1,841 word tokens; 64-dimensional embeddings |
| Decoder dimensions | 192 hidden units; 48-dimensional character embeddings |
| Weight representation | Per-row int8 weights, float32 scales/biases; flash-resident arrays |
| Compressed parameter arrays | 307,440 bytes, excluding vocabulary and runtime |
| Interface | Embedded HTML/CSS/JavaScript, local HTTP and wildcard DNS |
| Limits | 120 input characters; at most 160 reply characters |
| Concurrency | Four local sessions; one active generation job |

There is no runtime question/answer table, retrieval service or hand-written
rule choosing a response. Focused example pairs are used during training;
the deployed inference loop computes its replies from learned parameters.
The development-only UI preview server returns a fixed mock reply and is never
part of the device firmware.

## Architecture

```text
Training computer
  Public conversation data + original focused examples
    -> normalize and prepare -> train encoder/GRU -> checkpoint
    -> quantize and verify -> flash-resident parameter arrays

Firmware build
  Model arrays + inference + Wi-Fi portal + embedded page
    -> ESP8266 Arduino compiler -> one firmware image -> USB flash

Offline use
  Phone browser <-> ESP8266 hotspot / HTTP API
                          |
                   attention encoder
                          |
                   GRU character decoder
                          |
                    generated reply
```

The browser polls partial results while the board generates characters. Incremental
work and yield calls keep its network server responsive. The UI uses no remote
scripts, fonts, CDN or assets; repository badges above are only GitHub-page images.
See [architecture](source/docs/ARCHITECTURE.md) for implementation details.

## Measured results

The packaged image is the previously tested ESP8266EX portal firmware. The current
publication preparation also compiled the clean source and checked packaging.
These are separate from a new hardware flash, which was not performed in this pass.

| Observation | Recorded result | Interpretation |
| --- | --- | --- |
| Flashable image | 648,400 bytes | Includes image overhead; compiler reports 644,241 program bytes |
| Static memory | 38,408 bytes reported by compiler | Runtime heap varies with network activity |
| Prior post-chat free heap | 37,456 bytes | One actual-device observation |
| Final unseen-prompt diagnostic | 9 / 12 topic-keyword matches | Small narrow-domain check, not general chatbot accuracy |
| Earlier USB device/host comparison | 7 / 7 exact reply matches | Tests implementation consistency, not factual correctness |
| Prior portal verification | 19 checks passed | Includes real on-device neural reply and mobile browser flow |
| Current package unit tests | 10 passed | Includes integrity, syntax and mock installer checks |
| Current mobile UI checks | 11 passed | Includes widths 320, 390 and 768 px, sessions and no remote assets |

GitHub CI is configured; the workflow run on this repository is the authoritative
record of its remote status. See [validation and limits](source/docs/VALIDATION.md),
[recorded local checks](source/docs/RELEASE_VALIDATION.json), and the full evaluation
outputs under `model/`, including incorrect replies.

## Development and training

Clone the repository:

```sh
git clone https://github.com/srihariharanu/TinyLM-for-ESP8266.git
cd TinyLM-for-ESP8266/developer
```

For Windows development, install Python 3.12 and Arduino CLI, then follow
[DEVELOPMENT.md](source/docs/DEVELOPMENT.md). It includes the pinned ESP8266 core 3.0.2
installation, build commands, optional CUDA setup, hardware tests and runtime
relinking instructions. The reference training run used an RTX 4050; a GPU is
optional. Building supplied weights does not require retraining.

```powershell
# Install the Python development environment.
powershell -ExecutionPolicy Bypass -File .\setup-developer.ps1

# After installing the documented Arduino core, compile supplied weights.
powershell -ExecutionPolicy Bypass -File .\build-firmware.ps1

# Or prepare data, train, quantize and compile; overwrites generated outputs.
powershell -ExecutionPolicy Bypass -File .\train-and-build.ps1
```

Complete source data, prepared examples, vocabulary, checkpoint and quantized
arrays are included. Read [training and reproducibility](source/docs/TRAINING.md) and
[data attribution](source/data/ATTRIBUTION.md) before modifying or redistributing them.
Training and rebuilding are not claimed bit-for-bit reproducible across hosts.
Only load trusted checkpoints.

## Repository map

```text
TinyLM-for-ESP8266/
  source/                Complete source workspace
    data/                   Datasets, prepared examples and provenance
    firmware/RecurrentLM/   ESP8266 inference, model weights and portal
    model/                  Checkpoint, quantized arrays and evaluations
    web/                    Editable offline page
    tests/                  Installer, model/package, UI and device checks
    docs/                   Build, training, architecture and API guides
    third_party/            Runtime source/platform snapshot
    licenses/               Original third-party license copies
  firmware/                Ready-to-flash firmware package
    TinyLM-ESP8266.bin       Model and UI already included
    Setup and Flash.cmd     First-time Windows installation
    Flash.cmd               Reuse the installed flashing tool
    README.md               Installation, Wi-Fi and usage guide
    licenses/               Required runtime license notices
  .github/                  CI and contribution templates
  LICENSE / NOTICE          Apache 2.0 and original-work attribution
```

The [file guide](source/docs/FILE_GUIDE.md) explains individual source files. PDFs,
report/archive generators, personal machine/network logs, screenshots, caches,
browser profiles and installed tool environments are excluded from this public
repository. Third-party runtime sources needed for rebuilding are retained with
explicit snapshot exclusions for unused examples and local caches.

## Privacy and limitations

The firmware makes no cloud inference or telemetry request. Sessions and active
job state are held in board RAM; visible conversation turns are held by the
browser. This is local HTTP with a public demonstration Wi-Fi password, not a
secure identity or confidential multi-user service. Use non-sensitive inputs.
See [security and privacy](source/docs/SECURITY_AND_PRIVACY.md).

The model ignores input word order, shares a token for unknown words, and has no
conversation memory. It can repeat training phrasing, invent information or give
an unrelated answer. Do not use outputs for consequential decisions. Other board
variants and operating systems need their own validation. No ESP32 compatibility,
production certification or external security audit is claimed.

## Documentation

The [documentation index](source/docs/README.md) links all guides. Common references:

- [Architecture](source/docs/ARCHITECTURE.md) and [model card](source/docs/MODEL_CARD.md)
- [Developer setup](source/docs/DEVELOPMENT.md) and [training](source/docs/TRAINING.md)
- [Offline HTTP API](source/docs/API_REFERENCE.md) and [dependency inventory](source/docs/DEPENDENCIES.md)
- [End-user manual](firmware/README.md) and [support](SUPPORT.md)
- [Release procedure](source/docs/PUBLISHING.md), [version control](source/docs/VERSIONING.md) and [changelog](CHANGELOG.md)

## Contributing and future updates

Future updates are planned: better data/evaluation, unfamiliar-input handling,
smaller/faster inference and a smoother installation experience. Proposed work
has no promised delivery date; see [ROADMAP.md](ROADMAP.md).

Read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting changes. Include relevant
tests and honest hardware-test status. Use the issue templates for reproducible
bugs and scoped proposals, and never attach secrets or private network dumps.
[Governance](GOVERNANCE.md) and the [code of conduct](CODE_OF_CONDUCT.md) describe
maintainer decisions and community expectations. Report vulnerabilities privately
using [SECURITY.md](SECURITY.md). Support is voluntary, without a service SLA.

## Ownership and licensing

Copyright **2026 Sri Hariharan U** · **srihariharanu@gmail.com**.

Original project contributions are available free of charge under
[Apache License 2.0](LICENSE), with attribution in [NOTICE](NOTICE) and
[CREDITS.md](CREDITS.md). Copyright remains with the applicable rights holder;
Apache 2.0 permits use, modification, redistribution and commercial use subject
to its terms. No copyright assignment is required from contributors.

The compiled firmware and mixed training data are not exclusively Apache-2.0
work: upstream components retain their own terms. See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md), [COPYRIGHT.md](COPYRIGHT.md), and
`source/licenses/` and `firmware/licenses/`. Distribute the companion complete source with firmware releases
for runtime rebuilding and relinking. Model rights are granted only to the
extent held; attribution documents do not constitute government registration.

Citation metadata is supplied in [CITATION.cff](CITATION.cff).
