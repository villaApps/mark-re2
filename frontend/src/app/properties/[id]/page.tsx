import { Metadata } from 'next';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { APP_URL } from '@/lib/constants';
import { mockAPI } from '@/lib/api';
import { formatCurrency, formatLocation, formatPropertyType, generatePropertyStructuredData } from '@/lib/utils';
import PropertyGallery from '@/components/property/PropertyGallery';
import PropertyMap from '@/components/property/PropertyMap';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import {
  Bed,
  Bath,
  Square,
  MapPin,
  Calendar,
  Car,
  Home,
  Wind,
  Waves,
  TreePine,
  Sofa,
  TrendingUp,
  Calculator,
  ArrowRight,
  Share2,
  Heart,
} from 'lucide-react';

interface PropertyPageProps {
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

async function getSimilarProperties(id: string) {
  try {
    const result = await mockAPI.getProperties();
    return result.data.filter(p => p.id !== id).slice(0, 3);
  } catch (error) {
    return [];
  }
}

export async function generateMetadata({ params }: PropertyPageProps): Promise<Metadata> {
  const property = await getProperty(params.id);
  
  if (!property) {
    return {
      title: 'Property Not Found',
    };
  }
  
  const title = `${property.title} - ${formatLocation(property.location)} | ${formatCurrency(property.price)}`;
  
  return {
    title,
    description: property.description.slice(0, 160),
    alternates: {
      canonical: `${APP_URL}/properties/${property.id}`,
    },
    openGraph: {
      title,
      description: property.description.slice(0, 160),
      url: `${APP_URL}/properties/${property.id}`,
      type: 'website',
      images: property.images.length > 0 ? [{ url: property.images[0] }] : undefined,
    },
  };
}

export default async function PropertyPage({ params }: PropertyPageProps) {
  const property = await getProperty(params.id);
  
  if (!property) {
    notFound();
  }
  
  const similarProperties = await getSimilarProperties(params.id);
  const structuredData = generatePropertyStructuredData(property, APP_URL);
  const pricePerSqm = Math.round(property.price / property.sqm);
  
  return (
    <>
      {/* Structured Data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
      />
      
      <div className="bg-gray-50 min-h-screen">
        {/* Breadcrumb */}
        <div className="bg-white border-b border-gray-100">
          <div className="container-main py-4">
            <nav className="flex items-center gap-2 text-sm text-gray-500">
              <Link href="/" className="hover:text-primary-600">Home</Link>
              <span>/</span>
              <Link href="/properties" className="hover:text-primary-600">Properties</Link>
              <span>/</span>
              <span className="text-gray-900 truncate max-w-xs">{property.title}</span>
            </nav>
          </div>
        </div>
        
        {/* Main Content */}
        <div className="container-main py-8">
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Left Column - Property Details */}
            <div className="lg:col-span-2 space-y-8">
              {/* Gallery */}
              <PropertyGallery images={property.images} title={property.title} />
              
              {/* Title & Price */}
              <div className="bg-white rounded-xl p-6 shadow-sm">
                <div className="flex flex-wrap items-start justify-between gap-4 mb-4">
                  <div>
                    <Badge variant="primary" className="mb-2">
                      {formatPropertyType(property.property_type)}
                    </Badge>
                    <h1 className="text-2xl md:text-3xl font-bold text-gray-900">
                      {property.title}
                    </h1>
                    <div className="flex items-center gap-2 text-gray-600 mt-2">
                      <MapPin className="w-4 h-4" />
                      <span>{property.address}, {formatLocation(property.location)}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-3xl font-bold text-primary-600">
                      {formatCurrency(property.price)}
                    </p>
                    <p className="text-gray-500">
                      €{pricePerSqm.toLocaleString()}/m²
                    </p>
                  </div>
                </div>
                
                {/* Action Buttons */}
                <div className="flex flex-wrap gap-3 pt-4 border-t border-gray-100">
                  <Button variant="outline" size="sm" leftIcon={<Heart className="w-4 h-4" />}>
                    Save
                  </Button>
                  <Button variant="outline" size="sm" leftIcon={<Share2 className="w-4 h-4" />}>
                    Share
                  </Button>
                </div>
              </div>
              
              {/* Key Features */}
              <div className="bg-white rounded-xl p-6 shadow-sm">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Property Features</h2>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <FeatureItem
                    icon={Bed}
                    label="Bedrooms"
                    value={property.bedrooms === 0 ? 'Studio' : property.bedrooms.toString()}
                  />
                  <FeatureItem
                    icon={Bath}
                    label="Bathrooms"
                    value={property.bathrooms.toString()}
                  />
                  <FeatureItem
                    icon={Square}
                    label="Area"
                    value={`${property.sqm} m²`}
                  />
                  {property.year_built && (
                    <FeatureItem
                      icon={Calendar}
                      label="Year Built"
                      value={property.year_built.toString()}
                    />
                  )}
                  {property.parking_spaces > 0 && (
                    <FeatureItem
                      icon={Car}
                      label="Parking"
                      value={property.parking_spaces.toString()}
                    />
                  )}
                  {property.floor !== undefined && (
                    <FeatureItem
                      icon={Home}
                      label="Floor"
                      value={`${property.floor}${property.total_floors ? `/${property.total_floors}` : ''}`}
                    />
                  )}
                  {property.has_elevator && (
                    <FeatureItem
                      icon={Wind}
                      label="Elevator"
                      value="Yes"
                    />
                  )}
                  {property.has_pool && (
                    <FeatureItem
                      icon={Waves}
                      label="Pool"
                      value="Yes"
                    />
                  )}
                  {property.has_garden && (
                    <FeatureItem
                      icon={TreePine}
                      label="Garden"
                      value="Yes"
                    />
                  )}
                  {property.furnished && (
                    <FeatureItem
                      icon={Sofa}
                      label="Furnished"
                      value={property.furnished.charAt(0).toUpperCase() + property.furnished.slice(1)}
                    />
                  )}
                </div>
              </div>
              
              {/* Description */}
              <div className="bg-white rounded-xl p-6 shadow-sm">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Description</h2>
                <p className="text-gray-600 whitespace-pre-line">{property.description}</p>
              </div>
              
              {/* Features List */}
              {property.features.length > 0 && (
                <div className="bg-white rounded-xl p-6 shadow-sm">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">Additional Features</h2>
                  <div className="flex flex-wrap gap-2">
                    {property.features.map((feature, index) => (
                      <Badge key={index} variant="default" size="sm">
                        {feature}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Location Map */}
              <div className="bg-white rounded-xl p-6 shadow-sm">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Location</h2>
                <PropertyMap property={property} height="300px" />
              </div>
            </div>
            
            {/* Right Column - Sidebar */}
            <div className="space-y-6">
              {/* ROI Card */}
              <Card className="bg-gradient-to-br from-primary-600 to-primary-700 text-white">
                <div className="p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <TrendingUp className="w-5 h-5" />
                    <h3 className="font-semibold">Investment Analysis</h3>
                  </div>
                  <p className="text-primary-100 text-sm mb-6">
                    Get detailed ROI calculations and cash flow projections for this property.
                  </p>
                  <Link href={`/properties/${property.id}/roi`}>
                    <Button
                      variant="secondary"
                      fullWidth
                      rightIcon={<ArrowRight className="w-4 h-4" />}
                    >
                      View ROI Analysis
                    </Button>
                  </Link>
                </div>
              </Card>
              
              {/* Quick Stats */}
              <Card>
                <div className="p-6">
                  <h3 className="font-semibold text-gray-900 mb-4">Quick Stats</h3>
                  <div className="space-y-4">
                    <QuickStat label="Property Type" value={formatPropertyType(property.property_type)} />
                    <QuickStat label="Location" value={formatLocation(property.location)} />
                    <QuickStat label="Price per m²" value={`€${pricePerSqm.toLocaleString()}`} />
                    <QuickStat label="Listed" value={new Date(property.created_at).toLocaleDateString('en-MT')} />
                  </div>
                </div>
              </Card>
              
              {/* Contact Agent */}
              <Card>
                <div className="p-6">
                  <h3 className="font-semibold text-gray-900 mb-4">Contact Agent</h3>
                  {property.agent_name ? (
                    <div className="space-y-3">
                      <p className="font-medium">{property.agent_name}</p>
                      {property.agent_phone && (
                        <a
                          href={`tel:${property.agent_phone}`}
                          className="flex items-center gap-2 text-primary-600 hover:text-primary-700"
                        >
                          <Phone className="w-4 h-4" />
                          {property.agent_phone}
                        </a>
                      )}
                      {property.agent_email && (
                        <a
                          href={`mailto:${property.agent_email}`}
                          className="flex items-center gap-2 text-primary-600 hover:text-primary-700"
                        >
                          <Mail className="w-4 h-4" />
                          {property.agent_email}
                        </a>
                      )}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-sm">
                      Contact information available upon request.
                    </p>
                  )}
                </div>
              </Card>
            </div>
          </div>
          
          {/* Similar Properties */}
          {similarProperties.length > 0 && (
            <div className="mt-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Similar Properties</h2>
              <div className="grid md:grid-cols-3 gap-6">
                {similarProperties.map((prop) => (
                  <Link key={prop.id} href={`/properties/${prop.id}`}>
                    <Card hover className="h-full">
                      <div className="aspect-video bg-gray-100 rounded-t-lg overflow-hidden">
                        {prop.images[0] && (
                          <img
                            src={prop.images[0]}
                            alt={prop.title}
                            className="w-full h-full object-cover"
                          />
                        )}
                      </div>
                      <div className="p-4">
                        <p className="font-semibold text-gray-900 line-clamp-1">{prop.title}</p>
                        <p className="text-primary-600 font-bold mt-1">
                          {formatCurrency(prop.price)}
                        </p>
                        <div className="flex items-center gap-3 text-sm text-gray-500 mt-2">
                          <span>{prop.bedrooms} bed</span>
                          <span>{prop.bathrooms} bath</span>
                          <span>{prop.sqm} m²</span>
                        </div>
                      </div>
                    </Card>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

function FeatureItem({
  icon: Icon,
  label,
  value,
}: {
  icon: React.ElementType;
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
      <Icon className="w-5 h-5 text-gray-400" />
      <div>
        <p className="text-xs text-gray-500">{label}</p>
        <p className="font-medium text-gray-900">{value}</p>
      </div>
    </div>
  );
}

function QuickStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-gray-100 last:border-0">
      <span className="text-gray-600">{label}</span>
      <span className="font-medium text-gray-900">{value}</span>
    </div>
  );
}

// Import missing icons
import { Phone, Mail } from 'lucide-react';
