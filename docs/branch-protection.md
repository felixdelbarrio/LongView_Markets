# Branch Protection

LongView Markets uses GitFlow with `develop` as the integration branch and `master` as the release branch.

Required checks for pull requests into `develop`:

- `Backend CI / backend`
- `Frontend CI / frontend`
- `Coverage / coverage`
- `Security / security`
- `Docs / docs`
- `CodeQL / Analyze (python)`
- `CodeQL / Analyze (javascript-typescript)`
- `Release Dry Run / release-dry-run-linux`
- `Release Dry Run / release-dry-run-windows`
- `Release Dry Run / release-dry-run-macos`

Do not mark `Release / release` as required on pull requests. `release.yml` is intentionally limited to `push` on `master` and `workflow_dispatch`, so requiring it on PRs leaves branch protection checks pending.

`release-dry-run.yml` is the PR gate for release safety. It installs dependencies, runs validation, builds the platform package, validates `.env.example`, rejects packaged `.env`, validates branded launcher assets, and verifies `LongView Markets.exe` on Windows.
