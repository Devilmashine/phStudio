/**
 * E2E Tests for Enhanced Admin Dashboard
 * End-to-end тесты для улучшенного административного дашборда
 */

import { test, expect, Page } from '@playwright/test';

test.describe('Enhanced Admin Dashboard E2E Tests', () => {
  let page: Page;

  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage();
    
    // Mock API responses for dashboard data
    await page.route('**/api/v1/bookings**', async (route) => {
      if (route.request().method() === 'GET' && route.request().url().includes('/stats')) {
        // Mock booking stats
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            data: {
              total_bookings: 45,
              completed_bookings: 32,
              pending_bookings: 8,
              total_revenue: 225000,
              monthly_revenue: 75000,
              completion_rate: 71.1,
              average_booking_value: 5000
            },
            success: true,
          }),
        });
      } else if (route.request().method() === 'GET') {
        // Mock bookings list
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: [
              {
                id: 1,
                booking_reference: 'BK-2024-001',
                client_name: 'Тестовый Клиент 1',
                client_phone: '+79991234567',
                booking_date: '2024-02-15',
                start_time: '2024-02-15T10:00:00.000Z',
                end_time: '2024-02-15T12:00:00.000Z',
                state: 'confirmed',
                total_price: 5000,
                priority: 'normal',
                created_at: '2024-02-10T10:00:00.000Z'
              },
              {
                id: 2,
                booking_reference: 'BK-2024-002',
                client_name: 'Тестовый Клиент 2',
                client_phone: '+79991234568',
                booking_date: '2024-02-15',
                start_time: '2024-02-15T14:00:00.000Z',
                end_time: '2024-02-15T16:00:00.000Z',
                state: 'pending',
                total_price: 4500,
                priority: 'high',
                created_at: '2024-02-11T10:00:00.000Z'
              }
            ],
            total: 2,
            page: 1,
            pages: 1,
            per_page: 20,
            success: true,
          }),
        });
      }
    });

    // Mock employees API
    await page.route('**/api/v1/employees**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            {
              id: 1,
              employee_id: 'EMP001',
              username: 'manager',
              email: 'manager@example.com',
              full_name: 'Manager User',
              role: 'manager',
              status: 'active',
              last_login: '2024-02-14T10:00:00.000Z'
            },
            {
              id: 2,
              employee_id: 'EMP002',
              username: 'staff',
              email: 'staff@example.com',
              full_name: 'Staff User',
              role: 'staff',
              status: 'active',
              last_login: '2024-02-14T09:00:00.000Z'
            }
          ],
          total: 2,
          page: 1,
          pages: 1,
          per_page: 20,
          success: true,
        }),
      });
    });

    // Mock WebSocket connection
    await page.route('**/api/v1/ws**', async (route) => {
      // Mock successful WebSocket connection
      await route.fulfill({
        status: 101,
        headers: {
          'Upgrade': 'websocket',
          'Connection': 'Upgrade'
        }
      });
    });
  });

  test('Dashboard loads and displays all components', async () => {
    await page.goto('/admin/dashboard');

    // Verify dashboard header is visible
    await expect(page.locator('h1:text("Административный дашборд")')).toBeVisible();
    
    // Verify stat cards are displayed
    await expect(page.locator('[data-testid="stat-card-total-bookings"]')).toBeVisible();
    await expect(page.locator('[data-testid="stat-card-today-bookings"]')).toBeVisible();
    await expect(page.locator('[data-testid="stat-card-revenue"]')).toBeVisible();
    await expect(page.locator('[data-testid="stat-card-completion-rate"]')).toBeVisible();
    
    // Verify chart is displayed
    await expect(page.locator('[data-testid="booking-chart"]')).toBeVisible();
    
    // Verify recent bookings table is displayed
    await expect(page.locator('[data-testid="recent-bookings-table"]')).toBeVisible();
    
    // Verify employee activity section is displayed
    await expect(page.locator('[data-testid="employee-activity"]')).toBeVisible();
    
    // Verify system health section is displayed
    await expect(page.locator('[data-testid="system-health"]')).toBeVisible();
  });

  test('Dashboard displays correct statistics', async () => {
    await page.goto('/admin/dashboard');

    // Verify stat card values
    await expect(page.locator('[data-testid="stat-value-total-bookings"]')).toContainText('45');
    await expect(page.locator('[data-testid="stat-value-revenue"]')).toContainText('225 000 ₽');
    await expect(page.locator('[data-testid="stat-value-completion-rate"]')).toContainText('71.1%');
    
    // Verify recent bookings are displayed
    await expect(page.locator('text="Тестовый Клиент 1"')).toBeVisible();
    await expect(page.locator('text="Тестовый Клиент 2"')).toBeVisible();
    
    // Verify employee data is displayed
    await expect(page.locator('text="Manager User"')).toBeVisible();
    await expect(page.locator('text="Staff User"')).toBeVisible();
  });

  test('Dashboard refresh functionality', async () => {
    await page.goto('/admin/dashboard');

    // Click refresh button
    await page.click('[data-testid="refresh-dashboard"]');
    
    // Verify loading state
    await expect(page.locator('[data-testid="refresh-spinner"]')).toBeVisible();
    
    // Wait for refresh to complete
    await expect(page.locator('[data-testid="refresh-spinner"]')).not.toBeVisible();
    
    // Verify data is still displayed
    await expect(page.locator('[data-testid="stat-card-total-bookings"]')).toBeVisible();
  });

  test('Navigation to booking details', async () => {
    await page.goto('/admin/dashboard');

    // Click on a booking in the recent bookings table
    await page.click('text="BK-2024-001"');
    
    // Verify navigation to booking details page
    await expect(page).toHaveURL(/.*booking\/\d+/);
  });

  test('WebSocket connection status', async () => {
    await page.goto('/admin/dashboard');

    // Verify WebSocket connection indicator
    await expect(page.locator('[data-testid="websocket-connected"]')).toBeVisible();
    
    // Simulate disconnection
    await page.evaluate(() => {
      // Mock WebSocket disconnection
      window.dispatchEvent(new Event('offline'));
    });
    
    // Verify disconnection indicator
    await expect(page.locator('[data-testid="websocket-disconnected"]')).toBeVisible();
  });
});