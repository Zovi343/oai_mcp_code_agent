from collections.abc import Callable
from typing import Any, TypedDict


class FunctionSchema(TypedDict):
    """Schema for a function."""
    name: str
    description: str
    parameters: dict[str, Any]


class ToolSchema(TypedDict):
    """Schema for a tool."""
    type: str
    function: FunctionSchema
    strict: bool


class CustomOpenAITool(TypedDict):
    """Custom OpenAI tool wrapper supporting MCP tool calling."""
    name: str
    callable: Callable
    schema: ToolSchema
