import { Location, PropertyType, NavItem } from '@/types';

// App Metadata
export const APP_NAME = 'Malta Property Investment Analyzer';
export const APP_DESCRIPTION = 'Find high-ROI real estate investment opportunities in Malta with our advanced property analysis tools.';
export const APP_URL = process.env.NEXT_PUBLIC_APP_URL || 'https://malta-property-analyzer.com';

// Navigation
export const NAV_ITEMS: NavItem[] = [
  { label: 'Home', href: '/' },
  { label: 'Properties', href: '/properties' },
  { label: 'Opportunities', href: '/opportunities' },
  { label: 'Market Stats', href: '/stats' },
  { label: 'About', href: '/about' },
];

// Locations with display names
export const LOCATIONS: Record<Location, string> = {
  valletta: 'Valletta',
  sliema: 'Sliema',
  st_julians: 'St. Julian\'s',
  gzira: 'Gzira',
  msida: 'Msida',
  ta_xbiex: 'Ta\' Xbiex',
  bugibba: 'Bugibba',
  qawra: 'Qawra',
  mellieha: 'Mellieha',
  mosta: 'Mosta',
  naxxar: 'Naxxar',
  attard: 'Attard',
  balzan: 'Balzan',
  lija: 'Lija',
  iklin: 'Iklin',
  swieqi: 'Swieqi',
  pembroke: 'Pembroke',
  san_gwann: 'San Gwann',
  birkirkara: 'Birkirkara',
  siggiewi: 'Siggiewi',
  zabbar: 'Zabbar',
  zejtun: 'Zejtun',
  marsaskala: 'Marsaskala',
  marsaxlokk: 'Marsaxlokk',
  gozo: 'Gozo',
};

// Property types with display names
export const PROPERTY_TYPES: Record<PropertyType, string> = {
  apartment: 'Apartment',
  penthouse: 'Penthouse',
  maisonette: 'Maisonette',
  townhouse: 'Townhouse',
  villa: 'Villa',
  bungalow: 'Bungalow',
  studio: 'Studio',
  duplex: 'Duplex',
};

// Price ranges for filters
export const PRICE_RANGES = [
  { min: 0, max: 200000, label: 'Under €200,000' },
  { min: 200000, max: 300000, label: '€200,000 - €300,000' },
  { min: 300000, max: 400000, label: '€300,000 - €400,000' },
  { min: 400000, max: 500000, label: '€400,000 - €500,000' },
  { min: 500000, max: 750000, label: '€500,000 - €750,000' },
  { min: 750000, max: 1000000, label: '€750,000 - €1,000,000' },
  { min: 1000000, max: Infinity, label: 'Over €1,000,000' },
];

// Bedroom options
export const BEDROOM_OPTIONS = [
  { value: 0, label: 'Studio' },
  { value: 1, label: '1 Bedroom' },
  { value: 2, label: '2 Bedrooms' },
  { value: 3, label: '3 Bedrooms' },
  { value: 4, label: '4 Bedrooms' },
  { value: 5, label: '5+ Bedrooms' },
];

// Sort options
export const SORT_OPTIONS = [
  { value: 'newest', label: 'Newest First' },
  { value: 'price_asc', label: 'Price: Low to High' },
  { value: 'price_desc', label: 'Price: High to Low' },
  { value: 'roi_desc', label: 'Highest ROI' },
  { value: 'sqm_asc', label: 'Size: Small to Large' },
  { value: 'sqm_desc', label: 'Size: Large to Small' },
];

// Default ROI Calculator Values
export const DEFAULT_ROI_VALUES = {
  down_payment_percent: 20,
  interest_rate: 4.5,
  loan_term_years: 25,
  vacancy_rate: 5,
  maintenance_percent: 10,
  property_management_percent: 8,
  property_tax_annual: 0,
  insurance_annual: 500,
  appreciation_rate: 2,
};

// Opportunity Score Thresholds
export const OPPORTUNITY_SCORE_THRESHOLDS = {
  excellent: 85,
  good: 70,
  fair: 55,
  poor: 40,
};

// Colors for opportunity scores
export const SCORE_COLORS = {
  excellent: 'bg-success-500',
  good: 'bg-primary-500',
  fair: 'bg-warning-500',
  poor: 'bg-danger-500',
};

// API Endpoints
export const API_ENDPOINTS = {
  properties: '/api/properties',
  property: (id: string) => `/api/properties/${id}`,
  roi: (id: string) => `/api/properties/${id}/roi`,
  opportunities: '/api/opportunities',
  stats: '/api/stats',
};

// Cache durations (in seconds)
export const CACHE_DURATIONS = {
  properties: 300, // 5 minutes
  property: 600, // 10 minutes
  roi: 300,
  opportunities: 600,
  stats: 3600, // 1 hour
};

// Pagination defaults
export const PAGINATION_DEFAULTS = {
  page: 1,
  limit: 12,
  max_limit: 100,
};

// Currency formatting
export const CURRENCY_FORMAT = new Intl.NumberFormat('en-MT', {
  style: 'currency',
  currency: 'EUR',
  minimumFractionDigits: 0,
  maximumFractionDigits: 0,
});

// Number formatting
export const NUMBER_FORMAT = new Intl.NumberFormat('en-MT');

// Percentage formatting
export const PERCENT_FORMAT = new Intl.NumberFormat('en-MT', {
  style: 'percent',
  minimumFractionDigits: 1,
  maximumFractionDigits: 2,
});

// Date formatting
export const DATE_FORMAT = new Intl.DateTimeFormat('en-MT', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
});

// Social links
export const SOCIAL_LINKS = {
  facebook: 'https://facebook.com/maltapropertyanalyzer',
  twitter: 'https://twitter.com/maltaproperty',
  linkedin: 'https://linkedin.com/company/malta-property-analyzer',
  instagram: 'https://instagram.com/maltapropertyanalyzer',
};

// Contact info
export const CONTACT_INFO = {
  email: 'info@malta-property-analyzer.com',
  phone: '+356 1234 5678',
  address: '123 Investment Street, Valletta, Malta',
};

// Legal
export const LEGAL = {
  company_name: 'Malta Property Analyzer Ltd',
  vat_number: 'MT12345678',
  registration: 'C12345',
};
