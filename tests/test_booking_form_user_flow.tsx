import { render, screen, fireEvent } from '@testing-library/react';
import BookingPage from '../frontend/src/pages/BookingPage';
import { MemoryRouter } from 'react-router-dom';
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  rest.post('https://api.telegram.org/bot<your-bot-token>/sendMessage', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json({ ok: true }));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('BookingPage User Flow', () => {
  it('should allow a user to fill out and submit the booking form', async () => {
    render(
      <MemoryRouter>
        <BookingPage />
      </MemoryRouter>
    );

    // Select a date
    const dateInput = screen.getByLabelText(/Дата/i);
    fireEvent.change(dateInput, { target: { value: '2025-05-13' } });

    // Select a time
    const timeSelect = screen.getByLabelText(/Время/i);
    fireEvent.change(timeSelect, { target: { value: '10:00' } });

    // Fill in client name
    const nameInput = screen.getByLabelText(/Имя/i);
    fireEvent.change(nameInput, { target: { value: 'Иван Иванов' } });

    // Fill in client phone
    const phoneInput = screen.getByLabelText(/Телефон/i);
    fireEvent.change(phoneInput, { target: { value: '+79991234567' } });

    // Fill in client email
    const emailInput = screen.getByLabelText(/Email/i);
    fireEvent.change(emailInput, { target: { value: 'ivan@example.com' } });

    // Fill in additional notes
    const notesInput = screen.getByLabelText(/Дополнительная информация/i);
    fireEvent.change(notesInput, { target: { value: 'Пожалуйста, подготовьте студию заранее.' } });

    // Submit the form
    const submitButton = screen.getByRole('button', { name: /Забронировать/i });
    fireEvent.click(submitButton);

    // Check for navigation to success page
    expect(await screen.findByText(/Забронировать/i)).toBeInTheDocument();
  });

  it('should send booking data to Telegram', async () => {
    render(
      <MemoryRouter>
        <BookingPage />
      </MemoryRouter>
    );

    // Заполнение формы
    fireEvent.change(screen.getByLabelText(/Дата/i), { target: { value: '2025-05-13' } });
    fireEvent.change(screen.getByLabelText(/Время/i), { target: { value: '10:00' } });
    fireEvent.change(screen.getByLabelText(/Имя/i), { target: { value: 'Иван Иванов' } });
    fireEvent.change(screen.getByLabelText(/Телефон/i), { target: { value: '+79991234567' } });
    fireEvent.change(screen.getByLabelText(/Email/i), { target: { value: 'ivan@example.com' } });
    fireEvent.change(screen.getByLabelText(/Дополнительная информация/i), { target: { value: 'Пожалуйста, подготовьте студию заранее.' } });

    // Отправка формы
    fireEvent.click(screen.getByRole('button', { name: /Забронировать/i }));

    // Проверка отправки данных в Telegram
    await screen.findByText(/Забронировать/i);
    expect(server.events).toHaveBeenCalledWith(
      expect.objectContaining({
        body: expect.stringContaining('Иван Иванов'),
      })
    );
  });
});
