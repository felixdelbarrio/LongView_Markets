# LongView Markets Design System

Las paginas operativas deben componer UI con los componentes base de `frontend/src/design-system/components` y tokens de `frontend/src/design-system/tokens`.

Reglas:

- No hardcodear colores hex en `src/pages`.
- No usar `style={{ ... }}` en paginas operativas.
- Los graficos usan `tokens/charts.ts`.
- Las tarjetas, badges, estados y tablas salen de componentes compartidos.
