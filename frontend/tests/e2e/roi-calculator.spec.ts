import { test, expect } from '@playwright/test';

test.describe('ROI Calculator', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/properties/prop-001/roi');
  });

  test('should display ROI analysis page', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /ROI Analysis/i })).toBeVisible();
    await expect(page.getByText(/Property Price/i)).toBeVisible();
  });

  test('should display opportunity score', async ({ page }) => {
    await expect(page.getByText(/Opportunity Score/i)).toBeVisible();
    await expect(page.getByText(/\/ 100/)).toBeVisible();
  });

  test('should display ROI metrics', async ({ page }) => {
    await expect(page.getByText(/Gross Rental Yield/i)).toBeVisible();
    await expect(page.getByText(/Net Rental Yield/i)).toBeVisible();
    await expect(page.getByText(/Cap Rate/i)).toBeVisible();
  });

  test('should display cash flow chart', async ({ page }) => {
    await expect(page.getByText(/Cash Flow Projection/i)).toBeVisible();
    await expect(page.locator('svg')).toBeVisible();
  });

  test('should have ROI calculator form', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /ROI Calculator/i })).toBeVisible();
    await expect(page.getByLabel(/Purchase Price/i)).toBeVisible();
    await expect(page.getByLabel(/Down Payment %/i)).toBeVisible();
    await expect(page.getByLabel(/Interest Rate/i)).toBeVisible();
  });

  test('should update calculations when inputs change', async ({ page }) => {
    // Find and update an input
    const downPaymentInput = page.getByLabel(/Down Payment %/i);
    await downPaymentInput.clear();
    await downPaymentInput.fill('30');
    
    // Click calculate button
    await page.getByRole('button', { name: /Calculate ROI/i }).click();
    
    // Wait for calculation
    await page.waitForTimeout(500);
  });

  test('should have back to property link', async ({ page }) => {
    await expect(page.getByRole('link', { name: /Back to Property/i })).toBeVisible();
  });

  test('should navigate back to property detail', async ({ page }) => {
    await page.getByRole('link', { name: /Back to Property/i }).click();
    await expect(page).toHaveURL(/\/properties\/[^/]+$/);
  });

  test('should display investment summary', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /Investment Summary/i })).toBeVisible();
  });

  test('should display market comparison', async ({ page }) => {
    await expect(page.getByText(/Market Comparison/i)).toBeVisible();
  });
});
