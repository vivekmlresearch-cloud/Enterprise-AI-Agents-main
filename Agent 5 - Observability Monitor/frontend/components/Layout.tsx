import Link from 'next/link';
import React from 'react';

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="layout">
      <aside className="sidebar">
        <h2>Observability AI Agent</h2>
        <p>Custom incident console</p>
        <nav>
          <Link href="/">Overview</Link>
          <Link href="/incidents">Incident Console</Link>
          <Link href="/logs">Log Explorer</Link>
          <Link href="/forecast">Forecast Center</Link>
          <Link href="/actions">Action Center</Link>
          <Link href="/history">Knowledge & History</Link>
        </nav>
      </aside>
      <main className="main">{children}</main>
    </div>
  );
}
