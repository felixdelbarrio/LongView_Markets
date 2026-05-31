# Launcher

The development launcher seeds data, initializes SQLite and Parquet, starts backend and frontend, writes PID files, opens a native WebView app frame, and lets `make kill` stop only LongView processes. It does not open the system browser automatically. The packaged launcher detects PyInstaller runtime paths, serves the compiled frontend through FastAPI, initializes local data if missing and uses the official LongView icon.

## Operating Principle

Every financial page must expose source, date, data kind, confidence and limitations. Mock, simulation and forecast data are labeled separately from observed data.

## Disclaimer

LongView Markets es una herramienta informativa y educativa. No proporciona asesoramiento financiero, fiscal ni legal. Las predicciones y simulaciones no garantizan resultados futuros.
