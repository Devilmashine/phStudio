/**
 * Validates a phone number string
 * @param phone Phone number to validate
 * @returns true if the phone number is valid, false otherwise
 */
export function validatePhone(phone: string): boolean {
  // Удаляем все нецифровые символы
  const cleanPhone = phone.replace(/\D/g, '');

  // Проверяем что номер не пустой и не только код страны
  if (cleanPhone.length < 11 || cleanPhone === '7') {
    return false;
  }

  // Строгая проверка российских мобильных номеров
  // Поддерживаем форматы: 79XXXXXXXXX, 89XXXXXXXXX, 9XXXXXXXXX
  const mobilePhoneRegex = /^(7|8)?9\d{9}$/;
  
  // Проверяем что номер соответствует формату мобильного телефона
  if (mobilePhoneRegex.test(cleanPhone)) {
    return true;
  }

  return false;
}

/**
 * Форматирует номер телефона в читаемый вид
 * @param phone Номер телефона для форматирования
 * @returns Отформатированный номер телефона
 */
export function formatPhone(phone: string): string {
  const cleanPhone = phone.replace(/\D/g, '');
  
  // Если номер не соответствует ожидаемому формату, возвращаем как есть
  if (!validatePhone(cleanPhone)) {
    return phone;
  }

  // Добавляем 7 в начало, если номер из 10 цифр
  const normalizedPhone = cleanPhone.length === 10 ? `7${cleanPhone}` : cleanPhone;

  // Форматируем номер: +7 (9XX) XXX-XX-XX
  return normalizedPhone.replace(
    /(\d)(\d{3})(\d{3})(\d{2})(\d{2})/,
    '+$1 ($2) $3-$4-$5'
  );
}

/**
 * Validates an email address
 * @param email Email address to validate
 * @returns true if the email is valid, false otherwise
 */
export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validates a name string
 * @param name Name to validate
 * @returns true if the name is valid, false otherwise
 */
export function validateName(name: string): boolean {
  // Более строгая проверка имени
  const nameRegex = /^[А-ЯЁа-яё\s-]{2,50}$/;
  return nameRegex.test(name.trim());
}
