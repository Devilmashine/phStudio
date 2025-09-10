/**
 * E2E Tests for Employee Management
 * End-to-end тесты для управления сотрудниками
 */

import { test, expect, Page } from '@playwright/test';

test.describe('Employee Management E2E Tests', () => {
  let page: Page;

  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage();
    
    // Mock API responses for employee management
    await page.route('**/api/v1/employees**', async (route) => {
      const url = route.request().url();
      const method = route.request().method();
      
      if (method === 'GET' && !url.includes('/roles') && !url.includes('/permissions')) {
        // Mock employees list
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
                phone: '+79991234567',
                created_at: '2024-01-01T10:00:00.000Z',
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
                phone: '+79991234568',
                created_at: '2024-01-02T10:00:00.000Z',
                last_login: '2024-02-14T09:00:00.000Z'
              }
            ],
            total: 2,
            page: 1,
            pages: 1,
            per_page: 20,
            success: true,
          });
        });
      } else if (method === 'POST') {
        // Mock employee creation
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            data: {
              id: 3,
              employee_id: 'EMP003',
              username: 'newuser',
              email: 'newuser@example.com',
              full_name: 'New User',
              role: 'staff',
              status: 'pending_activation',
              phone: '+79991234569',
              created_at: new Date().toISOString()
            },
            success: true,
          });
        });
      } else if (method === 'PUT' && url.includes('/3')) {
        // Mock employee update
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            data: {
              id: 3,
              employee_id: 'EMP003',
              username: 'newuser',
              email: 'updated@example.com',
              full_name: 'Updated User',
              role: 'manager',
              status: 'active',
              phone: '+79991234570',
              created_at: new Date().toISOString()
            },
            success: true,
          });
        });
      } else if (method === 'DELETE' && url.includes('/3')) {
        // Mock employee deletion
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            message: 'Employee deleted successfully',
            success: true,
          });
        });
      } else if (url.includes('/roles')) {
        // Mock roles list
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            data: [
              { id: 'owner', name: 'Владелец' },
              { id: 'admin', name: 'Администратор' },
              { id: 'manager', name: 'Менеджер' },
              { id: 'staff', name: 'Сотрудник' },
              { id: 'viewer', name: 'Наблюдатель' }
            ],
            success: true,
          });
        });
      } else if (url.includes('/permissions')) {
        // Mock permissions list
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            data: [
              { id: 'bookings.create', name: 'Создание бронирований' },
              { id: 'bookings.edit', name: 'Редактирование бронирований' },
              { id: 'bookings.delete', name: 'Удаление бронирований' },
              { id: 'employees.manage', name: 'Управление сотрудниками' }
            ],
            success: true,
          });
        });
      }
    });
  });

  test('Employee list loads and displays correctly', async () => {
    await page.goto('/admin/employees');

    // Verify page header
    await expect(page.locator('h1:text("Управление сотрудниками")')).toBeVisible();
    
    // Verify employee table is displayed
    await expect(page.locator('[data-testid="employees-table"]')).toBeVisible();
    
    // Verify employees are displayed
    await expect(page.locator('text="Manager User"')).toBeVisible();
    await expect(page.locator('text="Staff User"')).toBeVisible();
    
    // Verify employee details
    await expect(page.locator('text="EMP001"')).toBeVisible();
    await expect(page.locator('text="manager@example.com"')).toBeVisible();
    await expect(page.locator('text="Активен"')).toBeVisible();
  });

  test('Create new employee', async () => {
    await page.goto('/admin/employees');

    // Click add employee button
    await page.click('[data-testid="add-employee-button"]');
    
    // Verify employee form is displayed
    await expect(page.locator('[data-testid="employee-form"]')).toBeVisible();
    
    // Fill employee form
    await page.fill('[data-testid="employee-username"]', 'newuser');
    await page.fill('[data-testid="employee-email"]', 'newuser@example.com');
    await page.fill('[data-testid="employee-full-name"]', 'New User');
    await page.fill('[data-testid="employee-phone"]', '+79991234569');
    await page.selectOption('[data-testid="employee-role"]', 'staff');
    
    // Submit form
    await page.click('[data-testid="save-employee-button"]');
    
    // Verify success message
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="success-message"]')).toContainText('Сотрудник успешно создан');
    
    // Verify employee appears in table
    await expect(page.locator('text="New User"')).toBeVisible();
  });

  test('Edit existing employee', async () => {
    await page.goto('/admin/employees');

    // Click edit button for first employee
    await page.click('[data-testid="edit-employee-1"]');
    
    // Verify form is populated with existing data
    await expect(page.locator('[data-testid="employee-username"]')).toHaveValue('manager');
    await expect(page.locator('[data-testid="employee-email"]')).toHaveValue('manager@example.com');
    
    // Update employee data
    await page.fill('[data-testid="employee-email"]', 'updated-manager@example.com');
    await page.selectOption('[data-testid="employee-role"]', 'admin');
    
    // Submit form
    await page.click('[data-testid="save-employee-button"]');
    
    // Verify success message
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="success-message"]')).toContainText('Сотрудник успешно обновлен');
  });

  test('Delete employee', async () => {
    await page.goto('/admin/employees');

    // Click delete button for an employee
    await page.click('[data-testid="delete-employee-2"]');
    
    // Confirm deletion
    await page.click('[data-testid="confirm-delete"]');
    
    // Verify success message
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="success-message"]')).toContainText('Сотрудник успешно удален');
    
    // Verify employee is removed from table
    await expect(page.locator('text="Staff User"')).not.toBeVisible();
  });

  test('Employee form validation', async () => {
    await page.goto('/admin/employees');
    await page.click('[data-testid="add-employee-button"]');

    // Try to submit empty form
    await page.click('[data-testid="save-employee-button"]');
    
    // Verify validation errors
    await expect(page.locator('[data-testid="username-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="email-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="full-name-error"]')).toBeVisible();
    
    // Fill with invalid data
    await page.fill('[data-testid="employee-username"]', 'ab');
    await page.fill('[data-testid="employee-email"]', 'invalid-email');
    await page.fill('[data-testid="employee-phone"]', '123');
    
    // Verify specific validation errors
    await expect(page.locator('[data-testid="username-error"]')).toContainText('минимум 3 символа');
    await expect(page.locator('[data-testid="email-error"]')).toContainText('корректный email');
    await expect(page.locator('[data-testid="phone-error"]')).toContainText('корректный номер');
  });

  test('Employee status management', async () => {
    await page.goto('/admin/employees');

    // Verify status badges are displayed correctly
    await expect(page.locator('[data-testid="employee-status-1"]')).toContainText('Активен');
    await expect(page.locator('[data-testid="employee-status-1"]')).toHaveClass(/bg-green-100/);
    
    // Change employee status
    await page.click('[data-testid="edit-employee-1"]');
    await page.selectOption('[data-testid="employee-status"]', 'suspended');
    await page.click('[data-testid="save-employee-button"]');
    
    // Verify status update
    await expect(page.locator('[data-testid="employee-status-1"]')).toContainText('Приостановлен');
    await expect(page.locator('[data-testid="employee-status-1"]')).toHaveClass(/bg-yellow-100/);
  });

  test('Employee search and filtering', async () => {
    await page.goto('/admin/employees');

    // Search for employee by name
    await page.fill('[data-testid="employee-search"]', 'Manager');
    
    // Verify search results
    await expect(page.locator('text="Manager User"')).toBeVisible();
    await expect(page.locator('text="Staff User"')).not.toBeVisible();
    
    // Filter by role
    await page.selectOption('[data-testid="role-filter"]', 'staff');
    
    // Verify filter results
    await expect(page.locator('text="Staff User"')).toBeVisible();
    await expect(page.locator('text="Manager User"')).not.toBeVisible();
    
    // Filter by status
    await page.selectOption('[data-testid="status-filter"]', 'active');
    
    // Verify status filter results
    await expect(page.locator('[data-testid="employee-status-filter"]')).toHaveValue('active');
  });

  test('Employee permissions management', async () => {
    await page.goto('/admin/employees');

    // Click permissions button for an employee
    await page.click('[data-testid="permissions-employee-1"]');
    
    // Verify permissions modal is displayed
    await expect(page.locator('[data-testid="permissions-modal"]')).toBeVisible();
    
    // Verify available permissions are displayed
    await expect(page.locator('text="Создание бронирований"')).toBeVisible();
    await expect(page.locator('text="Управление сотрудниками"')).toBeVisible();
    
    // Toggle a permission
    await page.click('[data-testid="permission-toggle-bookings.create"]');
    
    // Save permissions
    await page.click('[data-testid="save-permissions-button"]');
    
    // Verify success message
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="success-message"]')).toContainText('Права доступа успешно обновлены');
  });
});