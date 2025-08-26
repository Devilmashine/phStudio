import React from 'react';

interface SubmitButtonProps {
  isValid: boolean;
}

const SubmitButton = React.memo(({ isValid }: SubmitButtonProps) => {
  return (
    <button
      type="submit"
      disabled={!isValid}
      className="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
    >
      Отправить заявку
    </button>
  );
});

export default SubmitButton;