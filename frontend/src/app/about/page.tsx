import { Metadata } from 'next';
import Link from 'next/link';
import { APP_NAME, APP_URL, CONTACT_INFO } from '@/lib/constants';
import { Card } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import {
  Target,
  TrendingUp,
  Users,
  Shield,
  BarChart3,
  Calculator,
  MapPin,
  Mail,
  ArrowRight,
} from 'lucide-react';

export const metadata: Metadata = {
  title: 'About Us | Malta Property Investment Analyzer',
  description: 'Learn about Malta Property Analyzer, our mission to help investors find high-ROI real estate opportunities, and the team behind our platform.',
  alternates: {
    canonical: `${APP_URL}/about`,
  },
  openGraph: {
    title: 'About Malta Property Analyzer',
    description: 'Learn about our mission to help investors find high-ROI real estate opportunities.',
    url: `${APP_URL}/about`,
    type: 'website',
  },
};

// JSON-LD structured data
const structuredData = {
  '@context': 'https://schema.org',
  '@type': 'AboutPage',
  name: `About ${APP_NAME}`,
  description: 'Learn about our mission and the team behind Malta Property Analyzer',
  url: `${APP_URL}/about`,
  mainEntity: {
    '@type': 'Organization',
    name: APP_NAME,
    description: 'Property investment analysis platform for Malta real estate',
    url: APP_URL,
    email: CONTACT_INFO.email,
    address: {
      '@type': 'PostalAddress',
      streetAddress: '123 Investment Street',
      addressLocality: 'Valletta',
      addressCountry: 'MT',
    },
  },
};

export default function AboutPage() {
  return (
    <>
      {/* Structured Data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
      />
      
      <div className="bg-gray-50 min-h-screen">
        {/* Hero Section */}
        <div className="bg-gradient-to-br from-primary-900 via-primary-800 to-primary-900 text-white">
          <div className="container-main py-16 md:py-20">
            <div className="max-w-3xl">
              <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-6">
                About Malta Property Analyzer
              </h1>
              <p className="text-lg md:text-xl text-primary-100">
                We&apos;re on a mission to make property investment in Malta more transparent, 
                accessible, and profitable for everyone.
              </p>
            </div>
          </div>
        </div>
        
        {/* Mission Section */}
        <div className="container-main py-16">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-6">
                Our Mission
              </h2>
              <p className="text-gray-600 text-lg mb-6">
                Malta Property Analyzer was founded with a simple goal: to help investors 
                make smarter property investment decisions through data-driven analysis and 
                transparent market insights.
              </p>
              <p className="text-gray-600 mb-6">
                We believe that everyone should have access to the tools and information 
                needed to evaluate real estate opportunities effectively. Our platform 
                combines advanced analytics with local market expertise to provide 
                comprehensive property analysis.
              </p>
              <div className="flex flex-wrap gap-4">
                <Link href="/properties">
                  <Button rightIcon={<ArrowRight className="w-4 h-4" />}>
                    Explore Properties
                  </Button>
                </Link>
                <Link href="/opportunities">
                  <Button variant="outline">
                    View Opportunities
                  </Button>
                </Link>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <StatBox number="2,500+" label="Properties Analyzed" />
              <StatBox number="25+" label="Locations Covered" />
              <StatBox number="1,000+" label="Happy Investors" />
              <StatBox number="4.5%" label="Average ROI" />
            </div>
          </div>
        </div>
        
        {/* Features Section */}
        <div className="bg-white py-16">
          <div className="container-main">
            <div className="text-center max-w-2xl mx-auto mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                What We Offer
              </h2>
              <p className="text-gray-600">
                Our platform provides comprehensive tools and insights for property investment 
                analysis in Malta.
              </p>
            </div>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              <FeatureCard
                icon={BarChart3}
                title="Market Analysis"
                description="Comprehensive market statistics and trends across all locations in Malta."
              />
              <FeatureCard
                icon={Calculator}
                title="ROI Calculator"
                description="Advanced calculator with customizable parameters for accurate projections."
              />
              <FeatureCard
                icon={TrendingUp}
                title="Opportunity Scoring"
                description="Intelligent scoring system to identify the best investment opportunities."
              />
              <FeatureCard
                icon={MapPin}
                title="Location Insights"
                description="Detailed analysis of rental yields and price trends by location."
              />
              <FeatureCard
                icon={Shield}
                title="Data Accuracy"
                description="Regularly updated data from reliable sources for accurate analysis."
              />
              <FeatureCard
                icon={Users}
                title="Investor Community"
                description="Join a growing community of property investors in Malta."
              />
            </div>
          </div>
        </div>
        
        {/* How It Works */}
        <div className="container-main py-16">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-gray-600">
              Getting started with Malta Property Analyzer is simple and straightforward.
            </p>
          </div>
          
          <div className="grid md:grid-cols-4 gap-8">
            <StepCard
              number="1"
              title="Browse Properties"
              description="Explore our database of properties across Malta with detailed information."
            />
            <StepCard
              number="2"
              title="Analyze ROI"
              description="Use our calculator to estimate returns based on your investment parameters."
            />
            <StepCard
              number="3"
              title="Compare Opportunities"
              description="Review opportunity scores and compare properties side by side."
            />
            <StepCard
              number="4"
              title="Make Decisions"
              description="Make informed investment decisions with confidence."
            />
          </div>
        </div>
        
        {/* Contact Section */}
        <div className="bg-primary-900 text-white py-16">
          <div className="container-main">
            <div className="max-w-3xl mx-auto text-center">
              <h2 className="text-3xl font-bold mb-4">
                Get in Touch
              </h2>
              <p className="text-primary-100 mb-8">
                Have questions or feedback? We&apos;d love to hear from you.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <a
                  href={`mailto:${CONTACT_INFO.email}`}
                  className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-white text-primary-900 rounded-lg font-medium hover:bg-gray-100 transition-colors"
                >
                  <Mail className="w-5 h-5" />
                  Email Us
                </a>
                <Link href="/properties">
                  <Button
                    variant="outline"
                    className="border-white text-white hover:bg-white hover:text-primary-900"
                  >
                    Start Exploring
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

function StatBox({ number, label }: { number: string; label: string }) {
  return (
    <div className="bg-white rounded-xl p-6 text-center shadow-sm">
      <p className="text-3xl font-bold text-primary-600">{number}</p>
      <p className="text-gray-600 text-sm mt-1">{label}</p>
    </div>
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
    <Card className="h-full" hover>
      <div className="p-6">
        <div className="w-12 h-12 bg-primary-50 rounded-lg flex items-center justify-center mb-4">
          <Icon className="w-6 h-6 text-primary-600" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
        <p className="text-gray-600">{description}</p>
      </div>
    </Card>
  );
}

function StepCard({
  number,
  title,
  description,
}: {
  number: string;
  title: string;
  description: string;
}) {
  return (
    <div className="text-center">
      <div className="w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">
        {number}
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 text-sm">{description}</p>
    </div>
  );
}
