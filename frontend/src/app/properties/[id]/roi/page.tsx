import { Metadata } from 'next';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { APP_URL } from '@/lib/constants';
import { mockAPI } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';
import ROICalculator from '@/components/roi/ROICalculator';
import ROIDisplay from '@/components/roi/ROIDisplay';
import CashFlowChart from '@/components/roi/CashFlowChart';
import OpportunityScore from '@/components/roi/OpportunityScore';
import { Card } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { ArrowLeft, TrendingUp, Calculator, FileText } from 'lucide-react';

interface ROIAnalysisPageProps {
  params: {
    id: string;
  };
}

async function getProperty(id: string) {
  try {
    const result = await mockAPI.getProperty(id);
    return result.data;
  } catch (error) {
    return null;
  }
}

async function getROIAnalysis(propertyId: string) {
  try {
    const result = await mockAPI.getROIAnalysis(propertyId);
    return result.data;
  } catch (error) {
    return null;
  }
}

export async function generateMetadata({ params }: ROIAnalysisPageProps): Promise<Metadata> {
  const property = await getProperty(params.id);
  
  if (!property) {
    return {
      title: 'ROI Analysis Not Found',
    };
  }
  
  return {
    title: `ROI Analysis for ${property.title} | Malta Property Investment`,
    description: `Calculate ROI, rental yield, and cash flow projections for ${property.title}. Make informed investment decisions with our comprehensive analysis.`,
    alternates: {
      canonical: `${APP_URL}/properties/${property.id}/roi`,
    },
  };
}

export default async function ROIAnalysisPage({ params }: ROIAnalysisPageProps) {
  const property = await getProperty(params.id);
  const roiAnalysis = await getROIAnalysis(params.id);
  
  if (!property || !roiAnalysis) {
    notFound();
  }
  
  // Estimate monthly rent based on analysis
  const estimatedMonthlyRent = roiAnalysis.estimated_monthly_rent || Math.round(property.price * 0.004);
  
  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="bg-white border-b border-gray-100">
        <div className="container-main py-6">
          <Link
            href={`/properties/${property.id}`}
            className="inline-flex items-center gap-2 text-gray-600 hover:text-primary-600 mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Property
          </Link>
          
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-gray-900">
                ROI Analysis
              </h1>
              <p className="text-gray-600 mt-1">{property.title}</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Property Price</p>
              <p className="text-2xl font-bold text-primary-600">
                {formatCurrency(property.price)}
              </p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="container-main py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Analysis */}
          <div className="lg:col-span-2 space-y-8">
            {/* ROI Metrics */}
            <ROIDisplay analysis={roiAnalysis} />
            
            {/* Cash Flow Chart */}
            <CashFlowChart analysis={roiAnalysis} />
            
            {/* Investment Summary */}
            <Card>
              <div className="p-6">
                <div className="flex items-center gap-2 mb-4">
                  <FileText className="w-5 h-5 text-primary-600" />
                  <h3 className="font-semibold text-gray-900">Investment Summary</h3>
                </div>
                
                <div className="prose prose-gray max-w-none">
                  <p>
                    Based on our analysis, this property in {property.location} shows 
                    {roiAnalysis.opportunity_score >= 70 ? ' strong ' : roiAnalysis.opportunity_score >= 50 ? ' moderate ' : ' below average '}
                    investment potential with an opportunity score of {roiAnalysis.opportunity_score}/100.
                  </p>
                  
                  <h4 className="text-lg font-medium text-gray-900 mt-4 mb-2">Key Highlights</h4>
                  <ul className="list-disc list-inside space-y-1 text-gray-600">
                    <li>
                      Gross rental yield of {roiAnalysis.gross_rental_yield.toFixed(2)}% 
                      based on estimated monthly rent of {formatCurrency(roiAnalysis.estimated_monthly_rent)}
                    </li>
                    <li>
                      Net rental yield of {roiAnalysis.net_rental_yield.toFixed(2)}% after accounting for expenses
                    </li>
                    <li>
                      Price per square meter is {roiAnalysis.market_comparison.price_vs_market > 0 ? 'above' : 'below'} market average by {Math.abs(roiAnalysis.market_comparison.price_vs_market).toFixed(1)}%
                    </li>
                    <li>
                      Estimated cash-on-cash return of {roiAnalysis.cash_on_cash_return.toFixed(2)}%
                    </li>
                  </ul>
                  
                  <h4 className="text-lg font-medium text-gray-900 mt-4 mb-2">Considerations</h4>
                  <ul className="list-disc list-inside space-y-1 text-gray-600">
                    <li>Vacancy rate assumption: {roiAnalysis.assumptions.vacancy_rate}%</li>
                    <li>Maintenance costs: {roiAnalysis.assumptions.maintenance_percent}% of rental income</li>
                    <li>Property management: {roiAnalysis.assumptions.property_management_percent}% of rental income</li>
                    <li>Interest rate assumption: {roiAnalysis.assumptions.interest_rate}%</li>
                  </ul>
                </div>
              </div>
            </Card>
          </div>
          
          {/* Right Column - Calculator & Score */}
          <div className="space-y-6">
            {/* Opportunity Score */}
            <OpportunityScore score={roiAnalysis.opportunity_score} />
            
            {/* ROI Calculator */}
            <ROICalculator
              propertyId={property.id}
              purchasePrice={property.price}
              estimatedRent={estimatedMonthlyRent}
            />
            
            {/* Quick Actions */}
            <Card>
              <div className="p-6">
                <h3 className="font-semibold text-gray-900 mb-4">Quick Actions</h3>
                <div className="space-y-3">
                  <Link href={`/properties/${property.id}`}>
                    <Button variant="outline" fullWidth>
                      View Property Details
                    </Button>
                  </Link>
                  <Link href="/opportunities">
                    <Button variant="outline" fullWidth>
                      Compare with Top Opportunities
                    </Button>
                  </Link>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
