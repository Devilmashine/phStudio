import FeatureCard from './FeatureCard';
import { StudioFeature } from '../../types/index';

interface StudioFeaturesProps {
  features: StudioFeature[];
  title?: string;
  className?: string;
  gridClassName?: string;
}

export default function StudioFeatures({ features, title = "Преимущества нашей студии", className = "", gridClassName = "grid-cols-1 md:grid-cols-2 gap-6" }: StudioFeaturesProps) {
  return (
    <div className={`py-8 px-6 ${className}`}>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">{title}</h2>
      <div className={`grid ${gridClassName}`}>
        {features.map((feature, index) => (
          <FeatureCard key={index} feature={feature} />
        ))}
      </div>
    </div>
  );
}