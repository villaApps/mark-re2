import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { CURRENCY_FORMAT, NUMBER_FORMAT, PERCENT_FORMAT, DATE_FORMAT } from './constants';
import { Location, PropertyType, Property, OPPORTUNITY_SCORE_THRESHOLDS, SCORE_COLORS } from '@/types';

// Tailwind class merging
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Format currency (EUR)
export function formatCurrency(value: number): string {
  return CURRENCY_FORMAT.format(value);
}

// Format number
export function formatNumber(value: number): string {
  return NUMBER_FORMAT.format(value);
}

// Format percentage
export function formatPercent(value: number): string {
  return PERCENT_FORMAT.format(value / 100);
}

// Format date
export function formatDate(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return DATE_FORMAT.format(d);
}

// Format location name
export function formatLocation(location: Location): string {
  const locationNames: Record<Location, string> = {
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
  return locationNames[location] || location;
}

// Format property type
export function formatPropertyType(type: PropertyType): string {
  const typeNames: Record<PropertyType, string> = {
    apartment: 'Apartment',
    penthouse: 'Penthouse',
    maisonette: 'Maisonette',
    townhouse: 'Townhouse',
    villa: 'Villa',
    bungalow: 'Bungalow',
    studio: 'Studio',
    duplex: 'Duplex',
  };
  return typeNames[type] || type;
}

// Get opportunity score color
export function getScoreColor(score: number): string {
  if (score >= OPPORTUNITY_SCORE_THRESHOLDS.excellent) return SCORE_COLORS.excellent;
  if (score >= OPPORTUNITY_SCORE_THRESHOLDS.good) return SCORE_COLORS.good;
  if (score >= OPPORTUNITY_SCORE_THRESHOLDS.fair) return SCORE_COLORS.fair;
  return SCORE_COLORS.poor;
}

// Get opportunity score label
export function getScoreLabel(score: number): string {
  if (score >= OPPORTUNITY_SCORE_THRESHOLDS.excellent) return 'Excellent';
  if (score >= OPPORTUNITY_SCORE_THRESHOLDS.good) return 'Good';
  if (score >= OPPORTUNITY_SCORE_THRESHOLDS.fair) return 'Fair';
  return 'Below Average';
}

// Calculate price per sqm
export function calculatePricePerSqm(price: number, sqm: number): number {
  if (sqm <= 0) return 0;
  return Math.round(price / sqm);
}

// Truncate text
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength).trim() + '...';
}

// Generate property slug
export function generatePropertySlug(property: Property): string {
  const location = formatLocation(property.location).toLowerCase().replace(/\s+/g, '-');
  const type = formatPropertyType(property.property_type).toLowerCase();
  return `${type}-${property.bedrooms}-bed-${location}-${property.id}`;
}

// Debounce function
export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

// Generate structured data for property (JSON-LD)
export function generatePropertyStructuredData(property: Property, baseUrl: string): object {
  return {
    '@context': 'https://schema.org',
    '@type': 'RealEstateListing',
    name: property.title,
    description: property.description,
    url: `${baseUrl}/properties/${property.id}`,
    image: property.images.length > 0 ? property.images : [`${baseUrl}/images/placeholder-property.jpg`],
    address: {
      '@type': 'PostalAddress',
      addressLocality: formatLocation(property.location),
      addressCountry: 'MT',
      streetAddress: property.address,
    },
    price: formatCurrency(property.price),
    priceCurrency: 'EUR',
    numberOfRooms: property.bedrooms,
    numberOfBathroomsTotal: property.bathrooms,
    floorSize: {
      '@type': 'QuantitativeValue',
      value: property.sqm,
      unitCode: 'MTK',
    },
    datePosted: property.created_at,
  };
}

// Calculate monthly mortgage payment
export function calculateMortgagePayment(
  principal: number,
  annualRate: number,
  years: number
): number {
  const monthlyRate = annualRate / 100 / 12;
  const numPayments = years * 12;
  
  if (monthlyRate === 0) {
    return principal / numPayments;
  }
  
  return (
    (principal * monthlyRate * Math.pow(1 + monthlyRate, numPayments)) /
    (Math.pow(1 + monthlyRate, numPayments) - 1)
  );
}

// Validate email
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

// Sleep utility
export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// Generate random ID
export function generateId(): string {
  return Math.random().toString(36).substring(2, 15);
}

// Parse query params
export function parseQueryParams<T extends Record<string, unknown>>(
  searchParams: URLSearchParams,
  defaults: T
): T {
  const result = { ...defaults };
  
  for (const key of Object.keys(defaults)) {
    const value = searchParams.get(key);
    if (value !== null) {
      const defaultValue = defaults[key];
      if (typeof defaultValue === 'number') {
        (result as Record<string, unknown>)[key] = Number(value);
      } else if (typeof defaultValue === 'boolean') {
        (result as Record<string, unknown>)[key] = value === 'true';
      } else {
        (result as Record<string, unknown>)[key] = value;
      }
    }
  }
  
  return result;
}
