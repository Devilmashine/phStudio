/**
 * Terms and Conditions Component
 * Компонент для принятия условий и соглашений
 */

import React, { useState } from 'react';
import { Controller, Control, FieldErrors } from 'react-hook-form';
import Modal from '../../Modal';

interface TermsAndConditionsProps {
  control: Control<any>;
  errors: FieldErrors<any>;
}

export const TermsAndConditions: React.FC<TermsAndConditionsProps> = ({
  control,
  errors
}) => {
  const [showTermsModal, setShowTermsModal] = useState(false);
  const [showPrivacyModal, setShowPrivacyModal] = useState(false);
  const [showRulesModal, setShowRulesModal] = useState(false);

  return (
    <div className="space-y-4">
      {/* Terms of Service */}
      <Controller
        name="terms_accepted"
        control={control}
        render={({ field: { value, onChange } }) => (
          <div className="flex items-start">
            <div className="flex items-center h-5">
              <input
                type="checkbox"
                checked={value || false}
                onChange={onChange}
                className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 dark:border-gray-600 rounded"
              />
            </div>
            <div className="ml-3 text-sm">
              <span className="text-gray-700 dark:text-gray-300">
                Я принимаю{' '}
                <button
                  type="button"
                  onClick={() => setShowTermsModal(true)}
                  className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 underline"
                >
                  условия публичной оферты
                </button>
              </span>
              {errors.terms_accepted && (
                <p className="mt-1 text-red-600">{errors.terms_accepted.message}</p>
              )}
            </div>
          </div>
        )}
      />

      {/* Privacy Policy */}
      <Controller
        name="privacy_accepted"
        control={control}
        render={({ field: { value, onChange } }) => (
          <div className="flex items-start">
            <div className="flex items-center h-5">
              <input
                type="checkbox"
                checked={value || false}
                onChange={onChange}
                className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 dark:border-gray-600 rounded"
              />
            </div>
            <div className="ml-3 text-sm">
              <span className="text-gray-700 dark:text-gray-300">
                Я даю согласие на{' '}
                <button
                  type="button"
                  onClick={() => setShowPrivacyModal(true)}
                  className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 underline"
                >
                  обработку персональных данных
                </button>
              </span>
              {errors.privacy_accepted && (
                <p className="mt-1 text-red-600">{errors.privacy_accepted.message}</p>
              )}
            </div>
          </div>
        )}
      />

      {/* Studio Rules */}
      <Controller
        name="studio_rules_accepted"
        control={control}
        render={({ field: { value, onChange } }) => (
          <div className="flex items-start">
            <div className="flex items-center h-5">
              <input
                type="checkbox"
                checked={value || false}
                onChange={onChange}
                className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 dark:border-gray-600 rounded"
              />
            </div>
            <div className="ml-3 text-sm">
              <span className="text-gray-700 dark:text-gray-300">
                Я ознакомился с{' '}
                <button
                  type="button"
                  onClick={() => setShowRulesModal(true)}
                  className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 underline"
                >
                  правилами студии
                </button>
              </span>
              {errors.studio_rules_accepted && (
                <p className="mt-1 text-red-600">{errors.studio_rules_accepted.message}</p>
              )}
            </div>
          </div>
        )}
      />

      {/* Terms Modal */}
      <Modal
        isOpen={showTermsModal}
        onClose={() => setShowTermsModal(false)}
        title="Условия публичной оферты"
        size="lg"
      >
        <div className="prose prose-sm max-w-none dark:prose-invert">
          <h3>1. Общие положения</h3>
          <p>
            Настоящая публичная оферта (далее – «Оферта») является официальным предложением 
            ИП «Фотостудия» (далее – «Исполнитель») заключить договор оказания услуг по 
            предоставлению фотостудии в аренду.
          </p>
          
          <h3>2. Предмет договора</h3>
          <p>
            Исполнитель обязуется предоставить Заказчику в аренду фотостудию с оборудованием 
            на согласованное время, а Заказчик обязуется оплатить услуги в соответствии с 
            прейскурантом.
          </p>
          
          <h3>3. Порядок оказания услуг</h3>
          <ul>
            <li>Бронирование осуществляется через сайт или по телефону</li>
            <li>Подтверждение брони происходит после внесения предоплаты</li>
            <li>Отмена брони возможна не позднее чем за 24 часа</li>
          </ul>
          
          <h3>4. Стоимость услуг и порядок расчетов</h3>
          <p>
            Стоимость услуг определяется согласно действующему прейскуранту. Оплата 
            производится наличными или банковской картой.
          </p>
          
          <h3>5. Ответственность сторон</h3>
          <p>
            Заказчик несет полную материальную ответственность за сохранность 
            предоставленного оборудования и имущества студии.
          </p>
        </div>
      </Modal>

      {/* Privacy Modal */}
      <Modal
        isOpen={showPrivacyModal}
        onClose={() => setShowPrivacyModal(false)}
        title="Политика обработки персональных данных"
        size="lg"
      >
        <div className="prose prose-sm max-w-none dark:prose-invert">
          <h3>1. Общие положения</h3>
          <p>
            Настоящая Политика обработки персональных данных разработана в соответствии 
            с Федеральным законом от 27.07.2006 №152-ФЗ «О персональных данных».
          </p>
          
          <h3>2. Цели обработки персональных данных</h3>
          <ul>
            <li>Обработка заказов и бронирований</li>
            <li>Связь с клиентами</li>
            <li>Улучшение качества услуг</li>
            <li>Исполнение договорных обязательств</li>
          </ul>
          
          <h3>3. Состав персональных данных</h3>
          <p>
            Мы обрабатываем следующие категории персональных данных:
          </p>
          <ul>
            <li>ФИО</li>
            <li>Номер телефона</li>
            <li>Адрес электронной почты</li>
            <li>Данные о бронированиях</li>
          </ul>
          
          <h3>4. Сроки обработки персональных данных</h3>
          <p>
            Персональные данные обрабатываются в течение срока, необходимого для 
            достижения целей обработки, но не более 5 лет с момента последнего обращения.
          </p>
          
          <h3>5. Права субъекта персональных данных</h3>
          <p>
            Вы имеете право на доступ к своим персональным данным, их изменение, 
            удаление или ограничение обработки.
          </p>
        </div>
      </Modal>

      {/* Studio Rules Modal */}
      <Modal
        isOpen={showRulesModal}
        onClose={() => setShowRulesModal(false)}
        title="Правила студии"
        size="lg"
      >
        <div className="prose prose-sm max-w-none dark:prose-invert">
          <h3>Правила пользования фотостудией</h3>
          
          <h4>1. Общие правила</h4>
          <ul>
            <li>Прибытие строго в назначенное время</li>
            <li>Максимальное количество человек на съемке - 10</li>
            <li>Курение в студии запрещено</li>
            <li>Употребление алкоголя запрещено</li>
            <li>Еда и напитки разрешены только в специально отведенной зоне</li>
          </ul>
          
          <h4>2. Работа с оборудованием</h4>
          <ul>
            <li>Перемещение оборудования только с разрешения администратора</li>
            <li>Бережное обращение с техникой</li>
            <li>О любых поломках сообщать немедленно</li>
            <li>Самостоятельный ремонт оборудования запрещен</li>
          </ul>
          
          <h4>3. Безопасность</h4>
          <ul>
            <li>Соблюдение техники безопасности при работе с осветительным оборудованием</li>
            <li>Не оставлять включенное оборудование без присмотра</li>
            <li>В случае чрезвычайной ситуации обращаться к администратору</li>
          </ul>
          
          <h4>4. Уборка</h4>
          <ul>
            <li>Поддержание порядка в процессе съемки</li>
            <li>Уборка мусора после съемки</li>
            <li>Возвращение мебели и реквизита на место</li>
          </ul>
          
          <h4>5. Ответственность</h4>
          <p>
            За нарушение правил студии и причинение ущерба имуществу клиент несет 
            полную материальную ответственность согласно действующему прейскуранту.
          </p>
        </div>
      </Modal>
    </div>
  );
};

export default TermsAndConditions;
