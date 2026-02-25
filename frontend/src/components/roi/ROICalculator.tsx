'use client';

import React from 'react';
import { useROICalculator } from '@/hooks/useROI';
import { formatCurrency, formatPercent } from '@/lib/utils';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';
import { Card, CardHeader } from '@/components/ui/Card';
import { Calculator, RotateCcw } from 'lucide-react';

interface ROICalculatorProps {
  propertyId: string;
  purchasePrice: number;
  estimatedRent: number;
}

export default function ROICalculator({
  propertyId,
  purchasePrice,
  estimatedRent,
}: ROICalculatorProps) {
  const { inputs, updateInput, calculate, reset, result, isCalculating } = useROICalculator(propertyId);
  
  // Initialize with property values if not set
  React.useEffect(() => {
    if (inputs.purchase_price === 0) {
      updateInput('purchase_price', purchasePrice);
      updateInput('monthly_rent', estimatedRent);
    }
  }, [purchasePrice, estimatedRent]);
  
  const handleReset = () => {
    reset(purchasePrice, estimatedRent);
  };
  
  const loanAmount = inputs.purchase_price * (1 - inputs.down_payment_percent / 100);
  const downPaymentAmount = inputs.purchase_price * (inputs.down_payment_percent / 100);
  
  // Calculate monthly mortgage payment
  const monthlyRate = inputs.interest_rate / 100 / 12;
  const numPayments = inputs.loan_term_years * 12;
  const monthlyMortgage =
    monthlyRate === 0
      ? loanAmount / numPayments
      : (loanAmount * monthlyRate * Math.pow(1 + monthlyRate, numPayments)) /
        (Math.pow(1 + monthlyRate, numPayments) - 1);
  
  return (
    <Card>
      <CardHeader
        title="ROI Calculator"
        subtitle="Adjust parameters to see how they affect your returns"
        action={
          <Button
            variant="ghost"
            size="sm"
            leftIcon={<RotateCcw className="w-4 h-4" />}
            onClick={handleReset}
          >
            Reset
          </Button>
        }
      />
      
      <div className="space-y-6">
        {/* Purchase Details */}
        <div className="space-y-4">
          <h4 className="font-medium text-gray-900">Purchase Details</h4>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Purchase Price"
              type="number"
              value={inputs.purchase_price}
              onChange={(e) => updateInput('purchase_price', Number(e.target.value))}
              leftIcon={<span className="text-gray-400">€</span>}
            />
            
            <Input
              label="Down Payment %"
              type="number"
              min={0}
              max={100}
              value={inputs.down_payment_percent}
              onChange={(e) => updateInput('down_payment_percent', Number(e.target.value))}
              rightIcon={<span className="text-gray-400">%</span>}
            />
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Interest Rate"
              type="number"
              step={0.1}
              min={0}
              max={20}
              value={inputs.interest_rate}
              onChange={(e) => updateInput('interest_rate', Number(e.target.value))}
              rightIcon={<span className="text-gray-400">%</span>}
            />
            
            <Input
              label="Loan Term (Years)"
              type="number"
              min={1}
              max={40}
              value={inputs.loan_term_years}
              onChange={(e) => updateInput('loan_term_years', Number(e.target.value))}
            />
          </div>
          
          {/* Down Payment Summary */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Down Payment Amount:</span>
              <span className="font-semibold text-gray-900">
                {formatCurrency(downPaymentAmount)}
              </span>
            </div>
            <div className="flex justify-between items-center mt-2">
              <span className="text-sm text-gray-600">Loan Amount:</span>
              <span className="font-semibold text-gray-900">
                {formatCurrency(loanAmount)}
              </span>
            </div>
            <div className="flex justify-between items-center mt-2">
              <span className="text-sm text-gray-600">Monthly Mortgage:</span>
              <span className="font-semibold text-gray-900">
                {formatCurrency(monthlyMortgage)}
              </span>
            </div>
          </div>
        </div>
        
        {/* Rental Income */}
        <div className="space-y-4">
          <h4 className="font-medium text-gray-900">Rental Income</h4>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Monthly Rent"
              type="number"
              value={inputs.monthly_rent}
              onChange={(e) => updateInput('monthly_rent', Number(e.target.value))}
              leftIcon={<span className="text-gray-400">€</span>}
            />
            
            <Input
              label="Vacancy Rate"
              type="number"
              min={0}
              max={100}
              value={inputs.vacancy_rate}
              onChange={(e) => updateInput('vacancy_rate', Number(e.target.value))}
              rightIcon={<span className="text-gray-400">%</span>}
              helperText="Expected time property is unoccupied"
            />
          </div>
        </div>
        
        {/* Expenses */}
        <div className="space-y-4">
          <h4 className="font-medium text-gray-900">Expenses</h4>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Maintenance %"
              type="number"
              min={0}
              max={100}
              value={inputs.maintenance_percent}
              onChange={(e) => updateInput('maintenance_percent', Number(e.target.value))}
              rightIcon={<span className="text-gray-400">%</span>}
              helperText="Of rental income"
            />
            
            <Input
              label="Property Management %"
              type="number"
              min={0}
              max={100}
              value={inputs.property_management_percent}
              onChange={(e) => updateInput('property_management_percent', Number(e.target.value))}
              rightIcon={<span className="text-gray-400">%</span>}
              helperText="Of rental income"
            />
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Property Tax (Annual)"
              type="number"
              value={inputs.property_tax_annual}
              onChange={(e) => updateInput('property_tax_annual', Number(e.target.value))}
              leftIcon={<span className="text-gray-400">€</span>}
            />
            
            <Input
              label="Insurance (Annual)"
              type="number"
              value={inputs.insurance_annual}
              onChange={(e) => updateInput('insurance_annual', Number(e.target.value))}
              leftIcon={<span className="text-gray-400">€</span>}
            />
          </div>
        </div>
        
        {/* Calculate Button */}
        <Button
          onClick={calculate}
          isLoading={isCalculating}
          leftIcon={<Calculator className="w-4 h-4" />}
          fullWidth
        >
          Calculate ROI
        </Button>
      </div>
    </Card>
  );
}
