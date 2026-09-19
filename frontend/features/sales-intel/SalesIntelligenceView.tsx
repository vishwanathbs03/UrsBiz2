"use client";

import React from "react";
import {
  TrendingUp,
  TrendingDown,
  Users,
  Package,
  AlertTriangle,
  CheckCircle2,
  ArrowRight,
  Sparkles
} from "lucide-react";
import { DashboardCard } from "@/components/dashboard/DashboardCard";
import { ExecutiveInsightCard } from "@/components/dashboard/ExecutiveShared";
import { LineChart } from "@/components/dashboard/LineChart";
import { ProgressBar } from "@/components/dashboard/ProgressBar";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface SalesIntelData {
  dataset_health: {
    total_rows: number;
    valid_rows: number;
    missing_values: any;
    health_score: number;
  };
  customer_patterns: {
    new: number;
    repeat: number;
    high_value: number;
    at_risk: number;
  };
  top_customers: Array<{ name: string; revenue: number; rank: number }>;
  product_intelligence: Array<{
    product: string;
    category: string;
    volume_delta: number;
  }>;
  top_products: Array<{ product: string; revenue: number; volume: number }>;
  demand_forecast: Array<{
    period: string;
    baseline: number;
    upper_bound: number;
    lower_bound: number;
  }>;
  production_gap: {
    required: number;
    available: number;
    gap: number;
    status: string;
  } | null;
  forecast_confidence: string;
  confidence_explanation: string;
}

export function SalesIntelligenceView({
  data,
  onExplain
}: {
  data: SalesIntelData;
  onExplain: () => void
}) {
  return (
    <div className="flex flex-col gap-6 py-6 animate-page-fade">
      {/* Dataset Health */}
      <DashboardCard
        title="Dataset Health"
        caption={`Analyzed ${data.dataset_health.total_rows} transactions. Usable: ${data.dataset_health.valid_rows}`}
      >
        <div className="flex flex-col gap-4 py-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Data Quality Score</span>
            <span className="font-mono font-semibold">{Math.round(data.dataset_health.health_score)}%</span>
          </div>
          <ProgressBar value={data.dataset_health.health_score} />
          <div className="grid grid-cols-2 gap-4 text-xs text-muted-foreground mt-2">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="size-3 text-emerald-500" />
              <span>Valid rows: {data.dataset_health.valid_rows}</span>
            </div>
            <div className="flex items-center gap-2">
              <AlertTriangle className="size-3 text-amber-500" />
              <span>Missing values detected</span>
            </div>
          </div>
        </div>
      </DashboardCard>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Customer Patterns */}
        <ExecutiveInsightCard
          badge="Customer Insights"
          title="Buying Patterns"
          caption="Deterministic segmentation based on purchase frequency and value."
        >
          <div className="grid grid-cols-2 gap-3">
            <PatternCell icon={Users} label="Repeat" value={data.customer_patterns.repeat} color="text-primary" />
            <PatternCell icon={Sparkles} label="High Value" value={data.customer_patterns.high_value} color="text-amber-600" />
            <PatternCell icon={CheckCircle2} label="New" value={data.customer_patterns.new} color="text-emerald-600" />
            <PatternCell icon={AlertTriangle} label="At Risk" value={data.customer_patterns.at_risk} color="text-rose-600" />
          </div>
          <div className="mt-4 space-y-2">
            <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Top Customers</p>
            {data.top_customers.map((c) => (
              <div key={c.rank} className="flex items-center justify-between p-2 rounded-md bg-background/50 border border-border text-sm">
                <span className="flex items-center gap-2">
                  <span className="font-mono text-xs text-muted-foreground">#{c.rank}</span>
                  {c.name}
                </span>
                <span className="font-mono font-medium">${c.revenue.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </ExecutiveInsightCard>

        {/* Product Intelligence */}
        <ExecutiveInsightCard
          badge="Product Insights"
          title="Product Performance"
          caption="Growth trends and volume classification."
        >
          <div className="space-y-3">
            {data.product_intelligence.slice(0, 5).map((p, i) => (
              <div key={i} className="flex items-center justify-between p-2 rounded-md bg-background/50 border border-border text-sm">
                <div className="flex items-center gap-2">
                  {p.category === "Growing" ? <TrendingUp className="size-4 text-emerald-500" /> :
                   p.category === "Declining" ? <TrendingDown className="size-4 text-rose-500" /> :
                   <Package className="size-4 text-muted-foreground" />}
                  <span className="font-medium">{p.product}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className={cn(
                    "text-[10px] px-1.5 py-0.5 rounded-full font-semibold uppercase",
                    p.category === "Growing" && "bg-emerald-100 text-emerald-700",
                    p.category === "Declining" && "bg-rose-100 text-rose-700",
                    p.category === "Fast Moving" && "bg-primary/10 text-primary",
                    p.category === "Stable" && "bg-muted-foreground/10 text-muted-foreground"
                  )}>
                    {p.category}
                  </span>
                  <span className="font-mono text-xs">{Math.round(p.volume_delta * 100)}%</span>
                </div>
              </div>
            ))}
          </div>
        </ExecutiveInsightCard>
      </div>

      {/* Demand Forecast */}
      <ExecutiveInsightCard
        badge="Demand Forecast"
        title="Baseline Demand Prediction"
        caption={`Expected demand based on ${data.forecast_confidence} confidence. ${data.confidence_explanation}`}
      >
        <div className="flex flex-col gap-6">
          <LineChart
            labels={data.demand_forecast.map(f => f.period)}
            series={[
              { label: "Baseline", color: "hsl(var(--primary))", values: data.demand_forecast.map(f => f.baseline) },
              { label: "Upper Bound", color: "#10b981", values: data.demand_forecast.map(f => f.upper_bound) },
              { label: "Lower Bound", color: "#f43f5e", values: data.demand_forecast.map(f => f.lower_bound) },
            ]}
            size={{ width: 800, height: 300 }}
          />

          {data.production_gap && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 rounded-2xl bg-primary/5 border border-primary/20">
              <div className="flex flex-col">
                <span className="text-xs text-muted-foreground uppercase tracking-wider">Expected Demand</span>
                <span className="text-lg font-mono font-semibold">{Math.round(data.production_gap.required)} units</span>
              </div>
              <div className="flex flex-col">
                <span className="text-xs text-muted-foreground uppercase tracking-wider">Current Inventory</span>
                <span className="text-lg font-mono font-semibold">{Math.round(data.production_gap.available)} units</span>
              </div>
              <div className="flex flex-col">
                <span className="text-xs text-muted-foreground uppercase tracking-wider">Potential Gap</span>
                <span className={cn(
                  "text-lg font-mono font-bold",
                  data.production_gap.status === "Shortage" ? "text-rose-600" : "text-emerald-600"
                )}>
                  {Math.round(data.production_gap.gap)} units
                </span>
              </div>
            </div>
          )}
        </div>
      </ExecutiveInsightCard>

      {/* Business Action */}
      <div className="flex justify-center pt-4">
        <Button
          onClick={onExplain}
          className="gap-2 rounded-full px-8 py-6 text-lg"
          variant="default"
        >
          <Sparkles className="size-5" />
          Explain these results with AI
          <ArrowRight className="size-5" />
        </Button>
      </div>
    </div>
  );
}

function PatternCell({ icon: Icon, label, value, color }: { icon: any, label: string, value: number, color: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-4 rounded-xl border border-border bg-background/50">
      <Icon className={cn("size-5 mb-2", color)} />
      <span className="text-xs text-muted-foreground uppercase tracking-wider">{label}</span>
      <span className="text-xl font-mono font-bold">{value}</span>
    </div>
  );
}
