import React from 'react';
import { useTheme } from './ThemeProvider';

export const ThemeSwitcher: React.FC = () => {
  const { theme, setTheme } = useTheme();

  return (
    <div className="flex gap-2">
      <button onClick={() => setTheme('light')} disabled={theme === 'light'}>Светлая</button>
      <button onClick={() => setTheme('dark')} disabled={theme === 'dark'}>Тёмная</button>
      <button onClick={() => setTheme('high-contrast')} disabled={theme === 'high-contrast'}>Контраст</button>
    </div>
  );
}; 