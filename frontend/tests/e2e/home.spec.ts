import { test, expect } from '@playwright/test';

test.describe('Home Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display the home page with correct title', async ({ page }) => {
    await expect(page).toHaveTitle(/Malta Property Investment Analyzer/);
  });

  test('should display hero section with key elements', async ({ page }) => {
    // Hero heading
    await expect(page.getByRole('heading', { name: /Find High-ROI Real Estate/i })).toBeVisible();
    
    // Hero description
    await expect(page.getByText(/Analyze properties, calculate returns/i)).toBeVisible();
    
    // CTA buttons
    await expect(page.getByRole('link', { name: /Browse Properties/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Top Opportunities/i })).toBeVisible();
  });

  test('should display stats section', async ({ page }) => {
    await expect(page.getByText(/2,500\+/)).toBeVisible();
    await expect(page.getByText(/4\.5%/)).toBeVisible();
    await expect(page.getByText(/25\+/)).toBeVisible();
  });

  test('should display features section', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /How It Works/i })).toBeVisible();
    await expect(page.getByText(/Discover Properties/i)).toBeVisible();
    await expect(page.getByText(/Analyze ROI/i)).toBeVisible();
    await expect(page.getByText(/Compare Opportunities/i)).toBeVisible();
  });

  test('should display featured properties', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /Featured Opportunities/i })).toBeVisible();
    
    // Should have property cards
    const propertyCards = page.locator('[data-testid="property-card"]').or(page.locator('.grid > div'));
    await expect(propertyCards.first()).toBeVisible();
  });

  test('should navigate to properties page', async ({ page }) => {
    await page.getByRole('link', { name: /Browse Properties/i }).first().click();
    await expect(page).toHaveURL(/\/properties/);
    await expect(page.getByRole('heading', { name: /Properties for Sale/i })).toBeVisible();
  });

  test('should navigate to opportunities page', async ({ page }) => {
    await page.getByRole('link', { name: /Top Opportunities/i }).first().click();
    await expect(page).toHaveURL(/\/opportunities/);
    await expect(page.getByRole('heading', { name: /Best Property Investment Opportunities/i })).toBeVisible();
  });

  test('should have working navigation menu', async ({ page }) => {
    // Check header navigation
    await expect(page.getByRole('link', { name: /Home/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Properties/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Opportunities/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Market Stats/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /About/i })).toBeVisible();
  });

  test('should display footer with links', async ({ page }) => {
    await expect(page.getByText(/Malta Property Analyzer Ltd/)).toBeVisible();
    await expect(page.getByRole('link', { name: /Privacy Policy/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Terms of Service/i })).toBeVisible();
  });

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Mobile menu button should be visible
    await expect(page.getByRole('button', { name: /Toggle menu/i })).toBeVisible();
    
    // Hero content should still be visible
    await expect(page.getByRole('heading', { name: /Find High-ROI Real Estate/i })).toBeVisible();
  });
});
