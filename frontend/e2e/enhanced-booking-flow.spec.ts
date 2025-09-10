/**
 * E2E Tests for Enhanced Booking Flow
 * End-to-end тесты для улучшенного потока бронирования
 */

import { test, expect, Page } from '@playwright/test';

test.describe('Enhanced Booking Flow E2E Tests', () => {
  let page: Page;

  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage();
    
    // Mock API responses for enhanced booking flow
    await page.route('**/api/v1/bookings**', async (route) => {
      const url = route.request().url();
      const method = route.request().method();
      
      if (method === 'POST') {
        // Mock create booking response
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            data: {
              id: 1,
              booking_reference: 'BK-2024-001',
              client_name: 'Тестовый Клиент',
              client_phone: '+79991234567',
              client_email: 'test@example.com',
              booking_date: '2024-02-15',
              start_time: '2024-02-15T10:00:00.000Z',
              end_time: '2024-02-15T12:00:00.000Z',
              space_type: 'main_studio',
              equipment_requested: ['professional_lighting'],
              special_requirements: 'Нужен белый фон',
              notes: 'Тестовое бронирование',
              priority: 'normal',
              source: 'website',
              state: 'pending',
              base_price: 4000,
              equipment_price: 500,
              discount_amount: 0,
              total_price: 4500,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString()
            },
            success: true,
          }),
        });
      } else if (method === 'GET' && url.includes('/by-date')) {
        // Mock availability API
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            data: [
              {
                id: 2,
                start_time: '2024-02-15T10:00:00.000Z',
                end_time: '2024-02-15T12:00:00.000Z',
                space_type: 'main_studio',
                client_name: 'Existing Client',
              }
            ],
            success: true,
          });
        });
      } else if (method === 'GET') {
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
            success: true,
          });
        });
      }
    });
  });

  test('Complete enhanced booking flow with all steps', async () => {
    await page.goto('/booking');

    // Step 1: Select date and time using enhanced calendar
    await test.step('Select date and time', async () => {
      // Wait for enhanced calendar to load
      await expect(page.locator('[data-testid="enhanced-calendar"]')).toBeVisible();
      
      // Select date
      await page.click('[data-testid="calendar-date-2024-02-15"]');
      
      // Verify time slots are loaded
      await expect(page.locator('[data-testid="enhanced-time-slots"]')).toBeVisible();
      
      // Select multiple time slots
      await page.click('[data-testid="time-slot-13:00"]');
      await page.click('[data-testid="time-slot-14:00"]');
      await page.click('[data-testid="time-slot-15:00"]');
      
      // Select space type
      await page.selectOption('[data-testid="space-type-select"]', 'main_studio');
      
      // Verify price calculation
      await expect(page.locator('[data-testid="hourly-rate"]')).toContainText('2 000 ₽');
      await expect(page.locator('[data-testid="total-hours"]')).toContainText('3 часа');
      await expect(page.locator('[data-testid="base-price"]')).toContainText('6 000 ₽');
      
      // Proceed to next step
      await page.click('[data-testid="next-step-button"]');
    });

    // Step 2: Fill client information
    await test.step('Fill client information', async () => {
      await expect(page.locator('[data-testid="client-info-form"]')).toBeVisible();
      
      // Fill client details with validation
      await page.fill('[data-testid="client-name-input"]', 'Тестовый Клиент');
      await page.fill('[data-testid="client-phone-input"]', '+79991234567');
      await page.fill('[data-testid="client-email-input"]', 'test@example.com');
      
      // Verify phone input formatting
      await expect(page.locator('[data-testid="client-phone-input"]')).toHaveValue('+7 (999) 123-45-67');
      
      // Verify form validation
      await expect(page.locator('[data-testid="client-name-input"]')).not.toHaveClass(/border-red-500/);
      await expect(page.locator('[data-testid="client-phone-input"]')).not.toHaveClass(/border-red-500/);
      await expect(page.locator('[data-testid="client-email-input"]')).not.toHaveClass(/border-red-500/);
      
      // Proceed to next step
      await page.click('[data-testid="next-step-button"]');
    });

    // Step 3: Select equipment and details
    await test.step('Select equipment and details', async () => {
      await expect(page.locator('[data-testid="booking-details-form"]')).toBeVisible();
      
      // Select equipment with search
      await page.fill('[data-testid="equipment-search"]', 'освещение');
      await page.click('[data-testid="equipment-professional_lighting"]');
      
      // Fill special requirements
      await page.fill('[data-testid="special-requirements-textarea"]', 'Нужен белый фон для портретной съемки');
      
      // Fill notes
      await page.fill('[data-testid="notes-textarea"]', 'Тестовое бронирование через E2E');
      
      // Select priority
      await page.selectOption('[data-testid="priority-select"]', 'normal');
      
      // Verify price calculation with equipment
      await expect(page.locator('[data-testid="equipment-price"]')).toContainText('500 ₽');
      await expect(page.locator('[data-testid="total-price"]')).toContainText('6 500 ₽');
      
      // Verify discount section (should be hidden for regular users)
      await expect(page.locator('[data-testid="discount-section"]')).not.toBeVisible();
      
      // Proceed to next step
      await page.click('[data-testid="next-step-button"]');
    });

    // Step 4: Accept terms and conditions
    await test.step('Accept terms and conditions', async () => {
      await expect(page.locator('[data-testid="terms-form"]')).toBeVisible();
      
      // Test terms modal
      await page.click('[data-testid="terms-link"]');
      await expect(page.locator('[data-testid="terms-modal"]')).toBeVisible();
      await expect(page.locator('[data-testid="terms-content"]')).toContainText('Общие положения');
      await page.click('[data-testid="close-modal"]');
      
      // Test privacy policy modal
      await page.click('[data-testid="privacy-link"]');
      await expect(page.locator('[data-testid="privacy-modal"]')).toBeVisible();
      await expect(page.locator('[data-testid="privacy-content"]')).toContainText('персональных данных');
      await page.click('[data-testid="close-modal"]');
      
      // Test studio rules modal
      await page.click('[data-testid="studio-rules-link"]');
      await expect(page.locator('[data-testid="studio-rules-modal"]')).toBeVisible();
      await expect(page.locator('[data-testid="studio-rules-content"]')).toContainText('Правила пользования');
      await page.click('[data-testid="close-modal"]');
      
      // Accept all terms
      await page.check('[data-testid="terms-accepted-checkbox"]');
      await page.check('[data-testid="privacy-accepted-checkbox"]');
      await page.check('[data-testid="studio-rules-accepted-checkbox"]');
      
      // Verify all checkboxes are checked
      await expect(page.locator('[data-testid="terms-accepted-checkbox"]')).toBeChecked();
      await expect(page.locator('[data-testid="privacy-accepted-checkbox"]')).toBeChecked();
      await expect(page.locator('[data-testid="studio-rules-accepted-checkbox"]')).toBeChecked();
      
      // Proceed to confirmation
      await page.click('[data-testid="next-step-button"]');
    });

    // Step 5: Review and confirm
    await test.step('Review and confirm booking', async () => {
      await expect(page.locator('[data-testid="booking-confirmation"]')).toBeVisible();
      
      // Verify all information is displayed correctly
      await expect(page.locator('[data-testid="confirmation-client-name"]')).toContainText('Тестовый Клиент');
      await expect(page.locator('[data-testid="confirmation-phone"]')).toContainText('+7 (999) 123-45-67');
      await expect(page.locator('[data-testid="confirmation-email"]')).toContainText('test@example.com');
      await expect(page.locator('[data-testid="confirmation-date"]')).toContainText('15.02.2024');
      await expect(page.locator('[data-testid="confirmation-time"]')).toContainText('13:00 - 16:00');
      await expect(page.locator('[data-testid="confirmation-space"]')).toContainText('Основная студия');
      await expect(page.locator('[data-testid="confirmation-equipment"]')).toContainText('Профессиональное освещение');
      await expect(page.locator('[data-testid="confirmation-requirements"]')).toContainText('Нужен белый фон');
      await expect(page.locator('[data-testid="confirmation-notes"]')).toContainText('Тестовое бронирование');
      await expect(page.locator('[data-testid="confirmation-total"]')).toContainText('6 500 ₽');
      
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
      
      // Verify action buttons are available
      await expect(page.locator('[data-testid="add-to-calendar-button"]')).toBeVisible();
      await expect(page.locator('[data-testid="view-booking-button"]')).toBeVisible();
      await expect(page.locator('[data-testid="create-another-booking-button"]')).toBeVisible();
    });
  });

  test('Booking form validation in enhanced flow', async () => {
    await page.goto('/booking');

    // Test Step 1 validation
    await page.click('[data-testid="next-step-button"]');
    await expect(page.locator('[data-testid="date-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="time-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="space-error"]')).toBeVisible();

    // Test Step 2 validation
    await page.click('[data-testid="calendar-date-2024-02-15"]');
    await page.click('[data-testid="time-slot-10:00"]');
    await page.selectOption('[data-testid="space-type-select"]', 'main_studio');
    await page.click('[data-testid="next-step-button"]');
    
    await page.click('[data-testid="next-step-button"]');
    await expect(page.locator('[data-testid="name-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="phone-error"]')).toBeVisible();

    // Test invalid data
    await page.fill('[data-testid="client-name-input"]', 'A'); // Too short
    await page.fill('[data-testid="client-phone-input"]', 'invalid'); // Invalid format
    await page.fill('[data-testid="client-email-input"]', 'not-an-email'); // Invalid email
    
    await expect(page.locator('[data-testid="name-error"]')).toContainText('минимум 2 символа');
    await expect(page.locator('[data-testid="phone-error"]')).toContainText('корректный номер');
    await expect(page.locator('[data-testid="email-error"]')).toContainText('корректный email');

    // Test Step 3 validation
    await page.fill('[data-testid="client-name-input"]', 'Тестовый Клиент');
    await page.fill('[data-testid="client-phone-input"]', '+79991234567');
    await page.click('[data-testid="next-step-button"]');
    
    await page.fill('[data-testid="special-requirements-textarea"]', 'A'.repeat(1001)); // Too long
    await expect(page.locator('[data-testid="requirements-error"]')).toContainText('не могут превышать 1000 символов');
    
    await page.fill('[data-testid="notes-textarea"]', 'A'.repeat(501)); // Too long
    await expect(page.locator('[data-testid="notes-error"]')).toContainText('не могут превышать 500 символов');

    // Test Step 4 validation (terms acceptance)
    await page.fill('[data-testid="special-requirements-textarea"]', 'Требования');
    await page.fill('[data-testid="notes-textarea"]', 'Заметки');
    await page.click('[data-testid="next-step-button"]');
    
    await page.click('[data-testid="next-step-button"]');
    await expect(page.locator('[data-testid="terms-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="privacy-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="rules-error"]')).toBeVisible();
  });

  test('Time slot availability checking in enhanced calendar', async () => {
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
            },
            {
              id: 2,
              start_time: '2024-02-15T14:00:00.000Z',
              end_time: '2024-02-15T15:00:00.000Z',
              space_type: 'main_studio',
              client_name: 'Another Client',
            }
          ],
          success: true,
        });
      });
    });

    // Select date
    await page.click('[data-testid="calendar-date-2024-02-15"]');
    
    // Wait for time slots to load
    await expect(page.locator('[data-testid="enhanced-time-slots"]')).toBeVisible();
    
    // Verify unavailable slots are disabled
    await expect(page.locator('[data-testid="time-slot-10:00"]')).toHaveClass(/disabled/);
    await expect(page.locator('[data-testid="time-slot-11:00"]')).toHaveClass(/disabled/);
    await expect(page.locator('[data-testid="time-slot-14:00"]')).toHaveClass(/disabled/);
    
    // Available slots should be clickable
    await expect(page.locator('[data-testid="time-slot-13:00"]')).not.toHaveClass(/disabled/);
    await expect(page.locator('[data-testid="time-slot-16:00"]')).not.toHaveClass(/disabled/);
    
    // Test slot selection
    await page.click('[data-testid="time-slot-13:00"]');
    await expect(page.locator('[data-testid="time-slot-13:00"]')).toHaveClass(/selected/);
  });

  test('Equipment selection with search and filtering', async () => {
    await page.goto('/booking');
    
    // Complete first two steps
    await page.click('[data-testid="calendar-date-2024-02-15"]');
    await page.click('[data-testid="time-slot-13:00"]');
    await page.click('[data-testid="time-slot-14:00"]');
    await page.selectOption('[data-testid="space-type-select"]', 'main_studio');
    await page.click('[data-testid="next-step-button"]');
    
    await page.fill('[data-testid="client-name-input"]', 'Тестовый Клиент');
    await page.fill('[data-testid="client-phone-input"]', '+79991234567');
    await page.click('[data-testid="next-step-button"]');

    // Test equipment search
    await test.step('Search and select equipment', async () => {
      // Search for equipment
      await page.fill('[data-testid="equipment-search"]', 'освещение');
      
      // Verify search results
      await expect(page.locator('text="Профессиональное освещение"')).toBeVisible();
      await expect(page.locator('text="Световой набор"')).toBeVisible();
      await expect(page.locator('text="Фон"')).not.toBeVisible(); // Should be filtered out
      
      // Select equipment
      await page.click('[data-testid="equipment-professional_lighting"]');
      await page.click('[data-testid="equipment-lighting_kit"]');
      
      // Verify equipment is selected
      await expect(page.locator('[data-testid="selected-equipment"]')).toContainText('Профессиональное освещение');
      await expect(page.locator('[data-testid="selected-equipment"]')).toContainText('Световой набор');
      
      // Verify price updates
      await expect(page.locator('[data-testid="equipment-price"]')).toContainText('1 000 ₽');
      await expect(page.locator('[data-testid="total-price"]')).toContainText('7 000 ₽');
      
      // Remove equipment
      await page.click('[data-testid="remove-equipment-professional_lighting"]');
      
      // Verify equipment is removed
      await expect(page.locator('[data-testid="selected-equipment"]')).not.toContainText('Профессиональное освещение');
      await expect(page.locator('[data-testid="selected-equipment"]')).toContainText('Световой набор');
      
      // Verify price updates
      await expect(page.locator('[data-testid="equipment-price"]')).toContainText('500 ₽');
      await expect(page.locator('[data-testid="total-price"]')).toContainText('6 500 ₽');
    });
  });

  test('Responsive design and dark mode in enhanced booking form', async () => {
    // Test responsive design
    await test.step('Test mobile responsiveness', async () => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto('/booking');
      
      // Verify mobile layout
      await expect(page.locator('[data-testid="enhanced-booking-form"]')).toBeVisible();
      await expect(page.locator('[data-testid="step-indicator"]')).toBeVisible();
      
      // Calendar should be responsive
      await expect(page.locator('[data-testid="enhanced-calendar"]')).toBeVisible();
      
      // Form should be scrollable
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    });

    // Test dark mode
    await test.step('Test dark mode support', async () => {
      await page.setViewportSize({ width: 1280, height: 800 });
      await page.goto('/booking');
      
      // Toggle dark mode
      await page.click('[data-testid="dark-mode-toggle"]');
      
      // Verify dark mode classes are applied
      await expect(page.locator('html')).toHaveClass(/dark/);
      
      // Verify form elements have dark mode styles
      await expect(page.locator('[data-testid="enhanced-booking-form"]')).toHaveClass(/dark:bg-gray-800/);
      
      // Verify calendar has dark mode styles
      await expect(page.locator('[data-testid="enhanced-calendar"]')).toHaveClass(/dark:bg-gray-700/);
      
      // Toggle back to light mode
      await page.click('[data-testid="dark-mode-toggle"]');
      await expect(page.locator('html')).not.toHaveClass(/dark/);
    });
  });

  test('Error handling and retry in enhanced booking flow', async () => {
    // Mock API error for booking creation
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
    await page.click('[data-testid="time-slot-13:00"]');
    await page.click('[data-testid="time-slot-14:00"]');
    await page.selectOption('[data-testid="space-type-select"]', 'main_studio');
    await page.click('[data-testid="next-step-button"]');
    
    await page.fill('[data-testid="client-name-input"]', 'Тестовый Клиент');
    await page.fill('[data-testid="client-phone-input"]', '+79991234567');
    await page.fill('[data-testid="client-email-input"]', 'test@example.com');
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
    
    // Mock successful response for retry
    await page.route('**/api/v1/bookings', async (route) => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            data: {
              id: 1,
              booking_reference: 'BK-2024-001',
              // ... rest of successful response
            },
            success: true,
          }),
        });
      }
    });
    
    // Click retry button
    await page.click('[data-testid="retry-button"]');
    
    // Should show success message
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
  });
});