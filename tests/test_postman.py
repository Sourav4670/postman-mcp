"""
Tests for Postman MCP Server
"""
import pytest
from tools.postman_tools import register_all_tools


def test_tool_registration():
    """Test that all 41 tools are registered"""
    handlers = register_all_tools()
    
    assert len(handlers) == 41, f"Expected 41 tools, got {len(handlers)}"
    
    # Verify all handlers have names
    for handler in handlers:
        assert hasattr(handler, 'name'), "Handler missing 'name' attribute"
        assert handler.name, "Handler name is empty"


def test_tool_descriptions():
    """Test that all tools have valid descriptions"""
    handlers = register_all_tools()
    
    for handler in handlers:
        description = handler.get_tool_description()
        
        # Verify description attributes
        assert hasattr(description, 'name'), f"Tool {handler.name} missing name in description"
        assert hasattr(description, 'description'), f"Tool {handler.name} missing description"
        assert hasattr(description, 'inputSchema'), f"Tool {handler.name} missing inputSchema"
        
        # Verify description is not empty
        assert description.description, f"Tool {handler.name} has empty description"
        
        # Verify inputSchema is a dict
        assert isinstance(description.inputSchema, dict), f"Tool {handler.name} inputSchema is not a dict"
        assert description.inputSchema.get('type') == 'object', f"Tool {handler.name} inputSchema type is not 'object'"


def test_tool_names():
    """Test that all expected tool names are registered"""
    handlers = register_all_tools()
    tool_names = {h.name for h in handlers}
    
    expected_tools = {
        # User Info
        "getAuthenticatedUser",
        "getEnabledTools",
        
        # Collections
        "createCollection",
        "getCollection",
        "getCollections",
        "putCollection",
        "duplicateCollection",
        "getDuplicateCollectionTaskStatus",
        
        # Requests/Responses
        "createCollectionRequest",
        "updateCollectionRequest",
        "createCollectionResponse",
        
        # Environments
        "createEnvironment",
        "getEnvironment",
        "getEnvironments",
        "putEnvironment",
        
        # Mocks
        "createMock",
        "getMock",
        "getMocks",
        "updateMock",
        "publishMock",
        
        # Specs
        "createSpec",
        "getSpec",
        "getAllSpecs",
        "updateSpecProperties",
        "getSpecDefinition",
        "createSpecFile",
        "getSpecFiles",
        "getSpecFile",
        "updateSpecFile",
        
        # Spec-Collection Integration
        "generateCollection",
        "getSpecCollections",
        "generateSpecFromCollection",
        "getGeneratedCollectionSpecs",
        "syncCollectionWithSpec",
        "syncSpecWithCollection",
        
        # Workspaces
        "createWorkspace",
        "getWorkspace",
        "getWorkspaces",
        "updateWorkspace",
        
        # Other
        "getTaggedEntities",
        "runCollection",
    }
    
    assert tool_names == expected_tools, f"Tool names mismatch. Missing: {expected_tools - tool_names}, Extra: {tool_names - expected_tools}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
