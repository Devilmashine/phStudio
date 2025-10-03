import React from 'react';

export interface TermsCheckboxesProps {
  termsAccepted: boolean;
  privacyAccepted: boolean;
  onTermsChange: (value: boolean) => void;
  onPrivacyChange: (value: boolean) => void;
  onShowTerms: () => void;
  onShowPrivacy: () => void;
}

const TermsCheckboxes: React.FC<TermsCheckboxesProps> = ({
  termsAccepted,
  privacyAccepted,
  onTermsChange,
  onPrivacyChange,
  onShowTerms,
  onShowPrivacy
}) => (
  <div className="space-y-4">
    <label className="flex items-start space-x-3 cursor-pointer select-none">
      <input
        type="checkbox"
        checked={termsAccepted}
        onChange={(event) => onTermsChange(event.target.checked)}
        className="mt-1 accent-indigo-600 focus:ring-2 focus:ring-indigo-500 focus:outline-none transition-colors"
        required
      />
      <span className="text-sm text-gray-600">
        Я принимаю{' '}
        <button
          type="button"
          onClick={onShowTerms}
          className="text-indigo-600 hover:underline"
        >
          условия публичной оферты
        </button>
        {' '}и ознакомился с{' '}
        <a
          href="/legal/public-offer.html"
          target="_blank"
          rel="noopener noreferrer"
          className="text-indigo-600 hover:underline"
        >
          полным текстом
        </a>
      </span>
    </label>

    <label className="flex items-start space-x-3 cursor-pointer select-none">
      <input
        type="checkbox"
        checked={privacyAccepted}
        onChange={(event) => onPrivacyChange(event.target.checked)}
        className="mt-1 accent-indigo-600 focus:ring-2 focus:ring-indigo-500 focus:outline-none transition-colors"
        required
      />
      <span className="text-sm text-gray-600">
        Я даю{' '}
        <button
          type="button"
          onClick={onShowPrivacy}
          className="text-indigo-600 hover:underline"
        >
          согласие
        </button>
        {' '}на обработку персональных данных и прочитал(а){' '}
        <a
          href="/legal/personal-data-consent.html"
          target="_blank"
          rel="noopener noreferrer"
          className="text-indigo-600 hover:underline"
        >
          текст согласия
        </a>
      </span>
    </label>
  </div>
);

export default TermsCheckboxes;
