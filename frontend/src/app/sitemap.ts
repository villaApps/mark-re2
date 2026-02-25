import { MetadataRoute } from 'next';
import { APP_URL } from '@/lib/constants';
import { mockAPI } from '@/lib/api';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  // Static routes
  const staticRoutes: MetadataRoute.Sitemap = [
    {
      url: APP_URL,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 1.0,
    },
    {
      url: `${APP_URL}/properties`,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 0.9,
    },
    {
      url: `${APP_URL}/opportunities`,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 0.9,
    },
    {
      url: `${APP_URL}/stats`,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 0.8,
    },
    {
      url: `${APP_URL}/about`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.7,
    },
  ];
  
  // Dynamic property routes
  let propertyRoutes: MetadataRoute.Sitemap = [];
  try {
    const result = await mockAPI.getProperties(undefined, undefined, 1, 100);
    propertyRoutes = result.data.map((property) => ({
      url: `${APP_URL}/properties/${property.id}`,
      lastModified: new Date(property.updated_at),
      changeFrequency: 'daily',
      priority: 0.8,
    }));
    
    // Add ROI analysis pages
    const roiRoutes = result.data.map((property) => ({
      url: `${APP_URL}/properties/${property.id}/roi`,
      lastModified: new Date(property.updated_at),
      changeFrequency: 'weekly',
      priority: 0.7,
    }));
    
    propertyRoutes = [...propertyRoutes, ...roiRoutes];
  } catch (error) {
    console.error('Failed to generate property sitemap entries:', error);
  }
  
  return [...staticRoutes, ...propertyRoutes];
}
