# Calculation Engine

Operational calculations live in `backend/app/calculations`.

`OperationalCalculationEngine` is the facade for portfolio valuation, portfolio history, instrument history, FX conversion and scenarios. Responses include `calculation_version`, `calculated_at`, inputs, sources, warnings and quality flags.

The frontend must not calculate profitability, FIFO, PyG, FX, dividend return, forecasting or portfolio exposure. It presents backend responses and captures UX-level form input only.
