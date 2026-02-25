'use client';

import React, { useState, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { PropertyFilter, SortOption, Location, PropertyType } from '@/types';
import { LOCATIONS, PROPERTY_TYPES, PRICE_RANGES, BEDROOM_OPTIONS, SORT_OPTIONS } from '@/lib/constants';
import { cn } from '@/lib/utils';
import Select from '@/components/ui/Select';
import Button from '@/components/ui/Button';
import { Filter, X, SlidersHorizontal } from 'lucide-react';

interface PropertyFiltersProps {
  onFilterChange?: (filters: PropertyFilter) => void;
  onSortChange?: (sort: SortOption) => void;
  className?: string;
}

export default function PropertyFilters({
  onFilterChange,
  onSortChange,
  className,
}: PropertyFiltersProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isExpanded, setIsExpanded] = useState(false);
  
  // Parse current filters from URL
  const currentFilters: PropertyFilter = {
    location: (searchParams.get('location') as Location) || undefined,
    property_type: (searchParams.get('property_type') as PropertyType) || undefined,
    min_price: searchParams.get('min_price') ? Number(searchParams.get('min_price')) : undefined,
    max_price: searchParams.get('max_price') ? Number(searchParams.get('max_price')) : undefined,
    min_bedrooms: searchParams.get('min_bedrooms') ? Number(searchParams.get('min_bedrooms')) : undefined,
    max_bedrooms: searchParams.get('max_bedrooms') ? Number(searchParams.get('max_bedrooms')) : undefined,
  };
  
  const currentSort = (searchParams.get('sort') as SortOption) || 'newest';
  
  // Count active filters
  const activeFilterCount = Object.values(currentFilters).filter(v => v !== undefined).length;
  
  const updateFilters = useCallback((newFilters: PropertyFilter) => {
    const params = new URLSearchParams(searchParams.toString());
    
    // Update or remove filter params
    Object.entries(newFilters).forEach(([key, value]) => {
      if (value !== undefined && value !== '') {
        params.set(key, String(value));
      } else {
        params.delete(key);
      }
    });
    
    // Reset to page 1 when filters change
    params.delete('page');
    
    router.push(`/properties?${params.toString()}`);
    onFilterChange?.(newFilters);
  }, [router, searchParams, onFilterChange]);
  
  const updateSort = useCallback((sort: SortOption) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set('sort', sort);
    router.push(`/properties?${params.toString()}`);
    onSortChange?.(sort);
  }, [router, searchParams, onSortChange]);
  
  const clearFilters = useCallback(() => {
    const params = new URLSearchParams();
    params.set('sort', currentSort);
    router.push(`/properties?${params.toString()}`);
    onFilterChange?.({});
  }, [router, currentSort, onFilterChange]);
  
  const locationOptions = [
    { value: '', label: 'All Locations' },
    ...Object.entries(LOCATIONS).map(([value, label]) => ({ value, label })),
  ];
  
  const typeOptions = [
    { value: '', label: 'All Types' },
    ...Object.entries(PROPERTY_TYPES).map(([value, label]) => ({ value, label })),
  ];
  
  const priceOptions = [
    { value: '', label: 'Any Price' },
    ...PRICE_RANGES.map((range, i) => ({
      value: `${range.min}-${range.max}`,
      label: range.label,
    })),
  ];
  
  const bedroomOptions = [
    { value: '', label: 'Any Bedrooms' },
    ...BEDROOM_OPTIONS.map((opt) => ({
      value: String(opt.value),
      label: opt.label,
    })),
  ];
  
  const handlePriceChange = (value: string) => {
    if (!value) {
      updateFilters({ ...currentFilters, min_price: undefined, max_price: undefined });
      return;
    }
    const [min, max] = value.split('-').map(v => (v === 'Infinity' ? undefined : Number(v)));
    updateFilters({ ...currentFilters, min_price: min, max_price: max });
  };
  
  const getCurrentPriceValue = () => {
    if (!currentFilters.min_price && !currentFilters.max_price) return '';
    const min = currentFilters.min_price || 0;
    const max = currentFilters.max_price || 'Infinity';
    return `${min}-${max}`;
  };
  
  return (
    <div className={cn('bg-white rounded-xl shadow-sm border border-gray-100', className)}>
      {/* Header - Always visible */}
      <div className="p-4 flex items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            leftIcon={<SlidersHorizontal className="w-4 h-4" />}
            onClick={() => setIsExpanded(!isExpanded)}
          >
            Filters
            {activeFilterCount > 0 && (
              <span className="ml-2 px-2 py-0.5 bg-primary-100 text-primary-700 text-xs rounded-full">
                {activeFilterCount}
              </span>
            )}
          </Button>
          
          {activeFilterCount > 0 && (
            <Button
              variant="ghost"
              size="sm"
              leftIcon={<X className="w-4 h-4" />}
              onClick={clearFilters}
            >
              Clear
            </Button>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500 hidden sm:inline">Sort by:</span>
          <Select
            value={currentSort}
            onChange={(e) => updateSort(e.target.value as SortOption)}
            options={SORT_OPTIONS}
            className="w-40"
          />
        </div>
      </div>
      
      {/* Expanded Filters */}
      {isExpanded && (
        <div className="border-t border-gray-100 p-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Select
              label="Location"
              value={currentFilters.location || ''}
              onChange={(e) =>
                updateFilters({
                  ...currentFilters,
                  location: (e.target.value as Location) || undefined,
                })
              }
              options={locationOptions}
            />
            
            <Select
              label="Property Type"
              value={currentFilters.property_type || ''}
              onChange={(e) =>
                updateFilters({
                  ...currentFilters,
                  property_type: (e.target.value as PropertyType) || undefined,
                })
              }
              options={typeOptions}
            />
            
            <Select
              label="Price Range"
              value={getCurrentPriceValue()}
              onChange={(e) => handlePriceChange(e.target.value)}
              options={priceOptions}
            />
            
            <Select
              label="Bedrooms"
              value={String(currentFilters.min_bedrooms || '')}
              onChange={(e) =>
                updateFilters({
                  ...currentFilters,
                  min_bedrooms: e.target.value ? Number(e.target.value) : undefined,
                })
              }
              options={bedroomOptions}
            />
          </div>
        </div>
      )}
      
      {/* Active Filters Display */}
      {activeFilterCount > 0 && (
        <div className="border-t border-gray-100 px-4 py-3">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm text-gray-500">Active filters:</span>
            {currentFilters.location && (
              <FilterBadge
                label={LOCATIONS[currentFilters.location]}
                onRemove={() =>
                  updateFilters({ ...currentFilters, location: undefined })
                }
              />
            )}
            {currentFilters.property_type && (
              <FilterBadge
                label={PROPERTY_TYPES[currentFilters.property_type]}
                onRemove={() =>
                  updateFilters({ ...currentFilters, property_type: undefined })
                }
              />
            )}
            {(currentFilters.min_price !== undefined || currentFilters.max_price !== undefined) && (
              <FilterBadge
                label={formatPriceRange(currentFilters.min_price, currentFilters.max_price)}
                onRemove={() =>
                  updateFilters({
                    ...currentFilters,
                    min_price: undefined,
                    max_price: undefined,
                  })
                }
              />
            )}
            {currentFilters.min_bedrooms !== undefined && (
              <FilterBadge
                label={formatBedrooms(currentFilters.min_bedrooms)}
                onRemove={() =>
                  updateFilters({ ...currentFilters, min_bedrooms: undefined })
                }
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function FilterBadge({ label, onRemove }: { label: string; onRemove: () => void }) {
  return (
    <span className="inline-flex items-center gap-1 px-3 py-1 bg-primary-50 text-primary-700 text-sm rounded-full">
      {label}
      <button
        onClick={onRemove}
        className="hover:bg-primary-100 rounded-full p-0.5"
        aria-label={`Remove ${label} filter`}
      >
        <X className="w-3 h-3" />
      </button>
    </span>
  );
}

function formatPriceRange(min?: number, max?: number): string {
  if (!min && !max) return 'Any Price';
  if (!min) return `Under €${(max! / 1000).toFixed(0)}k`;
  if (!max || max === Infinity) return `Over €${(min / 1000).toFixed(0)}k`;
  return `€${(min / 1000).toFixed(0)}k - €${(max / 1000).toFixed(0)}k`;
}

function formatBedrooms(count: number): string {
  if (count === 0) return 'Studio';
  return `${count}+ Bedrooms`;
}
