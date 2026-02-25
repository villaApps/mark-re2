'use client';

import React from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { cn } from '@/lib/utils';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  totalItems: number;
  itemsPerPage?: number;
}

export default function Pagination({
  currentPage,
  totalPages,
  totalItems,
  itemsPerPage = 12,
}: PaginationProps) {
  const searchParams = useSearchParams();
  
  const getPageUrl = (page: number) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set('page', page.toString());
    return `?${params.toString()}`;
  };
  
  const startItem = (currentPage - 1) * itemsPerPage + 1;
  const endItem = Math.min(currentPage * itemsPerPage, totalItems);
  
  // Generate page numbers to display
  const getPageNumbers = () => {
    const pages: (number | string)[] = [];
    const maxVisible = 5;
    
    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Always show first page
      pages.push(1);
      
      if (currentPage > 3) {
        pages.push('...');
      }
      
      // Show pages around current
      const start = Math.max(2, currentPage - 1);
      const end = Math.min(totalPages - 1, currentPage + 1);
      
      for (let i = start; i <= end; i++) {
        if (!pages.includes(i)) {
          pages.push(i);
        }
      }
      
      if (currentPage < totalPages - 2) {
        pages.push('...');
      }
      
      // Always show last page
      if (!pages.includes(totalPages)) {
        pages.push(totalPages);
      }
    }
    
    return pages;
  };
  
  if (totalPages <= 1) return null;
  
  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
      {/* Results info */}
      <p className="text-sm text-gray-600">
        Showing <span className="font-medium">{startItem}</span> to{' '}
        <span className="font-medium">{endItem}</span> of{' '}
        <span className="font-medium">{totalItems.toLocaleString()}</span> results
      </p>
      
      {/* Page navigation */}
      <nav className="flex items-center gap-1" aria-label="Pagination">
        {/* Previous button */}
        <Link
          href={getPageUrl(currentPage - 1)}
          className={cn(
            'p-2 rounded-lg border transition-colors',
            currentPage === 1
              ? 'border-gray-100 text-gray-300 cursor-not-allowed'
              : 'border-gray-300 text-gray-600 hover:bg-gray-50 hover:border-gray-400'
          )}
          aria-label="Previous page"
          aria-disabled={currentPage === 1}
          onClick={(e) => currentPage === 1 && e.preventDefault()}
        >
          <ChevronLeft className="w-5 h-5" />
        </Link>
        
        {/* Page numbers */}
        {getPageNumbers().map((page, index) => {
          if (page === '...') {
            return (
              <span
                key={`ellipsis-${index}`}
                className="px-3 py-2 text-gray-400"
              >
                ...
              </span>
            );
          }
          
          const isActive = page === currentPage;
          
          return (
            <Link
              key={page}
              href={getPageUrl(page as number)}
              className={cn(
                'min-w-[40px] px-3 py-2 rounded-lg text-sm font-medium transition-colors text-center',
                isActive
                  ? 'bg-primary-600 text-white'
                  : 'border border-gray-300 text-gray-600 hover:bg-gray-50 hover:border-gray-400'
              )}
              aria-current={isActive ? 'page' : undefined}
              aria-label={`Page ${page}`}
            >
              {page}
            </Link>
          );
        })}
        
        {/* Next button */}
        <Link
          href={getPageUrl(currentPage + 1)}
          className={cn(
            'p-2 rounded-lg border transition-colors',
            currentPage === totalPages
              ? 'border-gray-100 text-gray-300 cursor-not-allowed'
              : 'border-gray-300 text-gray-600 hover:bg-gray-50 hover:border-gray-400'
          )}
          aria-label="Next page"
          aria-disabled={currentPage === totalPages}
          onClick={(e) => currentPage === totalPages && e.preventDefault()}
        >
          <ChevronRight className="w-5 h-5" />
        </Link>
      </nav>
    </div>
  );
}
