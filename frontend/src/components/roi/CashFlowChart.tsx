'use client';

import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts';
import { ROIAnalysis } from '@/types';
import { formatCurrency } from '@/lib/utils';
import { Card, CardHeader } from '@/components/ui/Card';

interface CashFlowChartProps {
  analysis: ROIAnalysis;
}

interface ChartData {
  year: number;
  rentalIncome: number;
  expenses: number;
  netIncome: number;
  cumulativeReturn: number;
}

export default function CashFlowChart({ analysis }: CashFlowChartProps) {
  const data: ChartData[] = analysis.cash_flow_projections.map((projection) => ({
    year: projection.year,
    rentalIncome: projection.rental_income,
    expenses: projection.expenses,
    netIncome: projection.net_income,
    cumulativeReturn: projection.cumulative_return,
  }));
  
  const CustomTooltip = ({ active, payload, label }: {
    active?: boolean;
    payload?: Array<{ color: string; name: string; value: number }>;
    label?: number;
  }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-4 rounded-lg shadow-lg border border-gray-100">
          <p className="font-semibold text-gray-900 mb-2">Year {label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {formatCurrency(entry.value)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };
  
  return (
    <Card>
      <CardHeader
        title="10-Year Cash Flow Projection"
        subtitle="Estimated rental income, expenses, and cumulative returns"
      />
      
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorRental" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.1}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorNet" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#22c55e" stopOpacity={0.1}/>
                <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorCumulative" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.1}/>
                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="year"
              tick={{ fill: '#6b7280', fontSize: 12 }}
              tickLine={{ stroke: '#e5e7eb' }}
              axisLine={{ stroke: '#e5e7eb' }}
            />
            <YAxis
              tick={{ fill: '#6b7280', fontSize: 12 }}
              tickLine={{ stroke: '#e5e7eb' }}
              axisLine={{ stroke: '#e5e7eb' }}
              tickFormatter={(value) => `€${(value / 1000).toFixed(0)}k`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ paddingTop: '20px' }}
              iconType="circle"
            />
            <Area
              type="monotone"
              dataKey="rentalIncome"
              name="Rental Income"
              stroke="#3b82f6"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorRental)"
            />
            <Area
              type="monotone"
              dataKey="expenses"
              name="Expenses"
              stroke="#ef4444"
              strokeWidth={2}
              fillOpacity={0}
              fill="transparent"
            />
            <Area
              type="monotone"
              dataKey="netIncome"
              name="Net Income"
              stroke="#22c55e"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorNet)"
            />
            <Line
              type="monotone"
              dataKey="cumulativeReturn"
              name="Cumulative Return"
              stroke="#8b5cf6"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      
      {/* Summary Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6 pt-6 border-t border-gray-100">
        <SummaryStat
          label="Total Rental Income (10yr)"
          value={formatCurrency(data.reduce((sum, d) => sum + d.rentalIncome, 0))}
          color="text-blue-600"
        />
        <SummaryStat
          label="Total Expenses (10yr)"
          value={formatCurrency(data.reduce((sum, d) => sum + d.expenses, 0))}
          color="text-red-600"
        />
        <SummaryStat
          label="Total Net Income (10yr)"
          value={formatCurrency(data.reduce((sum, d) => sum + d.netIncome, 0))}
          color="text-green-600"
        />
        <SummaryStat
          label="Final Cumulative Return"
          value={formatCurrency(data[data.length - 1]?.cumulativeReturn || 0)}
          color="text-purple-600"
        />
      </div>
    </Card>
  );
}

function SummaryStat({
  label,
  value,
  color,
}: {
  label: string;
  value: string;
  color: string;
}) {
  return (
    <div className="text-center">
      <p className={`text-lg font-bold ${color}`}>{value}</p>
      <p className="text-xs text-gray-600 mt-1">{label}</p>
    </div>
  );
}
