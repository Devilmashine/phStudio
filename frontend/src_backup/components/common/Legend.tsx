import React from 'react';

interface LegendItem {
  icon: React.ReactNode;
  label: string;
  description?: string;
}

interface LegendProps {
  items: LegendItem[];
  className?: string;
  compact?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export default function Legend({ items, className = '', compact = false, size = 'md' }: LegendProps) {
  const sizeClasses = {
    sm: compact ? "gap-2 text-xs" : "gap-3 text-xs", 
    md: compact ? "gap-3 text-xs" : "gap-4 text-sm",
    lg: compact ? "gap-4 text-sm" : "gap-4 text-base"
  };

  const baseClasses = "flex flex-wrap justify-center";
  const finalClasses = `${baseClasses} ${sizeClasses[size]} ${className}`;

  return (
    <div className={finalClasses}>
      {items.map((item, index) => (
        <div 
          key={index} 
          className="flex items-center gap-1.5 transition-opacity hover:opacity-80"
          title={item.description}
        >
          <div className="flex-shrink-0">{item.icon}</div>
          <span className="text-gray-700 whitespace-nowrap">{item.label}</span>
        </div>
      ))}
    </div>
  );
}

// Предустановленные наборы легенд для разных компонентов
export const CalendarLegendItems: LegendItem[] = [
  {
    icon: <div className="w-4 h-4 bg-green-100 border border-green-500 rounded"></div>,
    label: "Доступно",
    description: "Есть свободные слоты на этот день"
  },
  {
    icon: <div className="w-4 h-4 bg-yellow-100 border border-yellow-500 rounded"></div>,
    label: "Частично",
    description: "Есть и занятые, и свободные слоты"
  },
  {
    icon: <div className="w-4 h-4 bg-red-100 border border-red-500 rounded"></div>,
    label: "Занято", 
    description: "Все слоты на этот день заняты"
  }
];

export const TimeSlotsLegendItems: LegendItem[] = [
  {
    icon: <div className="w-4 h-4 bg-white border border-gray-400 rounded"></div>,
    label: "Доступно",
    description: "Слот можно выбрать"
  },
  {
    icon: (
      <div className="w-4 h-4 bg-gray-100 border border-gray-400 rounded relative">
        <span className="absolute -top-1 -right-1 text-red-600 text-xs leading-none"></span>
      </div>
    ),
    label: "Занято",
    description: "Слот уже забронирован"
  }
];