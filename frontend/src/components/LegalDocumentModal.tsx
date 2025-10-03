import React, { useEffect } from 'react';
import Modal from './Modal';
import { useLegalDocument } from '../hooks/useLegalDocument';

interface LegalDocumentModalProps {
  documentPath: string;
  isOpen: boolean;
  onClose: () => void;
  title: string;
}

const LegalDocumentModal: React.FC<LegalDocumentModalProps> = ({
  documentPath,
  isOpen,
  onClose,
  title
}) => {
  const { content, isLoading, error, load } = useLegalDocument(documentPath);

  useEffect(() => {
    if (isOpen) {
      void load();
    }
  }, [isOpen, load]);

  if (!isOpen) {
    return null;
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title}>
      <div className="prose prose-sm max-w-none dark:prose-invert">
        {isLoading && <p>Загрузка…</p>}
        {error && !isLoading && <p className="text-red-600">{error}</p>}
        {!isLoading && !error && (
          <div dangerouslySetInnerHTML={{ __html: content }} />
        )}
      </div>
    </Modal>
  );
};

export default LegalDocumentModal;
