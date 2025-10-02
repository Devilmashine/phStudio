import React from 'react';
import { Camera, UserCog } from 'lucide-react';

const Navbar = React.memo(() => {
  return (
    <nav className="fixed w-full bg-white/90 backdrop-blur-sm z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex items-center space-x-2">
            <Camera className="h-8 w-8 text-indigo-600" />
            <span className="text-xl font-bold text-gray-900">LuxeStudio</span>
          </div>
          <div className="hidden md:flex space-x-8">
            <a href="#studios" className="text-gray-700 hover:text-indigo-600 transition-colors">Studios</a>
            <a href="#booking" className="text-gray-700 hover:text-indigo-600 transition-colors">Book Now</a>
          </div>
          <div className="flex items-center space-x-3">
            <button className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors">
              Contact Us
            </button>
            {/* Минимальный вход для сотрудников */}
            <a
              href="/admin"
              className="inline-flex items-center justify-center w-10 h-10 border border-indigo-600 rounded-full text-indigo-600 hover:bg-indigo-50 transition-colors"
              aria-label="Вход для сотрудников"
            >
              <UserCog className="h-5 w-5" />
            </a>
          </div>
        </div>
      </div>
    </nav>
  );
});

export default Navbar;