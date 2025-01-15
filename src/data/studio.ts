import { Studio } from '../types/index';

export const studio: Studio = {
  id: 1,
  name: "Фотостудия Light",
  description: "Профессиональная фотостудия с большой циклорамой и двумя тематическими зонами",
  size: "120м²",
  pricePerHour: 2500,
  features: [
    {
      id: "cyclorama",
      title: "Большая циклорама",
      description: "Профессиональная белая циклорама 5×3 метра с идеально ровными углами для рекламных съемок",
      icon: "Aperture"
    },
    {
      id: "lighting",
      title: "Профессиональный свет",
      description: "Комплект импульсного света Profoto: 4 моноблока D1 Air и 2 аккумуляторных B1X с модификаторами",
      icon: "Lightbulb"
    },
    {
      id: "zones",
      title: "Тематические зоны",
      description: "Две отдельные зоны с уникальными интерьерами и реквизитом для разнообразных фотосессий",
      icon: "Layout"
    },
    {
      id: "decorations",
      title: "Сезонные декорации",
      description: "Регулярное обновление декораций под актуальные праздники и события для тематических съемок",
      icon: "Palette"
    }
  ],
  equipment: [
    "4 × Profoto D1 Air 1000Ws",
    "2 × Profoto B1X 500Ws TTL",
    "Софтбоксы и октабоксы разных размеров",
    "Рефлекторы, соты, шторки, флаги",
    "Стойки и журавли Manfrotto",
    "Радиосинхронизаторы Profoto Air",
    "Отражатели и лайт-диски",
    "Фоны бумажные разных цветов"
  ],
  images: [
    "https://images.unsplash.com/photo-1631759297023-bb5c5b354f57",
    "https://images.unsplash.com/photo-1631759297072-4f56d94fa4e8"
  ]
};