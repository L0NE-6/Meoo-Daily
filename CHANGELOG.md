# Changelog

## v1.0.1 - 2026-11-24

- Fixed scheduled GitHub Actions runs reporting a configuration error when no
  Cookie Secrets were configured.
- Added an explicit credentials preflight: missing credentials produce a
  visible SKIPPED notice, while configured runs still fail on script errors.
- Synchronized the Chinese README and all five translated guides with the
  workflow behavior.

## v1.0.0 - 2026-11-23

- Split the Meoo daily-login script and tests into an independent
  `L0NE-6/Meoo-Daily` repository.
- Added multi-account Cookie loading, per-account JSON results, summary output,
  optional PushPlus and WeCom notifications, and credential redaction.
- Added Chinese documentation plus English, Traditional Chinese, Japanese,
  Korean, and Brazilian Portuguese guides.
- Added MIT licensing, usage policy, third-party attribution, Python project
  metadata, and GitHub Actions automation.
- Added tests for grants, already-granted responses, authentication failures,
  redirects, invalid JSON, multi-account isolation, and `--status` behavior.
