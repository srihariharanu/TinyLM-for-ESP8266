# Version control and release policy

Project: TinyLM for ESP8266. Maintainer and original-work rights holder:
Sri Hariharan U <srihariharanu@gmail.com>. License: Apache-2.0 for original work.
Status: experimental. Current initial release candidate: 0.1.0-experimental.

## Branches and review

- main is the primary integration branch and the source of release tags.
- Use focused topic branches: feat/..., fix/..., docs/..., or chore/... .
- Keep commits descriptive and scoped. Never commit secrets, local environments,
  browser profiles or private research documents.
- Prefer pull requests with validation evidence before merging. For maintainer
  integration, review the diff and run relevant checks before a non-fast-forward
  merge, retaining topic-branch history. Do not force-push shared main or tags.
- GitHub branch protections and required-review settings are account settings;
  their enforcement is not claimed merely because this policy exists.

## Version scheme

Use MAJOR.MINOR.PATCH with an explicit prerelease suffix while experimental.
Initial version: 0.1.0-experimental; tag: v0.1.0-experimental.
A future bug-fix candidate may use 0.1.1-experimental; a larger experimental
feature/API change may use 0.2.0-experimental. During 0.x, incompatible changes
must be called out. A future stable 1.0.0 requires an explicit readiness review.
A version label is not evidence of safety certification or general model quality.

## Keep version metadata consistent

For changes released after the initial tag, update the root VERSION plus source/VERSION, package.json,
package-lock.json, CITATION.cff, firmware/VERSION and firmware.json together.
Update the README status/version badge, CHANGELOG.md, model card where affected,
and release asset names. The standalone product package is built directly from firmware/.
Documentation changes made before the first tag can remain in the initial version.

Record the behavior change and actual tests. A changed firmware/model requires
new hardware validation or explicit disclosure of what was not tested. Do not
silently replace a binary under an existing published version.

## Tags and artifacts

Create annotated tags on reviewed main commits. Tags are immutable release
references; use a new version instead of moving an existing tag. Signing is not
claimed unless a tag is actually signed and verification is available.

Distribute both developer and ready-to-flash ZIPs with SHA256SUMS.txt. Preserve
runtime source and notices needed for rebuilding/relinking. Treat experimental
GitHub releases as prereleases. A pushed tag is distinct from a GitHub Release;
uploaded release assets and release notes require their own publication step.

## Validation and rollback

Run source/installer tests, page consistency checks and firmware compilation when
relevant. Inspect GitHub Actions results before promoting a candidate as tested.
Record unavailable checks honestly. Use git revert for shared-history rollback;
retain earlier tags and changelog entries. Never rewrite history to hide a defect.
If credentials are exposed, revoke them and follow a separate incident cleanup.
