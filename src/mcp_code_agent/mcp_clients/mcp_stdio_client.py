from collections.abc import Callable
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import CallToolResult
from mcp_clients.too_typesl import CustomOpenAITool


class MCPStdioClient:
    """Manages MCP client session lifecycle."""

    def __init__(self, command: str, server_args: list[str]) -> None:
        """Initializes the MCP client.

        Args:
            command (str): command to start the server
            server_args (list[str]): arguments for starting server
        """
        self.session: ClientSession | None = None
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

    def session_is_active(self) -> bool:
        """Check if the MCP client session is active.

        Returns:
            bool:  True if the session is active, False otherwise
        """
        return bool(self.session)


    async def stop(self) -> None:
        """Stops and cleans up the MCP client session."""
        if self.session:
            await self.session.__aexit__(None, None, None)
        if self._client:
            await self._client.__aexit__(None, None, None)


    def create_callable_mcp_tool(self, tool_name: str) -> Callable:
        """Create a callable function for a specific tool.

        Args:
            tool_name: The name of the tool to create a callable for

        Returns:
            A callable async function that executes the specified tool
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        async def callable(*args, **kwargs) -> str:
            response: CallToolResult = await self.session.call_tool(
                tool_name,
                arguments=kwargs
            )
            return response.content[0].text

        return callable

    async def get_converted_mcp_tools(
            self,
        ) -> list[CustomOpenAITool]:
        """Gets MCP tools and converts them into a list of CustomOpenAITool.

        Returns:
            List of CustomOpenAITool
        """
        mcp_tools = await self.session.list_tools()
        custom_tools: dict[str, CustomOpenAITool] = {}

        for tool in mcp_tools.tools:
            custom_tools[tool.name] = {
                "name": tool.name,
                "callable": self.create_callable_mcp_tool(tool.name),
                "schema": {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    },
                    "strict": True,
                },
            }

        return custom_tools
