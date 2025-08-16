import React, { useEffect, useState } from 'react';
import { Box, Typography, CircularProgress, Paper } from '@mui/material';
import { Dayjs } from 'dayjs';
import { getAvailableSlots } from '../../data/availability';
import { BookingSlot } from '../../types/index';

interface TimeSelectorProps {
  date: Dayjs;
  selectedTimes: string[];
  onTimeSelect: (times: string[]) => void;
}

export const TimeSelector: React.FC<TimeSelectorProps> = ({
  date,
  selectedTimes,
  onTimeSelect
}) => {
  const [slots, setSlots] = useState<BookingSlot[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSlots = async () => {
      try {
        setLoading(true);
        const dateStr = date.format('YYYY-MM-DD');
        const response = await getAvailableSlots(dateStr);
        setSlots(response.slots || []);
        setError(null);
      } catch (err) {
        setError('Ошибка при загрузке доступного времени');
        console.error('Error fetching slots:', err);
      } finally {
        setLoading(false);
      }
    };

    if (date) {
      fetchSlots();
    }
  }, [date]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Paper elevation={0} sx={{ p: 2, bgcolor: 'error.light', color: 'error.contrastText' }}>
        <Typography align="center">
          {error}
        </Typography>
      </Paper>
    );
  }

  if (!slots.length) {
    return (
      <Paper elevation={0} sx={{ p: 2, bgcolor: 'warning.light' }}>
        <Typography align="center">
          Нет доступных слотов на выбранную дату
        </Typography>
      </Paper>
    );
  }

  return (
    <Box sx={{ mt: 3 }}>
      <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
        Выберите время
      </Typography>
      <Box 
        display="grid" 
        gridTemplateColumns={{
          xs: 'repeat(2, 1fr)',
          sm: 'repeat(3, 1fr)',
          md: 'repeat(4, 1fr)'
        }}
        gap={2}
      >
        {slots.map((slot) => (
          <Paper
            key={slot.time}
            onClick={() => {
              if (!slot.available) return;
              const isSelected = selectedTimes.includes(slot.time);
              const newTimes = isSelected
                ? selectedTimes.filter(t => t !== slot.time)
                : [...selectedTimes, slot.time].sort();
              onTimeSelect(newTimes);
            }}
            elevation={selectedTimes.includes(slot.time) ? 4 : 1}
            sx={{
              p: 2,
              cursor: slot.available ? 'pointer' : 'not-allowed',
              bgcolor: selectedTimes.includes(slot.time)
                ? 'primary.main'
                : slot.available
                  ? 'background.paper'
                  : 'action.disabledBackground',
              color: selectedTimes.includes(slot.time)
                ? 'primary.contrastText'
                : slot.available
                  ? 'text.primary'
                  : 'text.disabled',
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                transform: slot.available ? 'translateY(-2px)' : 'none',
                bgcolor: slot.available
                  ? selectedTimes.includes(slot.time)
                    ? 'primary.dark'
                    : 'primary.light'
                  : 'action.disabledBackground'
              }
            }}
          >
            <Typography 
              align="center" 
              variant="subtitle1" 
              sx={{ fontWeight: selectedTimes.includes(slot.time) ? 'bold' : 'normal' }}
            >
              {slot.time}
            </Typography>
          </Paper>
        ))}
      </Box>
    </Box>
  );
}; 