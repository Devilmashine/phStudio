import React, { useState, useEffect } from 'react';
import { CalendarService } from '../services/calendar';
import '../styles/Calendar.css';

interface CalendarEvent {
  id: string;
  title: string;
  start: string;
  end: string;
}

const Calendar: React.FC = () => {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentDate, setCurrentDate] = useState(new Date());

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        setLoading(true);
        const startDate = new Date(currentDate);
        startDate.setDate(1);
        const endDate = new Date(currentDate);
        endDate.setMonth(endDate.getMonth() + 1);
        endDate.setDate(0);

        const fetchedEvents = await CalendarService.getEvents(
          startDate.toISOString(),
          endDate.toISOString()
        );
        setEvents(fetchedEvents);
        setError(null);
      } catch (err) {
        setError('Ошибка при загрузке событий');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, [currentDate]);

  const handlePrevMonth = () => {
    setCurrentDate(new Date(currentDate.setMonth(currentDate.getMonth() - 1)));
  };

  const handleNextMonth = () => {
    setCurrentDate(new Date(currentDate.setMonth(currentDate.getMonth() + 1)));
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('ru-RU', { month: 'long', year: 'numeric' });
  };

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const firstDayOfMonth = new Date(year, month, 1).getDay();
    
    const days = [];
    for (let i = 0; i < firstDayOfMonth; i++) {
      days.push(null);
    }
    
    for (let i = 1; i <= daysInMonth; i++) {
      days.push(new Date(year, month, i));
    }
    
    return days;
  };

  const days = getDaysInMonth(currentDate);
  const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

  if (loading) {
    return <div className="calendar-loading">Загрузка...</div>;
  }

  if (error) {
    return <div className="calendar-error">{error}</div>;
  }

  return (
    <div className="calendar">
      <div className="calendar-header">
        <h2 className="calendar-title">{formatDate(currentDate)}</h2>
        <div className="calendar-controls">
          <button className="calendar-button" onClick={handlePrevMonth}>
            Предыдущий месяц
          </button>
          <button className="calendar-button" onClick={handleNextMonth}>
            Следующий месяц
          </button>
        </div>
      </div>
      
      <div className="calendar-grid">
        {weekDays.map((day) => (
          <div key={day} className="calendar-day-header">
            {day}
          </div>
        ))}
        
        {days.map((day, index) => (
          <div key={index} className="calendar-day">
            {day && (
              <>
                <div className="calendar-day-header">{day.getDate()}</div>
                {events
                  .filter((event) => {
                    const eventDate = new Date(event.start);
                    return (
                      eventDate.getDate() === day.getDate() &&
                      eventDate.getMonth() === day.getMonth() &&
                      eventDate.getFullYear() === day.getFullYear()
                    );
                  })
                  .map((event) => (
                    <div key={event.id} className="calendar-event">
                      <div>{event.title}</div>
                      <div className="calendar-event-time">
                        {new Date(event.start).toLocaleTimeString('ru-RU', {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </div>
                    </div>
                  ))}
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Calendar; 