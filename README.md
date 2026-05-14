# Postman MCP Server

A production-ready Model Context Protocol (MCP) server that provides **41 Postman API tools** for managing collections, environments, mocks, API specifications, and workspaces. Supports **Streamable HTTP**, **SSE**, and **stdio** transports.

## Features

- 📦 **41 Postman API Tools** - Complete Postman API automation
- 🔄 **Multiple Transports** - Streamable HTTP, SSE, and stdio support
- 🚀 **Production Ready** - Docker support with proper error handling
- 📚 **Collections** - Create, read, update, duplicate collections
- 🔐 **Environments** - Manage environment variables
- 🎭 **Mocks** - Create and manage mock servers
- 📝 **API Specs** - OpenAPI, AsyncAPI, protobuf, GraphQL support
- 🏢 **Workspaces** - Manage team and personal workspaces
- 🔗 **Integration** - Sync specs with collections

## Available Tools (41)

### Collections (7 tools)
- `createCollection` - Create a collection (v2.1.0 format)
- `getCollection` - Get collection info (map/minimal/full)
- `getCollections` - List workspace collections
- `putCollection` - Replace collection contents
- `duplicateCollection` - Duplicate to another workspace
- `getDuplicateCollectionTaskStatus` - Check duplication status

### Requests & Responses (3 tools)
- `createCollectionRequest` - Create request in collection
- `updateCollectionRequest` - Update existing request
- `createCollectionResponse` - Create request response

### Environments (4 tools)
- `createEnvironment` - Create environment
- `getEnvironment` - Get environment details
- `getEnvironments` - List all environments
- `putEnvironment` - Replace environment contents

### Mock Servers (5 tools)
- `createMock` - Create mock server
- `getMock` - Get mock server details
- `getMocks` - List all mock servers
- `updateMock` - Update mock server
- `publishMock` - Publish mock server (set public)

### API Specifications (9 tools)
- `createSpec` - Create API spec (OpenAPI/AsyncAPI/protobuf/GraphQL)
- `getSpec` - Get spec details
- `getAllSpecs` - List workspace specs
- `updateSpecProperties` - Update spec properties
- `getSpecDefinition` - Get complete spec definition
- `createSpecFile` - Create spec file
- `getSpecFiles` - List all spec files
- `getSpecFile` - Get file contents
- `updateSpecFile` - Update spec file

### Spec-Collection Integration (4 tools)
- `generateCollection` - Generate collection from spec
- `getSpecCollections` - List spec's generated collections
- `generateSpecFromCollection` - Generate spec from collection
- `getGeneratedCollectionSpecs` - Get collection's generated specs
- `syncCollectionWithSpec` - Sync collection with spec
- `syncSpecWithCollection` - Sync spec with collection

### Workspaces (4 tools)
- `createWorkspace` - Create workspace
- `getWorkspace` - Get workspace details
- `getWorkspaces` - List all workspaces
- `updateWorkspace` - Update workspace properties

### Other (4 tools)
- `getAuthenticatedUser` - Get current user info
- `getTaggedEntities` - Get entities by tag (Enterprise)
- `runCollection` - Run collection with Newman
- `getEnabledTools` - List enabled tools

## Quick Start

### Prerequisites

**Required:**
1. **Postman API Key** - Get from https://postman.com/settings/me/api-keys
2. **Python 3.10+**

### Installation

```bash
cd postman-tool

# Install in editable mode
pip install -e .

# Verify installation
postman-mcp --help
```

### Environment Variables

**Required:**
```bash
export POSTMAN_API_KEY="your_postman_api_key"
```

**Windows PowerShell:**
```powershell
$env:POSTMAN_API_KEY = "your_postman_api_key"
```

### Run Server

**Streamable HTTP (Recommended):**
```bash
postman-mcp --mode streamable-http --port 8010
```

**SSE:**
```bash
postman-mcp --mode sse --port 8010
```

**Stdio (for MCP clients):**
```bash
postman-mcp --mode stdio
```

### Docker

```bash
# Build image
docker build -t postman-mcp .

# Run container
docker run -e POSTMAN_API_KEY=your_key -p 8010:8010 postman-mcp
```

## MCP Client Configuration

### Streamable HTTP

```json
{
  "mcpServers": {
    "postman": {
      "type": "streamable-http",
      "url": "http://localhost:8010/mcp"
    }
  }
}
```

### Stdio

```json
{
  "mcpServers": {
    "postman": {
      "command": "postman-mcp",
      "args": ["--mode", "stdio"],
      "env": {
        "POSTMAN_API_KEY": "your_postman_api_key"
      }
    }
  }
}
```

## Usage Examples

### Get Current User

```python
await call_tool("getAuthenticatedUser", {})
```

### List Workspaces

```python
# List my personal workspaces
user = await call_tool("getAuthenticatedUser", {})
workspaces = await call_tool("getWorkspaces", {
    "createdBy": user["user"]["id"],
    "type": "personal",
    "limit": 100
})
```

### Create Collection

```python
await call_tool("createCollection", {
    "workspace": "workspace-id",
    "collection": {
        "info": {
            "name": "My API Collection",
            "description": "Collection for testing",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": []
    }
})
```

### Get Collection

```python
# Get lightweight map (default)
await call_tool("getCollection", {
    "collectionId": "12345-abc123def456"
})

# Get full payload
await call_tool("getCollection", {
    "collectionId": "12345-abc123def456",
    "model": "full"
})
```

### Create Mock Server

```python
await call_tool("createMock", {
    "workspace": "workspace-id",
    "mock": {
        "name": "My Mock Server",
        "collection": "12345-abc123def456",  # Collection UID
        "environment": "env-id",
        "private": false
    }
})
```

### Create API Specification

```python
await call_tool("createSpec", {
    "workspaceId": "workspace-id",
    "name": "My API",
    "type": "openapi",
    "files": [
        {
            "path": "openapi.yaml",
            "content": "openapi: 3.0.0\ninfo:\n  title: My API\n  version: 1.0.0"
        }
    ]
})
```

### Generate Collection from Spec

```python
await call_tool("generateCollection", {
    "specId": "spec-id",
    "name": "Generated Collection",
    "elementType": "collection",
    "options": {
        "requestParametersResolution": "example",
        "exampleParametersResolution": "example"
    }
})
```

### Create Environment

```python
await call_tool("createEnvironment", {
    "workspace": "workspace-id",
    "environment": {
        "name": "Production",
        "values": [
            {"key": "base_url", "value": "https://api.example.com", "enabled": true},
            {"key": "api_key", "value": "secret", "enabled": true, "type": "secret"}
        ]
    }
})
```

### Run Collection

```python
await call_tool("runCollection", {
    "collectionId": "12345-abc123def456",
    "environmentId": "env-id",
    "iterationCount": 1,
    "requestTimeout": 30000
})
```

## API Endpoints

When running with HTTP transports:

- `GET /` - Server info
- `GET /health` - Health check
- `/mcp/*` - MCP protocol endpoints (streamable-http)
- `/sse` - SSE endpoint
- `/messages` - SSE messages endpoint

## Development

### Run Tests

```bash
pytest
```

### Project Structure

```
postman-tool/
├── postman_server.py          # Main MCP server
├── tools/
│   ├── toolhandler.py         # Base class
│   └── postman_tools.py       # All 41 tool implementations
├── tests/
│   └── test_postman.py
├── pyproject.toml
├── Dockerfile
└── README.md
```

## Postman API Details

### Authentication

Uses `X-Api-Key` header with your Postman API key. Get yours at: https://postman.com/settings/me/api-keys

### Base URL

```
https://api.getpostman.com
```

### Collection UID Format

Many endpoints require collection UID in format: `<OWNER_ID>-<COLLECTION_ID>`

To get the UID:
1. Use `getCollection` and read the `uid` field
2. Construct from `{ownerId}-{collectionId}` where:
   - For team collections: `ownerId = me.teamId` (from `getAuthenticatedUser`)
   - For personal collections: `ownerId = me.user.id` (from `getAuthenticatedUser`)

### Rate Limits

Postman API has rate limits. See: https://learning.postman.com/docs/developer/postman-api/postman-api-rate-limits/

## Common Issues

### Authentication Error

**Error:** `Postman API error (401)`

**Solution:**
- Verify `POSTMAN_API_KEY` is set correctly
- Check key is valid at https://postman.com/settings/me/api-keys
- Ensure key has required permissions

### Collection UID Format

**Error:** `Collection not found`

**Solution:**
- Use full UID format: `12345-abc123def456`
- Get UID from `getCollection` response
- For createMock, pass collection UID, not bare ID

### Workspace Required

**Error:** `Workspace is required`

**Solution:**
- Call `getWorkspaces` to list available workspaces
- Pass `workspace` query parameter
- For "my workspaces", call `getAuthenticatedUser` first

### Newman Integration

The `runCollection` tool requires Newman (Postman's CLI runner) to be integrated programmatically. This is a placeholder that returns instructions.

## Requirements

- Python 3.10+
- Postman API Key
- MCP 1.12.0+
- httpx, Starlette, Uvicorn

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions, please visit the project repository.

## Additional Resources

- Postman API Documentation: https://learning.postman.com/docs/developer/postman-api/intro-api/
- Postman Collection Format: https://schema.postman.com/collection/json/v2.1.0/draft-07/docs/index.html
- MCP Protocol: https://modelcontextprotocol.io
