import { expect, test } from "@playwright/test";

test("LongView local smoke", async ({ page }) => {
  await page.goto("/dashboard");
  await expect(page.getByText(/Centro de decisiones|Decision center/)).toBeVisible();
  await page.getByRole("link", { name: /Mi cartera|My portfolio/ }).click();
  await expect(page.getByRole("heading", { name: /My portfolio|Mi cartera/ })).toBeVisible();
  await page.getByRole("link", { name: /Dividendos|Dividends/ }).click();
  await expect(page.getByRole("heading", { name: /Dividendos|Dividends/ })).toBeVisible();
  await page.getByRole("button", { name: "Sincronización global" }).click();
  await expect(page.getByText("Progreso de ingesta")).toBeVisible();
  await page.getByRole("button", { name: "Cerrar sincronización" }).click();
  await page.getByRole("button", { name: "Toggle theme" }).click();
  await page.getByRole("link", { name: /Configuración|Configuracion|Settings/ }).click();
  await expect(page.getByText(/Settings|Configuración|Configuracion/)).toBeVisible();
  const favicon = await page.locator("link[rel='icon']").getAttribute("href");
  expect(favicon).toContain("longview-icon.svg");
});
