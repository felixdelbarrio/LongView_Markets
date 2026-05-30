# Release

Release runs only on push to master, with optional manual `workflow_dispatch`. It executes validation, `make ci`, platform packaging, checksums and artifact upload. Windows runs PyInstaller on `windows-latest` and must produce `LongView Markets.exe` with the official `.ico`; diagnostic `.bat` files are not the primary entrypoint. Linux and macOS produce tarballs with runtime launch scripts. The package includes `.env.example`, never `.env`.

Use `make release-dry-run` locally for structural checks. The PR workflow `release-dry-run.yml` validates release packaging on Linux, Windows and macOS without publishing a GitHub Release.

## Operating Principle

Every financial page must expose source, date, data kind, confidence and limitations. Mock, simulation and forecast data are labeled separately from observed data.

## Disclaimer

LongView Markets es una herramienta informativa y educativa. No proporciona asesoramiento financiero, fiscal ni legal. Las predicciones y simulaciones no garantizan resultados futuros.
