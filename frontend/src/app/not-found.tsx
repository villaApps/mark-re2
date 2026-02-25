import Link from 'next/link';
import Button from '@/components/ui/Button';
import { Search, Home, ArrowLeft } from 'lucide-react';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Page Not Found',
  description: 'The page you are looking for does not exist.',
};

export default function NotFound() {
  return (
    <div className="flex-1 flex items-center justify-center min-h-[60vh] px-4">
      <div className="max-w-lg w-full text-center">
        {/* 404 Illustration */}
        <div className="relative mb-8">
          <div className="text-9xl font-bold text-gray-100 select-none">
            404
          </div>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-24 h-24 bg-primary-50 rounded-full flex items-center justify-center">
              <Search className="w-12 h-12 text-primary-600" />
            </div>
          </div>
        </div>
        
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Page Not Found
        </h1>
        
        <p className="text-lg text-gray-600 mb-8">
          Sorry, we couldn&apos;t find the page you&apos;re looking for. 
          It might have been moved, deleted, or never existed.
        </p>
        
        {/* Quick Links */}
        <div className="grid sm:grid-cols-2 gap-4 mb-8">
          <Link href="/">
            <Button fullWidth leftIcon={<Home className="w-4 h-4" />}>
              Back to Home
            </Button>
          </Link>
          <Link href="/properties">
            <Button variant="outline" fullWidth leftIcon={<Search className="w-4 h-4" />}>
              Browse Properties
            </Button>
          </Link>
        </div>
        
        {/* Helpful Links */}
        <div className="border-t border-gray-100 pt-8">
          <p className="text-sm text-gray-500 mb-4">You might want to check:</p>
          <div className="flex flex-wrap justify-center gap-3">
            <Link
              href="/properties"
              className="text-primary-600 hover:text-primary-700 text-sm font-medium"
            >
              All Properties
            </Link>
            <span className="text-gray-300">|</span>
            <Link
              href="/opportunities"
              className="text-primary-600 hover:text-primary-700 text-sm font-medium"
            >
              Top Opportunities
            </Link>
            <span className="text-gray-300">|</span>
            <Link
              href="/stats"
              className="text-primary-600 hover:text-primary-700 text-sm font-medium"
            >
              Market Stats
            </Link>
            <span className="text-gray-300">|</span>
            <Link
              href="/about"
              className="text-primary-600 hover:text-primary-700 text-sm font-medium"
            >
              About Us
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
