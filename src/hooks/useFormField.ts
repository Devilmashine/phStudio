import { useState } from 'react';

interface UseFormFieldProps<T> {
  initialValue: T;
  validate: (value: T) => string | undefined;
}

export function useFormField<T>({ initialValue, validate }: UseFormFieldProps<T>) {
  const [value, setValue] = useState<T>(initialValue);
  const [error, setError] = useState<string>();
  const [touched, setTouched] = useState(false);

  const handleChange = (newValue: T) => {
    setValue(newValue);
    if (touched) {
      const validationError = validate(newValue);
      setError(validationError);
    }
  };

  const handleBlur = () => {
    setTouched(true);
    const validationError = validate(value);
    setError(validationError);
  };

  const reset = () => {
    setValue(initialValue);
    setError(undefined);
    setTouched(false);
  };

  return {
    value,
    error,
    touched,
    handleChange,
    handleBlur,
    reset,
  };
}