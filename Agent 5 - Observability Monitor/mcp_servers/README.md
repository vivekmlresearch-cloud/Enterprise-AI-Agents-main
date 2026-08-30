# MCP Server Stubs

These directories contain skeleton integrations for the tool layer used by the agent.

- `logs/`: ClickHouse log querying tools
- `k8s_docker/`: cluster and container inspection tools
- `notifications/`: email / Slack / PagerDuty tools
- `knowledge/`: runbooks and incident memory

You can replace the simple HTTP handlers below with a full MCP server implementation over stdio or Streamable HTTP.
