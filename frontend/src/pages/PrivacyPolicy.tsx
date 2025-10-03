import React, { useEffect } from 'react';
import { useLegalDocument } from '../hooks/useLegalDocument';

const PrivacyPolicy: React.FC = () => {
  const { content, isLoading, error, load } = useLegalDocument('/legal/privacy-policy.html');

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-4">Политика конфиденциальности</h1>
      <div className="prose max-w-none">
        {isLoading && <p>Загрузка…</p>}
        {error && !isLoading && <p className="text-red-600">{error}</p>}
        {!isLoading && !error && (
          <div dangerouslySetInnerHTML={{ __html: content }} />
        )}
      </div>
    </div>
  );
};

export default PrivacyPolicy;
