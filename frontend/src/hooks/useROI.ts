'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { roiAPI, mockAPI, APIError } from '@/lib/api';
import { ROIAnalysis, ROICalculatorInput } from '@/types';
import { useState, useCallback } from 'react';
import { DEFAULT_ROI_VALUES } from '@/lib/constants';

const USE_MOCK_DATA = process.env.NEXT_PUBLIC_USE_MOCK_API === 'true';

// Query keys
export const roiKeys = {
  all: ['roi'] as const,
  analysis: (propertyId: string) => [...roiKeys.all, 'analysis', propertyId] as const,
  calculated: (propertyId: string) => [...roiKeys.all, 'calculated', propertyId] as const,
};

// Hook for fetching ROI analysis
export function useROIAnalysis(propertyId: string) {
  return useQuery<{ data: ROIAnalysis }, APIError>({
    queryKey: roiKeys.analysis(propertyId),
    queryFn: async () => {
      if (USE_MOCK_DATA) {
        return mockAPI.getROIAnalysis(propertyId);
      }
      return roiAPI.getROIAnalysis(propertyId);
    },
    enabled: !!propertyId,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
}

// Hook for calculating custom ROI
export function useROICalculator(propertyId: string) {
  const queryClient = useQueryClient();
  
  const [inputs, setInputs] = useState<ROICalculatorInput>({
    property_id: propertyId,
    purchase_price: 0,
    down_payment_percent: DEFAULT_ROI_VALUES.down_payment_percent,
    interest_rate: DEFAULT_ROI_VALUES.interest_rate,
    loan_term_years: DEFAULT_ROI_VALUES.loan_term_years,
    monthly_rent: 0,
    vacancy_rate: DEFAULT_ROI_VALUES.vacancy_rate,
    maintenance_percent: DEFAULT_ROI_VALUES.maintenance_percent,
    property_management_percent: DEFAULT_ROI_VALUES.property_management_percent,
    property_tax_annual: DEFAULT_ROI_VALUES.property_tax_annual,
    insurance_annual: DEFAULT_ROI_VALUES.insurance_annual,
    appreciation_rate: DEFAULT_ROI_VALUES.appreciation_rate,
  });
  
  const mutation = useMutation<{ data: ROIAnalysis }, APIError, ROICalculatorInput>({
    mutationFn: async (input) => {
      if (USE_MOCK_DATA) {
        // Simulate calculation delay
        await new Promise(resolve => setTimeout(resolve, 500));
        const baseAnalysis = await mockAPI.getROIAnalysis(propertyId);
        return {
          data: {
            ...baseAnalysis.data,
            assumptions: {
              down_payment_percent: input.down_payment_percent,
              interest_rate: input.interest_rate,
              loan_term_years: input.loan_term_years,
              vacancy_rate: input.vacancy_rate,
              maintenance_percent: input.maintenance_percent,
              property_management_percent: input.property_management_percent,
              property_tax_annual: input.property_tax_annual,
              insurance_annual: input.insurance_annual,
            },
            estimated_monthly_rent: input.monthly_rent,
            estimated_annual_rent: input.monthly_rent * 12,
            gross_rental_yield: (input.monthly_rent * 12) / input.purchase_price * 100,
          },
          success: true,
        };
      }
      return roiAPI.calculateROI(input);
    },
    onSuccess: (data) => {
      queryClient.setQueryData(roiKeys.calculated(propertyId), data);
    },
  });
  
  const updateInput = useCallback(<K extends keyof ROICalculatorInput>(
    key: K,
    value: ROICalculatorInput[K]
  ) => {
    setInputs(prev => ({ ...prev, [key]: value }));
  }, []);
  
  const calculate = useCallback(() => {
    mutation.mutate(inputs);
  }, [inputs, mutation]);
  
  const reset = useCallback((purchasePrice: number, monthlyRent: number) => {
    setInputs({
      property_id: propertyId,
      purchase_price: purchasePrice,
      down_payment_percent: DEFAULT_ROI_VALUES.down_payment_percent,
      interest_rate: DEFAULT_ROI_VALUES.interest_rate,
      loan_term_years: DEFAULT_ROI_VALUES.loan_term_years,
      monthly_rent: monthlyRent,
      vacancy_rate: DEFAULT_ROI_VALUES.vacancy_rate,
      maintenance_percent: DEFAULT_ROI_VALUES.maintenance_percent,
      property_management_percent: DEFAULT_ROI_VALUES.property_management_percent,
      property_tax_annual: DEFAULT_ROI_VALUES.property_tax_annual,
      insurance_annual: DEFAULT_ROI_VALUES.insurance_annual,
      appreciation_rate: DEFAULT_ROI_VALUES.appreciation_rate,
    });
    queryClient.removeQueries({ queryKey: roiKeys.calculated(propertyId) });
  }, [propertyId, queryClient]);
  
  return {
    inputs,
    updateInput,
    calculate,
    reset,
    result: mutation.data,
    isCalculating: mutation.isPending,
    error: mutation.error,
  };
}

// Hook for ROI comparison
export function useROIComparison(propertyIds: string[]) {
  return useQuery<{ data: ROIAnalysis[] }, APIError>({
    queryKey: [...roiKeys.all, 'comparison', propertyIds],
    queryFn: async () => {
      if (USE_MOCK_DATA) {
        const analyses = await Promise.all(
          propertyIds.map(id => mockAPI.getROIAnalysis(id))
        );
        return { data: analyses.map(a => a.data), success: true };
      }
      const analyses = await Promise.all(
        propertyIds.map(id => roiAPI.getROIAnalysis(id))
      );
      return { data: analyses.map(a => a.data), success: true };
    },
    enabled: propertyIds.length > 0,
  });
}

// Hook for opportunity score
export function useOpportunityScore(propertyId: string) {
  const { data, isLoading, error } = useROIAnalysis(propertyId);
  
  return {
    score: data?.data.opportunity_score ?? 0,
    isLoading,
    error,
  };
}

// Hook for cash flow projections
export function useCashFlowProjections(propertyId: string) {
  const { data, isLoading, error } = useROIAnalysis(propertyId);
  
  return {
    projections: data?.data.cash_flow_projections ?? [],
    isLoading,
    error,
  };
}
