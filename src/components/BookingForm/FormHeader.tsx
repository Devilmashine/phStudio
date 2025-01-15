import React from 'react';

const FormHeader = React.memo(() => {
  return (
    <div className="text-center mb-16">
      <h2 className="text-4xl font-bold text-gray-900 mb-4">
        Забронировать студию
      </h2>
      <p className="text-xl text-gray-600">
        Выберите удобное время для съёмки
      </p>
    </div>
  );
});

export default FormHeader;