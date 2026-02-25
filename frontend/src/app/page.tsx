import { Metadata } from 'next';
import Link from 'next/link';
import Image from 'next/image';
import { APP_NAME, APP_DESCRIPTION, APP_URL } from '@/lib/constants';
import { mockAPI } from '@/lib/api';
import PropertyList from '@/components/property/PropertyList';
import Button from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import {
  TrendingUp,
  Search,
  Calculator,
  BarChart3,
  ArrowRight,
  CheckCircle,
  MapPin,
  Home,
} from 'lucide-react';

export const metadata: Metadata = {
  title: APP_NAME,
  description: APP_DESCRIPTION,
  alternates: {
    canonical: APP_URL,
  },
  openGraph: {
    title: APP_NAME,
    description: APP_DESCRIPTION,
    url: APP_URL,
    type: 'website',
  },
};

// JSON-LD structured data
const structuredData = {
  '@context': 'https://schema.org',
  '@type': 'WebSite',
  name: APP_NAME,
  description: APP_DESCRIPTION,
  url: APP_URL,
  potentialAction: {
    '@type': 'SearchAction',
    target: `${APP_URL}/properties?search={search_term_string}`,
    'query-input': 'required name=search_term_string',
  },
};

async function getFeaturedProperties() {
  try {
    const result = await mockAPI.getProperties(undefined, undefined, 1, 6);
    return result.data;
  } catch (error) {
    console.error('Failed to fetch featured properties:', error);
    return [];
  }
}

export default async function HomePage() {
  const featuredProperties = await getFeaturedProperties();
  
  return (
    <>
      {/* Structured Data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
      />
      
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-primary-900 via-primary-800 to-primary-900 text-white overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
            <defs>
              <pattern id="hero-grid" width="10" height="10" patternUnits="userSpaceOnUse">
                <path d="M 10 0 L 0 0 0 10" fill="none" stroke="currentColor" strokeWidth="0.5"/>
              </pattern>
            </defs>
            <rect width="100" height="100" fill="url(#hero-grid)" />
          </svg>
        </div>
        
        <div className="relative container-main py-20 md:py-28 lg:py-32">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 rounded-full text-sm mb-6">
              <TrendingUp className="w-4 h-4" />
              <span>Smart Property Investment in Malta</span>
            </div>
            
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight mb-6">
              Find High-ROI Real Estate{' '}
              <span className="text-primary-300">Opportunities</span>
            </h1>
            
            <p className="text-lg md:text-xl text-primary-100 mb-8 max-w-2xl">
              Analyze properties, calculate returns, and discover the best investment opportunities 
              in Malta with our advanced property analysis tools.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4">
              <Link href="/properties">
                <Button size="lg" leftIcon={<Search className="w-5 h-5" />}>
                  Browse Properties
                </Button>
              </Link>
              <Link href="/opportunities">
                <Button
                  variant="outline"
                  size="lg"
                  className="border-white text-white hover:bg-white hover:text-primary-900"
                  leftIcon={<TrendingUp className="w-5 h-5" />}
                >
                  Top Opportunities
                </Button>
              </Link>
            </div>
            
            {/* Stats */}
            <div className="grid grid-cols-3 gap-8 mt-12 pt-12 border-t border-white/20">
              <div>
                <p className="text-3xl md:text-4xl font-bold">2,500+</p>
                <p className="text-primary-200 text-sm mt-1">Properties</p>
              </div>
              <div>
                <p className="text-3xl md:text-4xl font-bold">4.5%</p>
                <p className="text-primary-200 text-sm mt-1">Avg Yield</p>
              </div>
              <div>
                <p className="text-3xl md:text-4xl font-bold">25+</p>
                <p className="text-primary-200 text-sm mt-1">Locations</p>
              </div>
            </div>
          </div>
        </div>
        
        {/* Decorative Elements */}
        <div className="absolute top-20 right-20 w-64 h-64 bg-primary-500/20 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-40 w-48 h-48 bg-success-500/20 rounded-full blur-3xl" />
      </section>
      
      {/* Features Section */}
      <section className="section bg-white">
        <div className="container-main">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-lg text-gray-600">
              Our platform provides everything you need to make informed property investment decisions.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard
              icon={Search}
              title="Discover Properties"
              description="Browse thousands of properties across Malta with advanced filters and search capabilities."
            />
            <FeatureCard
              icon={Calculator}
              title="Analyze ROI"
              description="Calculate potential returns with our comprehensive ROI calculator and cash flow projections."
            />
            <FeatureCard
              icon={BarChart3}
              title="Compare Opportunities"
              description="Get opportunity scores and compare properties to find the best investment deals."
            />
          </div>
        </div>
      </section>
      
      {/* Featured Properties Section */}
      <section className="section bg-gray-50">
        <div className="container-main">
          <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-12">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                Featured Opportunities
              </h2>
              <p className="text-lg text-gray-600 max-w-xl">
                Explore our handpicked selection of properties with strong investment potential.
              </p>
            </div>
            <Link href="/properties">
              <Button variant="outline" rightIcon={<ArrowRight className="w-4 h-4" />}>
                View All Properties
              </Button>
            </Link>
          </div>
          
          <PropertyList properties={featuredProperties} />
        </div>
      </section>
      
      {/* Benefits Section */}
      <section className="section bg-white">
        <div className="container-main">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
                Why Choose Our Platform?
              </h2>
              <p className="text-lg text-gray-600 mb-8">
                We combine advanced analytics with local market expertise to help you make 
                smarter investment decisions in Malta's real estate market.
              </p>
              
              <div className="space-y-4">
                <BenefitItem
                  icon={CheckCircle}
                  title="Data-Driven Analysis"
                  description="Our algorithms analyze market data to identify the best opportunities."
                />
                <BenefitItem
                  icon={MapPin}
                  title="Local Market Expertise"
                  description="Deep understanding of Malta's property market across all locations."
                />
                <BenefitItem
                  icon={Calculator}
                  title="Accurate ROI Calculations"
                  description="Comprehensive financial modeling with customizable parameters."
                />
                <BenefitItem
                  icon={Home}
                  title="Complete Property Data"
                  description="Detailed information on every property including rental estimates."
                />
              </div>
            </div>
            
            <div className="relative">
              <div className="aspect-square rounded-2xl bg-gradient-to-br from-primary-100 to-primary-50 p-8 flex items-center justify-center">
                <div className="grid grid-cols-2 gap-4 w-full max-w-sm">
                  <StatBox label="Properties Analyzed" value="2,500+" />
                  <StatBox label="Avg ROI" value="5.2%" />
                  <StatBox label="Locations Covered" value="25+" />
                  <StatBox label="Happy Investors" value="1,000+" />
                </div>
              </div>
              
              {/* Decorative elements */}
              <div className="absolute -top-4 -right-4 w-24 h-24 bg-success-100 rounded-full flex items-center justify-center">
                <TrendingUp className="w-10 h-10 text-success-600" />
              </div>
            </div>
          </div>
        </div>
      </section>
      
      {/* CTA Section */}
      <section className="section bg-primary-900 text-white">
        <div className="container-main">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              Ready to Find Your Next Investment?
            </h2>
            <p className="text-lg text-primary-100 mb-8">
              Start exploring properties today and discover high-ROI opportunities in Malta.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/properties">
                <Button size="lg" variant="secondary">
                  Start Exploring
                </Button>
              </Link>
              <Link href="/opportunities">
                <Button
                  size="lg"
                  variant="outline"
                  className="border-white text-white hover:bg-white hover:text-primary-900"
                >
                  View Top Opportunities
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}

function FeatureCard({
  icon: Icon,
  title,
  description,
}: {
  icon: React.ElementType;
  title: string;
  description: string;
}) {
  return (
    <Card className="text-center h-full" hover>
      <div className="w-14 h-14 bg-primary-50 rounded-xl flex items-center justify-center mx-auto mb-6">
        <Icon className="w-7 h-7 text-primary-600" />
      </div>
      <h3 className="text-xl font-semibold text-gray-900 mb-3">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </Card>
  );
}

function BenefitItem({
  icon: Icon,
  title,
  description,
}: {
  icon: React.ElementType;
  title: string;
  description: string;
}) {
  return (
    <div className="flex gap-4">
      <div className="flex-shrink-0 w-10 h-10 bg-success-50 rounded-lg flex items-center justify-center">
        <Icon className="w-5 h-5 text-success-600" />
      </div>
      <div>
        <h4 className="font-semibold text-gray-900">{title}</h4>
        <p className="text-gray-600 text-sm mt-1">{description}</p>
      </div>
    </div>
  );
}

function StatBox({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-white rounded-xl p-6 text-center shadow-sm">
      <p className="text-2xl font-bold text-primary-600">{value}</p>
      <p className="text-sm text-gray-600 mt-1">{label}</p>
    </div>
  );
}
