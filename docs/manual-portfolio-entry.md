# Manual Portfolio Entry

Excel import is intentionally out of scope. Enter operations manually:

1. First buy: ticker, date, quantity, unit price, currency, fees, taxes, broker and notes.
2. Successive buys: add each purchase separately so acquisition lots stay auditable.
3. Partial sell: enter quantity sold, price, date, currency and fees. FIFO is applied by the backend.
4. Dividend: enter gross amount, currency and withholding tax. Dividends are separate from capital gains.
5. USD and other currencies: LongView converts to EUR by default and marks stale FX when using cached fallback rates.

Validate history in `/my-portfolio`, `/my-portfolio/history`, annual/monthly summaries and instrument history.
