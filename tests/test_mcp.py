from __future__ import annotations

import pytest
from mcp import Client

from rebot_mhs_lab.server import mcp


@pytest.mark.anyio
async def test_mcp_client_discovers_tools_and_resource():
    async with Client(mcp) as client:
        tools = await client.list_tools()
        assert [tool.name for tool in tools.tools] == [
            "discover_devices",
            "read_device",
            "write_device",
            "emergency_stop",
            "plan_two_arm_handoff",
        ]

        result = await client.call_tool("discover_devices", {})
        assert result.is_error is False
        assert result.structured_content is not None
        assert len(result.structured_content["devices"]) == 2

        resource = await client.read_resource("mhs-prototype://devices/rebot-dm")
        assert len(resource.contents) == 1
