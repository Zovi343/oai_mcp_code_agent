from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from src.mcp_code_agent.mcp_clients.client import MCPClient


class MCPStdioClient(MCPClient):
    """Manages MCP client session lifecycle."""

    def __init__(self, command: str, server_args: list[str]) -> None:
        """Initializes the MCP client.

        Args:
            command (str): command to start the server
            server_args (list[str]): arguments for starting server
        """
        super().__init__()
        self._client: Any = None
        self.server_params = StdioServerParameters(
            command=command,
            args=server_args,
            env=None
        )

    async def start(self) -> None:
        """Starts and initializes the MCP client session."""
        self._client = stdio_client(self.server_params)
        read, write = await self._client.__aenter__()

        session = ClientSession(read, write)
        self.session = await session.__aenter__()

        await self.session.initialize()

    async def stop(self) -> None:
        """Stops and cleans up the MCP client session."""
        if self.session:
            await self.session.__aexit__(None, None, None)
        if self._client:
            await self._client.__aexit__(None, None, None)

    def session_is_active(self) -> bool:
        """Check if the MCP client session is active.

        Returns:
            bool:  True if the session is active, False otherwise
        """
        return bool(self.session)
