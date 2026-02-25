'use client';

import React from 'react';
import { Property } from '@/types';
import PropertyCard from './PropertyCard';
import { PropertyListSkeleton } from '@/components/ui/Loading';

interface PropertyListProps {
  properties: Property[];
  isLoading?: boolean;
  opportunityScores?: Record<string, number>;
  showScores?: boolean;
  emptyMessage?: string;
  favoriteIds?: string[];
  onFavoriteToggle?: (id: string) => void;
}

export default function PropertyList({
  properties,
  isLoading = false,
  opportunityScores = {},
  showScores = false,
  emptyMessage = 'No properties found.',
  favoriteIds = [],
  onFavoriteToggle,
}: PropertyListProps) {
  if (isLoading) {
    return <PropertyListSkeleton count={6} />;
  }
  
  if (properties.length === 0) {
    return (
      <div className="text-center py-16">
        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg
            className="w-8 h-8 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
            />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">{emptyMessage}</h3>
        <p className="text-gray-500">Try adjusting your filters to see more results.</p>
      </div>
    );
  }
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {properties.map((property) => (
        <PropertyCard
          key={property.id}
          property={property}
          opportunityScore={opportunityScores[property.id]}
          showScore={showScores}
          isFavorite={favoriteIds.includes(property.id)}
          onFavoriteToggle={onFavoriteToggle}
        />
      ))}
    </div>
  );
}
