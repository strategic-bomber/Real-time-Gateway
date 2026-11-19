import pytest

import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))       # .../python_api/tests
PYTHON_API_DIR = os.path.dirname(CURRENT_DIR)                  # .../python_api
sys.path.insert(0, PYTHON_API_DIR)

from unittest.mock import patch, AsyncMock
from python_api.gw_client import publish_event

@pytest.mark.asyncio
async def test_publish_event_success():
    """Returns 'ok' when gateway responds 200."""
    mock_response = AsyncMock()
    mock_response.raise_for_status = lambda: None
    
    with patch("gw_client.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        result = await publish_event("deal-42", "update", {"kind": "test"}, None)
        assert result == "ok"

@pytest.mark.asyncio
async def test_publish_event_degraded_on_failure():
    """Returns 'degraded' when gateway is unreachable (architecture requirement)."""
    with patch("gw_client.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(side_effect=Exception("Connection refused"))
        
        result = await publish_event("deal-42", "update", {"kind": "test"}, None)
        assert result == "degraded"