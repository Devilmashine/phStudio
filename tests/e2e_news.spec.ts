import { test, expect } from '@playwright/test';

const adminHeaders = {
  'X-User-Role': 'admin',
  'X-User-Id': '1',
  'X-User-Name': 'admin',
};

const managerHeaders = {
  'X-User-Role': 'manager',
  'X-User-Id': '2',
  'X-User-Name': 'manager',
};

const apiUrl = 'http://localhost:8888/api/news/';

test.describe('Новости (e2e)', () => {
  let createdId: number;

  test('admin может создать новость', async ({ request }) => {
    const res = await request.post(apiUrl, {
      data: { title: 'E2E Новость', content: 'E2E контент', published: 1 },
      headers: adminHeaders,
    });
    expect(res.status()).toBe(201);
    const data = await res.json();
    expect(data.title).toBe('E2E Новость');
    createdId = data.id;
  });

  test('manager не может создать новость', async ({ request }) => {
    const res = await request.post(apiUrl, {
      data: { title: 'E2E Менеджер', content: 'fail', published: 1 },
      headers: managerHeaders,
    });
    expect(res.status()).toBe(403);
  });

  test('admin может обновить новость', async ({ request }) => {
    const res = await request.put(apiUrl + createdId, {
      data: { title: 'E2E Обновлено', content: 'Обновленный контент', published: 1 },
      headers: adminHeaders,
    });
    expect(res.status()).toBe(200);
    const data = await res.json();
    expect(data.title).toBe('E2E Обновлено');
  });

  test('manager не может обновить новость', async ({ request }) => {
    const res = await request.put(apiUrl + createdId, {
      data: { title: 'fail', content: 'fail', published: 1 },
      headers: managerHeaders,
    });
    expect([403, 404]).toContain(res.status());
  });

  test('admin может удалить новость', async ({ request }) => {
    const res = await request.delete(apiUrl + createdId, { headers: adminHeaders });
    expect(res.status()).toBe(204);
  });

  test('удалённая новость не найдена', async ({ request }) => {
    const res = await request.get(apiUrl + createdId);
    expect(res.status()).toBe(404);
  });
});
