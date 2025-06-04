import React from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';

const Sidebar = () => (
  <aside className="w-64 bg-gray-100 h-full p-4">
    <nav className="flex flex-col gap-2">
      <NavLink to="dashboard" className={({ isActive }) => isActive ? 'font-bold text-blue-600' : ''}>Дашборд</NavLink>
      <NavLink to="settings" className={({ isActive }) => isActive ? 'font-bold text-blue-600' : ''}>Настройки студии</NavLink>
      <NavLink to="gallery" className={({ isActive }) => isActive ? 'font-bold text-blue-600' : ''}>Галерея</NavLink>
      <NavLink to="news" className={({ isActive }) => isActive ? 'font-bold text-blue-600' : ''}>Новости</NavLink>
      <NavLink to="schedule" className={({ isActive }) => isActive ? 'font-bold text-blue-600' : ''}>Расписание</NavLink>
    </nav>
  </aside>
);

const AdminPanel: React.FC = () => {
  const navigate = useNavigate();
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('user');
    localStorage.removeItem('token_exp');
    navigate('/login');
  };
  return (
    <div className="flex h-full min-h-screen pt-20">
      {/* pt-20 добавляет отступ сверху для предотвращения наезда на header */}
      <Sidebar />
      <main className="flex-1 p-6">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold">Админ-панель</h1>
          <button
            onClick={handleLogout}
            className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition-colors"
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
