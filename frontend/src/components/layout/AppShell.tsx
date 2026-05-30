import { Moon, Search, SunMedium } from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { BrandMark } from "./BrandMark";
import { navItems } from "../../app/navigation";
import { Button } from "../ui/button";
import { usePreferences } from "../../stores/preferences";

export function AppShell() {
  const { t } = useTranslation();
  const { theme, setTheme } = usePreferences();
  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[280px_1fr]">
      <aside className="border-line/80 bg-panel/95 p-4 lg:sticky lg:top-0 lg:h-screen lg:border-r">
        <BrandMark />
        <nav className="mt-6 grid grid-cols-2 gap-1 lg:grid-cols-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex min-h-10 items-center gap-3 rounded-md px-3 text-sm font-semibold transition ${isActive ? "bg-accent text-white" : "text-muted hover:bg-canvas hover:text-text"}`
              }
            >
              <item.icon size={17} />
              <span>{t(item.key)}</span>
            </NavLink>
          ))}
        </nav>
      </aside>
      <main>
        <header className="sticky top-0 z-10 flex flex-wrap items-center justify-between gap-3 border-b border-line/80 bg-canvas/85 px-5 py-4 backdrop-blur">
          <div className="flex min-w-0 flex-1 items-center gap-3 rounded-md border border-line bg-panel px-3 py-2 text-muted">
            <Search size={17} />
            <input
              aria-label="Global search"
              className="min-w-0 flex-1 bg-transparent outline-none"
              placeholder="MSFT, dividendos, drawdown..."
            />
          </div>
          <Button
            aria-label="Toggle theme"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            {theme === "dark" ? <SunMedium size={17} /> : <Moon size={17} />}
          </Button>
        </header>
        <div className="mx-auto max-w-[1500px] px-5 py-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
