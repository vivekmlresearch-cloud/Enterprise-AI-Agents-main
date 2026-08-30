export default function ActionsPage() {
  return (
    <div>
      <h1 className="page-title">Action Center</h1>
      <div className="card">
        <p>Action execution is handled by Temporal workflows through the backend API.</p>
        <div className="code">POST /api/v1/actions/execute</div>
      </div>
    </div>
  );
}
