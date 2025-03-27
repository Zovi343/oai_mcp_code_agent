import os
import sys

# Add the parent directory to the sys.path
# This is necessary so that the chainlit can see the module imports.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import chainlit as cl
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
)

from src.mcp_code_agent.agent.agent import MCPAgent
from src.mcp_code_agent.mcp_clients.mcp_stdio_client import MCPStdioClient

print("Root call")

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
mcp_agent = MCPAgent()


@cl.set_starters
async def set_starters() -> list[cl.Starter]:
    """Function to set the starters for the chat.

    Returns:
        cl.Starter: Starters for the chat.
    """
    return [
        cl.Starter(
            label="List all rows from a table",
            message="List all the rows from the `test_table` table.",
        ),
        cl.Starter(
            label="Database tool query.",
            message="Can you list all the tables in the database?",
        ),
    ]

@cl.on_chat_start
async def on_chat_start():
    """Function to handle Chainlit on chat start hook event."""
    print("A new chat session has started!")
    if not mcp_stdio_client.session_is_active():
        await mcp_stdio_client.start()
        converted_tools = await mcp_stdio_client.get_converted_mcp_tools()
        mcp_agent.configure_tools(converted_tools)

@cl.step(type="tool", show_input=True)
async def handle_tool(tool_call: ChatCompletionMessageToolCall) -> str:
    """Function to handle tool calls.

    Args:
        tool_call (_type_): Tool call message received from the agent.

    Returns:
        str: Tool result.
    """
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
            await handle_tool(tool_call)

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
