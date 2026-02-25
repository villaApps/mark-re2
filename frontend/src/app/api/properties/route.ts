import { NextRequest, NextResponse } from 'next/server';
import { mockAPI } from '@/lib/api';
import { PropertyFilter, SortOption } from '@/types';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    
    // Parse filters
    const filters: PropertyFilter = {};
    const location = searchParams.get('location');
    const propertyType = searchParams.get('property_type');
    const minPrice = searchParams.get('min_price');
    const maxPrice = searchParams.get('max_price');
    const minBedrooms = searchParams.get('min_bedrooms');
    const maxBedrooms = searchParams.get('max_bedrooms');
    const minSqm = searchParams.get('min_sqm');
    const maxSqm = searchParams.get('max_sqm');
    
    if (location) filters.location = location as any;
    if (propertyType) filters.property_type = propertyType as any;
    if (minPrice) filters.min_price = Number(minPrice);
    if (maxPrice) filters.max_price = Number(maxPrice);
    if (minBedrooms) filters.min_bedrooms = Number(minBedrooms);
    if (maxBedrooms) filters.max_bedrooms = Number(maxBedrooms);
    if (minSqm) filters.min_sqm = Number(minSqm);
    if (maxSqm) filters.max_sqm = Number(maxSqm);
    
    // Parse pagination and sort
    const sort = (searchParams.get('sort') as SortOption) || 'newest';
    const page = Number(searchParams.get('page')) || 1;
    const limit = Math.min(Number(searchParams.get('limit')) || 12, 100);
    
    // Fetch properties
    const result = await mockAPI.getProperties(filters, sort, page, limit);
    
    return NextResponse.json(result, {
      headers: {
        'Cache-Control': 'public, max-age=300, stale-while-revalidate=600',
      },
    });
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      {
        success: false,
        message: 'Failed to fetch properties',
        error: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
