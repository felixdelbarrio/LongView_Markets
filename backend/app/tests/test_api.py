from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_dashboard_and_core_endpoints() -> None:
    assert client.get("/api/v1/health").json()["status"] == "ok"
    dashboard = client.get("/api/v1/dashboard").json()
    assert dashboard["empty_portfolio"] is True
    assert dashboard["hero"]["portfolio_value"] == 0
    assert dashboard["market_pulse_status"] == "pending_sync"
    assert client.get("/api/v1/markets").json()
    assert client.get("/api/v1/instruments/search?q=msft").json()[0]["ticker"] == "MSFT"
    assert client.get("/api/v1/instruments/MSFT").json()["instrument"]["ticker"] == "MSFT"
    assert client.get("/api/v1/prices/MSFT").status_code == 404
    assert client.post("/api/v1/prices/sync").json()["sqlite"]


def test_financial_workflow_endpoints() -> None:
    paths = [
        "/api/v1/analytics/MSFT",
        "/api/v1/insights/MSFT",
        "/api/v1/signals/MSFT",
        "/api/v1/alerts",
        "/api/v1/news",
        "/api/v1/news/MSFT",
        "/api/v1/portfolio",
        "/api/v1/portfolio/performance",
        "/api/v1/portfolio/allocation",
        "/api/v1/simulated-portfolio",
        "/api/v1/simulated-portfolio/performance",
        "/api/v1/dividends",
        "/api/v1/dividends/calendar",
        "/api/v1/dividends/opportunities",
        "/api/v1/tax/rules",
        "/api/v1/forecasting/MSFT",
        "/api/v1/data-quality",
        "/api/v1/screener",
        "/api/v1/watchlists",
        "/api/v1/journal",
        "/api/v1/playbooks",
        "/api/v1/copilot/context/MSFT",
        "/api/v1/settings",
    ]
    for path in paths:
        response = client.get(path)
        assert response.status_code == 200, path


def test_mutation_endpoints() -> None:
    assert client.post("/api/v1/alerts", json={"title": "Check drawdown"}).status_code == 200
    assert client.patch("/api/v1/alerts/1", json={"status": "read"}).json()["status"] == "read"
    assert (
        client.post("/api/v1/portfolio/transactions", json={"ticker": "MSFT"}).json()["ingestion_job"][
            "status"
        ]
        == "queued"
    )
    assert (
        client.post("/api/v1/simulated-portfolio/transactions", json={"ticker": "MSFT"}).json()["data_kind"]
        == "simulation"
    )
    assert client.post("/api/v1/simulated-portfolio/convert-to-real", json={"ticker": "MSFT"}).json()[
        "requires_confirmation"
    ]
    assert (
        client.post("/api/v1/tax/estimate", json={"residence_country": "ES", "dividends": 100}).json()[
            "net_after_estimated_tax"
        ]
        >= 0
    )
    assert client.post("/api/v1/screener/presets", json={"name": "Quality"}).json()["status"] == "saved"
    assert client.post("/api/v1/watchlists", json={"name": "Ideas"}).json()["status"] == "created"
    assert client.post("/api/v1/watchlists/ideas/items", json={"ticker": "MSFT"}).json()["status"] == "added"
    assert client.post("/api/v1/journal", json={"ticker": "MSFT"}).json()["ticker"] == "MSFT"
    assert client.patch("/api/v1/journal/1", json={"status": "reviewed"}).json()["status"] == "reviewed"
    assert client.post("/api/v1/settings", json={"language": "en"}).json()["settings"]["language"] == "en"
