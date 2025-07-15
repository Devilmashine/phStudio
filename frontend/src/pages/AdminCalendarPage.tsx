import React from 'react';
import CalendarLinks from '../../components/Calendar/CalendarLinks';
import CalendarEventsTable from '../../components/Calendar/CalendarEventsTable';

const AdminCalendarPage: React.FC = () => {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Календарь событий</h1>
      <CalendarLinks />
      <CalendarEventsTable />
      {/* Здесь можно добавить таблицу событий, фильтры, экспорт, модерирование и т.д. */}
      <div className="mt-6 text-gray-600 text-sm">
        <p>В этом разделе вы можете получить ссылку для подписки на календарь событий студии (iCal/Webcal), а также сбросить токен доступа.</p>
        <p>Для экспорта отдельного события используйте кнопку "Добавить в календарь" в деталях события.</p>
      </div>
    </div>
  );
};

export default AdminCalendarPage;
