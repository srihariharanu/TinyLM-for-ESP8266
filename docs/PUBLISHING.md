# GitHub publication and release checklist

Prepared locally. No GitHub remote, repository, tag, release, registration or
ownership verification has been created. The owner will supply the repository URL.

## Before first push

- Confirm the public repository and its owner. Use an empty repository or review
  existing content first. Never force-push over existing work.
- Push only this developer folder, not the enclosing research directory. Review
  the staged file list for private logs, PDFs, tools, caches and credentials.
- Review LICENSE, NOTICE and rights notices. The attribution email is intentionally
  public. Git commit identity may use a GitHub no-reply address; no identity is
  configured automatically. The license retains the supplied rights email.
- Run local tests and GitHub CI before tagging. Review available branch rules,
  require review and passing checks where supported, and enable secret scanning,
  push protection and dependency alerts where available. Never publish secrets.
- Suggested description: Experimental offline neural language model and mobile
  chat portal designed for ESP8266.
- Suggested topics: esp8266, tinyml, language-model, embedded-ai, offline,
  experimental. Enable public visibility when ready.

## First push after URL is supplied

The local repository is initialized on main without a commit or remote. Review
`git status`, configure an appropriate commit identity, stage intended files,
review `git diff --cached --stat`, and commit. Connect only the confirmed remote
and push main. Do not embed credentials in URLs, commands or documentation.

## First release

Use a reviewed tag such as v0.1.0-experimental and mark the release a pre-release.
State supported hardware, model limits and actual validation. Attach:

- TinyLM-ESP8266-developer-0.1.0-experimental.zip
- TinyLM-ESP8266-ready-to-flash-0.1.0-experimental.zip
- SHA256SUMS.txt

Always distribute source with the firmware and its notices for runtime rebuilding
and LGPL relinking. Do not publish an isolated binary without notices/source.
Hashes detect changes, not authenticity of an untrusted download. No binary
signing is claimed. Download from the owner's confirmed repository.

## Future releases

Update versions, firmware metadata, hashes, changelog, model card and release
notes. Rebuild and hardware-test changed firmware/models. Preserve third-party
notices and existing Apache-2.0 grants. Generate clean distribution ZIPs from reviewed
sources. No government registration or paid service has been performed or is
required by this preparation. It records licensing and project governance only.

Project maintainer and original-work rights holder: **Sri Hariharan U**.
Rights contact: **srihariharanu@gmail.com**.

## Completed project identity

The original-work licensor and maintainer is Sri Hariharan U; rights contact
is srihariharanu@gmail.com. Project-facing ownership fields are complete.
No additional address, phone, institution or personal identifiers are needed.
Generic how-to examples inside unmodified upstream license texts are part of
those licenses, not unfinished TinyLM ownership fields. They are retained to
preserve upstream wording and must not be reassigned to the TinyLM author.
