'use client';

import React from 'react';
import { MarketStats as MarketStatsType } from '@/types';
import { formatCurrency, formatLocation, formatPercent } from '@/lib/utils';
import { Card, CardHeader } from '@/components/ui/Card';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';
import { TrendingUp, TrendingDown, Home, DollarSign, BarChart3, MapPin } from 'lucide-react';

interface MarketStatsProps {
  stats: MarketStatsType;
}

export default function MarketStats({ stats }: MarketStatsProps) {
  // Prepare location data for chart
  const locationData = stats.location_stats.map((loc) => ({
    name: formatLocation(loc.location),
    avgPrice: loc.avg_price,
    avgPricePerSqm: loc.avg_price_per_sqm,
    yield: loc.avg_rental_yield,
    count: loc.property_count,
  }));
  
  // Prepare trend data
  const trendData = stats.price_trends.map((trend) => ({
    month: new Date(trend.month).toLocaleDateString('en-MT', { month: 'short', year: '2-digit' }),
    avgPrice: trend.avg_price,
    transactions: trend.transaction_count,
  }));
  
  return (
    <div className="space-y-8">
      {/* Overview Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Total Properties"
          value={stats.total_properties.toLocaleString()}
          icon={Home}
          trend="+5.2%"
          trendUp={true}
        />
        <StatCard
          label="Average Price"
          value={formatCurrency(stats.avg_price)}
          icon={DollarSign}
          trend="+3.8%"
          trendUp={true}
        />
        <StatCard
          label="Price per m²"
          value={`€${stats.avg_price_per_sqm.toLocaleString()}`}
          icon={BarChart3}
          trend="+2.1%"
          trendUp={true}
        />
        <StatCard
          label="Avg Rental Yield"
          value={formatPercent(stats.avg_rental_yield)}
          icon={TrendingUp}
          trend="-0.3%"
          trendUp={false}
        />
      </div>
      
      {/* Price Trends Chart */}
      <Card>
        <CardHeader
          title="Price Trends"
          subtitle="Average property prices over the last 12 months"
        />
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trendData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="month"
                tick={{ fill: '#6b7280', fontSize: 12 }}
                tickLine={{ stroke: '#e5e7eb' }}
              />
              <YAxis
                tick={{ fill: '#6b7280', fontSize: 12 }}
                tickLine={{ stroke: '#e5e7eb' }}
                tickFormatter={(value) => `€${(value / 1000).toFixed(0)}k`}
              />
              <Tooltip
                formatter={(value: number) => formatCurrency(value)}
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                }}
              />
              <Line
                type="monotone"
                dataKey="avgPrice"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={{ fill: '#3b82f6', strokeWidth: 2 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>
      
      {/* Location Comparison */}
      <Card>
        <CardHeader
          title="Prices by Location"
          subtitle="Average property prices across different locations"
        />
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={locationData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="name"
                tick={{ fill: '#6b7280', fontSize: 11 }}
                tickLine={{ stroke: '#e5e7eb' }}
                interval={0}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis
                tick={{ fill: '#6b7280', fontSize: 12 }}
                tickLine={{ stroke: '#e5e7eb' }}
                tickFormatter={(value) => `€${(value / 1000).toFixed(0)}k`}
              />
              <Tooltip
                formatter={(value: number) => formatCurrency(value)}
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                }}
              />
              <Bar
                dataKey="avgPrice"
                fill="#3b82f6"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
      
      {/* Location Details Table */}
      <Card>
        <CardHeader
          title="Location Statistics"
          subtitle="Detailed breakdown by location"
        />
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-100">
                <th className="text-left py-3 px-4 font-medium text-gray-700">Location</th>
                <th className="text-right py-3 px-4 font-medium text-gray-700">Properties</th>
                <th className="text-right py-3 px-4 font-medium text-gray-700">Avg Price</th>
                <th className="text-right py-3 px-4 font-medium text-gray-700">Price/m²</th>
                <th className="text-right py-3 px-4 font-medium text-gray-700">Rental Yield</th>
                <th className="text-right py-3 px-4 font-medium text-gray-700">YoY Change</th>
              </tr>
            </thead>
            <tbody>
              {stats.location_stats.map((loc) => (
                <tr key={loc.location} className="border-b border-gray-50 hover:bg-gray-50">
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-gray-400" />
                      <span className="font-medium text-gray-900">
                        {formatLocation(loc.location)}
                      </span>
                    </div>
                  </td>
                  <td className="text-right py-3 px-4 text-gray-600">
                    {loc.property_count.toLocaleString()}
                  </td>
                  <td className="text-right py-3 px-4 font-medium text-gray-900">
                    {formatCurrency(loc.avg_price)}
                  </td>
                  <td className="text-right py-3 px-4 text-gray-600">
                    €{loc.avg_price_per_sqm.toLocaleString()}
                  </td>
                  <td className="text-right py-3 px-4">
                    <span className={`inline-flex items-center gap-1 ${
                      loc.avg_rental_yield >= 5
                        ? 'text-success-600'
                        : loc.avg_rental_yield >= 3.5
                        ? 'text-primary-600'
                        : 'text-warning-600'
                    }`}>
                      {formatPercent(loc.avg_rental_yield)}
                    </span>
                  </td>
                  <td className="text-right py-3 px-4">
                    <span className={`inline-flex items-center gap-1 ${
                      loc.price_change_percent >= 0 ? 'text-success-600' : 'text-danger-600'
                    }`}>
                      {loc.price_change_percent >= 0 ? (
                        <TrendingUp className="w-4 h-4" />
                      ) : (
                        <TrendingDown className="w-4 h-4" />
                      )}
                      {loc.price_change_percent >= 0 ? '+' : ''}
                      {loc.price_change_percent.toFixed(1)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

function StatCard({
  label,
  value,
  icon: Icon,
  trend,
  trendUp,
}: {
  label: string;
  value: string;
  icon: React.ElementType;
  trend: string;
  trendUp: boolean;
}) {
  return (
    <Card padding="sm">
      <div className="flex items-start justify-between">
        <div className="p-2 bg-primary-50 rounded-lg">
          <Icon className="w-5 h-5 text-primary-600" />
        </div>
        <span className={`text-sm font-medium ${trendUp ? 'text-success-600' : 'text-danger-600'}`}>
          {trend}
        </span>
      </div>
      <div className="mt-3">
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        <p className="text-sm text-gray-600">{label}</p>
      </div>
    </Card>
  );
}
