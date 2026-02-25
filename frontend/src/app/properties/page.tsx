import { Metadata } from 'next';
import { Suspense } from 'react';
import { APP_URL } from '@/lib/constants';
import { mockAPI } from '@/lib/api';
import { PropertyFilter, SortOption } from '@/types';
import PropertyList from '@/components/property/PropertyList';
import PropertyFilters from '@/components/property/PropertyFilters';
import { PropertyListSkeleton } from '@/components/ui/Loading';
import Pagination from '@/components/ui/Pagination';

interface PropertiesPageProps {
  searchParams: {
    location?: string;
    property_type?: string;
    min_price?: string;
    max_price?: string;
    min_bedrooms?: string;
    max_bedrooms?: string;
    sort?: string;
    page?: string;
  };
}

export const metadata: Metadata = {
  title: 'Properties for Sale in Malta | Investment Opportunities',
  description: 'Browse properties for sale in Malta. Find apartments, penthouses, villas, and more with detailed ROI analysis and investment potential.',
  alternates: {
    canonical: `${APP_URL}/properties`,
  },
  openGraph: {
    title: 'Properties for Sale in Malta | Investment Opportunities',
    description: 'Browse properties for sale in Malta with detailed ROI analysis.',
    url: `${APP_URL}/properties`,
    type: 'website',
  },
};

// JSON-LD structured data
const structuredData = {
  '@context': 'https://schema.org',
  '@type': 'ItemList',
  name: 'Properties for Sale in Malta',
  description: 'Browse investment properties across Malta',
  url: `${APP_URL}/properties`,
  itemListElement: [],
};

async function getProperties(searchParams: PropertiesPageProps['searchParams']) {
  const filters: PropertyFilter = {};
  
  if (searchParams.location) filters.location = searchParams.location as any;
  if (searchParams.property_type) filters.property_type = searchParams.property_type as any;
  if (searchParams.min_price) filters.min_price = Number(searchParams.min_price);
  if (searchParams.max_price) filters.max_price = Number(searchParams.max_price);
  if (searchParams.min_bedrooms) filters.min_bedrooms = Number(searchParams.min_bedrooms);
  if (searchParams.max_bedrooms) filters.max_bedrooms = Number(searchParams.max_bedrooms);
  
  const sort = (searchParams.sort as SortOption) || 'newest';
  const page = Number(searchParams.page) || 1;
  
  try {
    const result = await mockAPI.getProperties(filters, sort, page, 12);
    return result;
  } catch (error) {
    console.error('Failed to fetch properties:', error);
    return {
      data: [],
      pagination: {
        page: 1,
        limit: 12,
        total: 0,
        total_pages: 0,
      },
      success: false,
    };
  }
}

export default async function PropertiesPage({ searchParams }: PropertiesPageProps) {
  const result = await getProperties(searchParams);
  
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
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
              Properties for Sale
            </h1>
            <p className="text-gray-600">
              Browse {result.pagination.total.toLocaleString()} properties across Malta with investment analysis
            </p>
          </div>
        </div>
        
        {/* Filters */}
        <div className="container-main py-6">
          <PropertyFilters />
        </div>
        
        {/* Results */}
        <div className="container-main pb-12">
          <Suspense fallback={<PropertyListSkeleton />}>
            <PropertyList 
              properties={result.data} 
              emptyMessage="No properties match your filters. Try adjusting your search criteria."
            />
          </Suspense>
          
          {/* Pagination */}
          {result.pagination.total_pages > 1 && (
            <div className="mt-12">
              <Pagination
                currentPage={result.pagination.page}
                totalPages={result.pagination.total_pages}
                totalItems={result.pagination.total}
              />
            </div>
          )}
        </div>
      </div>
    </>
  );
}
