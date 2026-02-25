import {
  Property,
  PropertyFilter,
  SortOption,
  PaginatedResponse,
  ApiResponse,
  ROIAnalysis,
  ROICalculatorInput,
  MarketStats,
  Opportunity,
  Pagination,
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Error class for API errors
export class APIError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public response?: Response
  ) {
    super(message);
    this.name = 'APIError';
  }
}

// Generic fetch function with error handling
async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  };
  
  const response = await fetch(url, {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
    },
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new APIError(
      errorData.message || `API Error: ${response.statusText}`,
      response.status,
      response
    );
  }
  
  return response.json();
}

// Build query string from filters
function buildQueryString(
  filters?: PropertyFilter,
  sort?: SortOption,
  pagination?: { page?: number; limit?: number }
): string {
  const params = new URLSearchParams();
  
  if (filters) {
    if (filters.location) params.append('location', filters.location);
    if (filters.property_type) params.append('property_type', filters.property_type);
    if (filters.min_price) params.append('min_price', filters.min_price.toString());
    if (filters.max_price) params.append('max_price', filters.max_price.toString());
    if (filters.min_bedrooms !== undefined) params.append('min_bedrooms', filters.min_bedrooms.toString());
    if (filters.max_bedrooms !== undefined) params.append('max_bedrooms', filters.max_bedrooms.toString());
    if (filters.min_sqm) params.append('min_sqm', filters.min_sqm.toString());
    if (filters.max_sqm) params.append('max_sqm', filters.max_sqm.toString());
    if (filters.has_parking !== undefined) params.append('has_parking', filters.has_parking.toString());
    if (filters.has_pool !== undefined) params.append('has_pool', filters.has_pool.toString());
    if (filters.furnished) params.append('furnished', filters.furnished);
  }
  
  if (sort) params.append('sort', sort);
  if (pagination?.page) params.append('page', pagination.page.toString());
  if (pagination?.limit) params.append('limit', pagination.limit.toString());
  
  const queryString = params.toString();
  return queryString ? `?${queryString}` : '';
}

// Property API
export const propertyAPI = {
  // Get all properties with filters
  async getProperties(
    filters?: PropertyFilter,
    sort?: SortOption,
    page = 1,
    limit = 12
  ): Promise<PaginatedResponse<Property>> {
    const queryString = buildQueryString(filters, sort, { page, limit });
    return fetchAPI<PaginatedResponse<Property>>(`/api/properties${queryString}`);
  },
  
  // Get single property by ID
  async getProperty(id: string): Promise<ApiResponse<Property>> {
    return fetchAPI<ApiResponse<Property>>(`/api/properties/${id}`);
  },
  
  // Get featured properties
  async getFeaturedProperties(limit = 6): Promise<ApiResponse<Property[]>> {
    return fetchAPI<ApiResponse<Property[]>>(`/api/properties/featured?limit=${limit}`);
  },
  
  // Get similar properties
  async getSimilarProperties(id: string, limit = 4): Promise<ApiResponse<Property[]>> {
    return fetchAPI<ApiResponse<Property[]>>(`/api/properties/${id}/similar?limit=${limit}`);
  },
};

// ROI API
export const roiAPI = {
  // Get ROI analysis for a property
  async getROIAnalysis(propertyId: string): Promise<ApiResponse<ROIAnalysis>> {
    return fetchAPI<ApiResponse<ROIAnalysis>>(`/api/properties/${propertyId}/roi`);
  },
  
  // Calculate custom ROI
  async calculateROI(input: ROICalculatorInput): Promise<ApiResponse<ROIAnalysis>> {
    return fetchAPI<ApiResponse<ROIAnalysis>>(`/api/properties/${input.property_id}/roi/calculate`, {
      method: 'POST',
      body: JSON.stringify(input),
    });
  },
};

// Opportunities API
export const opportunitiesAPI = {
  // Get top opportunities
  async getOpportunities(
    limit = 20,
    filters?: PropertyFilter
  ): Promise<ApiResponse<Opportunity[]>> {
    const queryString = buildQueryString(filters, undefined, { limit });
    return fetchAPI<ApiResponse<Opportunity[]>>(`/api/opportunities${queryString}`);
  },
};

// Market Stats API
export const statsAPI = {
  // Get market statistics
  async getMarketStats(): Promise<ApiResponse<MarketStats>> {
    return fetchAPI<ApiResponse<MarketStats>>('/api/stats');
  },
  
  // Get location statistics
  async getLocationStats(location: string): Promise<ApiResponse<MarketStats['location_stats'][0]>> {
    return fetchAPI<ApiResponse<MarketStats['location_stats'][0]>>(`/api/stats/location/${location}`);
  },
};

// Mock data for development
export const mockData = {
  properties: [
    {
      id: 'prop-001',
      title: 'Modern 2-Bedroom Apartment in Sliema',
      description: 'Beautiful modern apartment in the heart of Sliema, close to all amenities and the seafront.',
      price: 350000,
      price_currency: 'EUR',
      location: 'sliema' as const,
      address: '123 High Street, Sliema',
      property_type: 'apartment' as const,
      bedrooms: 2,
      bathrooms: 2,
      sqm: 95,
      status: 'for_sale' as const,
      images: ['https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800'],
      features: ['Sea View', 'Air Conditioning', 'Fully Equipped Kitchen'],
      year_built: 2015,
      floor: 3,
      total_floors: 6,
      parking_spaces: 1,
      has_elevator: true,
      has_pool: false,
      has_garden: false,
      furnished: 'furnished' as const,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'prop-002',
      title: 'Spacious 3-Bedroom Penthouse in St. Julian\'s',
      description: 'Luxury penthouse with panoramic views, private terrace, and modern finishes.',
      price: 650000,
      price_currency: 'EUR',
      location: 'st_julians' as const,
      address: '45 Tower Road, St. Julian\'s',
      property_type: 'penthouse' as const,
      bedrooms: 3,
      bathrooms: 3,
      sqm: 150,
      status: 'for_sale' as const,
      images: ['https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800'],
      features: ['Terrace', 'Sea View', 'Jacuzzi', 'Smart Home'],
      year_built: 2019,
      floor: 8,
      total_floors: 8,
      parking_spaces: 2,
      has_elevator: true,
      has_pool: true,
      has_garden: false,
      furnished: 'furnished' as const,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'prop-003',
      title: 'Charming Townhouse in Valletta',
      description: 'Traditional Mal townhouse with modern renovation, located in a quiet street.',
      price: 480000,
      price_currency: 'EUR',
      location: 'valletta' as const,
      address: '78 Old Bakery Street, Valletta',
      property_type: 'townhouse' as const,
      bedrooms: 3,
      bathrooms: 2,
      sqm: 120,
      status: 'for_sale' as const,
      images: ['https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800'],
      features: ['Traditional Features', 'Roof Terrace', 'Central Location'],
      year_built: 1850,
      floor: 0,
      total_floors: 3,
      parking_spaces: 0,
      has_elevator: false,
      has_pool: false,
      has_garden: true,
      furnished: 'unfurnished' as const,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'prop-004',
      title: 'Seafront Villa in Mellieha',
      description: 'Stunning seafront villa with private pool and direct beach access.',
      price: 1200000,
      price_currency: 'EUR',
      location: 'mellieha' as const,
      address: '12 Golden Bay Road, Mellieha',
      property_type: 'villa' as const,
      bedrooms: 5,
      bathrooms: 4,
      sqm: 350,
      status: 'for_sale' as const,
      images: ['https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=800'],
      features: ['Private Pool', 'Sea Access', 'Garden', 'Garage'],
      year_built: 2005,
      floor: 0,
      total_floors: 2,
      parking_spaces: 3,
      has_elevator: false,
      has_pool: true,
      has_garden: true,
      furnished: 'partly_furnished' as const,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'prop-005',
      title: 'Studio Apartment in Gzira',
      description: 'Compact studio perfect for investment, close to university and amenities.',
      price: 165000,
      price_currency: 'EUR',
      location: 'gzira' as const,
      address: '89 Rue d\'Argens, Gzira',
      property_type: 'studio' as const,
      bedrooms: 0,
      bathrooms: 1,
      sqm: 45,
      status: 'for_sale' as const,
      images: ['https://images.unsplash.com/photo-1536376072261-38c75010e6c9?w=800'],
      features: ['Investment Property', 'Central Location'],
      year_built: 2010,
      floor: 2,
      total_floors: 5,
      parking_spaces: 0,
      has_elevator: true,
      has_pool: false,
      has_garden: false,
      furnished: 'furnished' as const,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'prop-006',
      title: 'Luxury Maisonette in Swieqi',
      description: 'Elegant maisonette in a quiet residential area with private entrance.',
      price: 420000,
      price_currency: 'EUR',
      location: 'swieqi' as const,
      address: '34 Triq il-Qasam, Swieqi',
      property_type: 'maisonette' as const,
      bedrooms: 3,
      bathrooms: 2,
      sqm: 140,
      status: 'for_sale' as const,
      images: ['https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800'],
      features: ['Private Entrance', 'Backyard', 'Modern Kitchen'],
      year_built: 2012,
      floor: 0,
      total_floors: 2,
      parking_spaces: 1,
      has_elevator: false,
      has_pool: false,
      has_garden: true,
      furnished: 'partly_furnished' as const,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ],
  
  roiAnalysis: {
    property_id: 'prop-001',
    estimated_monthly_rent: 1400,
    estimated_annual_rent: 16800,
    gross_rental_yield: 4.8,
    net_rental_yield: 3.9,
    cap_rate: 4.2,
    cash_on_cash_return: 8.5,
    opportunity_score: 78,
    price_per_sqm: 3684,
    rent_per_sqm: 14.74,
    market_comparison: {
      avg_price_per_sqm: 4000,
      avg_rent_per_sqm: 14,
      price_vs_market: -7.9,
      rent_vs_market: 5.3,
    },
    cash_flow_projections: Array.from({ length: 10 }, (_, i) => ({
      year: i + 1,
      rental_income: 16800 * Math.pow(1.02, i),
      expenses: 4200 * Math.pow(1.03, i),
      net_income: (16800 * Math.pow(1.02, i)) - (4200 * Math.pow(1.03, i)),
      cumulative_return: 0,
    })).map((item, i, arr) => ({
      ...item,
      cumulative_return: arr.slice(0, i + 1).reduce((sum, curr) => sum + curr.net_income, 0),
    })),
    assumptions: {
      down_payment_percent: 20,
      interest_rate: 4.5,
      loan_term_years: 25,
      vacancy_rate: 5,
      maintenance_percent: 10,
      property_management_percent: 8,
      property_tax_annual: 0,
      insurance_annual: 500,
    },
    calculated_at: new Date().toISOString(),
  },
  
  marketStats: {
    total_properties: 2456,
    avg_price: 425000,
    avg_price_per_sqm: 3850,
    avg_rental_yield: 4.2,
    location_stats: [
      { location: 'sliema' as const, property_count: 342, avg_price: 520000, avg_price_per_sqm: 5200, avg_rental_yield: 4.5, price_change_percent: 3.2 },
      { location: 'st_julians' as const, property_count: 298, avg_price: 580000, avg_price_per_sqm: 5500, avg_rental_yield: 4.8, price_change_percent: 4.1 },
      { location: 'valletta' as const, property_count: 156, avg_price: 650000, avg_price_per_sqm: 6200, avg_rental_yield: 3.8, price_change_percent: 2.5 },
      { location: 'gzira' as const, property_count: 245, avg_price: 320000, avg_price_per_sqm: 3500, avg_rental_yield: 5.2, price_change_percent: 5.1 },
      { location: 'mellieha' as const, property_count: 189, avg_price: 480000, avg_price_per_sqm: 3800, avg_rental_yield: 3.5, price_change_percent: 1.8 },
    ],
    price_trends: Array.from({ length: 12 }, (_, i) => ({
      month: new Date(2024, i, 1).toISOString().slice(0, 7),
      avg_price: 400000 + Math.random() * 50000,
      transaction_count: Math.floor(100 + Math.random() * 200),
    })),
  },
};

// Mock API for development
export const mockAPI = {
  async getProperties(
    filters?: PropertyFilter,
    sort?: SortOption,
    page = 1,
    limit = 12
  ): Promise<PaginatedResponse<Property>> {
    let filtered = [...mockData.properties];
    
    if (filters) {
      if (filters.location) {
        filtered = filtered.filter(p => p.location === filters.location);
      }
      if (filters.property_type) {
        filtered = filtered.filter(p => p.property_type === filters.property_type);
      }
      if (filters.min_price) {
        filtered = filtered.filter(p => p.price >= filters.min_price!);
      }
      if (filters.max_price) {
        filtered = filtered.filter(p => p.price <= filters.max_price!);
      }
      if (filters.min_bedrooms !== undefined) {
        filtered = filtered.filter(p => p.bedrooms >= filters.min_bedrooms!);
      }
      if (filters.max_bedrooms !== undefined) {
        filtered = filtered.filter(p => p.bedrooms <= filters.max_bedrooms!);
      }
    }
    
    // Sort
    if (sort === 'price_asc') {
      filtered.sort((a, b) => a.price - b.price);
    } else if (sort === 'price_desc') {
      filtered.sort((a, b) => b.price - a.price);
    } else if (sort === 'newest') {
      filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
    }
    
    const total = filtered.length;
    const total_pages = Math.ceil(total / limit);
    const start = (page - 1) * limit;
    const paginated = filtered.slice(start, start + limit);
    
    return {
      data: paginated,
      pagination: {
        page,
        limit,
        total,
        total_pages,
      },
      success: true,
    };
  },
  
  async getProperty(id: string): Promise<ApiResponse<Property>> {
    const property = mockData.properties.find(p => p.id === id);
    if (!property) {
      throw new APIError('Property not found', 404);
    }
    return {
      data: property,
      success: true,
    };
  },
  
  async getROIAnalysis(propertyId: string): Promise<ApiResponse<ROIAnalysis>> {
    return {
      data: { ...mockData.roiAnalysis, property_id: propertyId },
      success: true,
    };
  },
  
  async getOpportunities(): Promise<ApiResponse<Opportunity[]>> {
    const opportunities = mockData.properties.map((property, index) => ({
      property,
      roi_analysis: { ...mockData.roiAnalysis, opportunity_score: 85 - index * 5 },
      rank: index + 1,
    }));
    
    return {
      data: opportunities,
      success: true,
    };
  },
  
  async getMarketStats(): Promise<ApiResponse<MarketStats>> {
    return {
      data: mockData.marketStats,
      success: true,
    };
  },
};
