import { FC } from 'react';
import { Aperture, Lightbulb, Layout, Palette, LucideIcon } from 'lucide-react';
import { StudioFeature } from '../../types';

const iconMap: Record<string, LucideIcon> = {
  Aperture,
  Lightbulb,
  Layout,
  Palette
};

interface FeatureCardProps {
  feature: StudioFeature;
}

const FeatureCard: FC<FeatureCardProps> = ({ feature }) => {
  const Icon = iconMap[feature.icon] || Aperture; // Fallback to Aperture if icon not found

  return (
    <div className="flex items-start space-x-4 p-6 rounded-lg bg-white shadow-sm hover:shadow-md transition-shadow">
      <div className="flex-shrink-0">
        <div className="p-3 bg-indigo-100 rounded-lg">
          <Icon className="w-6 h-6 text-indigo-600" />
        </div>
      </div>
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          {feature.title}
        </h3>
        <p className="text-gray-600 leading-relaxed">
          {feature.description}
        </p>
      </div>
    </div>
  );
};

export default FeatureCard;