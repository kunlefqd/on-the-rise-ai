import type { TrendDetail, TrendSummary } from "@/lib/types";

interface TrendDetailPanelProps {
  trend: TrendSummary | null;
  detail: TrendDetail | null;
  loading?: boolean;
}

function formatCount(value: number | null): string {
  if (value === null) return "n/a";
  return value.toLocaleString("en-CA");
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-CA", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

const SOURCE_LABEL: Record<string, string> = {
  youtube: "YouTube",
  blog: "Blog",
  retailer: "Retailer",
};

export function TrendDetailPanel({
  trend,
  detail,
  loading = false,
}: TrendDetailPanelProps) {
  if (!trend) {
    return (
      <section className="panel detail-panel">
        <div className="panel__header">
          <h2 className="panel__title">Trend detail</h2>
          <p className="panel__subtitle">Select a trend in the table</p>
        </div>
        <p className="detail-panel__empty">
          Choose a row to inspect why the signal is rising and which
          videos or blog posts support it.
        </p>
      </section>
    );
  }

  return (
    <section className="panel detail-panel">
      <div className="panel__header">
        <h2 className="panel__title">{trend.trend_name}</h2>
        <p className="panel__subtitle">
          {trend.category.replaceAll("_", " ")} · score {trend.trend_score} ·{" "}
          {trend.confidence} confidence ({trend.confidence_score})
        </p>
      </div>

      {loading ? (
        <p className="detail-panel__empty">Loading detail…</p>
      ) : detail ? (
        <>
          <div className="detail-block">
            <h3>Why it is trending</h3>
            <p>{detail.summary}</p>
          </div>
          <div className="detail-block detail-block--opportunity">
            <h3>Suggested R&amp;D opportunity</h3>
            <p>{detail.suggested_rd_opportunity}</p>
          </div>
          <div className="detail-block">
            <h3>Supporting evidence</h3>
            <ul className="evidence-list">
              {detail.supporting_items.map((item) => (
                <li key={item.url} className="evidence-item">
                  <span className={`source-chip source-chip--${item.source}`}>
                    {SOURCE_LABEL[item.source] ?? item.source}
                  </span>
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="evidence-item__title"
                  >
                    {item.title}
                  </a>
                  <p className="evidence-item__meta">
                    {item.author} · {formatDate(item.published_at)} ·{" "}
                    {formatCount(item.view_count)} views ·{" "}
                    {formatCount(item.like_count)} likes ·{" "}
                    {formatCount(item.comment_count)} comments
                  </p>
                  <p className="evidence-item__reason">{item.evidence_reason}</p>
                </li>
              ))}
            </ul>
          </div>
        </>
      ) : (
        <p className="detail-panel__empty">
          No detail found for this trend.
        </p>
      )}
    </section>
  );
}
