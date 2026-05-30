# Generative JSON Contracts

Prompts require valid JSON only: no Markdown, no prose around JSON, no comments, no trailing commas, ISO dates, ISO currencies, confidence from 0 to 1 and `not_financial_advice=true`.

Invalid responses are rejected. Deterministic repair may remove fences, extract a JSON object and remove trailing commas. Repaired responses are marked before import.
