export const colors = {
  background: {
    primary: "rgb(var(--color-canvas))",
    secondary: "rgb(var(--color-panel))",
    elevated: "rgb(var(--color-elevated))",
  },
  text: {
    primary: "rgb(var(--color-text))",
    secondary: "rgb(var(--color-muted))",
    muted: "rgb(var(--color-muted))",
  },
  border: {
    default: "rgb(var(--color-line))",
    strong: "rgb(var(--color-line-strong))",
  },
  brand: {
    primary: "rgb(var(--color-accent))",
    secondary: "rgb(var(--color-teal))",
  },
  status: {
    success: "rgb(var(--color-success))",
    warning: "rgb(var(--color-amber))",
    danger: "rgb(var(--color-danger))",
    info: "rgb(var(--color-accent))",
  },
  data: {
    positive: "rgb(var(--color-success))",
    negative: "rgb(var(--color-danger))",
    neutral: "rgb(var(--color-muted))",
  },
} as const;
