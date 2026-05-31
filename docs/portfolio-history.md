# Portfolio History

`GET /api/v1/portfolio/history` reconstructs end-of-day portfolio history from manual transactions, prices and FX. Purchases and sells affect the series from trade date. Missing exact prices or FX use last known fallback and mark quality flags.
