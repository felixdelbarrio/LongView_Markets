import { create } from "zustand";
import i18n from "../i18n/i18n";

type Theme = "light" | "dark" | "system";
type Language = "es" | "en" | "fr" | "de" | "it" | "pt";

type PreferenceStore = {
  theme: Theme;
  language: Language;
  setTheme: (theme: Theme) => void;
  setLanguage: (language: Language) => void;
};

function storageGet(key: string) {
  return typeof window !== "undefined" && typeof window.localStorage?.getItem === "function"
    ? window.localStorage.getItem(key)
    : null;
}

function storageSet(key: string, value: string) {
  if (typeof window !== "undefined" && typeof window.localStorage?.setItem === "function") {
    window.localStorage.setItem(key, value);
  }
}

function applyTheme(theme: Theme) {
  const prefersDark = window.matchMedia?.("(prefers-color-scheme: dark)").matches;
  document.documentElement.classList.toggle(
    "dark",
    theme === "dark" || (theme === "system" && prefersDark),
  );
}

export const usePreferences = create<PreferenceStore>((set) => ({
  theme: (storageGet("longview-theme") as Theme) ?? "system",
  language: (storageGet("longview-language") as Language) ?? "es",
  setTheme: (theme) => {
    storageSet("longview-theme", theme);
    applyTheme(theme);
    set({ theme });
  },
  setLanguage: (language) => {
    storageSet("longview-language", language);
    void i18n.changeLanguage(language);
    set({ language });
  },
}));

export function bootstrapPreferences() {
  const theme = (storageGet("longview-theme") as Theme) ?? "system";
  const language = (storageGet("longview-language") as Language) ?? "es";
  applyTheme(theme);
  void i18n.changeLanguage(language);
}
