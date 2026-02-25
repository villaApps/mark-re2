import { Metadata } from 'next';
import { APP_URL } from '@/lib/constants';
import { mockAPI } from '@/lib/api';
import MarketStats from '@/components/stats/MarketStats';
import { Card } from '@/components/ui/Card';
import { TrendingUp, Info } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Malta Real Estate Market Statistics | Investment Data',
  description: 'Explore Malta real estate market statistics including average prices, rental yields, price trends, and location-based data for informed investment decisions.',
  alternates: {
    canonical: `${APP_URL}/stats`,
  },
  openGraph: {
    title: 'Malta Real Estate Market Statistics',
    description: 'Comprehensive market data and trends for Malta property investment.',
    url: `${APP_URL}/stats`,
    type: 'website',
  },
};

// JSON-LD structured data
const structuredData = {
  '@context': 'https://schema.org',
  '@type': 'Dataset',
  name: 'Malta Real Estate Market Statistics',
  description: 'Comprehensive market data for property investment in Malta',
  url: `${APP_URL}/stats`,
  creator: {
    '@type': 'Organization',
    name: 'Malta Property Analyzer',
  },
  datePublished: new Date().toISOString(),
  license: 'https://creativecommons.org/licenses/by/4.0/',
};

async function getMarketStats() {
  try {
    const result = await mockAPI.getMarketStats();
    return result.data;
  } catch (error) {
    console.error('Failed to fetch market stats:', error);
    return null;
  }
}

export default async function StatsPage() {
  const stats = await getMarketStats();
  
  if (!stats) {
    return (
      <div className="bg-gray-50 min-h-screen">
        <div className="container-main py-16 text-center">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <TrendingUp className="w-8 h-8 text-gray-400" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Market Statistics Unavailable
          </h1>
          <p className="text-gray-600">
            We&apos;re currently updating our market data. Please check back soon.
          </p>
        </div>
      </div>
    );
  }
  
  return (
    <>
      {/* Structured Data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
      />
      
      <div className="bg-gray-50 min-h-screen">
        {/* Header */}
        <div className="bg-white border-b border-gray-100">
          <div className="container-main py-8">
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Malta Real Estate Market Statistics
            </h1>
            <p className="text-lg text-gray-600 max-w-2xl">
              Comprehensive market data and trends to help you make informed 
              property investment decisions in Malta.
            </p>
          </div>
        </div>
        
        {/* Main Content */}
        <div className="container-main py-8">
          <MarketStats stats={stats} />
          
          {/* Data Disclaimer */}
          <Card className="mt-8">
            <div className="p-6 flex items-start gap-4">
              <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center flex-shrink-0">
                <Info className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">About Our Data</h3>
                <p className="text-gray-600 text-sm">
                  Our market statistics are compiled from various sources including public records, 
                  property listings, and market research. Data is updated regularly to provide 
                  accurate insights. Rental yields are estimates based on current market conditions 
                  and may vary depending on specific property characteristics and location.
                </p>
                <p className="text-gray-500 text-sm mt-2">
                  Last updated: {new Date().toLocaleDateString('en-MT', { 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}
                </p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </>
  );
}
