# Architecture

LongView Markets uses a local monorepo with a FastAPI calculation backend, React frontend, deterministic seed data, SQLite metadata and Parquet analytical storage. The backend is the only owner of critical financial calculations.

## Operating Principle

Every financial page must expose source, date, data kind, confidence and limitations. Mock, simulation and forecast data are labeled separately from observed data.

## Disclaimer

LongView Markets es una herramienta informativa y educativa. No proporciona asesoramiento financiero, fiscal ni legal. Las predicciones y simulaciones no garantizan resultados futuros.
