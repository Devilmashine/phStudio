import React from 'react';
import { Camera, Mail, Phone, MapPin } from 'lucide-react';

const Footer = React.memo(() => {
  return (
    <footer className="bg-gray-900 text-white py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <Camera className="h-8 w-8 text-indigo-400" />
              <span className="text-xl font-bold">Эф Студия</span>
            </div>
            <p className="text-gray-400">
              Профессиональная фотостудия для фотографов, видеооператоров и креативщиков.
            </p>
            <p className="text-gray-400">
              Сайт создан @Devilmashine
            </p>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-4">Навигация</h3>
            <ul className="space-y-2">
              <li><a href="#studios" className="text-gray-400 hover:text-white">Пространство</a></li>
              <li><a href="#portfolio" className="text-gray-400 hover:text-white">Portfolio</a></li>
              <li><a href="#pricing" className="text-gray-400 hover:text-white">Pricing</a></li>
              <li><a href="#booking" className="text-gray-400 hover:text-white">Book Now</a></li>
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-4">Контакты</h3>
            <ul className="space-y-2">
              <li className="flex items-center space-x-2">
                <Phone className="h-5 w-5 text-indigo-400" />
                <span className="text-gray-400">+1 (555) 123-4567</span>
              </li>
              <li className="flex items-center space-x-2">
                <Mail className="h-5 w-5 text-indigo-400" />
                <span className="text-gray-400">info@luxestudio.com</span>
              </li>
              <li className="flex items-center space-x-2">
                <MapPin className="h-5 w-5 text-indigo-400" />
                <span className="text-gray-400">г. Краснодар, ул. Монтажников, 1А, БЦ "Лидер", 7 этаж, офис 166</span>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-4">Часы работы</h3>
            <ul className="space-y-2 text-gray-400">
              <li>Ежедневно: 9:00 - 20:00</li>
            </ul>
          </div>
        </div>
        <div className="border-t border-gray-800 mt-12 pt-8 text-center text-gray-400">
          <p>&copy; {new Date().getFullYear()} эФ Студия. Все права защищены.</p>
        </div>
      </div>
    </footer>
  );
});

export default Footer;