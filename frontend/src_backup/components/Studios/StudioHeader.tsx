import React from 'react';

interface StudioHeaderProps {
  name: string;
  description: string;
  imageUrl: string;
  height?: string;
  gradient?: string;
}

export default function StudioHeader({ name, description, imageUrl, height = "h-96", gradient = "from-black/60 to-transparent" }: StudioHeaderProps) {
  return (
    <div className={`relative ${height}`}>
      <img
        src={imageUrl}
        alt={name}
        className="w-full h-full object-cover"
      />
      <div className={`absolute inset-0 bg-gradient-to-t ${gradient}`} />
      <div className="absolute bottom-0 left-0 right-0 p-6">
        <h3 className="text-3xl font-bold text-white mb-2">{name}</h3>
        <p className="text-white/90">{description}</p>
      </div>
    </div>
  );
}