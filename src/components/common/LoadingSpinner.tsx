interface LoadingSpinnerProps {
  size?: number; // Размер спиннера (ширина и высота)
  color?: string; // Цвет границы спиннера
  className?: string; // Дополнительные классы для контейнера
}

export default function LoadingSpinner({ size = 8, color = 'indigo-600', className = '' }: LoadingSpinnerProps) {
  // Стили для спиннера
  const spinnerStyle = {
    width: `${size * 0.25}rem`, // Переводим размер в rem (по умолчанию 2rem для size=8)
    height: `${size * 0.25}rem`, // Переводим размер в rem
    borderBottomColor: `var(--${color})`, // Используем CSS-переменную для цвета
  };

  return (
    <div className={`flex justify-center items-center p-4 ${className}`}>
      <div
        className="animate-spin rounded-full border-b-2"
        style={spinnerStyle}
      ></div>
    </div>
  );
}