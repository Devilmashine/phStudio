import React from 'react';

const BookingPage: React.FC = () => {
  return (
    <div>
      <h1>Booking Page Placeholder</h1>
      <form>
        <label htmlFor="date">Дата</label>
        <input id="date" />
        <label htmlFor="time">Время</label>
        <input id="time" />
        <label htmlFor="name">Имя</label>
        <input id="name" />
        <label htmlFor="phone">Телефон</label>
        <input id="phone" />
        <label htmlFor="email">Email</label>
        <input id="email" />
        <label htmlFor="notes">Дополнительная информация</label>
        <textarea id="notes" />
        <button type="submit">Забронировать</button>
      </form>
    </div>
  );
};

export default BookingPage;
