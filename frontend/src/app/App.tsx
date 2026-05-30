import { Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "../components/layout/AppShell";
import { Alerts } from "../pages/Alerts";
import { Copilot } from "../pages/Copilot";
import { Dashboard } from "../pages/Dashboard";
import { DataQuality } from "../pages/DataQuality";
import { DecisionJournal } from "../pages/DecisionJournal";
import { DividendFisher } from "../pages/DividendFisher";
import { ExecutiveDemo } from "../pages/ExecutiveDemo";
import { Forecasting } from "../pages/Forecasting";
import { GenerativeIngestion } from "../pages/GenerativeIngestion";
import { Insights } from "../pages/Insights";
import { InstrumentDetail } from "../pages/InstrumentDetail";
import { Learn } from "../pages/Learn";
import { Markets } from "../pages/Markets";
import { MyPortfolio } from "../pages/MyPortfolio";
import { News } from "../pages/News";
import { Playbooks } from "../pages/Playbooks";
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
        <Route path="/markets" element={<Markets />} />
        <Route path="/instruments/:ticker" element={<InstrumentDetail />} />
        <Route path="/insights" element={<Insights />} />
        <Route path="/alerts" element={<Alerts />} />
        <Route path="/news" element={<News />} />
        <Route path="/my-portfolio" element={<MyPortfolio />} />
        <Route path="/simulated-portfolio" element={<SimulatedPortfolio />} />
        <Route path="/dividend-fisher" element={<DividendFisher />} />
        <Route path="/tax-advisor" element={<TaxAdvisor />} />
        <Route path="/forecasting" element={<Forecasting />} />
        <Route path="/generative-ingestion" element={<GenerativeIngestion />} />
        <Route path="/settings/generative" element={<GenerativeIngestion />} />
        <Route path="/data-quality" element={<DataQuality />} />
        <Route path="/screener" element={<Screener />} />
        <Route path="/watchlists" element={<Watchlists />} />
        <Route path="/journal" element={<DecisionJournal />} />
        <Route path="/playbooks" element={<Playbooks />} />
        <Route path="/learn" element={<Learn />} />
        <Route path="/demo" element={<ExecutiveDemo />} />
        <Route path="/copilot" element={<Copilot />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
    </Routes>
  );
}
