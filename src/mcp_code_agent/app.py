import os
import sys
from typing import Any

# Add the parent directory to the sys.path
# This is necessary so that the chainlit can see the module imports.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import chainlit as cl
from mcp import ClientSession
from mcp_clients.sse_client import MCPSSEClient
from mcp_clients.stdio_client import MCPStdioClient
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
)

from src.mcp_code_agent.agent.agent import MCPAgent

# Initiate the agent and MCP clients
mcp_stdio_client = MCPStdioClient(
    "docker",
    [
        "run",
        "--rm",
        "-i",
        "-v",
        "mcp-test:/mcp",
        "mcp/sqlite",
        "--db-path",
        "/mcp/test.db",
    ])
mcp_sse_client = MCPSSEClient(
    server_url=f"http://localhost:{os.getenv('WEATHER_API_PORT')}/sse"
    )
mcp_agent = MCPAgent()

@cl.on_mcp_connect
async def on_mcp_connect(connection: Any, session: ClientSession):
    """Function to handle Chainlit on MCP connect hook event.

    Args:
        connection (Any): Connection object.
        session (ClientSession): MCP client session object.
    """
    print("connection", connection)

    if connection.clientType == "sse":
        # Register SSE MCP server through Chainlit UI
        custom_mcp_server = MCPSSEClient(server_url="", session=session)
        (
            converted_mcp_tools,
            original_mcp_tools
        ) = await custom_mcp_server.get_converted_mcp_tools()

        mcp_agent.add_tools(converted_mcp_tools)
        cl.user_session.set("mcp_tools", original_mcp_tools.tools)
    elif connection.clientType == "stdio":
        print("Custom stdio server not supported yet.")

@cl.set_starters
async def set_starters() -> list[cl.Starter]:
    """Function to set the starters for the chat.

    Returns:
        cl.Starter: Starters for the chat.
    """
    return [
        cl.Starter(
            label="Create `users` table.",
            message="""
Create table called `users` with the following columns:
`id`, `name`, `street`, `city`, `country`.
            """,
        ),
        cl.Starter(
            label="Database tool query.",
            message="Can you list all the tables in the database?",
        ),
        cl.Starter(
            label="Weather query.",
            message="What is the weather in Toronto?",
        ),
    ]

@cl.on_chat_start
async def on_chat_start():
    """Function to handle Chainlit on chat start hook event."""
    print("A new chat session has started!")

    # Register custom MCP servers
    try:
        if not mcp_stdio_client.session_is_active():
            await mcp_stdio_client.start()
            stdio_converted_tools, _ = await mcp_stdio_client.get_converted_mcp_tools()
            mcp_agent.add_tools(stdio_converted_tools)
    except Exception:
        print("Failed to register stdio SQLite server.")

    try:
        if not mcp_sse_client.session_is_active():
            await mcp_sse_client.start()
            sse_converted_tools, _ = await mcp_sse_client.get_converted_mcp_tools()
            mcp_agent.add_tools(sse_converted_tools)
    except Exception:
        print("Failed to register SSE Weather server.")

@cl.step(type="tool", show_input=True)
async def tool(tool_call: ChatCompletionMessageToolCall) -> str:
    """Function to handle tool calls.

    Args:
        tool_call (_type_): Tool call message received from the agent.

    Returns:
        str: Tool result.
    """
    current_step = cl.context.current_step
    current_step.name = f"Tool: {tool_call.function.name}"
    tool_result = await mcp_agent.evaluate_tool(tool_call)
    return tool_result

@cl.on_message
async def on_message(msg: cl.Message):
    """Function to handle Chainlit on message hook event.

    Args:
        msg (cl.Message): message passed from Chainlit by user.
    """
    print("The user sent: ", msg.content)
    answer, tool_calls = await mcp_agent.query(msg.content)

    if tool_calls is not None:
        for tool_call in tool_calls:
            await tool(tool_call)

        tool_aware_answer = await mcp_agent.tool_aware_query()

        await cl.Message(
            content=tool_aware_answer,
        ).send()
    else:
        await cl.Message(
            content=answer,
        ).send()


@cl.on_chat_end
async def on_chat_end():
    """Function to handle Chainlit on chat end hook event."""
    print("The user disconnected!")
