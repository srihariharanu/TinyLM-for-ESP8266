# Security and privacy design

Firmware serves local HTTP with no cloud inference, analytics or telemetry. Its
WPA2 password is intentionally public in source, firmware and guides. Sign-in
uses a display name and cookie, not identity verification or secure hosting.
Cookies use HttpOnly and SameSite=Strict; local HTTP has no TLS.

Four sessions and one generation job are supported. Runtime names/tokens/job
state are held in RAM; visible turns stay in browser memory. Restart clears
device runtime state. Browser and OS persistence are outside firmware control.

Do not enter confidential information or expose this service to untrusted users.
To change the demo AP password, edit portal.h, rebuild, and update metadata.
Do not post private network credentials, tokens or machine logs in issues.
See root SECURITY.md for private reporting.

Project maintainer and original-work rights holder: **Sri Hariharan U**.
Rights contact: **srihariharanu@gmail.com**.
