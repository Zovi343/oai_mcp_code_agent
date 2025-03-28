from abc import ABC, abstractmethod
from collections.abc import Callable

from mcp import ClientSession
from mcp.types import CallToolResult
from mcp_clients.tool_types import CustomOpenAITool


class MCPClient(ABC):
    """Manages MCP client session lifecycle."""

    def __init__(self) -> None:
        """Initializes the MCP client."""
        self.session: ClientSession | None = None

    @abstractmethod
    async def start(self) -> None:
        """Starts and initializes the MCP client session."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stops and cleans up the MCP client session."""
        pass

    def session_is_active(self) -> bool:
        """Check if the MCP client session is active.

        Returns:
            bool:  True if the session is active, False otherwise
        """
        return bool(self.session)


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
        ) -> dict[str, CustomOpenAITool]:
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

        return custom_tools, mcp_tools
