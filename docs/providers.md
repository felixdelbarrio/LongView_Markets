# Providers

Default market provider is `yfinance`; secondary provider is `stooq`; news provider is RSS-compatible. Free-provider failures fall back explicitly when `MOCK_FALLBACK_ENABLED=true`, and responses mark source/data kind so users can distinguish observed, cached and mock data.

The provider interface supports instrument search, daily prices, dividends and company profiles. MockProvider works without API keys; external providers are swappable placeholders for v2.

## Operating Principle

Every financial page must expose source, date, data kind, confidence and limitations. Mock, simulation and forecast data are labeled separately from observed data.

## Disclaimer

LongView Markets es una herramienta informativa y educativa. No proporciona asesoramiento financiero, fiscal ni legal. Las predicciones y simulaciones no garantizan resultados futuros.
