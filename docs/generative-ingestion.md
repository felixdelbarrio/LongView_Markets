# Generative Ingestion

The generative layer treats GPT as an API-like structured system:

structured context -> strict JSON prompt -> strict JSON response -> validation -> storage -> app usage.

Default mode is `manual_url`: LongView builds prompts, the user opens the configured GPT URL, pastes JSON back, and the app validates before import. UI route: `/generative-ingestion`.
