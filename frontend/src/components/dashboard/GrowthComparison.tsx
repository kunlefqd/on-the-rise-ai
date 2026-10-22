"use client";

import { useMemo, useState } from "react";
import { buildGrowthChartData } from "@/lib/growth-series";
import type { TrendSummary } from "@/lib/types";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface GrowthComparisonProps {
  trends: TrendSummary[];
}

export function GrowthComparison({ trends }: GrowthComparisonProps) {
  const eligibleTrends = useMemo(
    () =>
      [...trends]
        .filter((t) => t.growth_7d !== null || t.growth_24h !== null)
        .sort((a, b) => b.trend_score - a.trend_score),
    [trends],
  );

  const [selectedTrend, setSelectedTrend] = useState(
    () => eligibleTrends[0]?.trend_name ?? "",
  );

  const activeTrend =
    eligibleTrends.find((t) => t.trend_name === selectedTrend) ??
    eligibleTrends[0] ??
    null;

  const chartData = activeTrend ? buildGrowthChartData(activeTrend) : [];

  if (eligibleTrends.length === 0) {
    return (
      <section className="panel">
        <div className="panel__header">
          <h2 className="panel__title">Growth comparison</h2>
          <p className="panel__subtitle">No growth data available</p>
        </div>
      </section>
    );
  }

  return (
    <section className="panel">
      <div className="panel__header panel__header--split">
        <div>
          <h2 className="panel__title">Growth comparison</h2>
          <p className="panel__subtitle">
            7-day cumulative vs daily 24-hour change (demo)
          </p>
        </div>
        <label className="chart-select">
          <span className="chart-select__label">Trend</span>
          <select
            className="chart-select__control"
            value={activeTrend?.trend_name ?? ""}
            onChange={(event) => setSelectedTrend(event.target.value)}
          >
            {eligibleTrends.map((trend) => (
              <option key={trend.trend_name} value={trend.trend_name}>
                {trend.trend_name}
              </option>
            ))}
          </select>
        </label>
      </div>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={240}>
          <LineChart
            data={chartData}
            margin={{ top: 8, right: 8, left: -12, bottom: 8 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#e3eaef"
              vertical={false}
            />
            <XAxis
              dataKey="day"
              tick={{ fontSize: 11, fill: "#5a6573" }}
            />
            <YAxis
              tick={{ fontSize: 11, fill: "#5a6573" }}
              tickFormatter={(value) => `${value}%`}
            />
            <Tooltip
              contentStyle={{
                borderRadius: 8,
                border: "1px solid #d4dde3",
                fontSize: 12,
              }}
              formatter={(value, name) => [
                `${value}%`,
                name === "growth7d" ? "7-day cumulative" : "24-hour change",
              ]}
            />
            <Legend
              iconType="line"
              iconSize={12}
              wrapperStyle={{ fontSize: 12, color: "#5a6573" }}
              formatter={(value) =>
                value === "growth7d" ? "7-day cumulative" : "24-hour change"
              }
            />
            <Line
              type="monotone"
              dataKey="growth7d"
              stroke="#1f6b4a"
              strokeWidth={2}
              dot={{ r: 3, fill: "#1f6b4a" }}
              activeDot={{ r: 5 }}
            />
            <Line
              type="monotone"
              dataKey="growth24h"
              stroke="#b86a1a"
              strokeWidth={2}
              dot={{ r: 3, fill: "#b86a1a" }}
              activeDot={{ r: 5 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
