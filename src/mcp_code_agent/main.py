import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from src.mcp_code_agent.agent.agent import MCPAgent
from src.mcp_code_agent.agent.helpers import convert_mcp_tools


async def main():
    """Sets up the MCP server, initialize  tools, and runs the agent."""
    # Configure Docker-based MCP server for SQLite
    server_params = StdioServerParameters(
        command="docker",
        args=[
            "run",
            "--rm",  # Remove container after exit
            "-i",  # Interactive mode
            "-v",  # Mount volume
            "mcp-test:/mcp",  # Map local volume to container path
            "mcp/sqlite",  # Use SQLite MCP image
            "--db-path",
            "/mcp/test.db",  # Database file path inside container
        ],
        env=None,
    )

    print("MCP Server Parameters: \n", server_params)
    print()

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read, write
        ) as session:
            await session.initialize()

            mcp_tools = await session.list_tools()

            parsed_tools = convert_mcp_tools(session, mcp_tools.tools)

            agent = MCPAgent(parsed_tools)

            answer = await agent.query_agent(
                "List all the rows from the table 'test_table'."
                )

            print("Agent answer: ", answer)

if __name__ == "__main__":
    asyncio.run(main())