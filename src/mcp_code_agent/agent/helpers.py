from collections.abc import Callable

from mcp import ClientSession
from mcp.types import CallToolResult, Tool

from src.mcp_code_agent.custom_types.tool import CustomOpenAITool


def create_callable_mcp_tool(session: ClientSession, tool_name: str) -> Callable:
    """Create a callable function for a specific tool.

    Args:
        session: MCP client session
        tool_name: The name of the tool to create a callable for

    Returns:
        A callable async function that executes the specified tool
    """
    if not session:
        raise RuntimeError("Not connected to MCP server")

    async def callable(*args, **kwargs) -> str:
        response: CallToolResult = await session.call_tool(tool_name, arguments=kwargs)
        return response.content[0].text

    return callable

def convert_mcp_tools(
        session: ClientSession,
          mcp_tools: list[Tool]
    ) -> list[CustomOpenAITool]:
    """Convert a list of MCP tools to a list of CustomOpenAITool.

    Args:
        session: MCP client session
        mcp_tools: List of MCP tools

    Returns:
        List of CustomOpenAITool
    """
    custom_tools: dict[str, CustomOpenAITool] = {}

    for tool in mcp_tools:
        custom_tools[tool.name] = {
            "name": tool.name,
            "callable": create_callable_mcp_tool(session, tool.name),
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