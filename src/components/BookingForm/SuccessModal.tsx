import React from 'react';
import Modal from '../Modal';

interface SuccessModalProps {
  isOpen: boolean;
  onClose: () => void;
  calendarUrl: string;
}

const SuccessModal = React.memo(({ isOpen, onClose, calendarUrl }: SuccessModalProps) => {
  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Заявка отправлена!"
    >
      <div className="space-y-4">
        <p className="text-gray-600">
          Спасибо за вашу заявку! Мы свяжемся с вами в ближайшее время для подтверждения бронирования.
        </p>
        <div className="flex justify-center">
          <a
            href={calendarUrl}
            download="booking.ics"
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            onClick={(e) => {
              e.stopPropagation();
            }}
          >
            Добавить в календарь
          </a>
        </div>
      </div>
    </Modal>
  );
});

export default SuccessModal;