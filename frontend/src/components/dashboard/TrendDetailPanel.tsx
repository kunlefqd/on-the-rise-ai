import type { TrendDetail, TrendSummary } from "@/lib/types";

interface TrendDetailPanelProps {
  trend: TrendSummary | null;
  detail: TrendDetail | null;
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

export function TrendDetailPanel({ trend, detail }: TrendDetailPanelProps) {
  if (!trend) {
    return (
      <section className="panel detail-panel">
        <div className="panel__header">
          <h2 className="panel__title">Trend detail</h2>
          <p className="panel__subtitle">Select a trend in the table</p>
        </div>
        <p className="detail-panel__empty">
          Choose a row to inspect why the signal is rising and which videos
          support it.
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

      {detail ? (
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
            <h3>Supporting video evidence</h3>
            <ul className="evidence-list">
              {detail.supporting_videos.map((video) => (
                <li key={video.video_url} className="evidence-item">
                  <a
                    href={video.video_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="evidence-item__title"
                  >
                    {video.title}
                  </a>
                  <p className="evidence-item__meta">
                    {video.channel_title} · {formatDate(video.published_at)} ·{" "}
                    {formatCount(video.view_count)} views ·{" "}
                    {formatCount(video.like_count)} likes ·{" "}
                    {formatCount(video.comment_count)} comments
                  </p>
                  <p className="evidence-item__reason">{video.evidence_reason}</p>
                </li>
              ))}
            </ul>
          </div>
        </>
      ) : (
        <p className="detail-panel__empty">
          No detail mock record found for this trend.
        </p>
      )}
    </section>
  );
}
