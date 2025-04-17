import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-800 text-white">
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-lg font-semibold mb-4">О нас</h3>
            <p className="text-gray-300">
              Профессиональная фотостудия с современным оборудованием и опытной командой.
            </p>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-4">Контакты</h3>
            <ul className="space-y-2 text-gray-300">
              <li>Телефон: +7 (999) 123-45-67</li>
              <li>Email: info@photostudio.ru</li>
              <li>Адрес: г. Москва, ул. Примерная, д. 1</li>
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-4">Часы работы</h3>
            <ul className="space-y-2 text-gray-300">
              <li>Пн-Пт: 9:00 - 21:00</li>
              <li>Сб-Вс: 10:00 - 20:00</li>
            </ul>
          </div>
        </div>
        <div className="mt-8 pt-8 border-t border-gray-700 text-center text-gray-300">
          <p>&copy; {new Date().getFullYear()} Photo Studio. Все права защищены.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 