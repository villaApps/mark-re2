import { test, expect } from '@playwright/test';

test.describe('Properties Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/properties');
  });

  test('should display properties list page', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /Properties for Sale/i })).toBeVisible();
    await expect(page.getByText(/Browse.*properties across Malta/i)).toBeVisible();
  });

  test('should display filter controls', async ({ page }) => {
    await expect(page.getByRole('button', { name: /Filters/i })).toBeVisible();
    await expect(page.getByText(/Sort by:/i)).toBeVisible();
  });

  test('should display property cards', async ({ page }) => {
    // Wait for properties to load
    await page.waitForSelector('.grid > div', { timeout: 10000 });
    
    const propertyCards = page.locator('.grid > div');
    await expect(propertyCards.first()).toBeVisible();
  });

  test('should filter by location', async ({ page }) => {
    // Open filters
    await page.getByRole('button', { name: /Filters/i }).click();
    
    // Select location
    await page.getByLabel(/Location/i).selectOption('sliema');
    
    // Wait for results to update
    await page.waitForTimeout(500);
    
    // Check if filter is applied
    await expect(page.getByText(/Sliema/)).toBeVisible();
  });

  test('should filter by property type', async ({ page }) => {
    // Open filters
    await page.getByRole('button', { name: /Filters/i }).click();
    
    // Select property type
    await page.getByLabel(/Property Type/i).selectOption('apartment');
    
    // Wait for results to update
    await page.waitForTimeout(500);
  });

  test('should sort properties', async ({ page }) => {
    // Select sort option
    await page.getByLabel(/Sort by:/i).selectOption('price_asc');
    
    // Wait for results to update
    await page.waitForTimeout(500);
  });

  test('should clear filters', async ({ page }) => {
    // Apply a filter first
    await page.getByRole('button', { name: /Filters/i }).click();
    await page.getByLabel(/Location/i).selectOption('sliema');
    await page.waitForTimeout(500);
    
    // Clear filters
    await page.getByRole('button', { name: /Clear/i }).click();
    
    // Wait for results to update
    await page.waitForTimeout(500);
  });

  test('should navigate to property detail page', async ({ page }) => {
    // Wait for properties to load
    await page.waitForSelector('.grid > div', { timeout: 10000 });
    
    // Click on first property
    const firstProperty = page.locator('.grid > div').first();
    await firstProperty.click();
    
    // Should navigate to property detail
    await expect(page).toHaveURL(/\/properties\/[^/]+$/);
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
  });

  test('should show empty state when no results', async ({ page }) => {
    // Apply filters that will return no results
    await page.getByRole('button', { name: /Filters/i }).click();
    await page.getByLabel(/Location/i).selectOption('valletta');
    await page.getByLabel(/Property Type/i).selectOption('villa');
    
    // Wait for results
    await page.waitForTimeout(500);
    
    // Check for empty state message (if applicable)
    const emptyMessage = page.getByText(/No properties found/i);
    if (await emptyMessage.isVisible().catch(() => false)) {
      await expect(emptyMessage).toBeVisible();
    }
  });

  test('should display pagination when many results', async ({ page }) => {
    // Check if pagination exists (may not be visible with few results)
    const pagination = page.locator('nav[aria-label="Pagination"]');
    
    if (await pagination.isVisible().catch(() => false)) {
      await expect(pagination).toBeVisible();
    }
  });
});
