import { describe, it, expect } from 'vitest';
import {
  cn,
  formatCurrency,
  formatNumber,
  formatPercent,
  formatDate,
  formatLocation,
  formatPropertyType,
  getScoreColor,
  getScoreLabel,
  calculatePricePerSqm,
  truncateText,
  calculateMortgagePayment,
  isValidEmail,
} from '@/lib/utils';

describe('Utils', () => {
  describe('cn', () => {
    it('merges class names correctly', () => {
      expect(cn('class1', 'class2')).toBe('class1 class2');
      expect(cn('class1', false && 'class2', 'class3')).toBe('class1 class3');
      expect(cn('px-4', 'px-6')).toBe('px-6'); // Tailwind merge
    });
  });

  describe('formatCurrency', () => {
    it('formats numbers as EUR currency', () => {
      expect(formatCurrency(350000)).toBe('€350,000');
      expect(formatCurrency(165000)).toBe('€165,000');
      expect(formatCurrency(1200000)).toBe('€1,200,000');
    });
  });

  describe('formatNumber', () => {
    it('formats numbers with locale separators', () => {
      expect(formatNumber(1000)).toBe('1,000');
      expect(formatNumber(1000000)).toBe('1,000,000');
    });
  });

  describe('formatPercent', () => {
    it('formats numbers as percentages', () => {
      expect(formatPercent(5)).toBe('5.0%');
      expect(formatPercent(4.5)).toBe('4.5%');
      expect(formatPercent(0)).toBe('0.0%');
    });
  });

  describe('formatDate', () => {
    it('formats dates correctly', () => {
      const date = '2024-01-15T10:00:00Z';
      const formatted = formatDate(date);
      expect(formatted).toContain('2024');
    });
  });

  describe('formatLocation', () => {
    it('formats location slugs to readable names', () => {
      expect(formatLocation('sliema')).toBe('Sliema');
      expect(formatLocation('st_julians')).toBe("St. Julian's");
      expect(formatLocation('valletta')).toBe('Valletta');
    });
  });

  describe('formatPropertyType', () => {
    it('formats property type slugs to readable names', () => {
      expect(formatPropertyType('apartment')).toBe('Apartment');
      expect(formatPropertyType('penthouse')).toBe('Penthouse');
      expect(formatPropertyType('townhouse')).toBe('Townhouse');
    });
  });

  describe('getScoreColor', () => {
    it('returns correct color classes for scores', () => {
      expect(getScoreColor(90)).toBe('bg-success-500');
      expect(getScoreColor(75)).toBe('bg-primary-500');
      expect(getScoreColor(60)).toBe('bg-warning-500');
      expect(getScoreColor(30)).toBe('bg-danger-500');
    });
  });

  describe('getScoreLabel', () => {
    it('returns correct labels for scores', () => {
      expect(getScoreLabel(90)).toBe('Excellent');
      expect(getScoreLabel(75)).toBe('Good');
      expect(getScoreLabel(60)).toBe('Fair');
      expect(getScoreLabel(30)).toBe('Below Average');
    });
  });

  describe('calculatePricePerSqm', () => {
    it('calculates price per square meter', () => {
      expect(calculatePricePerSqm(350000, 95)).toBe(3684);
      expect(calculatePricePerSqm(165000, 45)).toBe(3667);
    });

    it('returns 0 for zero sqm', () => {
      expect(calculatePricePerSqm(350000, 0)).toBe(0);
    });
  });

  describe('truncateText', () => {
    it('truncates text to specified length', () => {
      expect(truncateText('Hello World', 5)).toBe('Hello...');
      expect(truncateText('Hi', 10)).toBe('Hi');
    });
  });

  describe('calculateMortgagePayment', () => {
    it('calculates monthly mortgage payment', () => {
      // €280,000 loan at 4.5% for 25 years
      const payment = calculateMortgagePayment(280000, 4.5, 25);
      expect(payment).toBeGreaterThan(1500);
      expect(payment).toBeLessThan(1600);
    });

    it('handles zero interest rate', () => {
      const payment = calculateMortgagePayment(300000, 0, 25);
      expect(payment).toBe(1000); // 300000 / (25 * 12)
    });
  });

  describe('isValidEmail', () => {
    it('validates email addresses', () => {
      expect(isValidEmail('test@example.com')).toBe(true);
      expect(isValidEmail('user.name@domain.co.uk')).toBe(true);
      expect(isValidEmail('invalid')).toBe(false);
      expect(isValidEmail('@example.com')).toBe(false);
      expect(isValidEmail('test@')).toBe(false);
    });
  });
});
