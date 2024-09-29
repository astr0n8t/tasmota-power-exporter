import pytest
from httpx import AsyncClient
from metrics import app


@pytest.mark.asyncio
async def test_base_uri():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert "Welcome to Tasmota prometheus exporter!" in response.text
    assert "Use the /probe endpoint" in response.text


@pytest.mark.asyncio
async def test_probe_scrape(monkeypatch):
    async def mock_fetch(self):
        return {"Power": "10 W", "Voltage": "230 V", "Total": "15.6 kWh"}

    monkeypatch.setattr("metrics.TasmotaCollector.fetch", mock_fetch)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/probe?target=192.168.1.34")
    assert response.status_code == 200
    assert "tasmota_power_W" in response.text
    assert "tasmota_voltage_V" in response.text
    assert "tasmota_kWh_total" in response.text


@pytest.mark.asyncio
async def test_probe_fail(monkeypatch):
    async def mock_fetch(self):
        raise Exception("Failed to fetch data")

    monkeypatch.setattr("metrics.TasmotaCollector.fetch", mock_fetch)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/probe?target=192.168.1.38")
    assert response.status_code == 500
    assert "Failed to fetch data" in response.json()["detail"]


@pytest.mark.asyncio
async def test_probe_missing():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/probe")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_probe_with_auth(monkeypatch):
    async def mock_fetch(self):
        return {"Power": "10 W", "Voltage": "230 V", "Total": "15.6 kWh"}

    monkeypatch.setattr("metrics.TasmotaCollector.fetch", mock_fetch)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            "/probe?target=192.168.1.34&user=admin&password=password"
        )
    assert response.status_code == 200
    assert "tasmota_power_W" in response.text
    assert "tasmota_voltage_V" in response.text
    assert "tasmota_kWh_total" in response.text
