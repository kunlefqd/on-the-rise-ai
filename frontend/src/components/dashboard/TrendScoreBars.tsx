"use client";

import type { TrendSummary } from "@/lib/types";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface TrendScoreBarsProps {
  trends: TrendSummary[];
}

export function TrendScoreBars({ trends }: TrendScoreBarsProps) {
  const data = [...trends]
    .sort((a, b) => b.trend_score - a.trend_score)
    .slice(0, 6)
    .map((trend) => ({
      name: trend.trend_name,
      score: trend.trend_score,
    }));

  return (
    <section className="panel">
      <div className="panel__header">
        <h2 className="panel__title">Top trend scores</h2>
        <p className="panel__subtitle">Relative strength of leading signals</p>
      </div>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={240}>
          <BarChart
            data={data}
            margin={{ top: 8, right: 8, left: -12, bottom: 48 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#e3eaef"
              vertical={false}
            />
            <XAxis
              dataKey="name"
              tick={{ fontSize: 11, fill: "#5a6573" }}
              angle={-35}
              textAnchor="end"
              height={56}
              interval={0}
            />
            <YAxis tick={{ fontSize: 11, fill: "#5a6573" }} />
            <Tooltip
              contentStyle={{
                borderRadius: 8,
                border: "1px solid #d4dde3",
                fontSize: 12,
              }}
              formatter={(value) => [value, "Trend score"]}
            />
            <Bar
              dataKey="score"
              fill="#2f8f68"
              radius={[4, 4, 0, 0]}
              name="Trend score"
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
