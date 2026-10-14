from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_api_contract_and_healthy_state():
    """
    Test Case 1: Validate /api/health schema, types, and 'healthy' status calculation
    when the database connection check succeeds.
    """
    with patch("app.main.check_db_health", return_value="Connected (Healthy)"), \
         patch("psutil.cpu_percent", return_value=15.0), \
         patch("psutil.virtual_memory") as mock_mem, \
         patch("psutil.disk_usage") as mock_disk:
        
        mock_mem.return_value.percent = 40.0
        mock_mem.return_value.used = 4 * (1024 ** 3)
        mock_mem.return_value.total = 16 * (1024 ** 3)
        mock_disk.return_value.percent = 30.0

        response = client.get("/api/health")

        assert response.status_code == 200
        payload = response.json()
        
        # Verify contract schema
        required_keys = [
            "status", "cpu_usage_pct", "memory_usage_pct",
            "memory_used_gb", "memory_total_gb", "disk_usage_pct",
            "database_status"
        ]
        for key in required_keys:
            assert key in payload

        # Verify operational assertions
        assert payload["status"] == "healthy"
        assert payload["cpu_usage_pct"] == 15.0
        assert payload["database_status"] == "Connected (Healthy)"


def test_health_api_degraded_when_database_down():
    """
    Test Case 2: Validate that /api/health reports 'degraded' status
    when the database check returns a disconnected state.
    """
    with patch("app.main.check_db_health", return_value="Disconnected (OperationalError)"):
        response = client.get("/api/health")

        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "degraded"
        assert "Disconnected" in payload["database_status"]