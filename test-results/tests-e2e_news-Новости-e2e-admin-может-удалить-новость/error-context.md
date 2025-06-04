# Test info

- Name: Новости (e2e) >> admin может удалить новость
- Location: /workspaces/phStudio/tests/e2e_news.spec.ts:57:3

# Error details

```
Error: expect(received).toBe(expected) // Object.is equality

Expected: 204
Received: 422
    at /workspaces/phStudio/tests/e2e_news.spec.ts:59:26
```

# Test source

```ts
   1 | import { test, expect } from '@playwright/test';
   2 |
   3 | const adminHeaders = {
   4 |   'X-User-Role': 'admin',
   5 |   'X-User-Id': '1',
   6 |   'X-User-Name': 'admin',
   7 | };
   8 |
   9 | const managerHeaders = {
  10 |   'X-User-Role': 'manager',
  11 |   'X-User-Id': '2',
  12 |   'X-User-Name': 'manager',
  13 | };
  14 |
  15 | const apiUrl = 'http://localhost:8000/api/news/';
  16 |
  17 | test.describe('Новости (e2e)', () => {
  18 |   let createdId: number;
  19 |
  20 |   test('admin может создать новость', async ({ request }) => {
  21 |     const res = await request.post(apiUrl, {
  22 |       data: { title: 'E2E Новость', content: 'E2E контент', published: 1 },
  23 |       headers: adminHeaders,
  24 |     });
  25 |     expect(res.status()).toBe(201);
  26 |     const data = await res.json();
  27 |     expect(data.title).toBe('E2E Новость');
  28 |     createdId = data.id;
  29 |   });
  30 |
  31 |   test('manager не может создать новость', async ({ request }) => {
  32 |     const res = await request.post(apiUrl, {
  33 |       data: { title: 'E2E Менеджер', content: 'fail', published: 1 },
  34 |       headers: managerHeaders,
  35 |     });
  36 |     expect(res.status()).toBe(403);
  37 |   });
  38 |
  39 |   test('admin может обновить новость', async ({ request }) => {
  40 |     const res = await request.put(apiUrl + createdId, {
  41 |       data: { title: 'E2E Обновлено', content: 'Обновленный контент', published: 1 },
  42 |       headers: adminHeaders,
  43 |     });
  44 |     expect(res.status()).toBe(200);
  45 |     const data = await res.json();
  46 |     expect(data.title).toBe('E2E Обновлено');
  47 |   });
  48 |
  49 |   test('manager не может обновить новость', async ({ request }) => {
  50 |     const res = await request.put(apiUrl + createdId, {
  51 |       data: { title: 'fail', content: 'fail', published: 1 },
  52 |       headers: managerHeaders,
  53 |     });
  54 |     expect([403, 404]).toContain(res.status());
  55 |   });
  56 |
  57 |   test('admin может удалить новость', async ({ request }) => {
  58 |     const res = await request.delete(apiUrl + createdId, { headers: adminHeaders });
> 59 |     expect(res.status()).toBe(204);
     |                          ^ Error: expect(received).toBe(expected) // Object.is equality
  60 |   });
  61 |
  62 |   test('удалённая новость не найдена', async ({ request }) => {
  63 |     const res = await request.get(apiUrl + createdId);
  64 |     expect(res.status()).toBe(404);
  65 |   });
  66 | });
  67 |
```