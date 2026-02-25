import { test, expect } from '@playwright/test';

test.describe('Navigation', () => {
  test('should navigate to all main pages from home', async ({ page }) => {
    await page.goto('/');
    
    // Navigate to Properties
    await page.getByRole('link', { name: /Properties$/i }).click();
    await expect(page).toHaveURL(/\/properties/);
    
    // Navigate to Opportunities
    await page.getByRole('link', { name: /Opportunities$/i }).click();
    await expect(page).toHaveURL(/\/opportunities/);
    
    // Navigate to Stats
    await page.getByRole('link', { name: /Market Stats$/i }).click();
    await expect(page).toHaveURL(/\/stats/);
    
    // Navigate to About
    await page.getByRole('link', { name: /About$/i }).click();
    await expect(page).toHaveURL(/\/about/);
    
    // Navigate back to Home
    await page.getByRole('link', { name: /^Home$/i }).click();
    await expect(page).toHaveURL(/\/$/);
  });

  test('should have working footer links', async ({ page }) => {
    await page.goto('/');
    
    // Check footer links exist
    await expect(page.getByRole('link', { name: /All Properties/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Top Opportunities/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Market Statistics/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /About Us/i })).toBeVisible();
  });

  test('should handle 404 pages gracefully', async ({ page }) => {
    await page.goto('/non-existent-page');
    
    await expect(page.getByText(/Page Not Found/i).or(page.getByText(/Not Found/i))).toBeVisible();
    await expect(page.getByRole('link', { name: /Back to Home/i })).toBeVisible();
  });

  test('should have working mobile navigation', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    await page.goto('/');
    
    // Open mobile menu
    await page.getByRole('button', { name: /Toggle menu/i }).click();
    
    // Check mobile menu items
    await expect(page.getByRole('link', { name: /^Home$/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Properties$/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Opportunities$/i })).toBeVisible();
    
    // Navigate using mobile menu
    await page.getByRole('link', { name: /Properties$/i }).click();
    await expect(page).toHaveURL(/\/properties/);
  });
});
