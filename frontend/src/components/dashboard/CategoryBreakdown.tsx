"use client";

import type { TrendCategory, TrendSummary } from "@/lib/types";
import {
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

interface CategoryBreakdownProps {
  trends: TrendSummary[];
}

const CATEGORY_ORDER: TrendCategory[] = [
  "flavour",
  "ingredient",
  "format",
  "consumer_attribute",
];

const CATEGORY_COLORS: Record<TrendCategory, string> = {
  flavour: "#2f8f68",
  ingredient: "#3f6a8f",
  format: "#b86a1a",
  consumer_attribute: "#5a6573",
};

function label(category: TrendCategory): string {
  return category.replaceAll("_", " ");
}

export function CategoryBreakdown({ trends }: CategoryBreakdownProps) {
  const data = CATEGORY_ORDER.map((category) => ({
    category,
    name: label(category),
    count: trends.filter((t) => t.category === category).length,
  })).filter((item) => item.count > 0);

  return (
    <section className="panel">
      <div className="panel__header">
        <h2 className="panel__title">Category breakdown</h2>
        <p className="panel__subtitle">How trends distribute by type</p>
      </div>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={240}>
          <PieChart>
            <Pie
              data={data}
              dataKey="count"
              nameKey="name"
              cx="50%"
              cy="50%"
              innerRadius={48}
              outerRadius={82}
              paddingAngle={2}
            >
              {data.map((item) => (
                <Cell
                  key={item.category}
                  fill={CATEGORY_COLORS[item.category]}
                />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                borderRadius: 8,
                border: "1px solid #d4dde3",
                fontSize: 12,
              }}
              formatter={(value) => [value, "Trends"]}
            />
            <Legend
              iconType="circle"
              iconSize={8}
              wrapperStyle={{ fontSize: 12, color: "#5a6573" }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
