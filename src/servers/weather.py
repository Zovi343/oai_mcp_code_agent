import os

import uvicorn
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route

load_dotenv()

# Initialize FastMCP server for Weather tools (SSE)
mcp = FastMCP("weather")

@mcp.tool()
async def get_forecast(location: str) -> str:
    """Get mocked weather forecast for a location.

    Args:
        location: Location name or address.

    Returns:
        A string containing a single weather forecast period.
    """
    period = {
        "name": "Today",
        "temperature": 68,
        "temperatureUnit": "F",
        "windSpeed": "10 mph",
        "windDirection": "NE",
        "detailedForecast":
            "Partly cloudy with a chance of light rain in the afternoon.",
    }

    forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
    return forecast



def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can server the provied mcp server with SSE.

    Args:
        mcp_server (Server): MCP server to serve.
        debug (bool, optional): Enable debug mode. Defaults to False.

    Returns:
        Starlette: An application instance.
    """
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,  # noqa: SLF001
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


if __name__ == "__main__":
    mcp_server = mcp._mcp_server  # noqa: WPS437

    import argparse

    parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port',
                        type=int,
                        default=os.getenv('WEATHER_API_PORT'),
                        help='Port to listen on')
    args = parser.parse_args()

    # Bind SSE request handling to MCP server
    starlette_app = create_starlette_app(mcp_server, debug=True)

    uvicorn.run(starlette_app, host=args.host, port=args.port)
