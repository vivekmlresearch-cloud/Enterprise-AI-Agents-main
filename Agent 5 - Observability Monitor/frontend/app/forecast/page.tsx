import { fetchJson } from '../../lib/api';

export default async function ForecastPage() {
  const data = await fetchJson<any>('/api/v1/forecast/current').catch(() => ({ items: [] }));
  return (
    <div>
      <h1 className="page-title">Forecast Center</h1>
      <div className="list">
        {data.items.length === 0 ? <div className="card">No forecast records available.</div> : data.items.map((item: any, idx: number) => (
          <div className="list-item" key={idx}>
            <strong>{item.service}</strong>
            <div>{item.likely_event}</div>
            <div>Horizon: {item.horizon_minutes} minutes</div>
            <div>Rationale: {item.rationale}</div>
            <div className="badge">confidence {Math.round(item.confidence * 100)}%</div>
          </div>
        ))}
      </div>
    </div>
  );
}
