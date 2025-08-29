import React, { useState, useEffect } from 'react';

interface CookieCategory {
  name: string;
  description: string;
  examples: string[];
  retention: string;
  required: boolean;
}

const CookiePolicy: React.FC = () => {
  const [currentPreferences, setCurrentPreferences] = useState<Record<string, boolean>>({});

  useEffect(() => {
    // Load current cookie preferences
    const savedPreferences = localStorage.getItem('cookie_preferences');
    if (savedPreferences) {
      try {
        const preferences = JSON.parse(savedPreferences);
        setCurrentPreferences(preferences);
      } catch (error) {
        console.error('Failed to parse cookie preferences:', error);
      }
    }
  }, []);

  const cookieCategories: Record<string, CookieCategory> = {
    essential: {
      name: "Необходимые cookie",
      description: "Эти файлы cookie необходимы для работы сайта и не могут быть отключены в наших системах. Обычно они устанавливаются только в ответ на ваши действия, равнозначные запросу услуг, такие как настройка параметров конфиденциальности, вход в систему или заполнение форм.",
      examples: [
        "Сессионные идентификаторы",
        "Настройки безопасности",
        "Корзина покупок",
        "Состояние входа в систему"
      ],
      retention: "До закрытия браузера или окончания сессии",
      required: true
    },
    functional: {
      name: "Функциональные cookie",
      description: "Эти файлы cookie позволяют сайту обеспечивать улучшенную функциональность и персонализацию. Они могут устанавливаться нами или третьими сторонами, услуги которых мы добавили на наши страницы.",
      examples: [
        "Языковые предпочтения",
        "Региональные настройки",
        "Запомненные формы",
        "Пользовательские настройки интерфейса"
      ],
      retention: "До 1 года",
      required: false
    },
    analytics: {
      name: "Аналитические cookie",
      description: "Эти файлы cookie позволяют нам подсчитывать посещения и источники трафика, чтобы мы могли измерять и улучшать производительность нашего сайта. Они помогают нам узнать, какие страницы наиболее и наименее популярны, и увидеть, как посетители перемещаются по сайту.",
      examples: [
        "Google Analytics",
        "Счетчики посещений",
        "Карты кликов",
        "Аналитика производительности"
      ],
      retention: "До 2 лет",
      required: false
    },
    marketing: {
      name: "Маркетинговые cookie",
      description: "Эти файлы cookie могут устанавливаться через наш сайт нашими рекламными партнерами. Они могут использоваться этими компаниями для создания профиля ваших интересов и показа соответствующих объявлений на других сайтах.",
      examples: [
        "Рекламные идентификаторы",
        "Ретаргетинг",
        "Социальные сети",
        "Персонализированная реклама"
      ],
      retention: "До 1 года",
      required: false
    }
  };

  const handlePreferenceChange = async () => {
    // This would typically open the cookie consent banner
    // For now, we'll just scroll to top where the banner might be
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // Optionally trigger a custom event to show the consent banner
    window.dispatchEvent(new CustomEvent('showCookieConsent'));
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-3xl font-bold mb-6 text-gray-900">Политика использования файлов cookie</h1>
      
      <div className="prose max-w-none text-gray-700">
        <p className="text-sm text-gray-500 mb-6">
          <strong>Последнее обновление:</strong> {new Date().toLocaleDateString('ru-RU')}
        </p>

        <section className="mb-8">
          <h2 className="text-2xl font-bold mt-8 mb-4 text-gray-900">Что такое файлы cookie?</h2>
          <p className="mb-4">
            Файлы cookie — это небольшие текстовые файлы, которые сохраняются на вашем устройстве (компьютере, планшете или мобильном телефоне) 
            при посещении веб-сайта. Они широко используются для обеспечения работы веб-сайтов или повышения эффективности их работы, 
            а также для предоставления информации владельцам сайта.
          </p>
          <p className="mb-4">
            Наш сайт использует файлы cookie в соответствии с российским законодательством и требованиями защиты персональных данных 
            (Федеральный закон от 27.07.2006 № 152-ФЗ «О персональных данных»).
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold mt-8 mb-4 text-gray-900">Какие файлы cookie мы используем?</h2>
          
          <div className="grid gap-6">
            {Object.entries(cookieCategories).map(([key, category]) => (
              <div key={key} className="border border-gray-200 rounded-lg p-6 bg-gray-50">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-xl font-semibold text-gray-900">{category.name}</h3>
                  <div className="flex items-center gap-2">
                    {category.required ? (
                      <span className="bg-red-100 text-red-800 text-xs font-medium px-2.5 py-0.5 rounded">
                        Обязательные
                      </span>
                    ) : (
                      <span className={`text-xs font-medium px-2.5 py-0.5 rounded ${
                        currentPreferences[key] 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {currentPreferences[key] ? 'Включены' : 'Отключены'}
                      </span>
                    )}
                  </div>
                </div>
                
                <p className="text-gray-700 mb-4">{category.description}</p>
                
                <div className="mb-4">
                  <h4 className="font-medium text-gray-900 mb-2">Примеры использования:</h4>
                  <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                    {category.examples.map((example, index) => (
                      <li key={index}>{example}</li>
                    ))}
                  </ul>
                </div>
                
                <div className="text-sm text-gray-600">
                  <strong>Срок хранения:</strong> {category.retention}
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold mt-8 mb-4 text-gray-900">Управление файлами cookie</h2>
          
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
            <h3 className="font-semibold text-blue-900 mb-2">Изменение настроек на нашем сайте</h3>
            <p className="text-blue-800 mb-4">
              Вы можете в любое время изменить свои предпочтения относительно использования файлов cookie на нашем сайте.
            </p>
            <button
              onClick={handlePreferenceChange}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Изменить настройки cookie
            </button>
          </div>

          <div className="space-y-4">
            <h3 className="font-semibold text-gray-900">Настройки браузера</h3>
            <p className="text-gray-700">
              Большинство веб-браузеров позволяют управлять файлами cookie через настройки. Вы можете:
            </p>
            <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4">
              <li>Просматривать файлы cookie, сохраненные на вашем устройстве</li>
              <li>Удалять файлы cookie по отдельности или все сразу</li>
              <li>Блокировать файлы cookie с определенных сайтов</li>
              <li>Блокировать сторонние файлы cookie</li>
              <li>Удалять все файлы cookie при закрытии браузера</li>
            </ul>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold mt-8 mb-4 text-gray-900">Сторонние файлы cookie</h2>
          <p className="mb-4">
            Некоторые файлы cookie на нашем сайте могут быть размещены третьими сторонами, предоставляющими нам услуги. 
            Например, это могут быть:
          </p>
          <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4 mb-4">
            <li>Системы веб-аналитики для понимания того, как посетители используют наш сайт</li>
            <li>Рекламные сети для показа релевантной рекламы</li>
            <li>Социальные сети для интеграции с их платформами</li>
          </ul>
          <p className="text-gray-700">
            Мы не контролируем размещение этих файлов cookie, поэтому рекомендуем вам ознакомиться с политиками конфиденциальности 
            соответствующих третьих сторон для получения дополнительной информации.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold mt-8 mb-4 text-gray-900">Правовые основания</h2>
          <p className="mb-4">
            Использование файлов cookie осуществляется на следующих правовых основаниях:
          </p>
          <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4">
            <li><strong>Необходимые cookie:</strong> обеспечение работы сайта (законный интерес)</li>
            <li><strong>Функциональные cookie:</strong> улучшение пользовательского опыта (согласие)</li>
            <li><strong>Аналитические cookie:</strong> анализ использования сайта (согласие)</li>
            <li><strong>Маркетинговые cookie:</strong> персонализированная реклама (согласие)</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold mt-8 mb-4 text-gray-900">Обновления политики</h2>
          <p className="mb-4">
            Мы можем время от времени обновлять эту политику использования файлов cookie. Любые изменения будут опубликованы 
            на этой странице с указанием даты последнего обновления.
          </p>
          <p className="text-gray-700">
            Мы рекомендуем регулярно просматривать эту политику, чтобы быть в курсе любых изменений.
          </p>
        </section>

        <section className="mb-8 bg-gray-50 border border-gray-200 rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-4 text-gray-900">Контактная информация</h2>
          <p className="mb-4 text-gray-700">
            Если у вас есть вопросы о нашем использовании файлов cookie или этой политике, 
            пожалуйста, свяжитесь с нами:
          </p>
          <div className="text-gray-700 space-y-2">
            <p><strong>Email:</strong> privacy@photostudio.ru</p>
            <p><strong>Телефон:</strong> +7 (XXX) XXX-XX-XX</p>
            <p><strong>Адрес:</strong> г. Краснодар, ул. Монтажников, 1А, БЦ "Лидер", 7 этаж, офис 166</p>
          </div>
        </section>

        {/* Current preferences display */}
        {Object.keys(currentPreferences).length > 0 && (
          <section className="mb-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h2 className="text-xl font-bold mb-4 text-blue-900">Ваши текущие настройки</h2>
            <div className="grid grid-cols-2 gap-4">
              {Object.entries(cookieCategories).map(([key, category]) => (
                <div key={key} className="flex items-center justify-between">
                  <span className="text-blue-800">{category.name}:</span>
                  <span className={`font-medium ${
                    currentPreferences[key] || category.required ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {currentPreferences[key] || category.required ? 'Включены' : 'Отключены'}
                  </span>
                </div>
              ))}
            </div>
            <button
              onClick={handlePreferenceChange}
              className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm"
            >
              Изменить настройки
            </button>
          </section>
        )}
      </div>
    </div>
  );
};

export default CookiePolicy;