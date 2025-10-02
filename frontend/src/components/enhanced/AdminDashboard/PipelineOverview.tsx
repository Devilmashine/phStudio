import React from 'react';
import { CRMPipelineStage, BookingState } from '../../../stores/types';

interface PipelineOverviewProps {
  stages: CRMPipelineStage[];
  selectedState?: BookingState;
  onStageSelect?: (stage: CRMPipelineStage) => void;
}

export const PipelineOverview: React.FC<PipelineOverviewProps> = ({ stages, selectedState, onStageSelect }) => {
  const hasData = stages.some(stage => stage.count > 0);

  return (
    <div className="space-y-4">
      {stages.map(stage => {
        const isSelected = selectedState === stage.state;

        return (
          <button
            key={stage.state}
            type="button"
            onClick={() => onStageSelect?.(stage)}
            className={`w-full text-left space-y-1 p-3 rounded-md transition border ${
              isSelected
                ? 'border-indigo-500 shadow-sm bg-indigo-50/50 dark:bg-indigo-900/30'
                : 'border-transparent hover:border-indigo-200 dark:hover:border-indigo-700'
            }`}
          >
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-700 dark:text-gray-300 flex items-center gap-2">
                <span className={`inline-flex w-2 h-2 rounded-full ${isSelected ? 'bg-indigo-600' : 'bg-indigo-400 dark:bg-indigo-500'}`} />
                {stage.label}
              </span>
              <span className="font-semibold text-gray-900 dark:text-white">{stage.count}</span>
            </div>
            <div className="h-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                className={`h-full ${hasData ? 'bg-indigo-500' : 'bg-gray-400 dark:bg-gray-600'}`}
                style={{ width: `${hasData ? Math.min(stage.percentage, 100) : 0}%` }}
              />
            </div>
            <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
              <span>{stage.percentage.toFixed(1)}%</span>
              {isSelected && <span className="text-indigo-500 dark:text-indigo-300 font-semibold">Фильтр активен</span>}
              {!hasData && !isSelected && <span>Нет данных</span>}
            </div>
          </button>
        );
      })}

      {!hasData && (
        <div className="rounded-md border border-dashed border-gray-300 dark:border-gray-600 p-4 text-sm text-gray-500 dark:text-gray-400">
          Переходы по стадиям появятся после создания бронирований.
          Пока все значения равны нулю, но конвейер подготовлен и будет заполняться автоматически.
        </div>
      )}
    </div>
  );
};
