
from mcp import ClientSession
from mcp.client.sse import sse_client

from src.mcp_code_agent.mcp_clients.client import MCPClient


class MCPSSEClient(MCPClient):
    """SSE client for the MCP.

    Args:
        MCPClient (_type_): The base class for the MCP client.
    """
    def __init__(self, server_url: str):
        """Initialize the SSE client.

        Args:
            server_url (str): The URL of the server.
        """
        self.session: ClientSession | None = None
        self.server_url: str = server_url

    async def start(self):
        """Connect to an MCP server running with SSE transport."""
        self._streams_context = sse_client(url=self.server_url)
        streams = await self._streams_context.__aenter__()

        self._session_context = ClientSession(*streams)
        self.session: ClientSession = await self._session_context.__aenter__()

        await self.session.initialize()

    async def stop(self):
        """Properly clean up the session and streams."""
        if self._session_context:
            await self._session_context.__aexit__(None, None, None)
        if self._streams_context:
            await self._streams_context.__aexit__(None, None, None)
