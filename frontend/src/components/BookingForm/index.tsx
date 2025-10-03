import React from 'react';
import { useBookingForm } from '../../hooks/useBookingForm';
import Calendar from '../Calendar';
import TimeSlots from '../TimeSlots';
import BookingDetails from './BookingDetails';
import TermsCheckboxes from './TermsCheckboxes';
import ContactForm from './ContactForm';
import LegalDocumentModal from '../LegalDocumentModal';

const BookingForm = () => {
  const {
    selectedDate,
    selectedTimes,
    name,
    phone,
    termsAccepted,
    privacyAccepted,
    showTermsModal,
    showPrivacyModal,
    isSubmitting,
    formErrors,
    setName,
    setPhone,
    setTermsAccepted,
    setPrivacyAccepted,
    setShowTermsModal,
    setShowPrivacyModal,
    handleTimeSelect,
    handleDateChange,
    handleSubmit,
    totalPrice
  } = useBookingForm();

  return (
    <section id="booking" className="py-20">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">Забронировать студию</h2>
          <p className="text-xl text-gray-600">Выберите удобное время для съёмки</p>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          <fieldset disabled={isSubmitting} className="space-y-6 flex flex-col items-center lg:items-start">
            <div className="w-full max-w-md">
              <Calendar
                selectedDate={selectedDate}
                onChange={handleDateChange}
              />
            </div>

            {selectedDate && (
              <div className="w-full max-w-md">
                <TimeSlots
                  date={selectedDate}
                  selectedTimes={selectedTimes}
                  onSelectTime={handleTimeSelect}
                />
              </div>
            )}
          </fieldset>

          <form onSubmit={(e) => handleSubmit(e, totalPrice)} className="space-y-6 bg-white p-8 rounded-xl shadow-lg">
            <fieldset disabled={isSubmitting}>
              {formErrors.length > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <p className="text-sm font-medium text-red-800 mb-2">Пожалуйста, исправьте следующие ошибки:</p>
                  <ul className="list-disc list-inside text-sm text-red-700">
                    {formErrors.map((error, index) => (
                      <li key={index}>{error}</li>
                    ))}
                  </ul>
                </div>
              )}

              <ContactForm
                name={name}
                phone={phone}
                onNameChange={setName}
                onPhoneChange={setPhone}
              />

              <BookingDetails
                selectedDate={selectedDate}
                selectedTimes={selectedTimes}
                totalPrice={totalPrice}
              />

              <TermsCheckboxes
                termsAccepted={termsAccepted}
                privacyAccepted={privacyAccepted}
                onTermsChange={setTermsAccepted}
                onPrivacyChange={setPrivacyAccepted}
                onShowTerms={() => setShowTermsModal(true)}
                onShowPrivacy={() => setShowPrivacyModal(true)}
              />
            </fieldset>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Отправка...' : 'Забронировать'}
            </button>
          </form>
        </div>
      </div>

      <LegalDocumentModal
        isOpen={showTermsModal}
        onClose={() => setShowTermsModal(false)}
        title="Публичная оферта"
        documentPath="/legal/public-offer.html"
      />

      <LegalDocumentModal
        isOpen={showPrivacyModal}
        onClose={() => setShowPrivacyModal(false)}
        title="Согласие на обработку персональных данных"
        documentPath="/legal/personal-data-consent.html"
      />
    </section>
  );
};

export default BookingForm;
