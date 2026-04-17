# RocketSmith Project Rules

## CRITICAL: Never spawn rocketsmith subagents

Do NOT use the Agent tool with any `rocketsmith:*` subagent type (e.g. `rocketsmith:rocketsmith`, `rocketsmith:openrocket`, `rocketsmith:cadsmith`, etc.).

These agents return an `agentId` and require `SendMessage` to continue — but `SendMessage` is not available in this environment. Spawning a subagent and then being unable to continue it crashes the MCP server every time.

**Always use the rocketsmith MCP tools directly:**
- `mcp__plugin_rocketsmith_rocketsmith__openrocket_database`
- `mcp__plugin_rocketsmith_rocketsmith__openrocket_new`
- `mcp__plugin_rocketsmith_rocketsmith__openrocket_component`
- `mcp__plugin_rocketsmith_rocketsmith__openrocket_flight`
- `mcp__plugin_rocketsmith_rocketsmith__manufacturing_annotate_tree`
- `mcp__plugin_rocketsmith_rocketsmith__cadsmith_run_script`
- `mcp__plugin_rocketsmith_rocketsmith__cadsmith_generate_assets`
- `mcp__plugin_rocketsmith_rocketsmith__cadsmith_extract_part`
- `mcp__plugin_rocketsmith_rocketsmith__gui_server`
- `mcp__plugin_rocketsmith_rocketsmith__gui_navigate`
- `mcp__plugin_rocketsmith_rocketsmith__prusaslicer_slice`

This has crashed the MCP server 3 times. Do not repeat this mistake.
