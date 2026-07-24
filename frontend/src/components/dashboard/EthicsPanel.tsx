export function EthicsPanel() {
  return (
    <section className="panel ethics-panel">
      <div className="panel__header">
        <h2 className="panel__title">Ethics &amp; data status</h2>
        <p className="panel__subtitle">Collection principles for this tool</p>
      </div>
      <ul className="ethics-list">
        <li>Uses permitted public YouTube API signals only</li>
        <li>Does not collect private, gated, or members-only content</li>
        <li>Preserves source links for evidence and attribution</li>
        <li>Stores unavailable metrics as null instead of guessing</li>
        <li>Live YouTube pipeline is not connected yet — demo data only</li>
      </ul>
    </section>
  );
}
