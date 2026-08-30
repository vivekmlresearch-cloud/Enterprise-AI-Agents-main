import { fetchJson } from '../../lib/api';

async function getIncident() {
  try {
    return await fetchJson<any>('/api/v1/incidents/analyze', {
      method: 'POST',
      body: JSON.stringify({ service: 'checkout-service', environment: 'prod', window_minutes: 30 })
    });
  } catch {
    return null;
  }
}

export default async function IncidentsPage() {
  const incident = await getIncident();
  return (
    <div>
      <h1 className="page-title">Incident Console</h1>
      {!incident ? <div className="card">No incident data available.</div> : (
        <div className="grid-2">
          <div className="card">
            <h3>{incident.summary.title}</h3>
            <p><span className="badge">{incident.summary.severity}</span></p>
            <p>{incident.summary.summary}</p>
            <h3>Likely causes</h3>
            <ul>{incident.summary.likely_causes.map((cause: string) => <li key={cause}>{cause}</li>)}</ul>
            <h3>What may happen next</h3>
            <ul>{incident.summary.what_may_happen_next.map((item: string) => <li key={item}>{item}</li>)}</ul>
          </div>
          <div className="card">
            <h3>Recommended actions</h3>
            <div className="list">
              {incident.summary.recommendations.map((rec: any, idx: number) => (
                <div className="list-item" key={idx}>
                  <strong>{rec.title}</strong>
                  <div>{rec.detail}</div>
                  <div className="badge">confidence {Math.round(rec.confidence * 100)}%</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
