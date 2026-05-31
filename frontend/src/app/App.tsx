import { Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "../components/layout/AppShell";
import { Dashboard } from "../pages/Dashboard";
import { DataQuality } from "../pages/DataQuality";
import { DecisionJournal } from "../pages/DecisionJournal";
import { Dividends } from "../pages/Dividends";
import { InstrumentDetail } from "../pages/InstrumentDetail";
import { Markets } from "../pages/Markets";
import { MyPortfolio } from "../pages/MyPortfolio";
import { OperationalGuides } from "../pages/OperationalGuides";
import { Screener } from "../pages/Screener";
import { Settings } from "../pages/Settings";
import { SimulatedPortfolio } from "../pages/SimulatedPortfolio";
import { TaxAdvisor } from "../pages/TaxAdvisor";
import { Watchlists } from "../pages/Watchlists";

export function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/my-portfolio" element={<MyPortfolio />} />
        <Route path="/markets" element={<Markets />} />
        <Route path="/instruments/:ticker" element={<InstrumentDetail />} />
        <Route path="/screener" element={<Screener />} />
        <Route path="/simulated-portfolio" element={<SimulatedPortfolio />} />
        <Route path="/dividends" element={<Dividends />} />
        <Route path="/tax-advisor" element={<TaxAdvisor />} />
        <Route path="/data-quality" element={<DataQuality />} />
        <Route path="/watchlists" element={<Watchlists />} />
        <Route path="/journal" element={<DecisionJournal />} />
        <Route path="/guides" element={<OperationalGuides />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Route>
    </Routes>
  );
}
