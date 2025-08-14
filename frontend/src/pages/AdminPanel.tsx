import React, { useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';

const Sidebar = ({ open, onClose }: { open: boolean; onClose: () => void }) => (
  <aside
    className={`fixed z-40 top-0 left-0 h-full w-64 bg-gray-100 p-4 transition-transform duration-200 ease-in-out
      ${open ? 'translate-x-0' : '-translate-x-full'}
      md:static md:translate-x-0 md:w-64 md:block`}
    aria-label="Меню навигации"
  >
    <button
      className="md:hidden mb-4 text-gray-500 hover:text-gray-800 focus:outline-none"
      onClick={onClose}
      aria-label="Закрыть меню"
    >
      ✕
    </button>
    <nav className="flex flex-col gap-2">
      <NavLink to="dashboard" className={({ isActive }) => isActive ? 'font-bold text-blue-600' : ''}>Дашборд</NavLink>
      <NavLink to="settings" className={({ isActive }) => isActive ? 'font-bold text-blue-600' : ''}>Настройки студии</NavLink>
      <NavLink to="gallery" className={({ isActive }) => isActive ? 'font-bold text-blue-600' : ''}>Галерея</NavLink>
      <NavLink to="news" className={({ isActive }) => isActive ? 'font-bold text-blue-600' : ''}>Новости</NavLink>
      <NavLink to="schedule" className={({ isActive }) => isActive ? 'font-bold text-blue-600' : ''}>Расписание</NavLink>
      <NavLink to="calendar" className={({ isActive }) => isActive ? 'font-bold text-blue-600' : ''}>Календарь</NavLink>
      <NavLink to="users" className={({ isActive }) => isActive ? 'font-bold text-blue-600' : ''}>Пользователи</NavLink>
    </nav>
  </aside>
);

const AdminPanel: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const navigate = useNavigate();
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('user');
    localStorage.removeItem('token_exp');
    navigate('/login');
  };
  return (
    <div className="flex h-full min-h-screen pt-20 relative">
      {/* Кнопка-бургер для мобильных */}
      <button
        className="md:hidden fixed top-4 left-4 z-50 bg-white border rounded p-2 shadow"
        onClick={() => setSidebarOpen(true)}
        aria-label="Открыть меню"
      >
        <span className="block w-6 h-0.5 bg-gray-800 mb-1"></span>
        <span className="block w-6 h-0.5 bg-gray-800 mb-1"></span>
        <span className="block w-6 h-0.5 bg-gray-800"></span>
      </button>
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      {/* overlay для мобильного меню */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-30 z-30 md:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-label="Закрыть меню"
        />
      )}
      <main className="flex-1 p-2 sm:p-4 md:p-6 ml-0 md:ml-64 transition-all duration-200">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 gap-2">
          <h1 className="text-2xl font-bold">Админ-панель</h1>
          <button
            onClick={handleLogout}
            className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition-colors w-full sm:w-auto"
          >
            Выйти
          </button>
        </div>
        <Outlet />
      </main>
    </div>
  );
};

export default AdminPanel;
