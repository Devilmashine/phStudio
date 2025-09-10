/**
 * E2E Tests for Booking Flow
 * End-to-end тесты для полного flow бронирования
 */

import { test, expect, Page } from '@playwright/test';

// Test data
const testBooking = {
  clientName: 'Тестовый Клиент',
  clientPhone: '+7 (999) 123-45-67',
  clientEmail: 'test@example.com',
  bookingDate: '2024-02-15',
  startTime: '10:00',
  endTime: '12:00',
  spaceType: 'Основная студия',
  equipment: ['Профессиональное освещение'],
  specialRequirements: 'Нужен белый фон для портретной съемки',
  notes: 'Тестовое бронирование через E2E',
};

test.describe('Booking Flow E2E Tests', () => {
  let page: Page;

  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage();
    
    // Mock API responses
    await page.route('**/api/v1/bookings**', async (route) => {
      const url = route.request().url();
      
      if (route.request().method() === 'POST') {
        // Mock create booking response
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            data: {
              id: 1,
              booking_reference: 'BK-2024-001',
              ...testBooking,
              state: 'pending',
              total_price: 5000,
              created_at: new Date().toISOString(),
            },
            success: true,
          }),
        });
      } else if (url.includes('/analytics') || url.includes('/stats')) {
        // Mock analytics response
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            data: {
              total_bookings: 10,
              completed_bookings: 8,
              pending_bookings: 2,
              total_revenue: 50000,
              average_price: 5000,
            },
            success: true,
          }),
        });
      } else {
        // Mock get bookings response
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: [],
            total: 0,
            page: 1,
            pages: 1,
            per_page: 20,
          }),
        });
      }
    });

    // Mock availability API
    await page.route('**/api/v1/bookings/by-date/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: [],
          success: true,
        }),
      });
    });
  });

  test('Complete booking flow from start to finish', async () => {
    // Navigate to booking page
    await page.goto('/booking');

    // Step 1: Select date and time
    await test.step('Select date and time', async () => {
      // Wait for calendar to load
      await expect(page.locator('[data-testid="enhanced-calendar"]')).toBeVisible();
      
      // Select date (assuming calendar is visible)
      await page.click('[data-testid="calendar-date-2024-02-15"]');
      
      // Verify time slots are loaded
      await expect(page.locator('[data-testid="time-slots"]')).toBeVisible();
      
      // Select time slots
      await page.click('[data-testid="time-slot-10:00"]');
      await page.click('[data-testid="time-slot-11:00"]');
      
      // Select space type
      await page.selectOption('[data-testid="space-type-select"]', 'main_studio');
      
      // Proceed to next step
      await page.click('[data-testid="next-step-button"]');
    });

    // Step 2: Fill client information
    await test.step('Fill client information', async () => {
      await expect(page.locator('[data-testid="client-info-form"]')).toBeVisible();
      
      // Fill client details
      await page.fill('[data-testid="client-name-input"]', testBooking.clientName);
      await page.fill('[data-testid="client-phone-input"]', testBooking.clientPhone);
      await page.fill('[data-testid="client-email-input"]', testBooking.clientEmail);
      
      // Proceed to next step
      await page.click('[data-testid="next-step-button"]');
    });

    // Step 3: Select equipment and details
    await test.step('Select equipment and details', async () => {
      await expect(page.locator('[data-testid="booking-details-form"]')).toBeVisible();
      
      // Select equipment
      await page.check('[data-testid="equipment-professional_lighting"]');
      
      // Fill special requirements
      await page.fill('[data-testid="special-requirements-textarea"]', testBooking.specialRequirements);
      
      // Fill notes
      await page.fill('[data-testid="notes-textarea"]', testBooking.notes);
      
      // Select priority
      await page.selectOption('[data-testid="priority-select"]', 'normal');
      
      // Verify price calculation
      await expect(page.locator('[data-testid="total-price"]')).toContainText('5000');
      
      // Proceed to next step
      await page.click('[data-testid="next-step-button"]');
    });

    // Step 4: Accept terms and conditions
    await test.step('Accept terms and conditions', async () => {
      await expect(page.locator('[data-testid="terms-form"]')).toBeVisible();
      
      // Accept all terms
      await page.check('[data-testid="terms-accepted-checkbox"]');
      await page.check('[data-testid="privacy-accepted-checkbox"]');
      await page.check('[data-testid="studio-rules-accepted-checkbox"]');
      
      // Proceed to confirmation
      await page.click('[data-testid="next-step-button"]');
    });

    // Step 5: Review and confirm
    await test.step('Review and confirm booking', async () => {
      await expect(page.locator('[data-testid="booking-confirmation"]')).toBeVisible();
      
      // Verify all information is displayed correctly
      await expect(page.locator('[data-testid="confirmation-client-name"]')).toContainText(testBooking.clientName);
      await expect(page.locator('[data-testid="confirmation-phone"]')).toContainText(testBooking.clientPhone);
      await expect(page.locator('[data-testid="confirmation-date"]')).toContainText('15.02.2024');
      await expect(page.locator('[data-testid="confirmation-time"]')).toContainText('10:00, 11:00');
      await expect(page.locator('[data-testid="confirmation-total"]')).toContainText('5000 ₽');
      
      // Submit booking
      await page.click('[data-testid="submit-booking-button"]');
    });

    // Verify success
    await test.step('Verify booking success', async () => {
      // Wait for success message
      await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
      await expect(page.locator('[data-testid="success-message"]')).toContainText('Бронирование успешно создано');
      
      // Verify booking reference is shown
      await expect(page.locator('[data-testid="booking-reference"]')).toContainText('BK-2024-001');
    });
  });

  test('Booking form validation', async () => {
    await page.goto('/booking');

    // Try to proceed without filling required fields
    await page.click('[data-testid="next-step-button"]');
    
    // Should show validation errors
    await expect(page.locator('[data-testid="validation-error"]')).toBeVisible();
    
    // Fill invalid data
    await page.fill('[data-testid="client-name-input"]', 'A'); // Too short
    await page.fill('[data-testid="client-phone-input"]', 'invalid'); // Invalid format
    
    // Should show field-specific errors
    await expect(page.locator('[data-testid="name-error"]')).toContainText('минимум 2 символа');
    await expect(page.locator('[data-testid="phone-error"]')).toContainText('корректный номер');
  });

  test('Time slot availability checking', async () => {
    await page.goto('/booking');

    // Mock unavailable time slots
    await page.route('**/api/v1/bookings/by-date/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: [
            {
              id: 1,
              start_time: '2024-02-15T10:00:00.000Z',
              end_time: '2024-02-15T12:00:00.000Z',
              space_type: 'main_studio',
              client_name: 'Existing Client',
            }
          ],
          success: true,
        }),
      });
    });

    // Select date
    await page.click('[data-testid="calendar-date-2024-02-15"]');
    
    // Wait for time slots to load
    await expect(page.locator('[data-testid="time-slots"]')).toBeVisible();
    
    // Verify unavailable slots are disabled
    await expect(page.locator('[data-testid="time-slot-10:00"]')).toHaveClass(/disabled/);
    await expect(page.locator('[data-testid="time-slot-11:00"]')).toHaveClass(/disabled/);
    
    // Available slots should be clickable
    await expect(page.locator('[data-testid="time-slot-14:00"]')).not.toHaveClass(/disabled/);
  });

  test('Equipment selection and price calculation', async () => {
    await page.goto('/booking');

    // Complete first two steps
    await page.click('[data-testid="calendar-date-2024-02-15"]');
    await page.click('[data-testid="time-slot-10:00"]');
    await page.click('[data-testid="time-slot-11:00"]');
    await page.click('[data-testid="next-step-button"]');
    
    await page.fill('[data-testid="client-name-input"]', testBooking.clientName);
    await page.fill('[data-testid="client-phone-input"]', testBooking.clientPhone);
    await page.click('[data-testid="next-step-button"]');

    // Test equipment selection
    await test.step('Select equipment and verify price', async () => {
      // Base price should be shown
      await expect(page.locator('[data-testid="base-price"]')).toContainText('4000 ₽');
      
      // Select equipment
      await page.check('[data-testid="equipment-professional_lighting"]');
      
      // Price should update
      await expect(page.locator('[data-testid="equipment-price"]')).toContainText('500 ₽');
      await expect(page.locator('[data-testid="total-price"]')).toContainText('4500 ₽');
      
      // Select more equipment
      await page.check('[data-testid="equipment-backdrop_white"]');
      
      // Price should update again
      await expect(page.locator('[data-testid="total-price"]')).toContainText('4700 ₽');
    });
  });

  test('Terms and conditions modal', async () => {
    await page.goto('/booking');

    // Complete first three steps
    await page.click('[data-testid="calendar-date-2024-02-15"]');
    await page.click('[data-testid="time-slot-10:00"]');
    await page.click('[data-testid="next-step-button"]');
    
    await page.fill('[data-testid="client-name-input"]', testBooking.clientName);
    await page.fill('[data-testid="client-phone-input"]', testBooking.clientPhone);
    await page.click('[data-testid="next-step-button"]');
    
    await page.click('[data-testid="next-step-button"]');

    // Test terms modal
    await test.step('Open and read terms', async () => {
      // Click on terms link
      await page.click('[data-testid="terms-link"]');
      
      // Modal should open
      await expect(page.locator('[data-testid="terms-modal"]')).toBeVisible();
      await expect(page.locator('[data-testid="terms-content"]')).toContainText('Общие положения');
      
      // Close modal
      await page.click('[data-testid="close-modal"]');
      await expect(page.locator('[data-testid="terms-modal"]')).not.toBeVisible();
    });

    // Test privacy modal
    await test.step('Open and read privacy policy', async () => {
      await page.click('[data-testid="privacy-link"]');
      await expect(page.locator('[data-testid="privacy-modal"]')).toBeVisible();
      await expect(page.locator('[data-testid="privacy-content"]')).toContainText('персональных данных');
      
      await page.click('[data-testid="close-modal"]');
    });

    // Test studio rules modal
    await test.step('Open and read studio rules', async () => {
      await page.click('[data-testid="studio-rules-link"]');
      await expect(page.locator('[data-testid="studio-rules-modal"]')).toBeVisible();
      await expect(page.locator('[data-testid="studio-rules-content"]')).toContainText('Правила пользования');
      
      await page.click('[data-testid="close-modal"]');
    });
  });

  test('Responsive design on mobile', async () => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/booking');

    // Verify mobile layout
    await expect(page.locator('[data-testid="booking-form"]')).toBeVisible();
    
    // Calendar should be responsive
    await expect(page.locator('[data-testid="enhanced-calendar"]')).toBeVisible();
    
    // Time slots should stack vertically on mobile
    const timeSlots = page.locator('[data-testid="time-slot"]');
    await expect(timeSlots.first()).toBeVisible();
    
    // Form should be scrollable
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  });

  test('Dark mode support', async () => {
    await page.goto('/booking');
    
    // Toggle dark mode
    await page.click('[data-testid="dark-mode-toggle"]');
    
    // Verify dark mode classes are applied
    await expect(page.locator('html')).toHaveClass(/dark/);
    
    // Verify form elements have dark mode styles
    await expect(page.locator('[data-testid="booking-form"]')).toHaveClass(/dark:bg-gray-800/);
    
    // Toggle back to light mode
    await page.click('[data-testid="dark-mode-toggle"]');
    await expect(page.locator('html')).not.toHaveClass(/dark/);
  });

  test('Error handling and retry', async () => {
    // Mock API error
    await page.route('**/api/v1/bookings', async (route) => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({
            message: 'Internal server error',
            success: false,
          }),
        });
      }
    });

    await page.goto('/booking');

    // Complete booking flow
    await page.click('[data-testid="calendar-date-2024-02-15"]');
    await page.click('[data-testid="time-slot-10:00"]');
    await page.click('[data-testid="next-step-button"]');
    
    await page.fill('[data-testid="client-name-input"]', testBooking.clientName);
    await page.fill('[data-testid="client-phone-input"]', testBooking.clientPhone);
    await page.click('[data-testid="next-step-button"]');
    
    await page.click('[data-testid="next-step-button"]');
    
    await page.check('[data-testid="terms-accepted-checkbox"]');
    await page.check('[data-testid="privacy-accepted-checkbox"]');
    await page.check('[data-testid="studio-rules-accepted-checkbox"]');
    await page.click('[data-testid="next-step-button"]');
    
    // Submit booking
    await page.click('[data-testid="submit-booking-button"]');
    
    // Should show error message
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-message"]')).toContainText('Ошибка при создании бронирования');
    
    // Retry button should be available
    await expect(page.locator('[data-testid="retry-button"]')).toBeVisible();
  });
});
