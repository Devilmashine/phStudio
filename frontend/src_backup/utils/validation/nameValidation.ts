export const validateName = (name: string): string | undefined => {
  if (!name.trim()) {
    return 'Имя обязательно для заполнения';
  }
  if (name.trim().length < 2) {
    return 'Имя должно содержать минимум 2 символа';
  }
  return undefined;
};