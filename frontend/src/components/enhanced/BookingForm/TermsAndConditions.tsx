/**
 * Terms and Conditions Component
 * Компонент для принятия условий и соглашений
 */

import React, { useState } from 'react';
import { Controller, Control, FieldErrors } from 'react-hook-form';
import LegalDocumentModal from '../../LegalDocumentModal';

interface TermsAndConditionsProps {
  control: Control<any>;
  errors: FieldErrors<any>;
}

export const TermsAndConditions: React.FC<TermsAndConditionsProps> = ({
  control,
  errors
}) => {
  const [showTermsModal, setShowTermsModal] = useState(false);
  const [showPrivacyModal, setShowPrivacyModal] = useState(false);
  const [showRulesModal, setShowRulesModal] = useState(false);

  return (
    <div className="space-y-4">
      {/* Terms of Service */}
      <Controller
        name="terms_accepted"
        control={control}
        render={({ field: { value, onChange } }) => (
          <div className="flex items-start">
            <div className="flex items-center h-5">
              <input
                type="checkbox"
                checked={value || false}
                onChange={onChange}
                className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 dark:border-gray-600 rounded"
              />
            </div>
            <div className="ml-3 text-sm">
              <span className="text-gray-700 dark:text-gray-300">
                Я принимаю{' '}
                <button
                  type="button"
                  onClick={() => setShowTermsModal(true)}
                  className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 underline"
                >
                  условия публичной оферты
                </button>
              </span>
              {errors.terms_accepted && (
                <p className="mt-1 text-red-600">{errors.terms_accepted.message}</p>
              )}
            </div>
          </div>
        )}
      />

      {/* Privacy Policy */}
      <Controller
        name="privacy_accepted"
        control={control}
        render={({ field: { value, onChange } }) => (
          <div className="flex items-start">
            <div className="flex items-center h-5">
              <input
                type="checkbox"
                checked={value || false}
                onChange={onChange}
                className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 dark:border-gray-600 rounded"
              />
            </div>
            <div className="ml-3 text-sm">
              <span className="text-gray-700 dark:text-gray-300">
                Я даю согласие на{' '}
                <button
                  type="button"
                  onClick={() => setShowPrivacyModal(true)}
                  className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 underline"
                >
                  обработку персональных данных
                </button>
              </span>
              {errors.privacy_accepted && (
                <p className="mt-1 text-red-600">{errors.privacy_accepted.message}</p>
              )}
            </div>
          </div>
        )}
      />

      {/* Studio Rules */}
      <Controller
        name="studio_rules_accepted"
        control={control}
        render={({ field: { value, onChange } }) => (
          <div className="flex items-start">
            <div className="flex items-center h-5">
              <input
                type="checkbox"
                checked={value || false}
                onChange={onChange}
                className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 dark:border-gray-600 rounded"
              />
            </div>
            <div className="ml-3 text-sm">
              <span className="text-gray-700 dark:text-gray-300">
                Я ознакомился с{' '}
                <button
                  type="button"
                  onClick={() => setShowRulesModal(true)}
                  className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 underline"
                >
                  правилами студии
                </button>
              </span>
              {errors.studio_rules_accepted && (
                <p className="mt-1 text-red-600">{errors.studio_rules_accepted.message}</p>
              )}
            </div>
          </div>
        )}
      />

      {/* Terms Modal */}
      <LegalDocumentModal
        documentPath="/legal/public-offer.html"
        isOpen={showTermsModal}
        onClose={() => setShowTermsModal(false)}
        title="Публичная оферта"
      />

      <LegalDocumentModal
        documentPath="/legal/personal-data-consent.html"
        isOpen={showPrivacyModal}
        onClose={() => setShowPrivacyModal(false)}
        title="Политика обработки персональных данных"
      />

      <LegalDocumentModal
        documentPath="/legal/studio-rules.html"
        isOpen={showRulesModal}
        onClose={() => setShowRulesModal(false)}
        title="Правила студии"
      />
    </div>
  );
};

export default TermsAndConditions;
