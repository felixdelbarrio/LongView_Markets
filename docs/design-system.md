# Design System

LongView Markets centralizes visual decisions in `frontend/src/design-system`.

Pages must use shared components for headers, sections, cards, badges, tables, form fields, loading, empty and error states. Tokens cover background, text, borders, brand, status, data colors, spacing, radius, shadows, typography, motion, z-index and charts.

`make lint` runs `scripts/design/check_design_system.py` to reject inline `style={{ ... }}` and hardcoded hex colors in `frontend/src/pages`.
