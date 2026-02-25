'use client';

import React from 'react';
import { Property, Location } from '@/types';
import { formatLocation } from '@/lib/utils';
import { MapPin, Home } from 'lucide-react';

interface PropertyMapProps {
  property?: Property;
  properties?: Property[];
  center?: { lat: number; lng: number };
  zoom?: number;
  height?: string;
  className?: string;
}

// Location coordinates for Malta
const LOCATION_COORDINATES: Record<Location, { lat: number; lng: number }> = {
  valletta: { lat: 35.8989, lng: 14.5146 },
  sliema: { lat: 35.9122, lng: 14.5047 },
  st_julians: { lat: 35.9180, lng: 14.4890 },
  gzira: { lat: 35.9058, lng: 14.4953 },
  msida: { lat: 35.8978, lng: 14.4894 },
  ta_xbiex: { lat: 35.8992, lng: 14.4944 },
  bugibba: { lat: 35.9496, lng: 14.4144 },
  qawra: { lat: 35.9556, lng: 14.4236 },
  mellieha: { lat: 35.9564, lng: 14.3661 },
  mosta: { lat: 35.9142, lng: 14.4258 },
  naxxar: { lat: 35.9136, lng: 14.4436 },
  attard: { lat: 35.8897, lng: 14.4425 },
  balzan: { lat: 35.8958, lng: 14.4533 },
  lija: { lat: 35.9011, lng: 14.4436 },
  iklin: { lat: 35.9044, lng: 14.4561 },
  swieqi: { lat: 35.9194, lng: 14.4750 },
  pembroke: { lat: 35.9278, lng: 14.4811 },
  san_gwann: { lat: 35.9086, lng: 14.4769 },
  birkirkara: { lat: 35.8953, lng: 14.4611 },
  siggiewi: { lat: 35.8556, lng: 14.4364 },
  zabbar: { lat: 35.8761, lng: 14.5350 },
  zejtun: { lat: 35.8558, lng: 14.5333 },
  marsaskala: { lat: 35.8622, lng: 14.5675 },
  marsaxlokk: { lat: 35.8419, lng: 14.5431 },
  gozo: { lat: 36.0443, lng: 14.2515 },
};

export default function PropertyMap({
  property,
  properties,
  center,
  zoom = 13,
  height = '400px',
  className,
}: PropertyMapProps) {
  // Determine center point
  const mapCenter = center || (property
    ? LOCATION_COORDINATES[property.location]
    : { lat: 35.8992, lng: 14.4944 } // Default to Ta' Xbiex (central)
  );
  
  // Get properties to display
  const displayProperties = properties || (property ? [property] : []);
  
  return (
    <div className={className} style={{ height }}>
      <div className="relative w-full h-full rounded-xl overflow-hidden bg-gray-100">
        {/* Map Placeholder with Location Info */}
        <div className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center">
          <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mb-4">
            <MapPin className="w-8 h-8 text-primary-600" />
          </div>
          
          {property ? (
            <>
              <h3 className="text-lg font-semibold text-gray-900 mb-1">
                {formatLocation(property.location)}
              </h3>
              <p className="text-gray-600 mb-4">{property.address}</p>
              <a
                href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
                  `${property.address}, ${formatLocation(property.location)}, Malta`
                )}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                <MapPin className="w-4 h-4" />
                View on Google Maps
              </a>
            </>
          ) : displayProperties.length > 0 ? (
            <>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {displayProperties.length} Properties
              </h3>
              <div className="flex flex-wrap justify-center gap-2 mb-4">
                {Array.from(new Set(displayProperties.map(p => p.location))).map((loc) => (
                  <span
                    key={loc}
                    className="px-3 py-1 bg-white rounded-full text-sm text-gray-700 shadow-sm"
                  >
                    {formatLocation(loc)}
                  </span>
                ))}
              </div>
              <a
                href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
                  'Malta real estate'
                )}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                <Home className="w-4 h-4" />
                Explore on Map
              </a>
            </>
          ) : (
            <>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Map View
              </h3>
              <p className="text-gray-600 mb-4">
                Explore properties across Malta
              </p>
              <a
                href="https://www.google.com/maps/place/Malta"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                <MapPin className="w-4 h-4" />
                Open Malta Map
              </a>
            </>
          )}
        </div>
        
        {/* Decorative background pattern */}
        <div className="absolute inset-0 opacity-5 pointer-events-none">
          <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
            <defs>
              <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
                <path d="M 10 0 L 0 0 0 10" fill="none" stroke="currentColor" strokeWidth="0.5"/>
              </pattern>
            </defs>
            <rect width="100" height="100" fill="url(#grid)" />
          </svg>
        </div>
      </div>
    </div>
  );
}
