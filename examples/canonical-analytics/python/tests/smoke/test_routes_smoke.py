import pytest
from httpx import AsyncClient, ASGITransport
from src.analytics_workbench.main import app
from src.analytics_workbench.data.loader import get_dataset

@pytest.mark.asyncio
async def test_routes_smoke():
    # Ensure dataset is loaded
    dataset = get_dataset()
    
    first_service = dataset.services[0].name if dataset.services else "billing-api"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        endpoints = [
            "/",
            "/trends",
            "/services",
            "/distributions",
            "/heatmap",
            "/funnel",
            "/incidents",
            "/health",
            "/fragments/chart?view=trends",
            "/fragments/summary?view=trends",
            f"/fragments/details?view=services&service={first_service}"
        ]
        
        for endpoint in endpoints:
            response = await ac.get(endpoint)
            assert response.status_code == 200
            assert response.content
            
            if endpoint == "/health":
                assert response.json() == {"status": "ok"}
            elif endpoint.startswith("/fragments/chart"):
                assert "plotly" in response.text.lower()
                
        # Applying a filter
        res_filtered = await ac.get("/trends?environment=production")
        assert res_filtered.status_code == 200
        assert res_filtered.content
