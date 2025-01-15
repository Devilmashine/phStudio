interface StudioInfoProps {
  size: string;
  pricePerHour: number;
  sizeLabel?: string;
  priceLabel?: string;
}

export default function StudioInfo({ size, pricePerHour, sizeLabel = "Площадь студии", priceLabel = "Стоимость часа" }: StudioInfoProps) {
  return (
    <div className="flex justify-between items-center p-6 border-b border-gray-100">
      <div className="space-y-1">
        <span className="text-gray-600 text-sm">{sizeLabel}</span>
        <p className="text-lg font-medium">{size}</p>
      </div>
      <div className="text-right space-y-1">
        <span className="text-gray-600 text-sm">{priceLabel}</span>
        <p className="text-2xl font-bold text-indigo-600">
          {pricePerHour.toLocaleString('ru-RU')} ₽
        </p>
      </div>
    </div>
  );
}