// Small shared UI bits: loading spinner and empty-state block.

export function Spinner({ label }) {
  return (
    <span className="spinner-wrap">
      <span className="spinner" aria-hidden="true" />
      {label && <span className="spinner-label">{label}</span>}
    </span>
  );
}

export function Loading({ label = "Loading…" }) {
  return (
    <div className="loading-block">
      <span className="spinner spinner-lg" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}

export function EmptyState({ icon = "📭", title, children, action }) {
  return (
    <div className="empty-state">
      <div className="empty-icon">{icon}</div>
      {title && <div className="empty-title">{title}</div>}
      {children && <div className="empty-body">{children}</div>}
      {action}
    </div>
  );
}
