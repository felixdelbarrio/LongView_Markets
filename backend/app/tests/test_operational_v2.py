from __future__ import annotations

import json
from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.calculations.calculation_engine import (
    CALCULATION_ENGINE_VERSION,
    OperationalCalculationEngine,
)
from app.generative.response_repair import ResponseRepair
from app.generative.response_validator import ResponseValidator
from app.main import app
from app.repositories import demo_repository

client = TestClient(app)


def test_operational_portfolio_manual_transactions_and_history() -> None:
    transaction = {
        "ticker": "MSFT",
        "transaction_type": "buy",
        "quantity": 2,
        "price": 245,
        "currency": "USD",
        "fees": 1,
        "taxes": 0,
        "trade_date": "2024-01-03",
        "broker": "test",
    }
    assert client.post("/api/v1/portfolio/transactions", json=transaction).json()["status"] == "recorded"
    valuation = client.get("/api/v1/portfolio").json()
    assert valuation["calculation_version"] == CALCULATION_ENGINE_VERSION
    assert valuation["base_currency"] == "EUR"
    assert valuation["positions"]
    history = client.get("/api/v1/portfolio/history?start=2024-01-03&end=2024-01-10").json()
    assert history["history"]
    instrument_history = client.get(
        "/api/v1/portfolio/instruments/MSFT/history?start=2024-01-03&end=2024-01-10"
    ).json()
    assert instrument_history["ticker"] == "MSFT"


def test_fifo_dividends_fx_and_forecasts_are_backend_calculated() -> None:
    tx = [
        {
            "id": "1",
            "ticker": "MSFT",
            "transaction_type": "buy",
            "quantity": 10,
            "price": 100,
            "currency": "USD",
            "fees": 1,
            "taxes": 0,
            "trade_date": "2024-01-02",
        },
        {
            "id": "2",
            "ticker": "MSFT",
            "transaction_type": "buy",
            "quantity": 5,
            "price": 120,
            "currency": "USD",
            "fees": 1,
            "taxes": 0,
            "trade_date": "2024-02-02",
        },
        {
            "id": "3",
            "ticker": "MSFT",
            "transaction_type": "sell",
            "quantity": 3,
            "price": 150,
            "currency": "USD",
            "fees": 1,
            "taxes": 0,
            "trade_date": "2024-03-02",
        },
        {
            "id": "4",
            "ticker": "MSFT",
            "transaction_type": "dividend",
            "quantity": 0,
            "price": 0,
            "gross_amount": 12,
            "currency": "USD",
            "fees": 0,
            "taxes": 1,
            "trade_date": "2024-04-02",
        },
    ]
    engine = OperationalCalculationEngine("EUR")
    prices = {
        "MSFT": {
            "date": "2024-05-01",
            "close": 160,
            "adjusted_close": 160,
            "currency": "USD",
        }
    }
    valuation = engine.portfolio_valuation(tx, prices, demo_repository.get_instruments())
    assert valuation["positions"][0]["quantity"] == 12
    assert valuation["realized_pnl_base"] > 0
    assert valuation["dividends_received_base"] > 0
    assert engine.fx_conversion(100, "USD")["converted_amount"] > 0
    assert engine.forecast_instrument("MSFT", demo_repository.get_prices("MSFT"))["scenarios"]


def test_generative_json_validation_repair_and_batch_endpoints() -> None:
    job = client.post(
        "/api/v1/generative/jobs",
        json={"entity_type": "portfolio", "entity_id": "real"},
    ).json()
    payload = {
        "schema_version": "1.0.0",
        "prompt_version": "1.0.0",
        "analysis_type": "portfolio_context_analysis",
        "portfolio_id": "real",
        "generated_at": datetime.now(UTC).isoformat(),
        "language": "es",
        "executive_summary": {"summary": "Contexto prudente", "confidence": 0.8},
        "portfolio_state": {
            "main_strengths": [],
            "main_weaknesses": [],
            "main_changes": [],
            "confidence": 0.7,
        },
        "risk_review": {"overall_risk_level": "medium", "confidence": 0.7},
        "opportunities_to_review": [],
        "alerts_to_prioritize": [],
        "forecast_context": {"confidence": 0.6},
        "recommended_next_checks": [],
        "limitations": ["Datos gratuitos pueden retrasarse."],
        "not_financial_advice": True,
    }
    raw = json.dumps(payload)
    assert ResponseValidator().validate(raw, "portfolio_context_analysis")["valid"] is True
    assert client.post(
        f"/api/v1/generative/jobs/{job['id']}/validate-response", json={"response": raw}
    ).json()["valid"]
    assert client.post(f"/api/v1/generative/jobs/{job['id']}/import-response", json={"response": raw}).json()[
        "imported"
    ]
    repaired = ResponseRepair().repair(f"```json\n{raw},\n```", "portfolio_context_analysis")
    assert repaired["repaired"] is True
    assert client.get("/api/v1/generative/history").json()


def test_ingestion_universes_settings_and_release_related_endpoints() -> None:
    assert client.get("/api/v1/universes").json()
    assert client.post("/api/v1/ingestion/run-daily-close").json()["status"] == "completed"
    assert client.get("/api/v1/providers/status").json()
    assert client.get("/api/v1/fx/rates").json()
    assert isinstance(client.get("/api/v1/news/portfolio").json(), list)
    assert client.get("/api/v1/data-quality").json()["global_score"] == 0
    settings = client.post("/api/v1/settings", json={"theme": "dark", "generative_mode": "manual_url"}).json()
    assert settings["settings"]["generative_mode"] == "manual_url"
