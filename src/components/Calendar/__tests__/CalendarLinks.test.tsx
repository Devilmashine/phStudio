import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import CalendarLinks from '../CalendarLinks';
import axios from 'axios';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('CalendarLinks', () => {
  beforeEach(() => {
    localStorage.setItem('user', JSON.stringify({ id: 42, ical_token: 'demo-token' }));
  });
  afterEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
  });

  it('отображает ссылку для экспорта', () => {
    render(<CalendarLinks />);
    expect(screen.getByText(/экспорт календаря/i)).toBeInTheDocument();
    expect(screen.getByDisplayValue(/ical\/42\/demo-token/)).toBeInTheDocument();
  });

  it('копирует ссылку в буфер обмена', async () => {
    Object.assign(navigator, { clipboard: { writeText: jest.fn() } });
    render(<CalendarLinks />);
    const copyBtn = screen.getByText(/копировать ссылку/i);
    fireEvent.click(copyBtn);
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(expect.stringContaining('/ical/42/demo-token'));
  });

  it('сбрасывает токен и обновляет ссылку', async () => {
    mockedAxios.post.mockResolvedValue({ data: { ical_token: 'new-token' } });
    render(<CalendarLinks />);
    const resetBtn = screen.getByText(/сбросить токен/i);
    fireEvent.click(resetBtn);
    await waitFor(() => {
      expect(screen.getByDisplayValue(/ical\/42\/new-token/)).toBeInTheDocument();
    });
  });

  it('отображает ошибку при сбросе токена', async () => {
    mockedAxios.post.mockRejectedValue({ response: { data: { detail: 'Ошибка' } } });
    render(<CalendarLinks />);
    const resetBtn = screen.getByText(/сбросить токен/i);
    fireEvent.click(resetBtn);
    await waitFor(() => {
      expect(screen.getByText('Ошибка')).toBeInTheDocument();
    });
  });
});
