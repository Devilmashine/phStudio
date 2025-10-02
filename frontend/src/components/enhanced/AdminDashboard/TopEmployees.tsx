import React from 'react';
import { CRMEmployeePerformance } from '../../../stores/types';

interface TopEmployeesProps {
  employees: CRMEmployeePerformance[];
}

export const TopEmployees: React.FC<TopEmployeesProps> = ({ employees }) => {
  if (!employees.length) {
    return (
      <div className="text-sm text-gray-500 dark:text-gray-400">
        Активные сотрудники появятся после создания учетных записей.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {employees.map(employee => (
        <div key={employee.employee_id} className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-900 dark:text-white">{employee.full_name}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">{employee.role}</p>
          </div>
          <div className="text-right">
            <p className="text-sm font-semibold text-indigo-600 dark:text-indigo-400">{employee.completed_bookings} завершено</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {employee.revenue_generated.toLocaleString('ru-RU')} ₽ выручки
            </p>
          </div>
        </div>
      ))}
    </div>
  );
};
