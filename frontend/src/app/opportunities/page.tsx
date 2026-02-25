import { Metadata } from 'next';
import { APP_URL } from '@/lib/constants';
import { mockAPI } from '@/lib/api';
import PropertyList from '@/components/property/PropertyList';
import { Card } from '@/components/ui/Card';
import { TrendingUp, Trophy, Target, Star } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Top Property Investment Opportunities in Malta | High ROI Deals',
  description: 'Discover the highest-scoring property investment opportunities in Malta. Compare ROI, rental yields, and opportunity scores to find the best deals.',
  alternates: {
    canonical: `${APP_URL}/opportunities`,
  },
  openGraph: {
    title: 'Top Property Investment Opportunities in Malta',
    description: 'Discover high-ROI property deals with our opportunity scoring system.',
    url: `${APP_URL}/opportunities`,
    type: 'website',
  },
};

// JSON-LD structured data
const structuredData = {
  '@context': 'https://schema.org',
  '@type': 'ItemList',
  name: 'Top Property Investment Opportunities in Malta',
  description: 'Highest-scoring investment properties ranked by opportunity score',
  url: `${APP_URL}/opportunities`,
  itemListElement: [],
};

async function getOpportunities() {
  try {
    const result = await mockAPI.getOpportunities();
    return result.data.slice(0, 20); // Top 20
  } catch (error) {
    console.error('Failed to fetch opportunities:', error);
    return [];
  }
}

export default async function OpportunitiesPage() {
  const opportunities = await getOpportunities();
  
  // Create opportunity scores map
  const opportunityScores = opportunities.reduce((acc, opp) => {
    acc[opp.property.id] = opp.roi_analysis.opportunity_score;
    return acc;
  }, {} as Record<string, number>);
  
  const properties = opportunities.map(opp => opp.property);
  
  return (
    <>
      {/* Structured Data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
      />
      
      <div className="bg-gray-50 min-h-screen">
        {/* Hero Header */}
        <div className="bg-gradient-to-br from-primary-900 via-primary-800 to-primary-900 text-white">
          <div className="container-main py-12 md:py-16">
            <div className="max-w-3xl">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 rounded-full text-sm mb-6">
                <Trophy className="w-4 h-4" />
                <span>Top Investment Opportunities</span>
              </div>
              
              <h1 className="text-3xl md:text-4xl font-bold mb-4">
                Best Property Investment Opportunities
              </h1>
              
              <p className="text-lg text-primary-100">
                Discover properties with the highest investment potential based on our 
                comprehensive analysis of price, rental yield, location, and growth factors.
              </p>
            </div>
          </div>
        </div>
        
        {/* Stats Bar */}
        <div className="bg-white border-b border-gray-100">
          <div className="container-main py-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard
                icon={Trophy}
                value={opportunities.length.toString()}
                label="Top Opportunities"
              />
              <StatCard
                icon={TrendingUp}
                value={opportunities.length > 0 
                  ? `${(opportunities.reduce((acc, o) => acc + o.roi_analysis.gross_rental_yield, 0) / opportunities.length).toFixed(1)}%`
                  : '0%'}
                label="Avg Rental Yield"
              />
              <StatCard
                icon={Target}
                value={opportunities.length > 0
                  ? Math.round(opportunities.reduce((acc, o) => acc + o.roi_analysis.opportunity_score, 0) / opportunities.length).toString()
                  : '0'}
                label="Avg Opportunity Score"
              />
              <StatCard
                icon={Star}
                value={opportunities.length > 0 ? opportunities[0].roi_analysis.opportunity_score.toString() : '0'}
                label="Highest Score"
              />
            </div>
          </div>
        </div>
        
        {/* How Scoring Works */}
        <div className="container-main py-8">
          <Card className="mb-8">
            <div className="p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                How Opportunity Scoring Works
              </h2>
              <div className="grid md:grid-cols-4 gap-6">
                <ScoreFactor
                  title="Price vs Market"
                  description="Properties priced below market average score higher"
                  weight="25%"
                />
                <ScoreFactor
                  title="Rental Yield"
                  description="Higher expected rental yields increase the score"
                  weight="25%"
                />
                <ScoreFactor
                  title="Location Demand"
                  description="Popular rental locations receive higher scores"
                  weight="25%"
                />
                <ScoreFactor
                  title="Growth Potential"
                  description="Areas with strong price appreciation potential"
                  weight="25%"
                />
              </div>
            </div>
          </Card>
          
          {/* Results */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">
                Top {opportunities.length} Opportunities
              </h2>
              <p className="text-sm text-gray-500">
                Ranked by opportunity score
              </p>
            </div>
            
            <PropertyList
              properties={properties}
              opportunityScores={opportunityScores}
              showScores={true}
              emptyMessage="No opportunities found. Check back soon for new listings."
            />
          </div>
        </div>
      </div>
    </>
  );
}

function StatCard({
  icon: Icon,
  value,
  label,
}: {
  icon: React.ElementType;
  value: string;
  label: string;
}) {
  return (
    <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
      <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
        <Icon className="w-5 h-5 text-primary-600" />
      </div>
      <div>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        <p className="text-sm text-gray-600">{label}</p>
      </div>
    </div>
  );
}

function ScoreFactor({
  title,
  description,
  weight,
}: {
  title: string;
  description: string;
  weight: string;
}) {
  return (
    <div className="text-center">
      <div className="inline-flex items-center justify-center w-12 h-12 bg-primary-50 rounded-full mb-3">
        <span className="text-sm font-bold text-primary-600">{weight}</span>
      </div>
      <h3 className="font-medium text-gray-900 mb-1">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  );
}
