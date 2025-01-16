import React from 'react';
import { Camera } from 'lucide-react';

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
          <div>
            <button className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors">
              Contact Us
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
});

export default Navbar;