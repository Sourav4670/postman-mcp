"""
Abstract base class for Postman MCP tool handlers
"""
from abc import ABC, abstractmethod
from typing import Any
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource


class ToolHandler(ABC):
    """Base class for all Postman tool handlers"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def get_tool_description(self) -> Tool:
        """Return the MCP Tool description for this handler"""
        pass
    
    @abstractmethod
    async def run_tool(self, arguments: dict) -> list[TextContent | ImageContent | EmbeddedResource]:
        """Execute the tool with the given arguments"""
        pass
