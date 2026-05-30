import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import de from "./locales/de.json";
import en from "./locales/en.json";
import es from "./locales/es.json";
import fr from "./locales/fr.json";
import it from "./locales/it.json";
import pt from "./locales/pt.json";

const storedLanguage =
  typeof window !== "undefined" && typeof window.localStorage?.getItem === "function"
    ? window.localStorage.getItem("longview-language")
    : undefined;

void i18n.use(initReactI18next).init({
  resources: {
    es: { translation: es },
    en: { translation: en },
    fr: { translation: fr },
    de: { translation: de },
    it: { translation: it },
    pt: { translation: pt },
  },
  lng: storedLanguage ?? "es",
  fallbackLng: "en",
  interpolation: { escapeValue: false },
});

export default i18n;
