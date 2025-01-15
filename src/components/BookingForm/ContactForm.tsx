import React, { useState } from 'react';
import { validatePhone, formatPhoneNumber } from '../../utils/validation/phoneValidation';

interface ContactFormProps {
  name: string;
  phone: string;
  onNameChange: (value: string) => void;
  onPhoneChange: (value: string) => void;
}

const ContactForm = React.memo(({ name, phone, onNameChange, onPhoneChange }: ContactFormProps) => {
  const [touched, setTouched] = useState({ name: false, phone: false });
  const [errors, setErrors] = useState({ name: '', phone: '' });

  const validateName = (value: string) => {
    if (!value.trim()) {
      return 'Имя обязательно для заполнения';
    }
    if (value.trim().length < 2) {
      return 'Имя должно содержать минимум 2 символа';
    }
    return '';
  };

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    onNameChange(value);
    if (touched.name) {
      setErrors(prev => ({ ...prev, name: validateName(value) }));
    }
  };

  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formattedPhone = formatPhoneNumber(e.target.value);
    onPhoneChange(formattedPhone);
    
    if (touched.phone) {
      setErrors(prev => ({
        ...prev,
        phone: validatePhone(formattedPhone) ? '' : 'Введите номер в формате +7 (9XX) XXX-XX-XX'
      }));
    }
  };

  const handleBlur = (field: 'name' | 'phone') => {
    setTouched(prev => ({ ...prev, [field]: true }));
    if (field === 'name') {
      setErrors(prev => ({ ...prev, name: validateName(name) }));
    } else {
      setErrors(prev => ({
        ...prev,
        phone: validatePhone(phone) ? '' : 'Введите номер в формате +7 (9XX) XXX-XX-XX'
      }));
    }
  };

  return (
    <>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Ваше имя
        </label>
        <input
          type="text"
          value={name}
          onChange={handleNameChange}
          onBlur={() => handleBlur('name')}
          className={`w-full p-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 ${
            errors.name && touched.name ? 'border-red-500' : 'border-gray-300'
          }`}
          required
          minLength={2}
          placeholder="Введите ваше имя"
        />
        {errors.name && touched.name && (
          <p className="mt-1 text-sm text-red-500">{errors.name}</p>
        )}
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Телефон
        </label>
        <input
          type="tel"
          value={phone || '+7'}
          onChange={handlePhoneChange}
          onBlur={() => handleBlur('phone')}
          className={`w-full p-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 ${
            errors.phone && touched.phone ? 'border-red-500' : 'border-gray-300'
          }`}
          required
          placeholder="+7 (9XX) XXX-XX-XX"
        />
        {errors.phone && touched.phone && (
          <p className="mt-1 text-sm text-red-500">{errors.phone}</p>
        )}
      </div>
    </>
  );
});

export default ContactForm;