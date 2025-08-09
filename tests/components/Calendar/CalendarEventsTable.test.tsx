import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import CalendarEventsTable from '../../../../frontend/src/components/Calendar/CalendarEventsTable';
import axios from 'axios';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('CalendarEventsTable', () => {
  const mockEvents = [
    {
      id: 1,
      title: 'Тестовое событие',
      start: '2025-07-15T10:00:00',
      end: '2025-07-15T11:00:00',
      status: 'pending',
      user_name: 'Admin',
    },
    {
      id: 2,
      title: 'Второе событие',
      start: '2025-07-16T12:00:00',
      end: '2025-07-16T13:00:00',
      status: 'confirmed',
      user_name: 'Manager',
    },
  ];

  beforeEach(() => {
    mockedAxios.get.mockResolvedValue({ data: mockEvents });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('отображает события и фильтры', async () => {
    render(<CalendarEventsTable />);
    expect(screen.getByLabelText('Фильтр по статусу')).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText('Тестовое событие')).toBeInTheDocument();
      expect(screen.getByText('Второе событие')).toBeInTheDocument();
    });
  });

  it('фильтрует события по статусу', async () => {
    render(<CalendarEventsTable />);
    fireEvent.change(screen.getByLabelText('Фильтр по статусу'), { target: { value: 'confirmed' } });
    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/calendar-events?status=confirmed');
    });
  });

  it('вызывает экспорт .ics при клике по кнопке', async () => {
    window.open = jest.fn();
    render(<CalendarEventsTable />);
    await waitFor(() => screen.getByText('Тестовое событие'));
    const exportBtn = screen.getAllByRole('button', { name: /добавить в календарь/i })[0];
    fireEvent.click(exportBtn);
    expect(window.open).toHaveBeenCalledWith('/api/calendar-events/ics/1', '_blank');
  });

  it('отображает ошибку при ошибке загрузки', async () => {
    mockedAxios.get.mockRejectedValueOnce(new Error('Ошибка'));
    render(<CalendarEventsTable />);
    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('Ошибка загрузки событий');
    });
  });
});
