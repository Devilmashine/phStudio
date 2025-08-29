import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

interface CookieConsent {
  essential: boolean;
  functional: boolean;
  analytics: boolean;
  marketing: boolean;
}

interface CookieCategory {
  name: string;
  description: string;
  required: boolean;
}

const CookieConsentBanner: React.FC = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [consents, setConsents] = useState<CookieConsent>({
    essential: true, // Always required
    functional: false,
    analytics: false,
    marketing: false
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const cookieCategories: Record<keyof CookieConsent, CookieCategory> = {
    essential: {
      name: "Необходимые cookie",
      description: "Обеспечивают базовую функциональность сайта и не могут быть отключены",
      required: true
    },
    functional: {
      name: "Функциональные cookie",
      description: "Запоминают ваши настройки и предпочтения для улучшения опыта использования",
      required: false
    },
    analytics: {
      name: "Аналитические cookie",
      description: "Помогают нам понимать, как посетители взаимодействуют с сайтом",
      required: false
    },
    marketing: {
      name: "Маркетинговые cookie",
      description: "Используются для показа персонализированной рекламы",
      required: false
    }
  };

  useEffect(() => {
    // Check if user has already given consent
    const hasConsent = localStorage.getItem('cookie_consent_recorded');
    const consentDate = localStorage.getItem('cookie_consent_date');
    
    // Show banner if no consent or consent is older than 1 year
    if (!hasConsent || !consentDate) {
      setIsVisible(true);
    } else {
      const consentTimestamp = parseInt(consentDate, 10);
      const oneYearAgo = Date.now() - (365 * 24 * 60 * 60 * 1000);
      if (consentTimestamp < oneYearAgo) {
        setIsVisible(true);
      }
    }

    // Load previous preferences if they exist
    const savedPreferences = localStorage.getItem('cookie_preferences');
    if (savedPreferences) {
      try {
        const preferences = JSON.parse(savedPreferences);
        setConsents(preferences);
      } catch (error) {
        console.error('Failed to parse saved cookie preferences:', error);
      }
    }
  }, []);

  const recordConsent = async (consentData: CookieConsent) => {
    setIsSubmitting(true);
    
    try {
      const acceptedCategories = Object.entries(consentData)
        .filter(([_, accepted]) => accepted)
        .map(([category, _]) => category);

      const response = await fetch('/api/consent/cookie-consent/record', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ 
          accepted_categories: acceptedCategories 
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      // Save preferences locally
      localStorage.setItem('cookie_consent_recorded', 'true');
      localStorage.setItem('cookie_consent_date', Date.now().toString());
      localStorage.setItem('cookie_preferences', JSON.stringify(consentData));
      
      // Set consent cookies for immediate use
      acceptedCategories.forEach(category => {
        document.cookie = `cookie_consent_${category}=true; path=/; max-age=31536000; SameSite=Lax`;
      });

      console.log('Cookie consent recorded successfully:', result);
      setIsVisible(false);
      
    } catch (error) {
      console.error('Failed to record cookie consent:', error);
      // Still hide banner and save locally as fallback
      localStorage.setItem('cookie_consent_recorded', 'true');
      localStorage.setItem('cookie_consent_date', Date.now().toString());
      localStorage.setItem('cookie_preferences', JSON.stringify(consentData));
      setIsVisible(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAcceptAll = () => {
    const allConsents = {
      essential: true,
      functional: true,
      analytics: true,
      marketing: true
    };
    recordConsent(allConsents);
  };

  const handleRejectNonEssential = () => {
    const essentialOnly = {
      essential: true,
      functional: false,
      analytics: false,
      marketing: false
    };
    recordConsent(essentialOnly);
  };

  const handleCustomSave = () => {
    recordConsent(consents);
  };

  const handleCategoryChange = (category: keyof CookieConsent, value: boolean) => {
    if (category === 'essential') return; // Essential cookies cannot be disabled
    
    setConsents(prev => ({
      ...prev,
      [category]: value
    }));
  };

  if (!isVisible) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-gray-900 text-white p-4 z-50 shadow-lg border-t-2 border-blue-500">
      <div className="max-w-6xl mx-auto">
        {!showDetails ? (
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex-1">
              <h3 className="font-semibold mb-2 text-lg">Использование файлов cookie</h3>
              <p className="text-sm text-gray-300 leading-relaxed">
                Мы используем файлы cookie для обеспечения работы сайта, анализа использования и улучшения вашего опыта. 
                Продолжая использовать сайт, вы соглашаетесь с нашей{' '}
                <Link 
                  to="/cookie-policy" 
                  className="underline text-blue-300 hover:text-blue-200 transition-colors"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  политикой использования cookie
                </Link>
                .
              </p>
            </div>
            <div className="flex gap-2 flex-wrap justify-center">
              <button
                onClick={handleRejectNonEssential}
                disabled={isSubmitting}
                className="px-4 py-2 border border-gray-500 rounded-lg text-sm hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Только необходимые
              </button>
              <button
                onClick={() => setShowDetails(true)}
                disabled={isSubmitting}
                className="px-4 py-2 border border-gray-500 rounded-lg text-sm hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Настроить
              </button>
              <button
                onClick={handleAcceptAll}
                disabled={isSubmitting}
                className="px-6 py-2 bg-blue-600 rounded-lg text-sm hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {isSubmitting ? 'Сохранение...' : 'Принять все'}
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-lg">Настройки файлов cookie</h3>
              <button
                onClick={() => setShowDetails(false)}
                className="text-gray-400 hover:text-white transition-colors"
                aria-label="Закрыть настройки"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {Object.entries(cookieCategories).map(([key, category]) => (
                <div key={key} className="space-y-3">
                  <label className="flex items-start space-x-3 cursor-pointer">
                    <div className="mt-1">
                      <input
                        type="checkbox"
                        checked={consents[key as keyof CookieConsent]}
                        onChange={(e) => handleCategoryChange(key as keyof CookieConsent, e.target.checked)}
                        disabled={category.required || isSubmitting}
                        className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2 disabled:opacity-50"
                      />
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-white flex items-center gap-2">
                        {category.name}
                        {category.required && (
                          <span className="text-xs bg-red-600 text-white px-2 py-1 rounded">
                            Обязательные
                          </span>
                        )}
                      </div>
                      <div className="text-sm text-gray-300 mt-1 leading-relaxed">
                        {category.description}
                      </div>
                    </div>
                  </label>
                </div>
              ))}
            </div>

            <div className="pt-4 border-t border-gray-700">
              <div className="flex justify-between items-center">
                <button
                  onClick={() => setShowDetails(false)}
                  disabled={isSubmitting}
                  className="px-4 py-2 border border-gray-500 rounded-lg text-sm hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Назад
                </button>
                <div className="flex gap-2">
                  <button
                    onClick={handleRejectNonEssential}
                    disabled={isSubmitting}
                    className="px-4 py-2 border border-gray-500 rounded-lg text-sm hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Отклонить все
                  </button>
                  <button
                    onClick={handleCustomSave}
                    disabled={isSubmitting}
                    className="px-6 py-2 bg-blue-600 rounded-lg text-sm hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                  >
                    {isSubmitting ? 'Сохранение...' : 'Сохранить настройки'}
                  </button>
                </div>
              </div>
            </div>

            <div className="text-xs text-gray-400 pt-2 border-t border-gray-700">
              <p>
                Вы можете изменить эти настройки в любое время. Подробнее о том, как мы используем cookie, читайте в нашей{' '}
                <Link 
                  to="/cookie-policy" 
                  className="underline hover:text-gray-300 transition-colors"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  политике использования cookie
                </Link>
                .
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CookieConsentBanner;