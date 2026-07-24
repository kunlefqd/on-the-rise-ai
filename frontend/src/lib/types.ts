/**
 * YouTube-only trend summary shape for the dashboard MVP.
 *
 * NOTE: contracts/trend-summary.schema.json still uses older generic fields
 * (source_count, supporting_item_count, region). This UI implements the
 * agreed YouTube-focused mock shape below until the shared contract is updated.
 */

export type TrendCategory =
  | "format"
  | "flavour"
  | "ingredient"
  | "consumer_attribute";

export type ConfidenceLevel = "low" | "medium" | "high";

export interface TrendSummary {
  trend_name: string;
  category: TrendCategory;
  trend_score: number;
  growth_24h: number | null;
  growth_7d: number | null;
  confidence: ConfidenceLevel;
  confidence_score: number;
  supporting_video_count: number;
  query_region_code: string;
  last_updated: string;
}

export interface SupportingVideo {
  title: string;
  channel_title: string;
  video_url: string;
  published_at: string;
  view_count: number | null;
  like_count: number | null;
  comment_count: number | null;
  evidence_reason: string;
}

export interface TrendDetail {
  trend_name: string;
  summary: string;
  suggested_rd_opportunity: string;
  supporting_videos: SupportingVideo[];
}
