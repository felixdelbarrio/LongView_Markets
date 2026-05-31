# FX

Base currency is EUR by default. FX conversion is centralized in `backend/app/calculations/fx_calculator.py` and surfaced through `backend/app/fx/fx_engine.py`.

Supported currencies include EUR, USD, GBP, CHF, JPY, SEK, NOK and DKK. Cached fallback rates are marked with `stale_fx`.
