"""
Postman MCP Server - Streamable HTTP Implementation
Provides 41 Postman API tools for collections, environments, mocks, specs, and workspaces.
"""
import os
import sys
import logging
import argparse
import contextlib
from typing import Any, AsyncIterator

import mcp.types as types
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(levelname)-8s  %(name)-20s  %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)

logger = logging.getLogger("postman-mcp")

# Import all Postman tool handlers
from tools.postman_tools import register_all_tools

# Initialize MCP server
app = Server("postman-mcp")

# Store tool handlers globally
tool_handlers = {}


def register_all_postman_tools():
    """Register all 41 Postman tool handlers with the MCP server."""
    global tool_handlers
    
    handlers = register_all_tools()
    
    for handler in handlers:
        tool_handlers[handler.name] = handler


# Register tool handlers with MCP decorators
@app.list_tools()
async def list_tools_handler() -> list[types.Tool]:
    """List all available Postman tools."""
    return [
        types.Tool(
            name=h.name,
            description=h.get_tool_description().description,
            inputSchema=h.get_tool_description().inputSchema
        )
        for h in tool_handlers.values()
    ]


@app.call_tool()
async def call_tool_handler(name: str, arguments: dict) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Execute a Postman tool."""
    if name not in tool_handlers:
        raise ValueError(f"Unknown tool: {name}")
    
    handler = tool_handlers[name]
    return await handler.run_tool(arguments)


# ============================================================
# Streamable HTTP Transport Setup
# ============================================================

def create_streamable_http_app(port: int = 8000) -> Starlette:
    """Create Starlette app with MCP streamable HTTP support."""
    
    # Initialize session manager
    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=None,
        json_response=False,
        stateless=False,
    )
    
    class _StreamableHTTPRoute:
        async def __call__(self, scope, receive, send) -> None:
            await session_manager.handle_request(scope, receive, send)
    
    async def _health_endpoint(_request) -> JSONResponse:
        return JSONResponse({"status": "ok"})
    
    async def _root_endpoint(_request) -> JSONResponse:
        return JSONResponse({
            "status": "ok",
            "transport": "streamable-http",
            "server": "postman-mcp",
            "tools": len(tool_handlers)
        })
    
    @contextlib.asynccontextmanager
    async def _lifespan(_starlette_app: Starlette) -> AsyncIterator[None]:
        async with session_manager.run():
            yield
    
    # Create Starlette app with routes
    starlette_app = Starlette(
        debug=False,
        routes=[
            Route("/", endpoint=_root_endpoint),
            Route("/health", endpoint=_health_endpoint),
            Route("/healthz", endpoint=_health_endpoint),
            Route("/mcp", endpoint=_StreamableHTTPRoute()),
        ],
        lifespan=_lifespan,
    )
    
    # Add CORS middleware
    starlette_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["mcp-session-id", "mcp-protocol-version"],
        max_age=86400,
    )
    
    return starlette_app


def run_streamable_http(port: int = 8000):
    """Run MCP server with Streamable HTTP transport."""
    logger.info("Postman MCP Server starting up")
    
    # Register all tools
    register_all_postman_tools()
    
    logger.info(f"Total tools registered: {len(tool_handlers)}")
    logger.info(f"Starting Postman MCP Server on port {port} (streamable-http)")
    
    # Create and run Starlette app
    starlette_app = create_streamable_http_app(port)
    
    import uvicorn
    uvicorn.run(starlette_app, host="0.0.0.0", port=port)


# ============================================================
# SSE Transport Setup
# ============================================================

def create_sse_starlette_app():
    """Create Starlette app with SSE transport."""
    sse = SseServerTransport("/messages")
    
    class _SSEEndpoint:
        async def __call__(self, scope, receive, send) -> None:
            async with sse.connect_sse(scope, receive, send) as (
                read_stream,
                write_stream,
            ):
                await app.run(
                    read_stream,
                    write_stream,
                    app.create_initialization_options(),
                )
    
    async def _health_endpoint(_request) -> JSONResponse:
        return JSONResponse({"status": "ok"})
    
    async def _root_endpoint(_request) -> JSONResponse:
        return JSONResponse({
            "status": "ok",
            "transport": "sse",
            "server": "postman-mcp",
            "tools": len(tool_handlers)
        })
    
    starlette_app = Starlette(
        debug=False,
        routes=[
            Route("/", endpoint=_root_endpoint),
            Route("/health", endpoint=_health_endpoint),
            Route("/healthz", endpoint=_health_endpoint),
            Route("/sse", endpoint=_SSEEndpoint()),
            Mount("/messages", app=sse.handle_post_message),
        ],
    )
    
    starlette_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=86400,
    )
    
    return starlette_app


def run_sse(port: int = 8000):
    """Run MCP server with SSE transport."""
    logger.info("Postman MCP Server starting up (SSE mode)")
    
    register_all_postman_tools()
    
    logger.info(f"Total tools registered: {len(tool_handlers)}")
    logger.info(f"Starting Postman MCP Server on port {port} (SSE)")
    
    starlette_app = create_sse_starlette_app()
    
    import uvicorn
    uvicorn.run(starlette_app, host="0.0.0.0", port=port)


# ============================================================
# Stdio Transport Setup
# ============================================================

async def run_stdio():
    """Run MCP server with stdio transport."""
    logger.info("Postman MCP Server starting up (stdio mode)")
    
    register_all_postman_tools()
    
    logger.info(f"Total tools registered: {len(tool_handlers)}")
    
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def run_stdio_sync():
    """Synchronous wrapper for stdio mode."""
    import asyncio
    asyncio.run(run_stdio())


# ============================================================
# CLI Entry Point
# ============================================================

def cli_main():
    """Main CLI entry point for the Postman MCP server."""
    parser = argparse.ArgumentParser(
        description="Postman MCP Server - 41 Postman API tools"
    )
    parser.add_argument(
        "--mode",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport mode (default: stdio)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP-based transports (default: 8000)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "stdio":
        run_stdio_sync()
    elif args.mode == "sse":
        run_sse(args.port)
    elif args.mode == "streamable-http":
        run_streamable_http(args.port)


if __name__ == "__main__":
    cli_main()
