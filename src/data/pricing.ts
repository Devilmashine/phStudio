import { PricingPackage } from '../types';

export const pricingPackages: PricingPackage[] = [
  {
    id: 1,
    name: "Basic Session",
    price: 2999,
    duration: "2 часа",
    description: "Идеально для небольших фотосессий и портретной съемки",
    features: [
      "2 часа аренды студии",
      "Базовый набор света",
      "1 зал на выбор",
      "Помощь с настройкой света",
      "Гримерная комната",
      "Чай/кофе"
    ],
    recommended: false
  },
  {
    id: 2,
    name: "Professional",
    price: 5999,
    duration: "4 часа",
    description: "Оптимально для коммерческих съемок",
    features: [
      "4 часа аренды студии",
      "Расширенный набор света",
      "2 зала на выбор",
      "Ассистент фотографа",
      "Гримерная комната",
      "Кейтеринг",
      "Парковка"
    ],
    recommended: true
  },
  {
    id: 3,
    name: "Full Day",
    price: 9999,
    duration: "8 часов",
    description: "Для масштабных проектов и каталогов",
    features: [
      "8 часов аренды студии",
      "Полный набор света",
      "Все залы студии",
      "2 ассистента",
      "Гримерная комната",
      "Премиум кейтеринг",
      "Парковка",
      "Отдельная зона отдыха"
    ],
    recommended: false
  }
];