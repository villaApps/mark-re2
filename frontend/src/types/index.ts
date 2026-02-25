import { z } from 'zod';

// Property Types
export const PropertyTypeSchema = z.enum([
  'apartment',
  'penthouse',
  'maisonette',
  'townhouse',
  'villa',
  'bungalow',
  'studio',
  'duplex',
]);

export type PropertyType = z.infer<typeof PropertyTypeSchema>;

// Location Types
export const LocationSchema = z.enum([
  'valletta',
  'sliema',
  'st_julians',
  'gzira',
  'msida',
  'ta_xbiex',
  'bugibba',
  'qawra',
  'mellieha',
  'mosta',
  'naxxar',
  'attard',
  'balzan',
  'lija',
  'iklin',
  'swieqi',
  'pembroke',
  'san_gwann',
  'birkirkara',
  'siggiewi',
  'zabbar',
  'zejtun',
  'marsaskala',
  'marsaxlokk',
  'gozo',
]);

export type Location = z.infer<typeof LocationSchema>;

// Property Status
export const PropertyStatusSchema = z.enum([
  'for_sale',
  'for_rent',
  'sold',
  'under_offer',
]);

export type PropertyStatus = z.infer<typeof PropertyStatusSchema>;

// Property Schema
export const PropertySchema = z.object({
  id: z.string(),
  title: z.string(),
  description: z.string(),
  price: z.number().positive(),
  price_currency: z.string().default('EUR'),
  location: LocationSchema,
  address: z.string(),
  property_type: PropertyTypeSchema,
  bedrooms: z.number().int().min(0),
  bathrooms: z.number().int().min(0),
  sqm: z.number().positive(),
  status: PropertyStatusSchema,
  images: z.array(z.string()).default([]),
  features: z.array(z.string()).default([]),
  year_built: z.number().int().optional(),
  floor: z.number().int().optional(),
  total_floors: z.number().int().optional(),
  parking_spaces: z.number().int().min(0).default(0),
  has_elevator: z.boolean().default(false),
  has_pool: z.boolean().default(false),
  has_garden: z.boolean().default(false),
  furnished: z.enum(['furnished', 'unfurnished', 'partly_furnished']).optional(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
  agent_name: z.string().optional(),
  agent_phone: z.string().optional(),
  agent_email: z.string().email().optional(),
  external_url: z.string().url().optional(),
  source: z.string().optional(),
});

export type Property = z.infer<typeof PropertySchema>;

// ROI Analysis Types
export const ROIAnalysisSchema = z.object({
  property_id: z.string(),
  estimated_monthly_rent: z.number().positive(),
  estimated_annual_rent: z.number().positive(),
  gross_rental_yield: z.number(),
  net_rental_yield: z.number(),
  cap_rate: z.number(),
  cash_on_cash_return: z.number(),
  opportunity_score: z.number().min(0).max(100),
  price_per_sqm: z.number().positive(),
  rent_per_sqm: z.number().positive(),
  market_comparison: z.object({
    avg_price_per_sqm: z.number().positive(),
    avg_rent_per_sqm: z.number().positive(),
    price_vs_market: z.number(),
    rent_vs_market: z.number(),
  }),
  cash_flow_projections: z.array(z.object({
    year: z.number().int().positive(),
    rental_income: z.number(),
    expenses: z.number(),
    net_income: z.number(),
    cumulative_return: z.number(),
  })),
  assumptions: z.object({
    down_payment_percent: z.number().min(0).max(100),
    interest_rate: z.number().min(0),
    loan_term_years: z.number().int().positive(),
    vacancy_rate: z.number().min(0).max(100),
    maintenance_percent: z.number().min(0).max(100),
    property_management_percent: z.number().min(0).max(100),
    property_tax_annual: z.number().min(0),
    insurance_annual: z.number().min(0),
  }),
  calculated_at: z.string().datetime(),
});

export type ROIAnalysis = z.infer<typeof ROIAnalysisSchema>;

// ROI Calculator Input
export const ROICalculatorInputSchema = z.object({
  property_id: z.string(),
  purchase_price: z.number().positive(),
  down_payment_percent: z.number().min(0).max(100).default(20),
  interest_rate: z.number().min(0).default(4.5),
  loan_term_years: z.number().int().positive().default(25),
  monthly_rent: z.number().positive(),
  vacancy_rate: z.number().min(0).max(100).default(5),
  maintenance_percent: z.number().min(0).max(100).default(10),
  property_management_percent: z.number().min(0).max(100).default(8),
  property_tax_annual: z.number().min(0).default(0),
  insurance_annual: z.number().min(0).default(500),
  appreciation_rate: z.number().default(2),
});

export type ROICalculatorInput = z.infer<typeof ROICalculatorInputSchema>;

// Filter Types
export const PropertyFilterSchema = z.object({
  location: LocationSchema.optional(),
  property_type: PropertyTypeSchema.optional(),
  min_price: z.number().positive().optional(),
  max_price: z.number().positive().optional(),
  min_bedrooms: z.number().int().min(0).optional(),
  max_bedrooms: z.number().int().min(0).optional(),
  min_sqm: z.number().positive().optional(),
  max_sqm: z.number().positive().optional(),
  has_parking: z.boolean().optional(),
  has_pool: z.boolean().optional(),
  furnished: z.enum(['furnished', 'unfurnished', 'partly_furnished']).optional(),
});

export type PropertyFilter = z.infer<typeof PropertyFilterSchema>;

// Sort Options
export const SortOptionSchema = z.enum([
  'price_asc',
  'price_desc',
  'newest',
  'roi_desc',
  'sqm_asc',
  'sqm_desc',
]);

export type SortOption = z.infer<typeof SortOptionSchema>;

// Pagination
export const PaginationSchema = z.object({
  page: z.number().int().positive().default(1),
  limit: z.number().int().positive().default(12),
  total: z.number().int().nonnegative(),
  total_pages: z.number().int().nonnegative(),
});

export type Pagination = z.infer<typeof PaginationSchema>;

// API Response Types
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: Pagination;
  success: boolean;
}

// Market Statistics
export interface MarketStats {
  total_properties: number;
  avg_price: number;
  avg_price_per_sqm: number;
  avg_rental_yield: number;
  location_stats: LocationStat[];
  price_trends: PriceTrend[];
}

export interface LocationStat {
  location: Location;
  property_count: number;
  avg_price: number;
  avg_price_per_sqm: number;
  avg_rental_yield: number;
  price_change_percent: number;
}

export interface PriceTrend {
  month: string;
  avg_price: number;
  transaction_count: number;
}

// Opportunity
export interface Opportunity {
  property: Property;
  roi_analysis: ROIAnalysis;
  rank: number;
}

// Navigation Item
export interface NavItem {
  label: string;
  href: string;
  icon?: string;
}

// SEO Metadata
export interface SEOMetadata {
  title: string;
  description: string;
  keywords?: string[];
  ogImage?: string;
  canonical?: string;
}

// Structured Data for Properties (JSON-LD)
export interface PropertyStructuredData {
  '@context': 'https://schema.org';
  '@type': 'RealEstateListing';
  name: string;
  description: string;
  url: string;
  image: string[];
  address: {
    '@type': 'PostalAddress';
    addressLocality: string;
    addressCountry: 'MT';
    streetAddress: string;
  };
  price: string;
  priceCurrency: string;
  numberOfRooms: number;
  numberOfBathroomsTotal: number;
  floorSize: {
    '@type': 'QuantitativeValue';
    value: number;
    unitCode: 'MTK';
  };
}
