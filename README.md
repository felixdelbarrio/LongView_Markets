# LongView Markets

![Backend CI](https://github.com/felixdelbarrio/LongView_Markets/actions/workflows/backend-ci.yml/badge.svg)
![Frontend CI](https://github.com/felixdelbarrio/LongView_Markets/actions/workflows/frontend-ci.yml/badge.svg)
![CodeQL](https://github.com/felixdelbarrio/LongView_Markets/actions/workflows/codeql.yml/badge.svg)
![Security](https://github.com/felixdelbarrio/LongView_Markets/actions/workflows/security.yml/badge.svg)
![Coverage](https://github.com/felixdelbarrio/LongView_Markets/actions/workflows/coverage.yml/badge.svg)
![Docs](https://github.com/felixdelbarrio/LongView_Markets/actions/workflows/docs.yml/badge.svg)
![Release](https://github.com/felixdelbarrio/LongView_Markets/actions/workflows/release.yml/badge.svg)

![LongView Markets logo](frontend/public/brand/longview-logo.svg)

**Decisiones de inversión a largo plazo con datos, contexto y disciplina.**

LongView Markets is a local full-stack decision-support platform for long-term investors. It combines daily market data, deterministic seed data, real and simulated portfolios, dividend analysis, tax estimates, forecasting scenarios, alerts, data quality, screener workflows, watchlists, a decision journal, learning playbooks, an executive demo mode and an external GPT copilot context builder.

## Financial Disclaimer

LongView Markets es una herramienta informativa y educativa. No proporciona asesoramiento financiero, fiscal ni legal. Los datos pueden contener errores, retrasos o estimaciones. Las predicciones y simulaciones no garantizan resultados futuros. Antes de invertir, contrasta la información con fuentes oficiales y consulta con un profesional cualificado.

## Quickstart

```bash
make help
make install
make run
```

`make run` starts backend and frontend from one terminal, initializes `.env`, SQLite and Parquet seed data, stores PID files and opens LongView Markets in a native WebView app frame instead of an external browser.

The internal service URLs remain available for diagnostics:

- Frontend: http://127.0.0.1:5173
- Backend: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs

Stop only LongView processes with:

```bash
make kill
```

## Make Commands

- `make install`: backend and frontend dependencies, `.env`, SQLite and seed data.
- `make run`: one-command local launch with backend, frontend, PID files, logs and a native WebView app frame.
- `make build`: validates backend, compiles frontend and creates local release archives.
- `make clean`: removes caches, build outputs, logs and PID files without deleting user data.
- `make kill`: stops only processes started by `make run`.
- `make lint`, `make format`, `make typecheck`, `make test`, `make coverage`, `make security`, `make ci`.

## Product Highlights

- Premium dashboard with portfolio value, return, YTD, risk, dividends, alerts and data status.
- Market pulse, heatmap, long-term opportunities and risk storytelling.
- Real demo portfolio and simulated portfolio lab.
- Dividend Fisher with ex-dividend calendar, gross/net simulation and warnings.
- Configurable tax advisor using YAML rule files for ES, FR, DE, IT, GB, US and generic rules.
- Forecasting scenarios clearly labeled as estimates, not predictions.
- Data quality center with provider, ticker, confidence and issue visibility.
- Screener presets, watchlists, decision journal, playbooks, learn section and executive demo.
- External GPT copilot that prepares structured context without calling GPT APIs.
- Multi-language shell through i18next, light/dark/system theme and branded assets.

## Architecture

The app is a monorepo:

- `backend/`: FastAPI, Pydantic v2, Polars, PyArrow, DuckDB, SQLModel/SQLite, APScheduler-ready jobs, Typer CLI and pytest.
- `frontend/`: React, TypeScript, Vite, Tailwind CSS, shadcn-style local primitives, Recharts, Framer Motion, Lucide, TanStack Query, Zustand, i18next, React Hook Form, Zod, Vitest and Playwright smoke coverage.
- `data/`: deterministic seed JSON, SQLite metadata and generated Parquet lake.
- `scripts/`: one-command WebView launcher, kill script, packaging and validation helpers.
- `.github/`: separate CI, security, coverage, docs, CodeQL, Dependabot and release workflows.

## Data Model and Parquet

Canonical models include instruments, daily prices, dividends, news, portfolio transactions, insights, forecasts, watchlists and decision journal entries. Analytical data is generated into partitioned Parquet paths such as `data/parquet/prices/market=NASDAQ/ticker=AAPL/year=2026/prices.parquet`.

## Calculation Policy

Critical financial metrics are centralized in `backend/app/analytics/calculation_engine.py`. The frontend displays backend-provided metrics and does not recalculate CAGR, volatility, drawdown, Sharpe, total return, portfolio concentration or dividend yield.

## Launcher and Packaging

`make run` hides backend/frontend complexity during development and presents the product in a self-contained WebView application frame. `make build` compiles the frontend and creates Windows, Linux and macOS archives in `dist/` with WebView launcher scripts, backend code, compiled frontend, `.env.example`, checksums and official LongView icon assets. Windows release runners build `LongView Markets.exe` with PyInstaller and the official icon; `.bat` files are diagnostic only. The repository follows GitFlow with `master` as the production branch and `develop` as the integration branch. The release workflow runs only on pushes to `master`.

## Manual Portfolio Entry

LongView Markets does not import Excel in this iteration. Rebuild your history by entering every real transaction once:

- First buy: ticker, date, quantity, unit price, currency, fees, taxes, broker and notes.
- Successive buys: add each purchase with its real date so lots remain auditable.
- Partial sells: the backend consumes lots by FIFO and separates realized PnL from unrealized PnL.
- Dividends: enter gross amount, currency and withholding tax; dividends remain separate from capital gains.
- Multi-currency positions: values are converted to the base currency, EUR by default, with FX date and quality flags.

The backend calculation engine reconstructs daily portfolio history, instrument history, monthly and annual summaries, dividend totals, PyG diario, stale price/FX flags, forecasts and anomalies.

## Generative Ingestion

The `/generative-ingestion` screen prepares structured context, produces strict JSON prompts for an external GPT URL, validates pasted JSON responses, repairs simple JSON issues deterministically, stores validated responses historically and marks them as `generative_inference`. Generative output never replaces observed market data or quantitative calculations.

## Design And Calculations

The visual system lives in `frontend/src/design-system` with centralized tokens, reusable components and lint checks for page-level inline styles or hardcoded hex colors. Critical financial calculations live in `backend/app/calculations` with `CALCULATION_ENGINE_VERSION = "0.2.0"`; the frontend renders values and form validation only.

## Security

Security starts with strict Pydantic validation, configurable CORS, local rate limiting, security headers, `.env` secret handling, logs without secrets, Bandit, pip-audit, npm audit, CodeQL, Dependabot and a lightweight secret scan.

## Roadmap

v1:
- Demo local completa, datos seed, carteras, dividendos, fiscalidad, forecasting básico, copiloto externo GPT, screener, watchlists, decision journal, learn/playbooks, demo executive, launcher integrado, icono oficial y release multiplataforma.

v2:
- Autenticación, multiusuario, PostgreSQL, jobs programados reales, integraciones premium, backtesting avanzado, notificaciones email e instaladores firmados.

v3:
- Broker integrations, alternative data, optimización de cartera, app móvil, asistente integrado vía API opcional y reglas fiscales verificadas con fuentes oficiales.
