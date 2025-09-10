import React, { useState, ReactNode } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { 
  HomeIcon, 
  CogIcon, 
  PhotoIcon as PhotographIcon, 
  NewspaperIcon, 
  CalendarDaysIcon as CalendarIcon, 
  UserGroupIcon, 
  ChartBarIcon,
  Bars3Icon as MenuIcon,
  XMarkIcon as XIcon,
  MoonIcon,
  SunIcon
} from '@heroicons/react/24/outline';
import { useDarkMode } from '../../contexts/DarkModeContext';

interface AdminLayoutProps {
  children: ReactNode;
}

const navigation = [
  { name: 'Дашборд', href: 'dashboard', icon: HomeIcon },
  { name: 'Настройки студии', href: 'settings', icon: CogIcon },
  { name: 'Галерея', href: 'gallery', icon: PhotographIcon },
  { name: 'Новости', href: 'news', icon: NewspaperIcon },
  { name: 'Расписание', href: 'schedule', icon: CalendarIcon },
  { name: 'Календарь', href: 'calendar', icon: CalendarIcon },
  { name: 'Пользователи', href: 'users', icon: UserGroupIcon },
];

const AdminLayout: React.FC<AdminLayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const navigate = useNavigate();
  const { darkMode, toggleDarkMode } = useDarkMode();

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('user');
    localStorage.removeItem('token_exp');
    navigate('/login');
  };

  return (
    <div className={`flex h-screen ${darkMode ? 'dark bg-gray-900' : 'bg-gray-50'}`}>
      {/* Mobile sidebar */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 md:hidden">
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)} />
          <div className="relative flex-1 flex flex-col max-w-xs w-full bg-white dark:bg-gray-800">
            <div className="absolute top-0 right-0 -mr-12 pt-2">
              <button
                type="button"
                className="ml-1 flex items-center justify-center h-10 w-10 rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
                onClick={() => setSidebarOpen(false)}
              >
                <span className="sr-only">Закрыть меню</span>
                <XIcon className="h-6 w-6 text-white" aria-hidden="true" />
              </button>
            </div>
            <div className="flex-1 h-0 pt-5 pb-4 overflow-y-auto">
              <div className="flex-shrink-0 flex items-center px-4">
                <h1 className="text-xl font-bold text-indigo-600 dark:text-indigo-400">Админ-панель</h1>
              </div>
              <nav className="mt-5 px-2 space-y-1">
                {navigation.map((item) => (
                  <NavLink
                    key={item.name}
                    to={item.href}
                    className={({ isActive }) =>
                      isActive
                        ? 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-100 group flex items-center px-2 py-2 text-base font-medium rounded-md'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-white group flex items-center px-2 py-2 text-base font-medium rounded-md'
                    }
                  >
                    <item.icon
                      className="mr-4 flex-shrink-0 h-6 w-6 text-indigo-500 dark:text-indigo-400"
                      aria-hidden="true"
                    />
                    {item.name}
                  </NavLink>
                ))}
              </nav>
            </div>
          </div>
        </div>
      )}

      {/* Static sidebar for desktop */}
      <div className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0">
        <div className="flex-1 flex flex-col min-h-0 border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
          <div className="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto">
            <div className="flex items-center flex-shrink-0 px-4">
              <h1 className="text-xl font-bold text-indigo-600 dark:text-indigo-400">Админ-панель</h1>
            </div>
            <nav className="mt-5 flex-1 px-2 bg-white dark:bg-gray-800 space-y-1">
              {navigation.map((item) => (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={({ isActive }) =>
                    isActive
                      ? 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-100 group flex items-center px-2 py-2 text-sm font-medium rounded-md'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-white group flex items-center px-2 py-2 text-sm font-medium rounded-md'
                  }
                >
                  <item.icon
                    className="mr-3 flex-shrink-0 h-6 w-6 text-indigo-500 dark:text-indigo-400"
                    aria-hidden="true"
                  />
                  {item.name}
                </NavLink>
              ))}
            </nav>
          </div>
        </div>
      </div>

      <div className="md:pl-64 flex flex-col flex-1">
        <div className="sticky top-0 z-10 md:hidden pl-1 pt-1 sm:pl-3 sm:pt-3 bg-gray-50 dark:bg-gray-900">
          <button
            type="button"
            className="-ml-0.5 -mt-0.5 h-12 w-12 inline-flex items-center justify-center rounded-md text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500"
            onClick={() => setSidebarOpen(true)}
          >
            <span className="sr-only">Открыть меню</span>
            <MenuIcon className="h-6 w-6" aria-hidden="true" />
          </button>
        </div>
        <main className="flex-1">
          <div className="py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
              <div className="flex justify-between items-center py-4">
                <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Админ-панель</h1>
                <div className="flex items-center space-x-4">
                  <button
                    onClick={toggleDarkMode}
                    className="p-2 rounded-full text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    {darkMode ? (
                      <SunIcon className="h-5 w-5" aria-hidden="true" />
                    ) : (
                      <MoonIcon className="h-5 w-5" aria-hidden="true" />
                    )}
                  </button>
                  <button
                    onClick={handleLogout}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                  >
                    Выйти
                  </button>
                </div>
              </div>
              <div className="py-4">
                <div className="rounded-lg bg-white dark:bg-gray-800 shadow px-5 py-6 sm:px-6">
                  {children}
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;