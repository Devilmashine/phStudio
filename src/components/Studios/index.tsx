import { studio } from '../../data/studio';
import StudioHeader from './StudioHeader';
import StudioInfo from './StudioInfo';
import StudioFeatures from './StudioFeatures';
import EquipmentList from './EquipmentList';

interface StudiosProps {
  title?: string;
  description?: string;
  className?: string;
}

export default function Studios({ title = "Наша студия", description = "Профессиональное пространство для ваших съемок", className = "" }: StudiosProps) {
  return (
    <section id="studios" className={`py-20 bg-gray-50 ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">{title}</h2>
          <p className="text-xl text-gray-600">{description}</p>
        </div>

        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <StudioHeader
            name={studio.name}
            description={studio.description}
            imageUrl={studio.images[0]}
          />
          
          <StudioInfo
            size={studio.size}
            pricePerHour={studio.pricePerHour}
          />

          <StudioFeatures features={studio.features} />
          
          <EquipmentList equipment={studio.equipment} />
        </div>
      </div>
    </section>
  );
}