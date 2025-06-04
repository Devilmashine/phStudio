import React from 'react';

interface TermsCheckboxesProps {
  termsAccepted: boolean;
  privacyAccepted: boolean;
  onTermsChange: (value: boolean) => void;
  onPrivacyChange: (value: boolean) => void;
  onShowTerms: () => void;
  onShowPrivacy: () => void;
}

const TermsCheckboxes = React.memo(({
  termsAccepted,
  privacyAccepted,
  onTermsChange,
  onPrivacyChange,
  onShowTerms,
  onShowPrivacy,
}: TermsCheckboxesProps) => {
  return (
    <div className="space-y-4">
      <label className="flex items-start space-x-3">
        <input
          type="checkbox"
          checked={termsAccepted}
          onChange={(e) => onTermsChange(e.target.checked)}
          className="mt-1"
          required
        />
        <span className="text-sm text-gray-600">
          Я принимаю условия{' '}
          <button
            type="button"
            onClick={onShowTerms}
            className="text-indigo-600 hover:underline"
          >
            публичной оферты
          </button>
        </span>
      </label>
      
      <label className="flex items-start space-x-3">
        <input
          type="checkbox"
          checked={privacyAccepted}
          onChange={(e) => onPrivacyChange(e.target.checked)}
          className="mt-1"
          required
        />
        <span className="text-sm text-gray-600">
          Я согласен на{' '}
          <button
            type="button"
            onClick={onShowPrivacy}
            className="text-indigo-600 hover:underline"
          >
            обработку персональных данных
          </button>
        </span>
      </label>
    </div>
  );
});

export default TermsCheckboxes;