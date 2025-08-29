import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ClientEventsTable from '../ClientEventsTable';
import axios from 'axios';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('ClientEventsTable', () => {
  const mockEvents = [
    {
      id: 1,
      title: 'Открытие выставки',
      start: '2025-07-20T18:00:00',
      end: '2025-07-20T20:00:00',
      status: 'confirmed',
    },
  ];

  beforeEach(() => {
    mockedAxios.get.mockResolvedValue({ data: mockEvents });
  });
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('отображает события и кнопку экспорта', async () => {
    render(<ClientEventsTable />);
    await waitFor(() => {
      expect(screen.getByText('Открытие выставки')).toBeInTheDocument();
      expect(screen.getByText('Добавить в календарь')).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /добавить в календарь/i })).toHaveAttribute('href', expect.stringContaining('/ical'));
    });
  });

  it('отображает ошибку при ошибке загрузки', async () => {
    mockedAxios.get.mockRejectedValueOnce(new Error('Ошибка'));
    render(<ClientEventsTable />);
    await waitFor(() => {
      expect(screen.getByText('Ошибка загрузки событий')).toBeInTheDocument();
    });
  });
});
