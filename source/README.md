# TinyLM for ESP8266 — source and training workspace

Experimental neural language model designed for ESP8266EX, 4 MB flash, 160 MHz.
Created and maintained by Sri Hariharan U; rights: srihariharanu@gmail.com.

This folder contains the complete model, training and firmware development
workspace. The sibling [ready-to-flash product](../firmware/README.md) is
for users who want to install and chat without training or editing source.
See the [repository overview](../README.md) for results and model limitations.

## Start development

Clone the entire repository, then open the developer folder:

```sh
git clone https://github.com/srihariharanu/TinyLM-for-ESP8266.git
cd TinyLM-for-ESP8266/developer
```

Install Python 3.12 and Arduino CLI, then follow [DEVELOPMENT.md](docs/DEVELOPMENT.md)
for pinned dependencies and ESP8266 core 3.0.2. Compile supplied weights using
build-firmware.ps1, or run the complete training/export/build pipeline using
train-and-build.ps1. GPU training is optional; firmware inference runs on ESP8266.

## Guides

- [Documentation index](docs/README.md) and [source file guide](docs/FILE_GUIDE.md)
- [Architecture](docs/ARCHITECTURE.md), [model card](docs/MODEL_CARD.md), [validation](docs/VALIDATION.md)
- [Training and reproducibility](docs/TRAINING.md), [data attribution](data/ATTRIBUTION.md)
- [HTTP API](docs/API_REFERENCE.md), [version control](docs/VERSIONING.md)
- [Contributing](../CONTRIBUTING.md) and [security reporting](../SECURITY.md)

## Workspace contents

| Location | Role |
| --- | --- |
| firmware/RecurrentLM/ | Complete inference, hotspot/server, weights and embedded page |
| web/ | Editable offline mobile UI |
| data/ | Source datasets, prepared examples, vocabulary and provenance |
| model/ | Checkpoint, quantized arrays and complete evaluation outputs |
| tests/ | Source/product integrity, mock installer, UI and optional device tests |
| docs/ | Detailed build, training, architecture, API and release documentation |
| third_party/ | Unchanged runtime files with explicit snapshot exclusions |
| ../firmware/ | Firmware distribution, installer source and end-user manual |

Run source tests from this folder:
`python -B -m unittest discover -s tests -p "test_*.py"`.
Tests reference the sibling ready-to-flash folder; clone/extract the whole source
package rather than downloading only this directory. CI runs from this workspace.

Original contributions use [Apache License 2.0](LICENSE), with [NOTICE](NOTICE)
and [credits](CREDITS.md). Third-party components and data keep their own terms;
see [upstream notices](THIRD_PARTY_NOTICES.md). This is an experiment, not a general
assistant or production-certified device. Future updates: [roadmap](../ROADMAP.md).
