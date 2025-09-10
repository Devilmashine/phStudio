/**
 * E2E Tests for Enhanced Kanban Board
 * End-to-end тесты для улучшенной Kanban доски
 */

import { test, expect, Page } from '@playwright/test';

test.describe('Enhanced Kanban Board E2E Tests', () => {
  let page: Page;

  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage();
    
    // Mock API responses for kanban board data
    await page.route('**/api/v1/bookings**', async (route) => {
      const url = route.request().url();
      
      if (route.request().method() === 'GET' && url.includes('/kanban')) {
        // Mock kanban board data
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            data: {
              pending: [
                {
                  id: 1,
                  booking_reference: 'BK-PND-001',
                  client_name: 'Клиент 1',
                  client_phone: '+79991234567',
                  booking_date: '2024-02-15',
                  start_time: '2024-02-15T10:00:00.000Z',
                  end_time: '2024-02-15T12:00:00.000Z',
                  state: 'pending',
                  total_price: 5000,
                  priority: 'normal',
                  created_at: '2024-02-10T10:00:00.000Z'
                }
              ],
              confirmed: [
                {
                  id: 2,
                  booking_reference: 'BK-CNF-001',
                  client_name: 'Клиент 2',
                  client_phone: '+79991234568',
                  booking_date: '2024-02-15',
                  start_time: '2024-02-15T14:00:00.000Z',
                  end_time: '2024-02-15T16:00:00.000Z',
                  state: 'confirmed',
                  total_price: 4500,
                  priority: 'high',
                  created_at: '2024-02-11T10:00:00.000Z'
                }
              ],
              in_progress: [
                {
                  id: 3,
                  booking_reference: 'BK-IPG-001',
                  client_name: 'Клиент 3',
                  client_phone: '+79991234569',
                  booking_date: '2024-02-15',
                  start_time: '2024-02-15T16:00:00.000Z',
                  end_time: '2024-02-15T18:00:00.000Z',
                  state: 'in_progress',
                  total_price: 6000,
                  priority: 'urgent',
                  created_at: '2024-02-12T10:00:00.000Z'
                }
              ],
              completed: []
            },
            success: true,
          }),
        });
      } else if (route.request().method() === 'PUT' && url.includes('/transition')) {
        // Mock state transition
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            data: {
              id: 1,
              state: 'confirmed',
              updated_at: new Date().toISOString()
            },
            success: true,
          }),
        });
      } else if (route.request().method() === 'GET') {
        // Mock general bookings list
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
          }),
        });
      }
    });

    // Mock WebSocket connection
    await page.route('**/api/v1/ws**', async (route) => {
      await route.fulfill({
        status: 101,
        headers: {
          'Upgrade': 'websocket',
          'Connection': 'Upgrade'
        }
      });
    });
  });

  test('Kanban board loads and displays all columns', async () => {
    await page.goto('/admin/kanban');

    // Verify kanban board header
    await expect(page.locator('h1:text("Kanban доска")')).toBeVisible();
    
    // Verify all columns are displayed
    await expect(page.locator('text="Ожидает подтверждения"')).toBeVisible();
    await expect(page.locator('text="Подтверждено"')).toBeVisible();
    await expect(page.locator('text="В процессе"')).toBeVisible();
    await expect(page.locator('text="Завершено"')).toBeVisible();
    
    // Verify bookings in columns
    await expect(page.locator('[data-testid="kanban-card-1"]')).toBeVisible();
    await expect(page.locator('[data-testid="kanban-card-2"]')).toBeVisible();
    await expect(page.locator('[data-testid="kanban-card-3"]')).toBeVisible();
  });

  test('Drag and drop booking between columns', async () => {
    await page.goto('/admin/kanban');

    // Verify initial state
    await expect(page.locator('[data-column="pending"] [data-testid="kanban-card-1"]')).toBeVisible();
    
    // Drag booking from pending to confirmed column
    const bookingCard = await page.locator('[data-testid="kanban-card-1"]');
    const confirmedColumn = await page.locator('[data-column="confirmed"]');
    
    await bookingCard.dragTo(confirmedColumn);
    
    // Verify success message
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="success-message"]')).toContainText('Бронирование перемещено');
  });

  test('Invalid state transition is prevented', async () => {
    await page.goto('/admin/kanban');

    // Try to drag a completed booking to pending (invalid transition)
    // First, we need to have a completed booking, so let's mock one
    await page.route('**/api/v1/bookings/kanban', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: {
            pending: [],
            confirmed: [],
            in_progress: [],
            completed: [
              {
                id: 4,
                booking_reference: 'BK-CMP-001',
                client_name: 'Клиент 4',
                client_phone: '+79991234570',
                booking_date: '2024-02-14',
                start_time: '2024-02-14T10:00:00.000Z',
                end_time: '2024-02-14T12:00:00.000Z',
                state: 'completed',
                total_price: 5500,
                priority: 'normal',
                created_at: '2024-02-13T10:00:00.000Z'
              }
            ]
          },
          success: true,
        });
      });
    });
    
    // Reload the page to get the updated mock data
    await page.reload();
    
    // Try to drag completed booking to pending column (should be prevented)
    const completedCard = await page.locator('[data-testid="kanban-card-4"]');
    const pendingColumn = await page.locator('[data-column="pending"]');
    
    await completedCard.dragTo(pendingColumn);
    
    // Verify error message
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-message"]')).toContainText('Недопустимый переход статуса');
  });

  test('Create new booking from kanban board', async () => {
    await page.goto('/admin/kanban');

    // Click create booking button
    await page.click('[data-testid="create-booking-button"]');
    
    // Verify navigation to booking form
    await expect(page).toHaveURL(/.*\/booking$/);
  });

  test('Edit booking from kanban card', async () => {
    await page.goto('/admin/kanban');

    // Click edit button on a kanban card
    await page.click('[data-testid="kanban-card-1"] [data-testid="edit-booking-button"]');
    
    // Verify navigation to booking edit page
    await expect(page).toHaveURL(/.*\/booking\/\d+/);
  });

  test('Priority visualization in kanban cards', async () => {
    await page.goto('/admin/kanban');

    // Verify urgent priority booking has correct styling
    const urgentCard = await page.locator('[data-testid="kanban-card-3"]');
    await expect(urgentCard).toHaveClass(/border-red-500/);
    
    // Verify high priority booking has correct styling
    const highCard = await page.locator('[data-testid="kanban-card-2"]');
    await expect(highCard).toHaveClass(/border-orange-500/);
    
    // Verify normal priority booking has correct styling
    const normalCard = await page.locator('[data-testid="kanban-card-1"]');
    await expect(normalCard).toHaveClass(/border-blue-500/);
  });

  test('Column capacity indicators', async () => {
    await page.goto('/admin/kanban');

    // Verify pending column capacity indicator
    await expect(page.locator('[data-column="pending"] [data-testid="column-capacity"]')).toBeVisible();
    await expect(page.locator('[data-column="pending"] [data-testid="column-capacity"]')).toContainText('1/20');
    
    // Verify confirmed column capacity indicator
    await expect(page.locator('[data-column="confirmed"] [data-testid="column-capacity"]')).toBeVisible();
    await expect(page.locator('[data-column="confirmed"] [data-testid="column-capacity"]')).toContainText('1/15');
    
    // Verify in-progress column capacity indicator
    await expect(page.locator('[data-column="in_progress"] [data-testid="column-capacity"]')).toBeVisible();
    await expect(page.locator('[data-column="in_progress"] [data-testid="column-capacity"]')).toContainText('1/10');
  });
});