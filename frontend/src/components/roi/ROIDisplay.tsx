'use client';

import React from 'react';
import { ROIAnalysis } from '@/types';
import { formatCurrency, formatPercent } from '@/lib/utils';
import { Card, CardHeader } from '@/components/ui/ui/Card';
import Badge from '@/components/ui/Badge';
import { TrendingUp, TrendingDown, Minus, DollarSign, Percent, Home, Wallet } from 'lucide-react';

interface ROIDisplayProps {
  analysis: ROIAnalysis;
}

export default function ROIDisplay({ analysis }: ROIDisplayProps) {
  const metrics = [
    {
      label: 'Gross Rental Yield',
      value: formatPercent(analysis.gross_rental_yield),
      icon: Percent,
      description: 'Annual rent / Purchase price',
      trend: analysis.gross_rental_yield > 5 ? 'up' : analysis.gross_rental_yield < 3 ? 'down' : 'neutral',
    },
    {
      label: 'Net Rental Yield',
      value: formatPercent(analysis.net_rental_yield),
      icon: Percent,
      description: 'After expenses',
      trend: analysis.net_rental_yield > 4 ? 'up' : analysis.net_rental_yield < 2 ? 'down' : 'neutral',
    },
    {
      label: 'Cap Rate',
      value: formatPercent(analysis.cap_rate),
      icon: Home,
      description: 'Net operating income / Property value',
      trend: analysis.cap_rate > 5 ? 'up' : analysis.cap_rate < 3 ? 'down' : 'neutral',
    },
    {
      label: 'Cash on Cash Return',
      value: formatPercent(analysis.cash_on_cash_return),
      icon: DollarSign,
      description: 'Annual cash flow / Cash invested',
      trend: analysis.cash_on_cash_return > 8 ? 'up' : analysis.cash_on_cash_return < 4 ? 'down' : 'neutral',
    },
  ];
  
  const incomeMetrics = [
    {
      label: 'Estimated Monthly Rent',
      value: formatCurrency(analysis.estimated_monthly_rent),
    },
    {
      label: 'Estimated Annual Rent',
      value: formatCurrency(analysis.estimated_annual_rent),
    },
    {
      label: 'Price per m²',
      value: `€${analysis.price_per_sqm.toLocaleString()}`,
    },
    {
      label: 'Rent per m²',
      value: `€${analysis.rent_per_sqm.toFixed(2)}`,
    },
  ];
  
  return (
    <div className="space-y-6">
      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((metric) => {
          const Icon = metric.icon;
          const TrendIcon = metric.trend === 'up' ? TrendingUp : metric.trend === 'down' ? TrendingDown : Minus;
          const trendColor = metric.trend === 'up' ? 'text-success-600' : metric.trend === 'down' ? 'text-danger-600' : 'text-gray-400';
          
          return (
            <Card key={metric.label} padding="sm">
              <div className="flex items-start justify-between">
                <div className="p-2 bg-primary-50 rounded-lg">
                  <Icon className="w-5 h-5 text-primary-600" />
                </div>
                <TrendIcon className={`w-4 h-4 ${trendColor}`} />
              </div>
              <div className="mt-3">
                <p className="text-2xl font-bold text-gray-900">{metric.value}</p>
                <p className="text-sm text-gray-600">{metric.label}</p>
                <p className="text-xs text-gray-400 mt-1">{metric.description}</p>
              </div>
            </Card>
          );
        })}
      </div>
      
      {/* Income Details */}
      <Card>
        <CardHeader title="Rental Income Details" />
        <div className="grid grid-cols-2 gap-4">
          {incomeMetrics.map((metric) => (
            <div key={metric.label} className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">{metric.label}</p>
              <p className="text-xl font-semibold text-gray-900">{metric.value}</p>
            </div>
          ))}
        </div>
      </Card>
      
      {/* Market Comparison */}
      <Card>
        <CardHeader title="Market Comparison" />
        <div className="space-y-4">
          <ComparisonRow
            label="Price per m²"
            propertyValue={analysis.price_per_sqm}
            marketValue={analysis.market_comparison.avg_price_per_sqm}
            isCurrency
          />
          <ComparisonRow
            label="Rent per m²"
            propertyValue={analysis.rent_per_sqm}
            marketValue={analysis.market_comparison.avg_rent_per_sqm}
            isCurrency
          />
        </div>
      </Card>
      
      {/* Assumptions Summary */}
      <Card>
        <CardHeader title="Calculation Assumptions" />
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-sm">
          <AssumptionItem
            label="Down Payment"
            value={`${analysis.assumptions.down_payment_percent}%`}
          />
          <AssumptionItem
            label="Interest Rate"
            value={`${analysis.assumptions.interest_rate}%`}
          />
          <AssumptionItem
            label="Loan Term"
            value={`${analysis.assumptions.loan_term_years} years`}
          />
          <AssumptionItem
            label="Vacancy Rate"
            value={`${analysis.assumptions.vacancy_rate}%`}
          />
          <AssumptionItem
            label="Maintenance"
            value={`${analysis.assumptions.maintenance_percent}%`}
          />
          <AssumptionItem
            label="Property Management"
            value={`${analysis.assumptions.property_management_percent}%`}
          />
        </div>
      </Card>
    </div>
  );
}

function ComparisonRow({
  label,
  propertyValue,
  marketValue,
  isCurrency = false,
}: {
  label: string;
  propertyValue: number;
  marketValue: number;
  isCurrency?: boolean;
}) {
  const difference = ((propertyValue - marketValue) / marketValue) * 100;
  const isBetter = difference < 0; // Lower price is better
  const isHigher = difference > 0;
  
  const formatValue = (value: number) => {
    if (isCurrency) return `€${value.toLocaleString()}`;
    return `€${value.toFixed(2)}`;
  };
  
  return (
    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
      <div>
        <p className="font-medium text-gray-900">{label}</p>
        <div className="flex items-center gap-4 mt-1 text-sm">
          <span className="text-gray-600">
            Property: <span className="font-medium text-gray-900">{formatValue(propertyValue)}</span>
          </span>
          <span className="text-gray-400">|</span>
          <span className="text-gray-600">
            Market Avg: <span className="font-medium text-gray-900">{formatValue(marketValue)}</span>
          </span>
        </div>
      </div>
      <Badge
        variant={isBetter ? 'success' : isHigher ? 'danger' : 'default'}
        className="flex items-center gap-1"
      >
        {difference > 0 ? '+' : ''}
        {difference.toFixed(1)}%
      </Badge>
    </div>
  );
}

function AssumptionItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="p-3 bg-gray-50 rounded-lg">
      <p className="text-gray-600">{label}</p>
      <p className="font-medium text-gray-900">{value}</p>
    </div>
  );
}
