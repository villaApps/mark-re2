'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { Loader2 } from 'lucide-react';

export interface LoadingProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
  fullScreen?: boolean;
}

const Loading = React.forwardRef<HTMLDivElement, LoadingProps>(
  (
    {
      className,
      size = 'md',
      text = 'Loading...',
      fullScreen = false,
      ...props
    },
    ref
  ) => {
    const sizes = {
      sm: 'h-4 w-4',
      md: 'h-8 w-8',
      lg: 'h-12 w-12',
    };
    
    const content = (
      <div
        ref={ref}
        className={cn(
          'flex flex-col items-center justify-center',
          fullScreen && 'fixed inset-0 bg-white/80 backdrop-blur-sm z-50',
          className
        )}
        {...props}
      >
        <Loader2 className={cn('animate-spin text-primary-600', sizes[size])} />
        {text && (
          <p className="mt-3 text-sm text-gray-600">{text}</p>
        )}
      </div>
    );
    
    return content;
  }
);

Loading.displayName = 'Loading';

// Skeleton loading component
export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'text' | 'circular' | 'rectangular' | 'rounded';
  width?: string | number;
  height?: string | number;
}

const Skeleton = React.forwardRef<HTMLDivElement, SkeletonProps>(
  (
    {
      className,
      variant = 'text',
      width,
      height,
      style,
      ...props
    },
    ref
  ) => {
    const variants = {
      text: 'rounded',
      circular: 'rounded-full',
      rectangular: 'rounded-none',
      rounded: 'rounded-lg',
    };
    
    return (
      <div
        ref={ref}
        className={cn(
          'animate-pulse bg-gray-200',
          variants[variant],
          className
        )}
        style={{
          width,
          height,
          ...style,
        }}
        {...props}
      />
    );
  }
);

Skeleton.displayName = 'Skeleton';

// Property card skeleton
export function PropertyCardSkeleton() {
  return (
    <div className="bg-white rounded-xl overflow-hidden shadow-sm border border-gray-100">
      <Skeleton variant="rectangular" height={200} className="w-full" />
      <div className="p-4">
        <Skeleton variant="text" width="70%" height={24} className="mb-2" />
        <Skeleton variant="text" width="50%" height={16} className="mb-4" />
        <div className="flex gap-2 mb-4">
          <Skeleton variant="rounded" width={60} height={24} />
          <Skeleton variant="rounded" width={60} height={24} />
          <Skeleton variant="rounded" width={60} height={24} />
        </div>
        <Skeleton variant="text" width="40%" height={28} />
      </div>
    </div>
  );
}

// List of property card skeletons
export function PropertyListSkeleton({ count = 6 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {Array.from({ length: count }).map((_, i) => (
        <PropertyCardSkeleton key={i} />
      ))}
    </div>
  );
}

export { Loading, Skeleton };
