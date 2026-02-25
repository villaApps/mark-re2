'use client';

import { useQuery, useQueryClient } from '@tanstack/react-query';
import { propertyAPI, mockAPI, APIError } from '@/lib/api';
import { Property, PropertyFilter, SortOption, PaginatedResponse } from '@/types';
import { useCallback } from 'react';

const USE_MOCK_DATA = process.env.NEXT_PUBLIC_USE_MOCK_API === 'true';

// Query keys
export const propertyKeys = {
  all: ['properties'] as const,
  lists: () => [...propertyKeys.all, 'list'] as const,
  list: (filters: PropertyFilter, sort?: SortOption, page?: number) =>
    [...propertyKeys.lists(), { filters, sort, page }] as const,
  details: () => [...propertyKeys.all, 'detail'] as const,
  detail: (id: string) => [...propertyKeys.details(), id] as const,
  featured: () => [...propertyKeys.all, 'featured'] as const,
  similar: (id: string) => [...propertyKeys.details(), id, 'similar'] as const,
};

// Hook for fetching properties list
export function useProperties(
  filters?: PropertyFilter,
  sort?: SortOption,
  page = 1,
  limit = 12
) {
  return useQuery<PaginatedResponse<Property>, APIError>({
    queryKey: propertyKeys.list(filters || {}, sort, page),
    queryFn: async () => {
      if (USE_MOCK_DATA) {
        return mockAPI.getProperties(filters, sort, page, limit);
      }
      return propertyAPI.getProperties(filters, sort, page, limit);
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
}

// Hook for fetching a single property
export function useProperty(id: string) {
  return useQuery<{ data: Property }, APIError>({
    queryKey: propertyKeys.detail(id),
    queryFn: async () => {
      if (USE_MOCK_DATA) {
        return mockAPI.getProperty(id);
      }
      return propertyAPI.getProperty(id);
    },
    enabled: !!id,
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
  });
}

// Hook for fetching featured properties
export function useFeaturedProperties(limit = 6) {
  return useQuery<{ data: Property[] }, APIError>({
    queryKey: propertyKeys.featured(),
    queryFn: async () => {
      if (USE_MOCK_DATA) {
        const result = await mockAPI.getProperties(undefined, undefined, 1, limit);
        return { data: result.data, success: true };
      }
      return propertyAPI.getFeaturedProperties(limit);
    },
    staleTime: 10 * 60 * 1000,
    gcTime: 30 * 60 * 1000,
  });
}

// Hook for prefetching property details
export function usePrefetchProperty() {
  const queryClient = useQueryClient();
  
  return useCallback(
    (id: string) => {
      queryClient.prefetchQuery({
        queryKey: propertyKeys.detail(id),
        queryFn: async () => {
          if (USE_MOCK_DATA) {
            return mockAPI.getProperty(id);
          }
          return propertyAPI.getProperty(id);
        },
        staleTime: 10 * 60 * 1000,
      });
    },
    [queryClient]
  );
}

// Hook for invalidating property cache
export function useInvalidateProperties() {
  const queryClient = useQueryClient();
  
  return useCallback(() => {
    queryClient.invalidateQueries({ queryKey: propertyKeys.all });
  }, [queryClient]);
}
