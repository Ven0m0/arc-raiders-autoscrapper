---
name: mcp-development
description: Build Model Context Protocol (MCP) servers with tools, resources, prompts, and client configs. Use when creating MCP servers, choosing transports, designing schemas, or implementing custom MCP integrations in Python or TypeScript.
allowed-tools: "Bash, Read, Write, Edit, Glob, Grep"
---

# MCP Development

Build and debug Model Context Protocol (MCP) servers and integrations in Python and TypeScript.

<instructions>

## Workflow

Think through MCP server design step-by-step:

1. **Define scope**: What tools/resources/prompts does the server need?
2. **Choose transport**: stdio, HTTP/SSE, or WebSocket based on client/runtime
3. **Design schemas**: Input/output schemas for each tool, URI templates for resources
4. **Implement**: Tool logic with validation, error handling, structured output
5. **Configure clients**: Claude Desktop, editor MCP config, web deployment
6. **Test**: MCP Inspector plus unit/integration coverage
7. **Deploy**: Package with environment-based config and clear operational limits

## Project Structure

```text
my-mcp-server/
├── src/
│   └── index.ts | server.py
├── package.json | pyproject.toml
└── README.md
```

## Transport Decision

| Use Case              | Transport         | Why                           |
| --------------------- | ----------------- | ----------------------------- |
| Claude Desktop        | stdio             | Native support, simple setup  |
| Local CLI tool        | stdio             | Pipes, process communication  |
| Web application       | HTTP/SSE          | Browser-compatible streaming  |
| High-scale deployment | HTTP (stateless)  | Horizontal scaling            |
| Multi-user service    | HTTP or WebSocket | Session management / realtime |
| Development/testing   | stdio             | Easier debugging              |

</instructions>

<core_concepts>

## Tools

Functions the LLM can call. Each tool should have:

- Clear action-oriented name
- Input schema with descriptions and validation
- Structured output
- A description that explains what it does and when to use it

## Resources

Data the LLM can read.

| Type     | Use                         |
| -------- | --------------------------- |
| Static   | Fixed docs/config           |
| Dynamic  | Computed on request         |
| Template | URI pattern with parameters |

URI patterns:

| Pattern       | Example             |
| ------------- | ------------------- |
| Fixed         | `docs://readme`     |
| Parameterized | `users://{userId}`  |
| Collection    | `files://project/*` |

## Prompts

Reusable templates with arguments. Return formatted prompt text for repeatable workflows.

## Context

Shared capabilities: logging (stderr only), progress reporting, sampling (LLM generation), elicitation (user input).

</core_concepts>

<patterns>

## Tool Definition Pattern

1. Define input schema with validation rules
2. Write a clear description (what it does AND when to use it)
3. Implement logic with error handling
4. Return structured output (human-readable + machine-readable)
5. Never leak internal errors to the LLM

## Resource Pattern

1. Define URI template: `resource://type/{id}`
2. Parse and validate URI parameters
3. Fetch/compute content
4. Return with appropriate MIME type
5. Handle missing resources gracefully

## Configuration Pattern

| Field     | Purpose               |
| --------- | --------------------- |
| `command` | Executable to run     |
| `args`    | Command arguments     |
| `env`     | Environment variables |

Example:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["dist/index.js"],
      "env": {
        "API_BASE_URL": "https://api.example.com"
      }
    }
  }
}
```

## Error Handling

- Catch errors in tools; return error objects, don't crash the server
- Provide clear error messages with context
- Log errors to stderr with tool name and parameters
- Use structured logging in production

</patterns>

<language_specific>

## Python (FastMCP)

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
async def search_docs(query: str, limit: int = 10) -> list[dict]:
    """Search documentation by keyword. Use when the user asks about API usage."""
    results = await doc_index.search(query, limit=limit)
    return [{"title": r.title, "url": r.url, "snippet": r.snippet} for r in results]

@mcp.resource("docs://{topic}")
async def get_doc(topic: str) -> str:
    """Get documentation for a specific topic."""
    return await doc_index.get(topic)
```

- Use Pydantic for schema validation
- All I/O should be async
- Log to stderr (stdout is the protocol channel)

## TypeScript

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

const server = new McpServer({ name: "my-server", version: "1.0.0" });

server.tool("search_docs", { query: z.string(), limit: z.number().default(10) }, async ({ query, limit }) => {
  const results = await docIndex.search(query, limit);
  return { content: [{ type: "text", text: JSON.stringify(results) }] };
});
```

- Use Zod for runtime validation
- ES modules required
- Handle transport cleanup on disconnect

</language_specific>

<testing>

## Testing

| Type        | Focus                                |
| ----------- | ------------------------------------ |
| Unit        | Tool/resource logic                  |
| Integration | Full server startup + protocol flow  |
| Contract    | Schema validation and response shape |

```bash
# Interactive testing
npx @modelcontextprotocol/inspector python -m my_server

# Manual stdio test
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python -m my_server
```

</testing>

<debugging>

| Problem                   | Likely Cause                          | Fix                                        |
| ------------------------- | ------------------------------------- | ------------------------------------------ |
| Schema validation fails   | Type mismatch, missing required field | Check Pydantic/Zod schema vs input         |
| Tools not appearing       | Registration error                    | Verify decorator/method call, check logs   |
| Transport errors          | Malformed JSON-RPC                    | Validate message format, check stderr logs |
| Async errors              | Blocking I/O                          | Ensure all I/O uses async/await            |
| stdout corruption (stdio) | Logging to stdout                     | Redirect all logs to stderr                |

</debugging>

<security>
- Validate all tool inputs (sanitize file paths, prevent directory traversal)
- Never hardcode secrets; use environment variables
- Implement auth for production HTTP servers
- Rate-limit expensive operations
- Restrict file access to allowed directories
- Check file sizes before reading
</security>

<examples>

### Complete Python MCP server

```python
from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("weather")

@mcp.tool()
async def get_weather(city: str) -> dict:
    """Get current weather for a city. Use when the user asks about weather conditions."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://api.weather.example/v1/{city}")
        resp.raise_for_status()
        data = resp.json()
    return {"city": city, "temp_f": data["temp"], "condition": data["condition"]}

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

</examples>

## Success Criteria

MCP server or integration is complete when:

- All tools/resources return correct results for valid inputs
- Schema validation rejects invalid inputs with clear messages
- Errors are handled gracefully (server never crashes on bad input)
- Tests pass (unit for logic, integration for full workflow)
- LLM can discover and correctly use all tools
- Logging is sufficient to debug issues in production
- Client config is documented and reproducible
