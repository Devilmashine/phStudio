import { CheckCircle } from 'lucide-react';

interface EquipmentListProps {
  equipment: string[];
  title?: string;
  className?: string;
}

export default function EquipmentList({ equipment, title = "Профессиональное оборудование", className = "" }: EquipmentListProps) {
  return (
    <div className={`py-8 px-6 bg-gray-50 rounded-xl ${className}`}>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">{title}</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {equipment.map((item, index) => (
          <div key={index} className="flex items-center space-x-3 p-3 bg-white rounded-lg">
            <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
            <span className="text-gray-700">{item}</span>
          </div>
        ))}
      </div>
    </div>
  );
}