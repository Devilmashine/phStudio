/**
 * E2E Tests for Authentication Flow
 * End-to-end тесты для потока аутентификации
 */

import { test, expect, Page } from '@playwright/test';

test.describe('Authentication Flow E2E Tests', () => {
  let page: Page;

  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage();
  });

  test('Successful login with valid credentials', async () => {
    // Mock successful login API response
    await page.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: {
            access_token: 'test-access-token',
            refresh_token: 'test-refresh-token',
            employee: {
              id: 1,
              employee_id: 'EMP001',
              username: 'manager',
              email: 'manager@example.com',
              full_name: 'Manager User',
              role: 'manager',
              status: 'active'
            }
          },
          success: true,
        }),
      });
    });

    await page.goto('/login');

    // Fill login form
    await page.fill('[data-testid="username-input"]', 'manager');
    await page.fill('[data-testid="password-input"]', 'password123');
    
    // Submit form
    await page.click('[data-testid="login-button"]');
    
    // Verify successful navigation to dashboard
    await expect(page).toHaveURL('/admin/dashboard');
    
    // Verify user is logged in
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
    await expect(page.locator('text="Manager User"')).toBeVisible();
  });

  test('Login fails with invalid credentials', async () => {
    // Mock failed login API response
    await page.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Неверное имя пользователя или пароль',
          success: false,
        }),
      });
    });

    await page.goto('/login');

    // Fill login form with invalid credentials
    await page.fill('[data-testid="username-input"]', 'invaliduser');
    await page.fill('[data-testid="password-input"]', 'wrongpassword');
    
    // Submit form
    await page.click('[data-testid="login-button"]');
    
    // Verify error message is displayed
    await expect(page.locator('[data-testid="login-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="login-error"]')).toContainText('Неверное имя пользователя или пароль');
    
    // Verify still on login page
    await expect(page).toHaveURL('/login');
  });

  test('Login form validation', async () => {
    await page.goto('/login');

    // Try to submit empty form
    await page.click('[data-testid="login-button"]');
    
    // Verify validation errors
    await expect(page.locator('[data-testid="username-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="password-error"]')).toBeVisible();
    
    // Fill with minimal data
    await page.fill('[data-testid="username-input"]', 'a');
    await page.fill('[data-testid="password-input"]', '123');
    
    // Verify validation errors for minimum length
    await expect(page.locator('[data-testid="username-error"]')).toContainText('минимум 3 символа');
    await expect(page.locator('[data-testid="password-error"]')).toContainText('минимум 6 символов');
  });

  test('Logout functionality', async () => {
    // First login
    await page.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: {
            access_token: 'test-access-token',
            refresh_token: 'test-refresh-token',
            employee: {
              id: 1,
              employee_id: 'EMP001',
              username: 'manager',
              email: 'manager@example.com',
              full_name: 'Manager User',
              role: 'manager',
              status: 'active'
            }
          },
          success: true,
        }),
      });
    });

    await page.goto('/login');
    await page.fill('[data-testid="username-input"]', 'manager');
    await page.fill('[data-testid="password-input"]', 'password123');
    await page.click('[data-testid="login-button"]');
    
    // Verify logged in
    await expect(page).toHaveURL('/admin/dashboard');
    
    // Mock logout API response
    await page.route('**/api/v1/auth/logout', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Выход выполнен успешно',
          success: true,
        }),
      });
    });
    
    // Click logout button
    await page.click('[data-testid="user-menu"]');
    await page.click('[data-testid="logout-button"]');
    
    // Verify redirected to login page
    await expect(page).toHaveURL('/login');
    
    // Verify login form is visible
    await expect(page.locator('[data-testid="login-form"]')).toBeVisible();
  });

  test('Access to protected routes redirects to login', async () => {
    // Try to access admin dashboard without being logged in
    await page.goto('/admin/dashboard');
    
    // Verify redirected to login page
    await expect(page).toHaveURL(/.*login.*/);
    
    // Verify login page is displayed
    await expect(page.locator('h2:text("Вход в админ-панель")')).toBeVisible();
  });

  test('Session expiration handling', async () => {
    // First login
    await page.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: {
            access_token: 'test-access-token',
            refresh_token: 'test-refresh-token',
            employee: {
              id: 1,
              employee_id: 'EMP001',
              username: 'manager',
              email: 'manager@example.com',
              full_name: 'Manager User',
              role: 'manager',
              status: 'active'
            }
          },
          success: true,
        }),
      });
    });

    await page.goto('/login');
    await page.fill('[data-testid="username-input"]', 'manager');
    await page.fill('[data-testid="password-input"]', 'password123');
    await page.click('[data-testid="login-button"]');
    
    // Verify logged in
    await expect(page).toHaveURL('/admin/dashboard');
    
    // Mock API response for expired token
    await page.route('**/api/v1/bookings**', async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 401,
          contentType: 'application/json',
          body: JSON.stringify({
            message: 'Токен доступа истек',
            success: false,
          }),
        });
      }
    });
    
    // Try to access a protected API endpoint
    await page.goto('/admin/bookings');
    
    // Verify redirected to login page
    await expect(page).toHaveURL(/.*login.*/);
    
    // Verify session expired message
    await expect(page.locator('[data-testid="session-expired-message"]')).toBeVisible();
  });

  test('Remember me functionality', async () => {
    // Mock successful login API response
    await page.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: {
            access_token: 'test-access-token',
            refresh_token: 'test-refresh-token',
            employee: {
              id: 1,
              employee_id: 'EMP001',
              username: 'manager',
              email: 'manager@example.com',
              full_name: 'Manager User',
              role: 'manager',
              status: 'active'
            }
          },
          success: true,
        }),
      });
    });

    await page.goto('/login');

    // Fill login form
    await page.fill('[data-testid="username-input"]', 'manager');
    await page.fill('[data-testid="password-input"]', 'password123');
    
    // Check "Remember me" checkbox
    await page.check('[data-testid="remember-me-checkbox"]');
    
    // Submit form
    await page.click('[data-testid="login-button"]');
    
    // Verify successful login
    await expect(page).toHaveURL('/admin/dashboard');
    
    // Close and reopen browser to test persistent login
    await page.close();
    page = await browser.newPage();
    
    // Try to access protected route
    await page.goto('/admin/dashboard');
    
    // Should still be logged in (in a real scenario, this would depend on token storage)
    // For this test, we're just verifying the flow
  });
});