/**
 * Client Info Form Component
 * Форма для ввода контактной информации клиента
 */

import React from 'react';
import { Controller, Control, FieldErrors } from 'react-hook-form';
import { PhoneInput } from '../../ui/PhoneInput';
import InputField from '../../ui/InputField';

interface ClientInfoFormProps {
  control: Control<any>;
  errors: FieldErrors<any>;
}

export const ClientInfoForm: React.FC<ClientInfoFormProps> = ({
  control,
  errors
}) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <Controller
        name="client_name"
        control={control}
        render={({ field }) => (
          <InputField
            {...field}
            label="Имя клиента"
            placeholder="Введите полное имя"
            required
            error={errors.client_name?.message}
            className="col-span-2 md:col-span-1"
          />
        )}
      />

      <Controller
        name="client_phone"
        control={control}
        render={({ field }) => (
          <PhoneInput
            {...field}
            label="Номер телефона"
            placeholder="+7 (999) 999-99-99"
            required
            error={errors.client_phone?.message}
            className="col-span-2 md:col-span-1"
          />
        )}
      />

      <Controller
        name="client_email"
        control={control}
        render={({ field }) => (
          <InputField
            {...field}
            type="email"
            label="Email (необязательно)"
            placeholder="client@example.com"
            error={errors.client_email?.message}
            className="col-span-2"
          />
        )}
      />
    </div>
  );
};

export default ClientInfoForm;
