import { render, screen, fireEvent } from '@testing-library/react';
import BookingPage from '../frontend/src/pages/BookingPage';
import { MemoryRouter } from 'react-router-dom';

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
});
