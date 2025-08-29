import React from 'react';

const Hero = React.memo(() => {
  return (
    <div className="relative h-screen">
      <div className="absolute inset-0">
        <img
          src="https://images.unsplash.com/photo-1610071780881-59bdd0183713?q=80&w=4140&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
          alt="Studio"
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-black/50" />
      </div>
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-full flex items-center">
        <div className="text-white max-w-3xl">
          <h1 className="text-5xl font-bold mb-6">Профессиональная фотостудия для вашего творчества</h1>
          <p className="text-xl mb-8">Пространства премиум-класса, профессиональное оборудование и исключительный сервис для фотографов, видеооператоров и креативщиков.</p>
          <div className="space-x-4">
            <a href="#booking" className="bg-indigo-600 text-white px-8 py-3 rounded-lg hover:bg-indigo-700 transition-colors inline-block">
              Забронировать
            </a>
            <a href="#studios" className="border-2 border-white text-white px-8 py-3 rounded-lg hover:bg-white/10 transition-colors inline-block">
              Подробнее
            </a>
          </div>
        </div>
      </div>
    </div>
  );
});

export default Hero;