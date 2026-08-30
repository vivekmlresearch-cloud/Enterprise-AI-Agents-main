import { fetchJson } from '../../lib/api';

async function getLogs() {
  try {
    return await fetchJson<any>('/api/v1/logs/search', {
      method: 'POST',
      body: JSON.stringify({ service: 'checkout-service', environment: 'prod', limit: 50 })
    });
  } catch {
    return { records: [] };
  }
}

export default async function LogsPage() {
  const data = await getLogs();
  return (
    <div>
      <h1 className="page-title">Log Explorer</h1>
      <div className="card">
        <table className="table">
          <thead>
            <tr><th>Timestamp</th><th>Service</th><th>Severity</th><th>Message</th></tr>
          </thead>
          <tbody>
            {data.records.map((row: any, idx: number) => (
              <tr key={idx}>
                <td>{new Date(row.timestamp).toLocaleString()}</td>
                <td>{row.service}</td>
                <td>{row.severity}</td>
                <td>{row.message}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
