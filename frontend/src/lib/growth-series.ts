import type { TrendSummary } from "@/lib/types";

export interface GrowthSeriesPoint {
  day: string;
  growth7d: number;
  growth24h: number;
}

const DAYS = 7;

/**
 * We only store a single 7-day and 24-hour growth figure per trend, not a
 * real daily time series. This synthesizes a smooth demo curve that lands
 * on those two known endpoints so the chart has something to plot.
 */
export function buildGrowthChartData(trend: TrendSummary): GrowthSeriesPoint[] {
  const finalGrowth7d = trend.growth_7d ?? 0;
  const finalGrowth24h = trend.growth_24h ?? 0;

  return Array.from({ length: DAYS }, (_, index) => {
    const fraction = (index + 1) / DAYS;
    return {
      day: `Day ${index + 1}`,
      growth7d: Math.round(finalGrowth7d * fraction * 10) / 10,
      growth24h: Math.round(finalGrowth24h * (0.6 + 0.4 * fraction) * 10) / 10,
    };
  });
}
