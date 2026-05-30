import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import "../i18n/i18n";
import { App } from "../app/App";

function renderApp(path = "/dashboard") {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[path]}>
        <App />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("LongView Markets", () => {
  it("renders the premium dashboard", async () => {
    renderApp();
    expect(await screen.findByText(/Centro de decisiones|Decision center/)).toBeInTheDocument();
    expect(screen.getByAltText("LongView Markets")).toBeInTheDocument();
  });

  it("toggles theme", async () => {
    renderApp();
    await userEvent.click(screen.getByLabelText("Toggle theme"));
    expect(document.documentElement.classList.contains("dark")).toBe(true);
  });

  it("renders core pages", async () => {
    renderApp("/dividend-fisher");
    expect(await screen.findByText("Dividend fisher")).toBeInTheDocument();
    renderApp("/tax-advisor");
    expect(await screen.findByText("Tax advisor")).toBeInTheDocument();
    renderApp("/settings");
    expect(await screen.findByText("Settings")).toBeInTheDocument();
  });

  it("renders operational portfolio and generative ingestion pages", async () => {
    renderApp("/my-portfolio");
    expect(await screen.findByRole("heading", { name: "Mi cartera" })).toBeInTheDocument();
    expect(screen.getByText("Nueva operación")).toBeInTheDocument();
    renderApp("/generative-ingestion");
    expect(await screen.findByText("GPT en JSON estricto")).toBeInTheDocument();
  });
});
