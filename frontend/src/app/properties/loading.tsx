import { PropertyListSkeleton } from '@/components/ui/Loading';

export default function PropertiesLoading() {
  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Header Skeleton */}
      <div className="bg-white border-b border-gray-100">
        <div className="container-main py-8">
          <div className="h-10 bg-gray-200 rounded w-1/3 mb-2 animate-pulse" />
          <div className="h-5 bg-gray-200 rounded w-1/2 animate-pulse" />
        </div>
      </div>
      
      {/* Filters Skeleton */}
      <div className="container-main py-6">
        <div className="h-16 bg-white rounded-xl shadow-sm animate-pulse" />
      </div>
      
      {/* Results Skeleton */}
      <div className="container-main pb-12">
        <PropertyListSkeleton count={12} />
      </div>
    </div>
  );
}
