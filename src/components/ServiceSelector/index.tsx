import React from 'react';
import { 
  FormControl, 
  InputLabel, 
  MenuItem, 
  Select, 
  SelectChangeEvent,
  Box,
  Typography,
  Paper
} from '@mui/material';
import { Camera, Video, Package } from 'lucide-react';

interface ServiceSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

const services = [
  { 
    id: 'photo', 
    name: 'Фотосессия', 
    price: 2000,
    icon: Camera,
    description: 'Профессиональная фотосъемка'
  },
  { 
    id: 'video', 
    name: 'Видеосъемка', 
    price: 3000,
    icon: Video,
    description: 'Съемка и монтаж видео'
  },
  { 
    id: 'both', 
    name: 'Фото + Видео', 
    price: 4500,
    icon: Package,
    description: 'Комплексная съемка'
  }
];

export const ServiceSelector: React.FC<ServiceSelectorProps> = ({ value = '', onChange }) => {
  const handleChange = (event: SelectChangeEvent) => {
    onChange(event.target.value);
  };

  return (
    <Box sx={{ mt: 3 }}>
      <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
        Выберите услугу
      </Typography>
      <Box 
        display="grid" 
        gridTemplateColumns={{
          xs: '1fr',
          sm: 'repeat(2, 1fr)',
          md: 'repeat(3, 1fr)'
        }}
        gap={2}
      >
        {services.map((service) => {
          const Icon = service.icon;
          const isSelected = value === service.id;
          
          return (
            <Paper
              key={service.id}
              onClick={() => onChange(service.id)}
              elevation={isSelected ? 4 : 1}
              sx={{
                p: 2,
                cursor: 'pointer',
                bgcolor: isSelected ? 'primary.main' : 'background.paper',
                color: isSelected ? 'primary.contrastText' : 'text.primary',
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  bgcolor: isSelected ? 'primary.dark' : 'primary.light',
                  color: 'primary.contrastText'
                }
              }}
            >
              <Box display="flex" flexDirection="column" alignItems="center" gap={1}>
                <Icon size={24} />
                <Typography variant="h6">{service.name}</Typography>
                <Typography variant="body2" align="center">
                  {service.description}
                </Typography>
                <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                  {service.price} ₽/час
                </Typography>
              </Box>
            </Paper>
          );
        })}
      </Box>
    </Box>
  );
}; 