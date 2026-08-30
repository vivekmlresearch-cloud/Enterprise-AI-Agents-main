# Technical architecture

## Lanes

### 1. Ingestion lane
OpenTelemetry Collector and Fluent Bit receive logs, metrics, and traces, then normalize metadata.

### 2. Storage and query lane
ClickHouse stores logs and forecast outputs. It powers search, historical comparisons, and retrieval.

### 3. Agent lane
FastAPI exposes APIs. LangGraph orchestrates anomaly detection, historical retrieval, LLM reasoning, and action recommendations.

### 4. Recommendation lane
A separate service computes likely next events and writes them back to ClickHouse in parallel so the main incident flow stays fast.

### 5. Workflow lane
Temporal executes durable alert and escalation workflows.

### 6. Tool lane
MCP-style servers expose operational tools for logs, cluster context, notifications, and knowledge retrieval.

### 7. UI lane
Next.js renders the custom observability console with pages for incidents, logs, forecasts, actions, and history.
