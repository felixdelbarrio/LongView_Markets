import { expect, test } from "@playwright/test";

test("LongView local smoke", async ({ page }) => {
  await page.goto("/dashboard");
  await expect(page.getByText(/Centro de decisiones|Decision center/)).toBeVisible();
  await page.getByRole("link", { name: /Mi cartera|My portfolio/ }).click();
  await expect(page.getByText(/My portfolio|Mi cartera/)).toBeVisible();
  await page.getByRole("link", { name: /Pescador de dividendos|Dividend fisher/ }).click();
  await expect(page.getByText("Dividend fisher")).toBeVisible();
  await page.getByRole("button", { name: "Toggle theme" }).click();
  await page.getByRole("link", { name: /Configuracion|Settings/ }).click();
  await expect(page.getByText(/Settings|Configuracion/)).toBeVisible();
  const favicon = await page.locator("link[rel='icon']").getAttribute("href");
  expect(favicon).toContain("longview-icon.svg");
});
