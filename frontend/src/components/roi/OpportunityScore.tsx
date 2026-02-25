'use client';

import React from 'react';
import { getScoreColor, getScoreLabel } from '@/lib/utils';
import { Card, CardHeader } from '@/components/ui/Card';
import { TrendingUp, TrendingDown, AlertCircle, CheckCircle, Info } from 'lucide-react';

interface OpportunityScoreProps {
  score: number;
  showDetails?: boolean;
}

interface ScoreFactor {
  name: string;
  score: number;
  maxScore: number;
  description: string;
}

// Mock score factors - in real app, these would come from the API
const getScoreFactors = (totalScore: number): ScoreFactor[] => [
  {
    name: 'Price vs Market',
    score: Math.min(totalScore + 5, 100),
    maxScore: 25,
    description: 'How the property price compares to market average',
  },
  {
    name: 'Rental Yield',
    score: Math.min(totalScore + 3, 100),
    maxScore: 25,
    description: 'Expected return from rental income',
  },
  {
    name: 'Location Demand',
    score: Math.min(totalScore - 2, 100),
    maxScore: 25,
    description: 'Demand for rentals in this area',
  },
  {
    name: 'Growth Potential',
    score: Math.min(totalScore, 100),
    maxScore: 25,
    description: 'Expected property value appreciation',
  },
];

export default function OpportunityScore({ score, showDetails = true }: OpportunityScoreProps) {
  const colorClass = getScoreColor(score);
  const label = getScoreLabel(score);
  const factors = getScoreFactors(score);
  
  // Calculate stroke dasharray for circular progress
  const circumference = 2 * Math.PI * 45; // radius = 45
  const strokeDasharray = circumference;
  const strokeDashoffset = circumference - (score / 100) * circumference;
  
  return (
    <Card>
      <CardHeader
        title="Opportunity Score"
        subtitle="Overall investment attractiveness rating"
      />
      
      <div className="flex flex-col items-center py-6">
        {/* Circular Score Display */}
        <div className="relative w-40 h-40">
          {/* Background circle */}
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="80"
              cy="80"
              r="45"
              fill="none"
              stroke="#e5e7eb"
              strokeWidth="10"
            />
            {/* Progress circle */}
            <circle
              cx="80"
              cy="80"
              r="45"
              fill="none"
              stroke="currentColor"
              strokeWidth="10"
              strokeLinecap="round"
              strokeDasharray={strokeDasharray}
              strokeDashoffset={strokeDashoffset}
              className={`${colorClass} transition-all duration-1000 ease-out`}
            />
          </svg>
          
          {/* Score text */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-4xl font-bold text-gray-900">{score}</span>
            <span className="text-sm text-gray-500">/ 100</span>
          </div>
        </div>
        
        {/* Score Label */}
        <div className="mt-4 text-center">
          <span className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium ${colorClass.replace('bg-', 'bg-opacity-10 bg-')} ${colorClass.replace('bg-', 'text-')}`}>
            {score >= 70 ? <TrendingUp className="w-4 h-4" /> : score >= 50 ? <Info className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
            {label}
          </span>
        </div>
        
        {/* Score Interpretation */}
        <div className="mt-6 text-center max-w-sm">
          <p className="text-sm text-gray-600">
            {getScoreInterpretation(score)}
          </p>
        </div>
      </div>
      
      {/* Score Factors */}
      {showDetails && (
        <div className="border-t border-gray-100 pt-6">
          <h4 className="font-medium text-gray-900 mb-4">Score Breakdown</h4>
          <div className="space-y-4">
            {factors.map((factor) => (
              <ScoreFactorBar key={factor.name} factor={factor} />
            ))}
          </div>
        </div>
      )}
    </Card>
  );
}

function ScoreFactorBar({ factor }: { factor: ScoreFactor }) {
  const percentage = (factor.score / factor.maxScore) * 100;
  
  return (
    <div>
      <div className="flex justify-between items-center mb-1">
        <span className="text-sm font-medium text-gray-700">{factor.name}</span>
        <span className="text-sm text-gray-500">
          {factor.score}/{factor.maxScore}
        </span>
      </div>
      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${
            percentage >= 80
              ? 'bg-success-500'
              : percentage >= 60
              ? 'bg-primary-500'
              : percentage >= 40
              ? 'bg-warning-500'
              : 'bg-danger-500'
          }`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <p className="text-xs text-gray-500 mt-1">{factor.description}</p>
    </div>
  );
}

function getScoreInterpretation(score: number): string {
  if (score >= 85) {
    return 'Excellent investment opportunity! This property shows strong potential for high returns with favorable market conditions.';
  }
  if (score >= 70) {
    return 'Good investment opportunity. This property offers solid returns and is worth serious consideration.';
  }
  if (score >= 55) {
    return 'Fair opportunity. While not exceptional, this property may still provide reasonable returns.';
  }
  if (score >= 40) {
    return 'Below average opportunity. Consider negotiating a better price or looking at alternative properties.';
  }
  return 'This property may not be a good investment at the current price. We recommend exploring other options.';
}
