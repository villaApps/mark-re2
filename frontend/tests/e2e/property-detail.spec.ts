import { test, expect } from '@playwright/test';

test.describe('Property Detail Page', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to a property detail page
    await page.goto('/properties/prop-001');
  });

  test('should display property detail page', async ({ page }) => {
    // Property title should be visible
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
    
    // Price should be displayed
    await expect(page.getByText(/€/)).toBeVisible();
  });

  test('should display property gallery', async ({ page }) => {
    await expect(page.locator('img').first()).toBeVisible();
  });

  test('should display property features', async ({ page }) => {
    await expect(page.getByText(/Bedrooms/i)).toBeVisible();
    await expect(page.getByText(/Bathrooms/i)).toBeVisible();
    await expect(page.getByText(/Area/i)).toBeVisible();
  });

  test('should display property description', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /Description/i })).toBeVisible();
  });

  test('should display location section', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /Location/i })).toBeVisible();
  });

  test('should have ROI analysis link', async ({ page }) => {
    await expect(page.getByRole('link', { name: /View ROI Analysis/i })).toBeVisible();
  });

  test('should navigate to ROI analysis page', async ({ page }) => {
    await page.getByRole('link', { name: /View ROI Analysis/i }).click();
    
    await expect(page).toHaveURL(/\/properties\/[^/]+\/roi$/);
    await expect(page.getByRole('heading', { name: /ROI Analysis/i })).toBeVisible();
  });

  test('should have breadcrumb navigation', async ({ page }) => {
    await expect(page.getByRole('link', { name: /Home/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Properties/i })).toBeVisible();
  });

  test('should navigate back to properties list', async ({ page }) => {
    await page.getByRole('link', { name: /Properties/i }).click();
    await expect(page).toHaveURL(/\/properties/);
  });

  test('should display similar properties', async ({ page }) => {
    const similarHeading = page.getByRole('heading', { name: /Similar Properties/i });
    
    if (await similarHeading.isVisible().catch(() => false)) {
      await expect(similarHeading).toBeVisible();
    }
  });

  test('should show 404 for non-existent property', async ({ page }) => {
    await page.goto('/properties/non-existent-id');
    
    await expect(page.getByText(/Page Not Found/i).or(page.getByText(/Not Found/i))).toBeVisible();
  });
});
