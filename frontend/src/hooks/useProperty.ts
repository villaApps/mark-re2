'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { propertyAPI, mockAPI, APIError } from '@/lib/api';
import { Property, PropertyFilter, SortOption } from '@/types';
import { propertyKeys } from './useProperties';

const USE_MOCK_DATA = process.env.NEXT_PUBLIC_USE_MOCK_API === 'true';

// Extended hook with additional functionality
export function usePropertyDetail(id: string) {
  const queryClient = useQueryClient();
  
  const query = useQuery<{ data: Property }, APIError>({
    queryKey: propertyKeys.detail(id),
    queryFn: async () => {
      if (USE_MOCK_DATA) {
        return mockAPI.getProperty(id);
      }
      return propertyAPI.getProperty(id);
    },
    enabled: !!id,
    staleTime: 10 * 60 * 1000,
    gcTime: 30 * 60 * 1000,
  });
  
  // Prefetch similar properties
  const prefetchSimilar = () => {
    queryClient.prefetchQuery({
      queryKey: propertyKeys.similar(id),
      queryFn: async () => {
        if (USE_MOCK_DATA) {
          const result = await mockAPI.getProperties();
          return { data: result.data.slice(0, 4), success: true };
        }
        return propertyAPI.getSimilarProperties(id);
      },
      staleTime: 5 * 60 * 1000,
    });
  };
  
  return {
    ...query,
    prefetchSimilar,
  };
}

// Hook for property search with debouncing support
export function usePropertySearch(
  searchTerm: string,
  filters?: PropertyFilter,
  sort?: SortOption
) {
  return useQuery<{ data: Property[] }, APIError>({
    queryKey: [...propertyKeys.lists(), 'search', searchTerm, filters, sort],
    queryFn: async () => {
      if (USE_MOCK_DATA) {
        const all = await mockAPI.getProperties();
        const filtered = all.data.filter(p =>
          p.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          p.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
          p.address.toLowerCase().includes(searchTerm.toLowerCase())
        );
        return { data: filtered, success: true };
      }
      // In real implementation, this would call a search endpoint
      const result = await propertyAPI.getProperties(filters, sort, 1, 50);
      return { data: result.data, success: true };
    },
    enabled: searchTerm.length >= 2,
    staleTime: 2 * 60 * 1000,
  });
}

// Hook for saved/favorite properties
export function useSavedProperties() {
  const queryClient = useQueryClient();
  
  // Get saved property IDs from localStorage
  const getSavedIds = (): string[] => {
    if (typeof window === 'undefined') return [];
    const saved = localStorage.getItem('savedProperties');
    return saved ? JSON.parse(saved) : [];
  };
  
  // Save property ID
  const saveProperty = (id: string) => {
    const saved = getSavedIds();
    if (!saved.includes(id)) {
      const updated = [...saved, id];
      localStorage.setItem('savedProperties', JSON.stringify(updated));
      queryClient.invalidateQueries({ queryKey: ['savedProperties'] });
    }
  };
  
  // Remove property ID
  const unsaveProperty = (id: string) => {
    const saved = getSavedIds();
    const updated = saved.filter(savedId => savedId !== id);
    localStorage.setItem('savedProperties', JSON.stringify(updated));
    queryClient.invalidateQueries({ queryKey: ['savedProperties'] });
  };
  
  // Check if property is saved
  const isSaved = (id: string): boolean => {
    return getSavedIds().includes(id);
  };
  
  // Get all saved properties
  const useSavedPropertiesList = () => {
    const savedIds = getSavedIds();
    return useQuery<{ data: Property[] }, APIError>({
      queryKey: ['savedProperties', savedIds],
      queryFn: async () => {
        if (USE_MOCK_DATA) {
          const all = await mockAPI.getProperties();
          const saved = all.data.filter(p => savedIds.includes(p.id));
          return { data: saved, success: true };
        }
        // In real implementation, fetch by IDs
        const properties = await Promise.all(
          savedIds.map(id => propertyAPI.getProperty(id))
        );
        return { data: properties.map(p => p.data), success: true };
      },
      enabled: savedIds.length > 0,
    });
  };
  
  return {
    getSavedIds,
    saveProperty,
    unsaveProperty,
    isSaved,
    useSavedPropertiesList,
  };
}

// Hook for recently viewed properties
export function useRecentlyViewed(maxItems = 10) {
  const STORAGE_KEY = 'recentlyViewedProperties';
  
  const getRecentlyViewed = (): string[] => {
    if (typeof window === 'undefined') return [];
    const viewed = localStorage.getItem(STORAGE_KEY);
    return viewed ? JSON.parse(viewed) : [];
  };
  
  const addToRecentlyViewed = (id: string) => {
    const viewed = getRecentlyViewed();
    const updated = [id, ...viewed.filter(v => v !== id)].slice(0, maxItems);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  };
  
  const clearRecentlyViewed = () => {
    localStorage.removeItem(STORAGE_KEY);
  };
  
  return {
    getRecentlyViewed,
    addToRecentlyViewed,
    clearRecentlyViewed,
  };
}
