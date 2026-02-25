'use client';

import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { Property } from '@/types';
import { formatCurrency, formatLocation, formatPropertyType, getScoreColor, getScoreLabel } from '@/lib/utils';
import { Card } from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import { Bed, Bath, Square, MapPin, TrendingUp, Heart } from 'lucide-react';

interface PropertyCardProps {
  property: Property;
  opportunityScore?: number;
  showScore?: boolean;
  isFavorite?: boolean;
  onFavoriteToggle?: (id: string) => void;
}

export default function PropertyCard({
  property,
  opportunityScore,
  showScore = false,
  isFavorite = false,
  onFavoriteToggle,
}: PropertyCardProps) {
  const imageUrl = property.images[0] || '/images/placeholder-property.jpg';
  const pricePerSqm = Math.round(property.price / property.sqm);
  
  return (
    <Card hover className="h-full flex flex-col">
      {/* Image */}
      <div className="relative aspect-[4/3] overflow-hidden">
        <Link href={`/properties/${property.id}`}>
          <Image
            src={imageUrl}
            alt={property.title}
            fill
            className="object-cover transition-transform duration-300 hover:scale-105"
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
          />
        </Link>
        
        {/* Opportunity Score Badge */}
        {showScore && opportunityScore !== undefined && (
          <div className="absolute top-3 left-3">
            <Badge
              variant={opportunityScore >= 70 ? 'success' : opportunityScore >= 50 ? 'warning' : 'default'}
              className="flex items-center gap-1"
            >
              <TrendingUp className="w-3 h-3" />
              Score: {opportunityScore}
            </Badge>
          </div>
        )}
        
        {/* Favorite Button */}
        {onFavoriteToggle && (
          <button
            onClick={(e) => {
              e.preventDefault();
              onFavoriteToggle(property.id);
            }}
            className="absolute top-3 right-3 p-2 rounded-full bg-white/90 hover:bg-white transition-colors shadow-sm"
            aria-label={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
          >
            <Heart
              className={`w-4 h-4 ${isFavorite ? 'fill-danger-500 text-danger-500' : 'text-gray-600'}`}
            />
          </button>
        )}
        
        {/* Property Type Badge */}
        <div className="absolute bottom-3 left-3">
          <Badge variant="default" size="sm">
            {formatPropertyType(property.property_type)}
          </Badge>
        </div>
      </div>
      
      {/* Content */}
      <div className="flex-1 p-4 flex flex-col">
        {/* Location */}
        <div className="flex items-center gap-1 text-gray-500 text-sm mb-2">
          <MapPin className="w-4 h-4" />
          <span>{formatLocation(property.location)}</span>
        </div>
        
        {/* Title */}
        <Link href={`/properties/${property.id}`}>
          <h3 className="font-semibold text-gray-900 line-clamp-2 hover:text-primary-600 transition-colors mb-2">
            {property.title}
          </h3>
        </Link>
        
        {/* Features */}
        <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
          {property.bedrooms > 0 && (
            <div className="flex items-center gap-1">
              <Bed className="w-4 h-4" />
              <span>{property.bedrooms}</span>
            </div>
          )}
          <div className="flex items-center gap-1">
            <Bath className="w-4 h-4" />
            <span>{property.bathrooms}</span>
          </div>
          <div className="flex items-center gap-1">
            <Square className="w-4 h-4" />
            <span>{property.sqm} m²</span>
          </div>
        </div>
        
        {/* Price */}
        <div className="mt-auto pt-4 border-t border-gray-100">
          <div className="flex items-baseline justify-between">
            <div>
              <p className="text-2xl font-bold text-primary-600">
                {formatCurrency(property.price)}
              </p>
              <p className="text-sm text-gray-500">
                €{pricePerSqm.toLocaleString()}/m²
              </p>
            </div>
            
            {/* Opportunity Score (if shown) */}
            {showScore && opportunityScore !== undefined && (
              <div className="text-right">
                <div
                  className={`inline-flex items-center justify-center w-12 h-12 rounded-full text-white font-bold ${getScoreColor(opportunityScore)}`}
                >
                  {opportunityScore}
                </div>
                <p className="text-xs text-gray-500 mt-1">{getScoreLabel(opportunityScore)}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
}
