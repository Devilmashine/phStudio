import { useState } from 'react';

const usePhoneMask = (initialValue: string = '') => {
  const [value, setValue] = useState(initialValue);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputVal = e.target.value.replace(/\D/g, '');
    let formattedVal = '';

    if (inputVal.length > 0) {
      formattedVal = '+7 ';
      if (inputVal.length > 1) {
        formattedVal += '(' + inputVal.slice(1, 4);
      }
      if (inputVal.length > 4) {
        formattedVal += ') ' + inputVal.slice(4, 7);
      }
      if (inputVal.length > 7) {
        formattedVal += '-' + inputVal.slice(7, 9);
      }
      if (inputVal.length > 9) {
        formattedVal += '-' + inputVal.slice(9, 11);
      }
    }

    setValue(formattedVal);
  };

  return { value, handleChange, setValue };
};

export default usePhoneMask;
