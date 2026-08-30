import { fetchJson } from '../lib/api';

async function getForecast() {
  try {
    return await fetchJson<any>('/api/v1/forecast/current');
  } catch {
    return { items: [] };
  }
}

export default async function OverviewPage() {
  const forecast = await getForecast();
  return (
    <div>
      <div className="page-title">
        <h1>Overview</h1>
        <p>AI-first observability with incidents, logs, forecasts, and actions.</p>
      </div>
      <div className="cards">
        <div className="card"><h3>System health</h3><div className="metric">Healthy</div></div>
        <div className="card"><h3>Active anomalies</h3><div className="metric">3</div></div>
        <div className="card"><h3>Forecast items</h3><div className="metric">{forecast.items.length}</div></div>
        <div className="card"><h3>Automation mode</h3><div className="metric">Guarded</div></div>
      </div>
      <div className="grid-2">
        <div className="card">
          <h3>Forecast highlights</h3>
          <div className="list">
            {forecast.items.length === 0 ? <div>No forecast data yet.</div> : forecast.items.slice(0, 5).map((item: any, idx: number) => (
              <div className="list-item" key={idx}>
                <strong>{item.service}</strong>
                <div>{item.likely_event}</div>
                <div className="badge">confidence {Math.round(item.confidence * 100)}%</div>
              </div>
            ))}
          </div>
        </div>
        <div className="card">
          <h3>Architecture modules</h3>
          <div className="list">
            {['Telemetry ingestion', 'ClickHouse storage', 'LangGraph orchestration', 'Temporal workflows', 'Parallel recommendation lane', 'MCP tool integrations'].map((x) => (
              <div className="list-item" key={x}>{x}</div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
